# Project Structure & Architecture

## Why Structure Matters for Production

A single `main.py` works for 50 lines. For 5000 lines it becomes unreadable. Production apps separate concerns so each file has one job.

Think of a hospital:
- **Reception** (routers) — takes requests, gives responses
- **Doctor** (services) — makes decisions, applies business rules
- **Medical records** (models) — stores and retrieves data
- **Lab** (database) — the actual storage

## The Service Layer Pattern

```
HTTP Request
    │
    ▼
Router ───► Service ───► Model/Database
    │            │
    │            └── Business rules here
    │
    ▼
HTTP Response
```

### Routing layer (routers/)
- Parse the HTTP request
- Call the right service function
- Return the right status code and response

### Service layer (services/)
- Business logic (e.g. "no double booking")
- Calls database through models
- Raises domain-specific exceptions

### Data layer (models/, db/)
- SQLAlchemy/SQLModel table definitions
- Database connection and session management

## The Directory Structure

```
05_healthcare_appointment_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app, include routers
│   ├── config.py              # pydantic-settings
│   ├── database.py            # engine, session, get_session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── patient.py         # Patient table model
│   │   ├── doctor.py          # Doctor table model
│   │   └── appointment.py     # Appointment table model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── patient.py         # Pydantic request/response schemas
│   │   ├── doctor.py
│   │   └── appointment.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── patient_service.py
│   │   ├── doctor_service.py
│   │   └── appointment_service.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── patients.py
│   │   ├── doctors.py
│   │   └── appointments.py
│   └── dependencies.py        # Shared Depends() functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # pytest fixtures
│   ├── test_patients.py
│   ├── test_doctors.py
│   └── test_appointments.py
├── .env
├── requirements.txt
└── README.md
```

## Why Models/ and Schemas/ Are Separate

| Concerns | Models | Schemas |
|---|---|---|
| Purpose | Database table | API request/response |
| Base class | `SQLModel(table=True)` or `Base` | `BaseModel` |
| Fields | Includes DB columns, relationships | Only what the API exposes |
| Example | `Patient` with `hashed_password` | `PatientResponse` with no password |

## main.py

```python
from fastapi import FastAPI
from app.routers import patients, doctors, appointments

app = FastAPI(title="Healthcare Appointment API")

app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
```

No route definitions here. Just wiring.

## References

- [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI APIRouter](https://fastapi.tiangolo.com/reference/apirouter/)
