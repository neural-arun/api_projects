from datetime import datetime

from pydantic import BaseModel, field_validator


class TaskCreate(BaseModel):
    title: str
    due_at: datetime | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title must not be blank.")
        return value


class TaskReplace(BaseModel):
    title: str
    due_at: datetime | None
    completed: bool

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title must not be blank.")
        return value


class TaskUpdate(BaseModel):
    title: str | None = None
    due_at: datetime | None = None
    completed: bool | None = None

    @field_validator("title", "completed", mode="before")
    @classmethod
    def reject_null_for_non_nullable_fields(cls, value: object) -> object:
        if value is None:
            raise ValueError("This field cannot be null.")
        return value

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title must not be blank.")
        return value


class TaskResponse(BaseModel):
    id: int
    patient_id: int
    title: str
    due_at: datetime | None
    completed: bool
