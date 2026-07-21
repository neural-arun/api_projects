# Building the Appointment System

## Models — SQLAlchemy Tables

```python
# app/models/patient.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(unique=True, max_length=100)
    phone: str = Field(max_length=20)
    created_at: datetime = Field(default_factory=datetime.now)
    appointments: list["Appointment"] = Relationship(back_populates="patient")
```

```python
# app/models/doctor.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Doctor(SQLModel, table=True):
    __tablename__ = "doctors"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    specialty: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)
    appointments: list["Appointment"] = Relationship(back_populates="doctor")
```

```python
# app/models/appointment.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    doctor_id: int = Field(foreign_key="doctors.id")
    start_time: datetime
    end_time: datetime
    status: str = Field(default="scheduled")  # scheduled, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.now)

    patient: Patient = Relationship(back_populates="appointments")
    doctor: Doctor = Relationship(back_populates="appointments")
```

## Schemas — Pydantic Request/Response

```python
# app/schemas/appointment.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: datetime
    duration_minutes: int = 30

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
```

## Service — Business Logic

```python
# app/services/appointment_service.py
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.appointment import AppointmentCreate


class AppointmentService:
    def __init__(self, session: Session):
        self.session = session

    def get_appointments(
        self,
        doctor_id: int | None = None,
        patient_id: int | None = None,
        date: str | None = None,
    ) -> list[Appointment]:
        query = select(Appointment)
        if doctor_id:
            query = query.where(Appointment.doctor_id == doctor_id)
        if patient_id:
            query = query.where(Appointment.patient_id == patient_id)
        if date:
            query = query.where(Appointment.start_time >= date)
        return self.session.exec(query.order_by(Appointment.start_time)).all()

    def check_conflict(self, doctor_id: int, start: datetime, end: datetime) -> bool:
        existing = self.session.exec(
            select(Appointment).where(
                Appointment.doctor_id == doctor_id,
                Appointment.status != "cancelled",
                Appointment.start_time < end,
                Appointment.end_time > start,
            )
        ).first()
        return existing is not None

    def create_appointment(self, data: AppointmentCreate) -> Appointment:
        start = data.start_time
        end = start + timedelta(minutes=data.duration_minutes)

        # Validate patient exists
        patient = self.session.get(Patient, data.patient_id)
        if not patient:
            raise ValueError("Patient not found")

        # Validate doctor exists
        doctor = self.session.get(Doctor, data.doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        # Check double booking
        if self.check_conflict(data.doctor_id, start, end):
            raise ValueError("Doctor is not available at this time")

        apt = Appointment(
            patient_id=data.patient_id,
            doctor_id=data.doctor_id,
            start_time=start,
            end_time=end,
            status="scheduled",
        )
        self.session.add(apt)
        self.session.commit()
        self.session.refresh(apt)
        return apt

    def cancel_appointment(self, appointment_id: int) -> Appointment:
        apt = self.session.get(Appointment, appointment_id)
        if not apt:
            raise ValueError("Appointment not found")
        if apt.status == "cancelled":
            raise ValueError("Appointment is already cancelled")
        apt.status = "cancelled"
        self.session.add(apt)
        self.session.commit()
        self.session.refresh(apt)
        return apt

    def reschedule_appointment(
        self, appointment_id: int, new_start: datetime, duration: int = 30
    ) -> Appointment:
        apt = self.session.get(Appointment, appointment_id)
        if not apt:
            raise ValueError("Appointment not found")
        if apt.status == "cancelled":
            raise ValueError("Cannot reschedule a cancelled appointment")

        end = new_start + timedelta(minutes=duration)
        if self.check_conflict(apt.doctor_id, new_start, end):
            raise ValueError("Doctor is not available at this time")

        apt.start_time = new_start
        apt.end_time = end
        self.session.add(apt)
        self.session.commit()
        self.session.refresh(apt)
        return apt
```

## Router — HTTP Endpoints

```python
# app/routers/appointments.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from datetime import datetime
from app.database import get_session
from app.services.appointment_service import AppointmentService
from app.schemas.appointment import AppointmentCreate, AppointmentResponse

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_service(session: Session = Depends(get_session)):
    return AppointmentService(session)


@router.get("", response_model=list[AppointmentResponse])
def list_appointments(
    doctor_id: int | None = Query(None),
    patient_id: int | None = Query(None),
    date: str | None = Query(None),
    service: AppointmentService = Depends(get_service),
):
    return service.get_appointments(doctor_id, patient_id, date)


@router.post("", response_model=AppointmentResponse, status_code=201)
def book_appointment(
    data: AppointmentCreate,
    service: AppointmentService = Depends(get_service),
):
    try:
        return service.create_appointment(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: int,
    service: AppointmentService = Depends(get_service),
):
    try:
        return service.cancel_appointment(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{appointment_id}/reschedule", response_model=AppointmentResponse)
def reschedule_appointment(
    appointment_id: int,
    new_start: datetime,
    duration: int = 30,
    service: AppointmentService = Depends(get_service),
):
    try:
        return service.reschedule_appointment(appointment_id, new_start, duration)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
```

## Patient and Doctor Routers

Similar CRUD pattern from Build 2, but routed through services:

```python
# app/routers/patients.py
router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("", response_model=list[PatientResponse])
def list_patients(session: Session = Depends(get_session)):
    return session.exec(select(Patient)).all()

@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(data: PatientCreate, session: Session = Depends(get_session)):
    patient = Patient.model_validate(data)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, session: Session = Depends(get_session)):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    return patient
```

## Business Rules Summary

| Rule | Implementation |
|---|---|
| No double booking | `check_conflict()` queries overlapping time ranges |
| Valid patient/doctor | Check existence before creating appointment |
| Can't cancel twice | Check `status != "cancelled"` |
| Can't reschedule cancelled | Raise ValueError |
| Default 30-min slots | `duration_minutes: int = 30` |
| Status tracking | `scheduled` → `completed` or `cancelled` |

## Database Setup

```python
# app/database.py
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

engine = create_engine(settings.database_url)

def get_session():
    with Session(engine) as session:
        yield session

def create_tables():
    SQLModel.metadata.create_all(engine)
```

## Running the App

```bash
uvicorn app.main:app --reload
```

## References

- [FastAPI SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLModel Relationships](https://sqlmodel.tiangolo.com/tutorial/relationship/)
