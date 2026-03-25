"""GlassBox Orchestrator — Run API routes."""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.run import Run, Step, RunStatus
from app.schemas.run import RunCreate, RunResponse, RunListResponse, ApprovalRequest
from app.services.engine import run_engine
from app.services.events import event_bus

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.post("", response_model=RunResponse, status_code=201)
async def create_run(body: RunCreate, db: AsyncSession = Depends(get_db)):
    """Create a new run with steps, then start execution in background."""
    steps_data = [s.model_dump() for s in body.steps]
    run = await run_engine.create_run(db, body.task_description, steps_data)

    # Fire-and-forget execution
    asyncio.create_task(_execute_in_new_session(run.id))

    return run


@router.get("", response_model=list[RunListResponse])
async def list_runs(limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """List recent runs."""
    result = await db.execute(
        select(Run).order_by(Run.created_at.desc()).offset(offset).limit(limit)
    )
    runs = result.scalars().all()
    out = []
    for r in runs:
        count_result = await db.execute(
            select(func.count()).select_from(Step).where(Step.run_id == r.id)
        )
        out.append(RunListResponse(
            id=r.id,
            task_description=r.task_description,
            status=r.status.value,
            created_at=r.created_at,
            step_count=count_result.scalar() or 0,
        ))
    return out


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    """Get run detail with all steps."""
    result = await db.execute(
        select(Run).options(selectinload(Run.steps)).where(Run.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post("/{run_id}/approve")
async def approve_step(run_id: str, body: ApprovalRequest, db: AsyncSession = Depends(get_db)):
    """Approve or reject a paused HITL step."""
    try:
        await run_engine.approve_step(db, run_id, body.step_id, body.approved)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{run_id}/cancel")
async def cancel_run(run_id: str, db: AsyncSession = Depends(get_db)):
    """Cancel a running/paused run."""
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status not in (RunStatus.RUNNING, RunStatus.PAUSED, RunStatus.PENDING, RunStatus.PROVISIONING):
        raise HTTPException(status_code=400, detail=f"Cannot cancel run in status {run.status}")
    run.status = RunStatus.CANCELLED
    await db.commit()
    await event_bus.emit(run.id, "run_status", {"status": "cancelled"})
    return {"ok": True}


@router.websocket("/ws/{run_id}")
async def run_websocket(websocket: WebSocket, run_id: str):
    """WebSocket endpoint for real-time run events."""
    await websocket.accept()
    event_bus.subscribe(run_id, websocket)
    try:
        while True:
            # Keep alive — client can send pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        event_bus.unsubscribe(run_id, websocket)


async def _execute_in_new_session(run_id: str):
    """Execute run in a fresh DB session (background task)."""
    from app.core.database import async_session
    async with async_session() as db:
        await run_engine.execute_run(db, run_id)
