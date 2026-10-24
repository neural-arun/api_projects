from fastapi import APIRouter

from app.schemas.task import TaskResponse

router = APIRouter()


@router.get("/patients/{patient_id}/tasks", response_model=list[TaskResponse])
def list_patient_tasks(patient_id: int):
    """Temporary empty response; the in-memory store comes in a later step."""
    return []
