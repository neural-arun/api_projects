# Testing with pytest

## Why Test Healthcare APIs

An untested appointment system can:
- Book two patients at the same time
- Cancel the wrong appointment
- Lose data on error

Tests catch these before they reach production.

## pytest Basics

```bash
pip install pytest httpx
```

```python
# tests/test_simple.py
def test_addition():
    assert 1 + 1 == 2

def test_string():
    assert "hello".upper() == "HELLO"
```

Run with:
```bash
pytest                          # discover and run all tests
pytest -v                       # verbose output
pytest tests/test_simple.py     # specific file
pytest -k "appointment"         # run tests matching name
```

## TestClient — Testing FastAPI Endpoints

```python
# tests/test_appointments.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_patient():
    response = client.post("/patients", json={
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "123-456-7890"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert "id" in data
```

## Testing with a Database — Fixtures

Use pytest fixtures to create a fresh test database for each test.

```python
# tests/conftest.py
import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_session

# Use SQLite in-memory for tests
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})


def override_get_session():
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def session():
    with Session(engine) as s:
        yield s
```

Now tests use the fixtures:

```python
def test_book_appointment(client, session):
    # Create patient
    patient_resp = client.post("/patients", json={"name": "Jane", "email": "j@e.com", "phone": "111"})
    patient_id = patient_resp.json()["id"]

    # Create doctor
    doctor_resp = client.post("/doctors", json={"name": "Dr. Smith", "specialty": "Cardiology"})
    doctor_id = doctor_resp.json()["id"]

    # Book appointment
    resp = client.post("/appointments", json={
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_time": "2026-07-20T09:00:00",
        "duration_minutes": 30
    })
    assert resp.status_code == 201
```

## Unit Tests vs Integration Tests

| Test type | What it tests | Speed | Example |
|---|---|---|---|
| Unit | Single function/class | Fast (ms) | `test_check_conflict()` |
| Integration | Multiple components | Medium (s) | `test_book_appointment()` |
| End-to-end | Full system | Slow (min) | UI → API → DB |

**Focus on integration tests for APIs.** Unit test service methods in isolation.

```python
# Unit test for service method
def test_check_conflict_detects_overlap(session):
    from app.services.appointment_service import AppointmentService
    service = AppointmentService(session)

    # Create an appointment first
    start = datetime(2026, 7, 20, 9, 0)
    end = datetime(2026, 7, 20, 9, 30)
    session.add(Appointment(doctor_id=1, patient_id=1, start_time=start, end_time=end, status="scheduled"))
    session.commit()

    # Should detect overlap
    assert service.check_conflict(1, start, end) is True
    assert service.check_conflict(1, start + timedelta(minutes=15), end + timedelta(minutes=15)) is True
    assert service.check_conflict(1, end, end + timedelta(hours=1)) is False
```

## Mocking External Services

If your service sends emails or SMS, mock them in tests.

```python
from unittest.mock import patch


def test_appointment_creates_notification(client):
    with patch("app.services.notification.send_email") as mock_send:
        resp = client.post("/appointments", json={...})
        assert resp.status_code == 201
        mock_send.assert_called_once()
```

## References

- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest docs](https://docs.pytest.org/)
- [pytest fixtures](https://docs.pytest.org/en/stable/fixture.html)
