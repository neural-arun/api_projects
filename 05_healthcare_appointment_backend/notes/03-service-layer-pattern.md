# Service Layer Pattern

## What Is a Service Layer?

The service layer is where **business logic** lives. It sits between the HTTP interface (routers) and the data layer (models/database).

| Layer | Job | Example |
|---|---|---|
| Router | HTTP concerns | Parse request, return 201/404/409 |
| Service | Business rules | "Can't double-book a doctor" |
| Model | Data access | Save appointment to DB |

## Why Separate Services?

Without services, routes get bloated:

```python
# BAD — all logic in route
@app.post("/appointments")
def book_appointment(data: AppointmentCreate, session: Session = Depends(get_session)):
    # Parse time
    start = datetime.fromisoformat(data.start_time)
    end = start + timedelta(minutes=30)

    # Check conflict
    existing = session.exec(
        select(Appointment).where(
            Appointment.doctor_id == data.doctor_id,
            Appointment.start_time < end,
            Appointment.end_time > start
        )
    ).first()
    if existing:
        raise HTTPException(409, "Time slot taken")

    # Create appointment
    apt = Appointment(doctor_id=data.doctor_id, patient_id=data.patient_id, ...)
    session.add(apt)
    session.commit()
    return apt
```

The route does too much. If you need the same logic elsewhere (e.g., an admin endpoint), you copy-paste and bugs multiply.

## With a Service Layer

```python
# app/services/appointment_service.py
from sqlmodel import Session, select
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate


class AppointmentService:
    def __init__(self, session: Session):
        self.session = session

    def check_conflict(self, doctor_id: int, start: datetime, end: datetime) -> bool:
        """Return True if appointment overlaps existing ones."""
        existing = self.session.exec(
            select(Appointment).where(
                Appointment.doctor_id == doctor_id,
                Appointment.start_time < end,
                Appointment.end_time > start
            )
        ).first()
        return existing is not None

    def create_appointment(self, data: AppointmentCreate) -> Appointment:
        start = data.start_time
        end = start + timedelta(minutes=data.duration_minutes)

        if self.check_conflict(data.doctor_id, start, end):
            raise ValueError("Time slot is already booked")

        apt = Appointment(
            patient_id=data.patient_id,
            doctor_id=data.doctor_id,
            start_time=start,
            end_time=end,
            status="scheduled"
        )
        self.session.add(apt)
        self.session.commit()
        self.session.refresh(apt)
        return apt
```

Now the route is thin:

```python
# app/routers/appointments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.services.appointment_service import AppointmentService
from app.schemas.appointment import AppointmentCreate, AppointmentResponse

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_appointment_service(session: Session = Depends(get_session)):
    return AppointmentService(session)


@router.post("", response_model=AppointmentResponse, status_code=201)
def book_appointment(
    data: AppointmentCreate,
    service: AppointmentService = Depends(get_appointment_service)
):
    try:
        return service.create_appointment(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
```

## Benefits of the Pattern

1. **Testability** — test `AppointmentService` directly without HTTP
2. **Reusability** — call `service.create_appointment()` from any route
3. **Separation of concerns** — route handles status codes, service handles rules
4. **Single responsibility** — each class has one reason to change

## Injecting Services via Depends()

FastAPI's `Depends()` isn't just for database sessions. Use it to inject services too.

```python
def get_patient_service(session: Session = Depends(get_session)):
    return PatientService(session)


def get_doctor_service(session: Session = Depends(get_session)):
    return DoctorService(session)
```

This keeps your route signatures clean and makes dependencies explicit.

## References

- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
