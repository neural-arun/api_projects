# Full Project Walkthrough — Build From Scratch

This is the cookbook. Follow these steps in order to build the entire Clinical Notes Backend.

---

## Step 1: Create the environment and install dependencies

```bash
cd 02_clinical_notes_backend

python -m venv .venv
source .venv/bin/activate

pip install fastapi uvicorn sqlmodel alembic psycopg2-binary python-dotenv
```

**What each package does:**
- `fastapi` — the web framework
- `uvicorn` — ASGI server to run FastAPI
- `sqlmodel` — ORM (database → Python)
- `alembic` — database migrations
- `psycopg2-binary` — PostgreSQL driver (lets Python talk to Postgres)
- `python-dotenv` — loads .env files

---

## Step 2: Set up PostgreSQL

```bash
# Create the database
createdb clinical_notes_db

# Or via psql:
psql -U postgres -c "CREATE DATABASE clinical_notes_db;"

# Verify it exists
psql -U postgres -c "\l" | grep clinical_notes_db
```

---

## Step 3: Create the .env file

```
# .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/clinical_notes_db
```

Replace `password` with your actual PostgreSQL password. If you're using the default `postgres` user with no password on Linux:

```
DATABASE_URL=postgresql://postgres@localhost:5432/clinical_notes_db
```

---

## Step 4: Create the project structure

```bash
mkdir -p app/routers
touch app/__init__.py
touch app/routers/__init__.py
```

---

## Step 5: Write app/database.py

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

---

## Step 6: Write app/models.py

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

---

## Step 7: Write app/routers/patients.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models import Patient, PatientCreate, PatientResponse
from app.database import get_session

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
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
    session: Session = Depends(get_session),
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


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, session: Session = Depends(get_session)):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    session.delete(db_patient)
    session.commit()
    return None
```

---

## Step 8: Write app/routers/notes.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from app.models import Note, NoteCreate, NoteResponse, Patient
from app.database import get_session

router = APIRouter(tags=["Notes"])


@router.post(
    "/patients/{patient_id}/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_note(
    patient_id: int,
    note: NoteCreate,
    session: Session = Depends(get_session),
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
    session: Session = Depends(get_session),
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


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
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

---

## Step 9: Write app/main.py

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

---

## Step 10: Run the app and verify

```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` and test:

```bash
# Create a patient
curl -X POST http://localhost:8000/patients \
  -H "Content-Type: application/json" \
  -d '{"name": "Priya Sharma", "age": 32, "gender": "Female"}'

# Create a note for that patient
curl -X POST http://localhost:8000/patients/1/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Initial Visit", "content": "Patient has fever and cough. Prescribed antibiotics."}'

# List patient notes (visit history)
curl http://localhost:8000/patients/1/notes

# Search notes
curl "http://localhost:8000/notes/search?q=fever"
```

---

## Step 11: Set up Alembic migrations

```bash
alembic init alembic
```

Edit `alembic.ini` — set `sqlalchemy.url` to match your `.env` DATABASE_URL (or configure `env.py` to read it from `.env`).

Edit `alembic/env.py`:
```python
from sqlmodel import SQLModel
from app.models import Patient, Note   # add these imports
target_metadata = SQLModel.metadata     # change None to this
```

Generate and apply the initial migration:
```bash
alembic revision --autogenerate -m "create patients and notes tables"
alembic upgrade head
```

Now when you change models:
```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

---

## Step 12: Verify the migration

```bash
alembic current        # Shows applied migration
psql -d clinical_notes_db -c "\dt"  # Shows tables
psql -d clinical_notes_db -c "\d patients"  # Shows columns
```

---

## Complete File Listing

At the end, your directory should look like:

```
02_clinical_notes_backend/
├── .venv/
├── .env
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── abc123_create_patients_and_notes_tables.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── patients.py
│   │   └── notes.py
└── README.md
```

## Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| POST | `/patients` | Create patient |
| GET | `/patients` | List patients |
| GET | `/patients/{id}` | Get patient |
| PUT | `/patients/{id}` | Update patient |
| DELETE | `/patients/{id}` | Delete patient |
| POST | `/patients/{id}/notes` | Create note for patient |
| GET | `/patients/{id}/notes` | List patient notes (visit history) |
| GET | `/notes/{id}` | Get single note |
| PUT | `/notes/{id}` | Update note |
| DELETE | `/notes/{id}` | Delete note |
| GET | `/notes/search?q=` | Search notes |

You're now ready to build Build 2.
