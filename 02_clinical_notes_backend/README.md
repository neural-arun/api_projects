# Clinical Notes Backend

**Build 2** of the FastAPI for Healthcare + Medical Education Systems roadmap.

A backend system for doctors to create, edit, search, and manage clinical notes for patients — backed by a real PostgreSQL database instead of in-memory storage.

---

## What We're Building

A Doctor Notes System where:

- A **Patient** can be created and stored in the database
- A **Doctor** can write a clinical note for a patient visit
- Notes can be **edited** after creation
- Notes can be **searched** by content or patient name
- **Visit history** can be viewed — all notes for a patient, in order

---

## What This Build Teaches

This is where you move from "toy API" to "real backend." Here's exactly what you'll learn:

### 1. PostgreSQL — The Actual Database

In Build 1, tasks lived in a Python list. Restart the server and everything vanished. PostgreSQL stores data permanently on disk, handles concurrent requests safely, and is what real production systems use.

### 2. SQLAlchemy — The ORM

Instead of writing raw SQL like `SELECT * FROM patients WHERE id = 1`, you write Python:

```python
patient = session.query(Patient).filter(Patient.id == 1).first()
```

SQLAlchemy translates that to SQL automatically. It also handles:
- **Creating tables** from Python classes
- **Relationships** (one patient → many notes)
- **Transactions** (if something fails, nothing gets saved)

### 3. SQLModel vs SQLAlchemy — Which One?

Both are listed in the syllabus. The difference:
- **SQLAlchemy** — the mature, widely-used ORM. More control, more boilerplate.
- **SQLModel** — newer library that merges SQLAlchemy + Pydantic. Less code, tighter FastAPI integration.

**Pick one.** SQLModel is recommended for this build since it reduces boilerplate and plays well with FastAPI. You can always switch later.

### 4. Alembic — Database Migrations

When you add a column (e.g., `patient.age`), you don't want to delete all your data and recreate the table. Alembic generates migration scripts that alter the existing table safely.

Think of it as **Git for your database schema**:

```
alembic revision --autogenerate -m "add age to patients"
alembic upgrade head
```

### 5. Dependency Injection (Depends())

You already used FastAPI's `Depends()` without realizing it — route parameters like `task_id: int` are a simple form of it. In this build, you'll use `Depends()` to inject database sessions into routes cleanly:

```python
@app.get("/patients")
def list_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()
```

This keeps your routes clean and makes testing easier.

### 6. Project Structure

Build 1 had everything in one file (`main.py`). That won't work for a real project. You'll learn to organize code like this:

```
02_clinical_notes_backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, route registration
│   ├── database.py           # DB connection, session setup
│   ├── models.py             # SQLAlchemy/SQLModel table definitions
│   ├── schemas.py            # Pydantic request/response models
│   ├── crud.py               # Database operations (create patient, etc.)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── patients.py       # /patients routes
│   │   └── notes.py          # /notes routes
│   └── dependencies.py       # Shared dependencies (get_db, etc.)
├── alembic/                  # Alembic migration files (auto-generated)
├── alembic.ini               # Alembic configuration
├── requirements.txt
├── .env                      # Database URL, secrets
└── README.md
```

### 7. Relationships

A **Patient** has many **Notes**. This is a one-to-many relationship. You'll learn how to define this at the database level (foreign keys) and at the ORM level (relationship attributes).

---

## Expected API Endpoints

| Method   | Endpoint                    | Description              |
|----------|-----------------------------|--------------------------|
| `POST`   | `/patients`                 | Create a patient         |
| `GET`    | `/patients`                 | List all patients        |
| `GET`    | `/patients/{patient_id}`    | Get a patient            |
| `PUT`    | `/patients/{patient_id}`    | Update a patient         |
| `DELETE` | `/patients/{patient_id}`    | Delete a patient         |
| `POST`   | `/patients/{patient_id}/notes` | Create a note for patient |
| `GET`    | `/patients/{patient_id}/notes` | List notes for a patient (visit history) |
| `GET`    | `/notes/{note_id}`          | Get a single note        |
| `PUT`    | `/notes/{note_id}`          | Edit a note              |
| `GET`    | `/notes/search?q=keyword`   | Search notes by content  |

---

## How It All Fits Together (The Flow)

```
Client (browser/curl)
    │
    ▼
FastAPI Route (e.g., POST /patients)
    │
    ▼
Pydantic Schema (validates request body)
    │
    ▼
CRUD Function (e.g., create_patient in crud.py)
    │
    ▼
SQLAlchemy/SQLModel (translates to SQL)
    │
    ▼
PostgreSQL (stores permanently on disk)
```

When reading data, the same flow reverses: PostgreSQL → ORM → Pydantic → JSON response.

---

## Prerequisites

- Python 3.10+
- PostgreSQL installed and running locally (or via Docker)
- Basic understanding of SQL (SELECT, INSERT, UPDATE, DELETE)

---

## Initial Setup (We'll Do This Together When Building)

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install fastapi uvicorn sqlmodel alembic psycopg2-binary python-dotenv

# 3. Start PostgreSQL and create database
psql -U postgres
CREATE DATABASE clinical_notes;

# 4. Set up Alembic
alembic init alembic
# ... (configure alembic.ini and env.py)

# 5. Run migrations
alembic revision --autogenerate -m "initial tables"
alembic upgrade head

# 6. Run the app
uvicorn app.main:app --reload
```

---

## Outcome

After this build, you should be able to:
- Set up PostgreSQL and connect it to a FastAPI app
- Define database tables using an ORM
- Create and run Alembic migrations
- Use FastAPI's dependency injection for database sessions
- Structure a real backend project with separate modules
- Perform CRUD with proper relationships (one-to-many)
