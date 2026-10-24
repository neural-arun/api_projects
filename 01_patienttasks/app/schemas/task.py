from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    due_at: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    due_at: datetime | None = None
    completed: bool | None = None


class TaskResponse(BaseModel):
    id: int
    patient_id: int
    title: str
    due_at: datetime | None
    completed: bool
