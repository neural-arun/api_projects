# Models & Relationships

## Our Two Tables

The Clinical Notes system needs two tables:

```
patients
├── id (primary key)
├── name
├── age
├── gender
└── created_at

notes
├── id (primary key)
├── patient_id (foreign key → patients.id)
├── title
├── content
├── created_at
└── updated_at
```

**Relationship:** One patient → many notes. A note always belongs to exactly one patient.

## Defining the Models with SQLModel

### Step 1: Install

```bash
pip install sqlmodel
```

### Step 2: Define Patient Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)
    created_at: datetime = Field(default_factory=datetime.now)
```

**Why `table=True`?** This tells SQLModel this class represents a database table. Without it, the class is just a Pydantic model (for validation only, no table created).

**Why `int | None` for id?** When creating a new patient, you don't pass an id — PostgreSQL auto-generates it. After saving, SQLModel sets the id from the database. So the field needs to accept `None` at creation time.

### Step 3: Define Note Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Note(SQLModel, table=True):
    __tablename__ = "notes"
    
    id: int | None = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    title: str = Field(max_length=200)
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

**The foreign key:**
```python
patient_id: int = Field(foreign_key="patients.id")
```

This means:
- `patient_id` is required (it's `int`, not `int | None`)
- It must match an existing `patients.id` value
- PostgreSQL enforces this — you can't create a note for a non-existent patient

## The Relationship — Connecting Patient and Note

Right now, the tables exist but they're independent. To get a patient's notes, you'd have to:

```python
# Without relationship — manual filtering
notes = session.exec(select(Note).where(Note.patient_id == 1)).all()
```

SQLModel gives us a cleaner way using **relationships**:

```python
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship — Patient has many Notes
    notes: list["Note"] = Relationship(back_populates="patient")


class Note(SQLModel, table=True):
    __tablename__ = "notes"
    
    id: int | None = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    title: str = Field(max_length=200)
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship — Note belongs to one Patient
    patient: Optional["Patient"] = Relationship(back_populates="notes")
```

**What `back_populates` does:** It links both sides of the relationship. When you access `patient.notes`, SQLModel knows to look at `Note.patient_id`. When you access `note.patient`, it knows to look up the matching `Patient`.

## Using the Relationship

```python
from sqlmodel import Session, select

# Create a patient
patient = Patient(name="Priya Sharma", age=32)

# Create a note for them
note = Note(
    patient_id=patient.id,  # or just patient.id
    title="Initial Consultation",
    content="Patient complains of persistent headache."
)

# Session work
with Session(engine) as session:
    session.add(patient)
    session.add(note)
    session.commit()

# After committing, we can use the relationship
with Session(engine) as session:
    # Get a patient
    patient = session.exec(select(Patient).where(Patient.id == 1)).first()
    
    # Get all their notes via relationship
    for note in patient.notes:
        print(f"{note.title}: {note.content}")
    
    # Or go the other way
    note = session.exec(select(Note).where(Note.id == 1)).first()
    print(f"Written by: {note.patient.name}")  # Accesses the related patient
```

## Important: Loading Relationships

By default, SQLModel/SQLAlchemy uses **lazy loading** — it only fetches related data when you access it. That means:

```python
patient = session.exec(select(Patient).where(Patient.id == 1)).first()
# At this point, only patient data is loaded

print(patient.notes)  # ⚡ Triggers another SQL query to fetch notes
```

This is fine for simple cases. You can also use **eager loading** (fetch everything at once) with `options`:

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

statement = select(Patient).options(selectinload(Patient.notes))
patient = session.exec(statement).first()
# Both patient AND their notes are loaded in one go
```

## Reusable Schema Pattern

For FastAPI, we want different models for creating vs responding:

```python
# Base — shared fields
class PatientBase(SQLModel):
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)

# DB table
class Patient(PatientBase, table=True):
    __tablename__ = "patients"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    notes: list["Note"] = Relationship(back_populates="patient")

# Request body (create)
class PatientCreate(PatientBase):
    pass

# Response body (returned to client)
class PatientResponse(PatientBase):
    id: int
    created_at: datetime
```

## Complete Models File

Here's what your `models.py` should look like for Build 2:

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


# ─── Patient Models ──────────────────────────────────────

class PatientBase(SQLModel):
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)


class PatientCreate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    created_at: datetime


class Patient(PatientBase, table=True):
    __tablename__ = "patients"
    
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    notes: list["Note"] = Relationship(back_populates="patient")


# ─── Note Models ──────────────────────────────────────────

class NoteBase(SQLModel):
    title: str = Field(max_length=200)
    content: str


class NoteCreate(NoteBase):
    pass


class NoteResponse(NoteBase):
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime


class Note(NoteBase, table=True):
    __tablename__ = "notes"
    
    id: int | None = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    patient: Optional["Patient"] = Relationship(back_populates="notes")
```

## Key Takeaways

| Concept | What It Means |
|---|---|
| `table=True` | Creates an actual database table |
| `primary_key=True` | Unique identifier (auto-increment) |
| `foreign_key="table.column"` | Links to another table |
| `Relationship()` | Python-level connection between models |
| `back_populates` | Keeps both relationship directions in sync |
| `PatientBase` | Reusable fields to avoid duplication |

Next: How to connect FastAPI to the database using dependency injection.
