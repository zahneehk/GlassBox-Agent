"""GlassBox Orchestrator — Run execution engine.

Handles the lifecycle: create run → provision container → dispatch steps → HITL → complete/fail.
"""
import asyncio
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.run import Run, Step, RunStatus, StepStatus, RiskLevel
from app.services.container import container_manager
from app.services.events import event_bus

VALID_ACTIONS = {"goto", "click", "type", "press", "wait_for", "extract_text", "screenshot"}


class RunEngine:
    """Orchestrates a single run from creation to completion."""

    async def create_run(self, db: AsyncSession, task_description: str, steps_data: list[dict]) -> Run:
        """Create a Run with Steps in the database."""
        run = Run(task_description=task_description, status=RunStatus.PENDING)
        db.add(run)
        await db.flush()

        for i, s in enumerate(steps_data):
            action = s["action"]
            if action not in VALID_ACTIONS:
                raise ValueError(f"Invalid action: {action}. Must be one of {VALID_ACTIONS}")
            step = Step(
                run_id=run.id,
                order=i,
                action=action,
                selector=s.get("selector"),
                value=s.get("value"),
                risk=RiskLevel(s.get("risk", "low")),
                timeout_ms=s.get("timeout_ms", 10000),
                status=StepStatus.PENDING,
            )
            db.add(step)

        await db.commit()
        await db.refresh(run, ["steps"])
        return run

    async def execute_run(self, db: AsyncSession, run_id: str):
        """Full run execution loop: provision → dispatch steps → complete."""
        run = await self._get_run(db, run_id)
        if not run:
            return

        try:
            # 1. Provision container
            await self._update_run_status(db, run, RunStatus.PROVISIONING)
            await event_bus.emit(run.id, "run_status", {"status": "provisioning"})

            info = await container_manager.create_container(run.id)
            run.container_id = info["container_id"]
            run.container_ip = info["container_ip"]
            run.novnc_port = info["novnc_port"]
            run.vnc_port = info["vnc_port"]
            run.runner_port = info["runner_port"]
            await db.commit()

            # Wait for runner to be ready
            await self._wait_for_runner(info["runner_port"])

            await self._update_run_status(db, run, RunStatus.RUNNING)
            await event_bus.emit(run.id, "run_status", {
                "status": "running",
                "novnc_port": info["novnc_port"],
                "container_id": info["container_id"],
            })

            # 2. Dispatch steps sequentially
            for step in sorted(run.steps, key=lambda s: s.order):
                if run.status == RunStatus.CANCELLED:
                    break

                # HITL check — system-level interception
                if step.risk == RiskLevel.HIGH:
                    step.status = StepStatus.AWAITING_APPROVAL
                    await db.commit()
                    await self._update_run_status(db, run, RunStatus.PAUSED)
                    await event_bus.emit(run.id, "hitl_pause", {
                        "step_id": step.id,
                        "step_order": step.order,
                        "action": step.action,
                        "selector": step.selector,
                        "value": step.value,
                        "risk": step.risk.value,
                    })
                    # Wait for approval (will be resumed by approve_step)
                    approved = await self._wait_for_approval(db, step)
                    if not approved:
                        step.status = StepStatus.SKIPPED
                        await db.commit()
                        await event_bus.emit(run.id, "step_skipped", {"step_id": step.id})
                        continue
                    await self._update_run_status(db, run, RunStatus.RUNNING)

                # Dispatch to runner
                step.status = StepStatus.EXECUTING
                step.started_at = datetime.now(timezone.utc)
                await db.commit()
                await event_bus.emit(run.id, "step_started", {
                    "step_id": step.id,
                    "order": step.order,
                    "action": step.action,
                })

                result = await self._dispatch_action(info["runner_port"], step)

                if result.get("success"):
                    step.status = StepStatus.COMPLETED
                    step.result = result.get("data")
                else:
                    step.status = StepStatus.FAILED
                    step.error_message = result.get("error", "Unknown error")

                step.completed_at = datetime.now(timezone.utc)
                await db.commit()
                await event_bus.emit(run.id, "step_completed", {
                    "step_id": step.id,
                    "status": step.status.value,
                    "result": step.result,
                    "error": step.error_message,
                })

                if step.status == StepStatus.FAILED:
                    raise RuntimeError(f"Step {step.order} failed: {step.error_message}")

            # 3. Complete
            await self._update_run_status(db, run, RunStatus.COMPLETED)
            await event_bus.emit(run.id, "run_status", {"status": "completed"})

        except Exception as e:
            run.status = RunStatus.FAILED
            run.error_message = str(e)
            await db.commit()
            await event_bus.emit(run.id, "run_status", {"status": "failed", "error": str(e)})

        finally:
            # GC: destroy container
            if run.container_id:
                await container_manager.destroy_container(run.container_id)

    async def approve_step(self, db: AsyncSession, run_id: str, step_id: str, approved: bool):
        """Approve or reject a HITL-paused step."""
        step = await db.get(Step, step_id)
        if not step or step.run_id != run_id:
            raise ValueError("Step not found")
        if step.status != StepStatus.AWAITING_APPROVAL:
            raise ValueError(f"Step is not awaiting approval (current: {step.status})")

        step.status = StepStatus.APPROVED if approved else StepStatus.SKIPPED
        await db.commit()
        await event_bus.emit(run_id, "hitl_resolved", {
            "step_id": step_id,
            "approved": approved,
        })

    # ── Private helpers ─────────────────────────────────────────────

    async def _get_run(self, db: AsyncSession, run_id: str) -> Run | None:
        result = await db.execute(
            select(Run).options(selectinload(Run.steps)).where(Run.id == run_id)
        )
        return result.scalar_one_or_none()

    async def _update_run_status(self, db: AsyncSession, run: Run, status: RunStatus):
        run.status = status
        run.updated_at = datetime.now(timezone.utc)
        await db.commit()

    async def _wait_for_runner(self, runner_port: int, max_retries: int = 30, interval: float = 1.0):
        """Poll runner /status until ready."""
        url = f"http://localhost:{runner_port}/status"
        async with httpx.AsyncClient() as client:
            for _ in range(max_retries):
                try:
                    resp = await client.get(url, timeout=2)
                    if resp.status_code == 200:
                        return
                except httpx.ConnectError:
                    pass
                await asyncio.sleep(interval)
        raise TimeoutError("Runner did not become ready in time")

    async def _dispatch_action(self, runner_port: int, step: Step) -> dict:
        """Send action to runner and return result."""
        url = f"http://localhost:{runner_port}/actions/execute"
        payload = {
            "task_id": step.run_id,
            "step_id": step.id,
            "action": step.action,
            "selector": step.selector,
            "value": step.value,
            "risk": step.risk.value,
            "timeout_ms": step.timeout_ms,
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json=payload, timeout=step.timeout_ms / 1000 + 5)
                return resp.json()
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def _wait_for_approval(self, db: AsyncSession, step: Step, poll_interval: float = 1.0) -> bool:
        """Poll DB for step approval status."""
        from app.core.config import settings
        elapsed = 0
        while elapsed < settings.hitl_timeout_seconds:
            await db.refresh(step)
            if step.status == StepStatus.APPROVED:
                return True
            if step.status == StepStatus.SKIPPED:
                return False
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        # Timeout → auto-reject
        step.status = StepStatus.SKIPPED
        await db.commit()
        return False


run_engine = RunEngine()
