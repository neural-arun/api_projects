import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import task_store


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_in_memory_tasks(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(task_store, "_tasks_by_id", {})
    monkeypatch.setattr(task_store, "_next_task_id", 1)


def create_task_request(
    client: TestClient,
    patient_id: int = 42,
    title: str = "Walk for 20 minutes",
    due_at: str | None = None,
):
    return client.post(
        f"/patients/{patient_id}/tasks",
        json={"title": title, "due_at": due_at},
    )


def test_create_and_list_tasks_for_the_correct_patient(client: TestClient):
    created = create_task_request(
        client,
        title="  Take medication  ",
    )

    assert created.status_code == 201
    assert created.json() == {
        "id": 1,
        "patient_id": 42,
        "title": "Take medication",
        "due_at": None,
        "completed": False,
    }

    patient_tasks = client.get("/patients/42/tasks")
    another_patient_tasks = client.get("/patients/43/tasks")

    assert patient_tasks.status_code == 200
    assert patient_tasks.json() == [created.json()]
    assert another_patient_tasks.json() == []


def test_list_filter_uses_completion_status(client: TestClient):
    first = create_task_request(client, title="Walk")
    second = create_task_request(client, title="Take medication")

    completed = client.patch(
        f"/tasks/{first.json()['id']}",
        json={"completed": True},
    )

    completed_tasks = client.get("/patients/42/tasks?completed=true")
    incomplete_tasks = client.get("/patients/42/tasks?completed=false")

    assert completed.status_code == 200
    assert completed_tasks.json() == [completed.json()]
    assert incomplete_tasks.json() == [second.json()]
    assert client.get("/patients/42/tasks?completed=maybe").status_code == 422


def test_patch_changes_only_sent_fields_and_put_replaces_editable_fields(
    client: TestClient,
):
    created = create_task_request(
        client,
        title="Morning walk",
        due_at="2027-02-03T09:30:00Z",
    )
    task_id = created.json()["id"]

    completed = client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert completed.status_code == 200
    assert completed.json()["title"] == "Morning walk"
    assert completed.json()["due_at"] == "2027-02-03T09:30:00Z"
    assert completed.json()["completed"] is True

    due_time_cleared = client.patch(
        f"/tasks/{task_id}",
        json={"due_at": None},
    )
    assert due_time_cleared.json()["due_at"] is None
    assert due_time_cleared.json()["completed"] is True

    replaced = client.put(
        f"/tasks/{task_id}",
        json={"title": "Evening walk", "due_at": None, "completed": False},
    )
    assert replaced.status_code == 200
    assert replaced.json()["title"] == "Evening walk"
    assert replaced.json()["due_at"] is None
    assert replaced.json()["completed"] is False


def test_invalid_input_is_rejected_without_changing_saved_tasks(
    client: TestClient,
):
    assert create_task_request(client, title="   ").status_code == 422
    assert create_task_request(client, due_at="not-a-date").status_code == 422
    assert client.get("/patients/42/tasks").json() == []

    created = create_task_request(client, title="Keep this task")
    task_id = created.json()["id"]
    invalid_update = client.patch(f"/tasks/{task_id}", json={"title": None})

    assert invalid_update.status_code == 422
    assert client.get(f"/tasks/{task_id}").json() == created.json()


def test_missing_tasks_and_delete_responses(client: TestClient):
    assert client.get("/tasks/999").status_code == 404

    created = create_task_request(client)
    task_id = created.json()["id"]
    deleted = client.delete(f"/tasks/{task_id}")

    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/tasks/{task_id}").status_code == 404
    assert client.delete(f"/tasks/{task_id}").status_code == 404
