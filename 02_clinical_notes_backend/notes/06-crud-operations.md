# CRUD Operations with SQLModel

Now we connect everything — routes that use SQLModel through Depends().

## Setting Up the App

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from models import Patient, PatientCreate, PatientResponse, Note, NoteCreate, NoteResponse
from database import engine, get_session, create_db_and_tables

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()  # Creates tables if they don't exist
```

`app.on_event("startup")` runs when the server starts. It's the right place to initialize the database.

## Patient CRUD

### POST /patients — Create

```python
@app.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, session: Session = Depends(get_session)):
    db_patient = Patient.model_validate(patient)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient
```

**Whats happening:**
- `Patient.model_validate(patient)` — converts the Pydantic `PatientCreate` into a `Patient` DB model
- `session.add(db_patient)` — stages the insert
- `session.commit()` — saves to database (PostgreSQL now generates the id)
- `session.refresh(db_patient)` — updates our Python object with the DB-assigned id and created_at
- `response_model=PatientResponse` — FastAPI uses this to return only the fields in PatientResponse (not the notes relationship, etc.)

### GET /patients — List All

```python
@app.get("/patients", response_model=list[PatientResponse])
def list_patients(session: Session = Depends(get_session)):
    patients = session.exec(select(Patient)).all()
    return patients
```

**Key syntax:**
- `select(Patient)` — creates a SELECT * query on the patients table
- `session.exec(...)` — executes the query via SQLModel
- `.all()` — returns all matching rows as a list

### GET /patients/{patient_id} — Get One

```python
@app.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, session: Session = Depends(get_session)):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
```

**Key syntax:**
- `session.get(Patient, patient_id)` — primary key lookup (fastest way to get by id)
- If not found, returns `None` — we raise 404 just like Build 1

### PUT /patients/{patient_id} — Update

```python
@app.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_update: PatientCreate,
    session: Session = Depends(get_session)
):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Update only the provided fields
    patient_data = patient_update.model_dump(exclude_unset=True)
    db_patient.sqlmodel_update(patient_data)
    
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient
```

**Whats happening:**
- `model_dump(exclude_unset=True)` — converts to dict, only including fields that were actually sent
- `sqlmodel_update(patient_data)` — applies those fields to the DB model
- `session.add(...)` — stages the update (SQLAlchemy detects this is an existing row, does UPDATE not INSERT)
- `commit()` + `refresh()` — save and return fresh data

### DELETE /patients/{patient_id} — Delete

```python
@app.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, session: Session = Depends(get_session)):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    session.delete(db_patient)
    session.commit()
    return None
```

## Note CRUD

Notes are always tied to a specific patient.

### POST /patients/{patient_id}/notes — Create Note for Patient

```python
@app.post("/patients/{patient_id}/notes", response_model=NoteResponse, status_code=201)
def create_note(
    patient_id: int,
    note: NoteCreate,
    session: Session = Depends(get_session)
):
    # Verify patient exists
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Create note linked to patient
    db_note = Note.model_validate(note)
    db_note.patient_id = patient_id
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note
```

**Important:** We validate the patient exists before creating the note. This gives a cleaner error message than relying on the foreign key constraint.

### GET /patients/{patient_id}/notes — Visit History

```python
@app.get("/patients/{patient_id}/notes", response_model=list[NoteResponse])
def list_patient_notes(
    patient_id: int,
    session: Session = Depends(get_session)
):
    # Verify patient exists
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get all notes for this patient, ordered by date
    statement = (
        select(Note)
        .where(Note.patient_id == patient_id)
        .order_by(Note.created_at.desc())
    )
    notes = session.exec(statement).all()
    return notes
```

### GET /notes/{note_id} — Get Single Note

```python
@app.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note
```

### PUT /notes/{note_id} — Update Note

```python
@app.put("/notes/{note_id}", response_model=NoteResponse)
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
    db_note.updated_at = datetime.now()  # Update the timestamp
    
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note
```

### GET /notes/search — Search Notes

```python
@app.get("/notes/search", response_model=list[NoteResponse])
def search_notes(
    q: str,
    session: Session = Depends(get_session)
):
    statement = select(Note).where(
        Note.content.contains(q) | Note.title.contains(q)
    )
    notes = session.exec(statement).all()
    return notes
```

**The search:**
- `Note.content.contains(q)` — checks if content includes the search term (SQL equivalent: `LIKE '%q%'`)
- `|` — OR operator (content matches OR title matches)

## Important Session Pattern: Commit → Refresh

Every mutation (create, update, delete) follows this pattern:

```python
1. session.add(obj)       # Stage the change
2. session.commit()       # Save to database
3. session.refresh(obj)   # Get DB-generated values (id, timestamps)
```

If you forget `refresh`, you'll return an object without the id:

```python
# Without refresh
session.add(db_patient)
session.commit()
return db_patient  # patient.id is None!

# With refresh
session.add(db_patient)
session.commit()
session.refresh(db_patient)
return db_patient  # patient.id = 1 ✓
```

## Error Handling

All 404s use the same pattern:

```python
db_object = session.get(Model, id)
if not db_object:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{Model.__name__} not found"
    )
```

For validation errors (422), FastAPI + Pydantic handles them automatically — you don't need to do anything.

## Summary

| Operation | SQLModel Code | HTTP |
|---|---|---|
| Create | `session.add()` + `commit()` + `refresh()` | POST 201 |
| List all | `session.exec(select(Model)).all()` | GET 200 |
| Get one | `session.get(Model, id)` | GET 200 |
| Update | `get()` → modify fields → `add()` + `commit()` + `refresh()` | PUT 200 |
| Delete | `get()` → `session.delete()` → `commit()` | DELETE 204 |
| Filter | `.where(Model.column == value)` | GET with params |
| Search | `.where(Model.column.contains(text))` | GET ?q= |
| Order | `.order_by(Model.column.desc())` | — |

Next: Alembic migrations — tracking database changes safely.
