"""Temporary in-memory storage for patient tasks."""

from typing import Any

from app.schemas.task import TaskCreate

TaskRecord = dict[str, Any]

_tasks_by_id: dict[int, TaskRecord] = {}
_next_task_id = 1


def create_task(patient_id: int, task_data: TaskCreate) -> TaskRecord:
    global _next_task_id

    task = {
        "id": _next_task_id,
        "patient_id": patient_id,
        **task_data.model_dump(),
        "completed": False,
    }
    _tasks_by_id[_next_task_id] = task
    _next_task_id += 1
    return task


def get_task(task_id: int) -> TaskRecord | None:
    return _tasks_by_id.get(task_id)


def list_tasks_for_patient(
    patient_id: int,
    completed: bool | None = None,
) -> list[TaskRecord]:
    return [
        task
        for task in _tasks_by_id.values()
        if task["patient_id"] == patient_id
        and (completed is None or task["completed"] == completed)
    ]


def update_task(task_id: int, changes: dict[str, Any]) -> TaskRecord | None:
    task = _tasks_by_id.get(task_id)
    if task is None:
        return None

    task.update(changes)
    return task


def delete_task(task_id: int) -> bool:
    return _tasks_by_id.pop(task_id, None) is not None
