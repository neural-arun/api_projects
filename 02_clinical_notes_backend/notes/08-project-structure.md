# Project Structure

## Why Structure Matters

Build 1 had everything in `main.py` — 135 lines. That's fine for learning.

Build 2 will have models, database setup, Alembic config, multiple route files, CRUD logic, and error handling. If everything is in one file, it becomes unreadable.

The rule: **Separate concerns.** Each file has one job.

## The Structure

```
02_clinical_notes_backend/
├── app/
│   ├── __init__.py          # Empty file — makes app/ a Python package
│   ├── main.py              # FastAPI app instance, startup events
│   ├── database.py          # Engine, session, get_session dependency
│   ├── models.py            # SQLModel table definitions + Pydantic schemas
│   ├── crud.py              # Database operation functions
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── patients.py      # /patients routes
│   │   └── notes.py         # /notes routes
│   └── dependencies.py      # Shared dependencies (if more complex)
├── alembic/
│   ├── env.py               # Alembic environment config
│   ├── script.py.mako
│   └── versions/            # Migration files
├── alembic.ini
├── .env                     # DATABASE_URL and secrets
├── requirements.txt
└── README.md
```

## What Each File Does

### `app/__init__.py`

Empty file. It tells Python "this directory is a package." Without it, you can't do `from app.database import get_session`.

### `app/main.py`

Entry point. Creates the FastAPI app, includes routers, and handles startup events.

```python
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import patients, notes

app = FastAPI(title="Clinical Notes API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(patients.router)
app.include_router(notes.router)
```

**Notice:** No route definitions here. Just imports and app setup.

### `app/database.py`

Everything related to database connection.

```python
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### `app/models.py`

All SQLModel table definitions and Pydantic schemas.

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class PatientBase(SQLModel):
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)


class Patient(PatientBase, table=True):
    __tablename__ = "patients"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    notes: list["Note"] = Relationship(back_populates="patient")


class PatientCreate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    created_at: datetime


class NoteBase(SQLModel):
    title: str = Field(max_length=200)
    content: str


class Note(NoteBase, table=True):
    __tablename__ = "notes"
    id: int | None = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    patient: Optional["Patient"] = Relationship(back_populates="notes")


class NoteCreate(NoteBase):
    pass


class NoteResponse(NoteBase):
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime
```

### `app/routers/patients.py`

All `/patients` routes.

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models import Patient, PatientCreate, PatientResponse
from app.database import get_session

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(patient: PatientCreate, session: Session = Depends(get_session)):
    db_patient = Patient.model_validate(patient)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient


@router.get("", response_model=list[PatientResponse])
def list_patients(session: Session = Depends(get_session)):
    patients = session.exec(select(Patient)).all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, session: Session = Depends(get_session)):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_update: PatientCreate,
    session: Session = Depends(get_session)
):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient_data = patient_update.model_dump(exclude_unset=True)
    db_patient.sqlmodel_update(patient_data)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient


@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, session: Session = Depends(get_session)):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    session.delete(db_patient)
    session.commit()
    return None
```

**Key pattern:** `APIRouter(prefix="/patients", tags=["Patients"])`
- `prefix` — all routes in this file start with `/patients`
- `tags` — groups endpoints in /docs UI

### `app/routers/notes.py`

All `/notes` and `/patients/{patient_id}/notes` routes.

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from app.models import Note, NoteCreate, NoteResponse, Patient
from app.database import get_session

router = APIRouter(tags=["Notes"])


@router.post("/patients/{patient_id}/notes", response_model=NoteResponse, status_code=201)
def create_note(
    patient_id: int,
    note: NoteCreate,
    session: Session = Depends(get_session)
):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db_note = Note.model_validate(note)
    db_note.patient_id = patient_id
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note


@router.get("/patients/{patient_id}/notes", response_model=list[NoteResponse])
def list_patient_notes(patient_id: int, session: Session = Depends(get_session)):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    statement = (
        select(Note)
        .where(Note.patient_id == patient_id)
        .order_by(Note.created_at.desc())
    )
    notes = session.exec(statement).all()
    return notes


@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_update: NoteCreate,
    session: Session = Depends(get_session)
):
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    note_data = note_update.model_dump(exclude_unset=True)
    db_note.sqlmodel_update(note_data)
    db_note.updated_at = datetime.now()
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note


@router.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: Session = Depends(get_session)):
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(db_note)
    session.commit()
    return None


@router.get("/notes/search", response_model=list[NoteResponse])
def search_notes(q: str, session: Session = Depends(get_session)):
    statement = select(Note).where(
        Note.content.contains(q) | Note.title.contains(q)
    )
    notes = session.exec(statement).all()
    return notes
```

### `app/crud.py` (Optional — for Cleaner Code)

As your project grows, routes can get bloated with database logic. Extracting CRUD into a separate file keeps routes thin:

```python
from sqlmodel import Session, select
from app.models import Patient, Note


def get_patient_or_404(session: Session, patient_id: int) -> Patient:
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


def create_patient_in_db(session: Session, patient_data) -> Patient:
    db_patient = Patient.model_validate(patient_data)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient
```

Then routes become one-liners:

```python
@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(patient: PatientCreate, session: Session = Depends(get_session)):
    return create_patient_in_db(session, patient)
```

## The Import Flow

```
main.py
  ├── imports app.database (engine, get_session, create_db_and_tables)
  ├── imports app.routers.patients (all /patients routes)
  └── imports app.routers.notes (all /notes routes)

app/routers/patients.py
  ├── imports app.models (Patient, PatientCreate, PatientResponse)
  └── imports app.database (get_session)

app/routers/notes.py
  ├── imports app.models (Note, NoteCreate, NoteResponse, Patient)
  └── imports app.database (get_session)
```

Each file imports only what it needs. No circular imports if structured this way.

## Running the App

```bash
uvicorn app.main:app --reload
```

**Note:** It's `app.main:app` not `main:app` — the app is inside the `app/` package.

## Summary

| Directory/File | Purpose |
|---|---|
| `app/` | Python package |
| `app/main.py` | App creation, router inclusion, startup |
| `app/database.py` | Engine, session, get_session |
| `app/models.py` | All SQLModel + Pydantic schemas |
| `app/crud.py` | Database operation functions (optional) |
| `app/routers/` | Route definitions by resource |
| `alembic/` | Migration files and config |
| `.env` | Environment variables (don't commit this) |

Next: Putting it all together — building the complete project from scratch.
