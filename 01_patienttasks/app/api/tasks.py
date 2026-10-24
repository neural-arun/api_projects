from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.task import TaskCreate, TaskReplace, TaskResponse, TaskUpdate
from app.storage.task_store import (
    create_task,
    delete_task as delete_stored_task,
    get_task,
    list_tasks_for_patient,
    update_task,
)

router = APIRouter()


@router.get("/patients/{patient_id}/tasks", response_model=list[TaskResponse])
def list_patient_tasks(patient_id: int, completed: bool | None = None):
    return list_tasks_for_patient(patient_id, completed)


@router.post(
    "/patients/{patient_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient_task(patient_id: int, task_data: TaskCreate):
    return create_task(patient_id, task_data)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: int):
    task = get_task(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def replace_task(task_id: int, task_data: TaskReplace):
    task = update_task(task_id, task_data.model_dump())
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def patch_task(task_id: int, task_data: TaskUpdate):
    changes = task_data.model_dump(exclude_unset=True)
    task = update_task(task_id, changes)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def remove_task(task_id: int):
    if not delete_stored_task(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
