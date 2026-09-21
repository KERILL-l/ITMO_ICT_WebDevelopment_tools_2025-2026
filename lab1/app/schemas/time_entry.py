from datetime import datetime
from pydantic import BaseModel, Field


class TimeEntryCreate(BaseModel):
    duration_minutes: int = Field(..., gt=0)
    started_at: datetime
    ended_at: datetime | None = None
    comment: str | None = None


class TimeEntryRead(BaseModel):
    id: int
    task_id: int
    duration_minutes: int
    started_at: datetime
    ended_at: datetime | None
    comment: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TimeEntryUpdate(BaseModel):
    duration_minutes: int | None = Field(None, gt=0)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    comment: str | None = None
