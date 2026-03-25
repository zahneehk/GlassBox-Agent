"""GlassBox Orchestrator — Pydantic schemas for API request/response."""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


# ── Action Protocol (固定协议) ──────────────────────────────────────
class ActionPayload(BaseModel):
    """Single action to be dispatched to Runner."""
    action: str = Field(..., description="goto|click|type|press|wait_for|extract_text|screenshot")
    selector: str | None = Field(None, description="CSS selector for target element")
    value: str | None = Field(None, description="URL for goto, text for type, key for press")
    risk: str = Field("low", description="low|medium|high")
    timeout_ms: int = Field(10000, ge=1000, le=60000)


# ── Run Creation ────────────────────────────────────────────────────
class StepCreate(BaseModel):
    action: str
    selector: str | None = None
    value: str | None = None
    risk: str = "low"
    timeout_ms: int = 10000


class RunCreate(BaseModel):
    task_description: str = Field(..., min_length=1, max_length=2000)
    steps: list[StepCreate] = Field(..., min_length=1, max_length=100)


# ── Responses ───────────────────────────────────────────────────────
class StepResponse(BaseModel):
    id: str
    order: int
    action: str
    selector: str | None
    value: str | None
    risk: str
    timeout_ms: int
    status: str
    result: dict | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None

    class Config:
        from_attributes = True


class RunResponse(BaseModel):
    id: str
    task_description: str
    status: str
    container_id: str | None
    novnc_port: int | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    steps: list[StepResponse] = []

    class Config:
        from_attributes = True


class RunListResponse(BaseModel):
    id: str
    task_description: str
    status: str
    created_at: datetime
    step_count: int = 0

    class Config:
        from_attributes = True


# ── HITL Approval ───────────────────────────────────────────────────
class ApprovalRequest(BaseModel):
    step_id: str
    approved: bool = True
    reason: str | None = None
