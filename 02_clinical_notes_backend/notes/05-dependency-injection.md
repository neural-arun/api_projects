# Dependency Injection: The Database Session

## The Problem

Every route in Build 2 needs access to the database:

```python
@app.post("/patients")
def create_patient(patient: PatientCreate):
    # Need database session here
    
@app.get("/patients")
def list_patients():
    # Need database session here too
    
@app.get("/patients/{patient_id}")
def get_patient(patient_id: int):
    # And here...
```

You could create a new database connection in every route — but that's wasteful and repetitive.

## The Solution: Dependency Injection with Depends()

FastAPI's `Depends()` lets you write a function that provides a shared resource, and any route can "depend" on it.

You've actually already used this in Build 1 — when you wrote:

```python
@app.get("/tasks/{task_id}")
def get_task(task_id: int):  # ← "task_id: int" is technically a dependency
```

FastAPI sees the type hint and knows to extract it from the URL path. `Depends()` is the explicit version.

## Creating a Database Dependency

### Step 1: Create the engine and session

First, set up the database connection:

```python
# database.py
from sqlmodel import SQLModel, create_engine, Session

# Connection string format:
# postgresql://username:password@host:port/database_name
DATABASE_URL = "postgresql://postgres:password@localhost:5432/clinical_notes_db"

# The engine manages the connection pool
engine = create_engine(DATABASE_URL)
```

**The connection string breakdown:**
```
postgresql://  postgres  :  password  @  localhost  :  5432  /  clinical_notes_db
     ↑           ↑             ↑              ↑           ↑           ↑
   protocol   username     password        host       port      database name
```

### Step 2: Create the get_session dependency

```python
# database.py (continued)
def get_session():
    with Session(engine) as session:
        yield session
```

This function:
1. Creates a new database session
2. Yields it (gives it to FastAPI)
3. Automatically closes the session when the request is done

### Step 3: Use it in routes

```python
from fastapi import Depends
from sqlmodel import Session

@app.post("/patients")
def create_patient(
    patient: PatientCreate,
    session: Session = Depends(get_session)  # ← The magic line
):
    db_patient = Patient.model_validate(patient)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient
```

**What happens when a request comes in:**

```
Request → FastAPI sees "session: Session = Depends(get_session)"
         → Calls get_session()
         → get_session() creates a Session and yields it
         → FastAPI passes the session to your route function
         → Your route uses the session
         → After the route returns, get_session() resumes and closes the session
```

## Complete database.py

```python
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "postgresql://postgres:password@localhost:5432/clinical_notes_db"

engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Create all tables that haven't been created yet.
    Useful for development. In production, use Alembic (next note)."""
    SQLModel.metadata.create_all(engine)
```

## Using Sessions Correctly

### DO: Use `with` statement

```python
def get_session():
    with Session(engine) as session:
        yield session
```

The `with` block ensures the session is always closed, even if an error occurs.

### DO: Commit changes

```python
session.add(patient)
session.commit()       # Saves to database
session.refresh(patient)  # Updates patient.id with the DB-assigned value
return patient
```

### DON'T: Forget to commit

```python
session.add(patient)
# session.commit()  ← Without this, nothing is saved!
return patient
```

### DON'T: Pass sessions around unnecessarily

```python
# Bad — mixing concerns
@app.post("/patients")
def create_patient(patient: PatientCreate, session: Session = Depends(get_session)):
    # Database logic + validation + response all here → messy

# Good — separate concerns
@app.post("/patients")
def create_patient(patient: PatientCreate, session: Session = Depends(get_session)):
    db_patient = Patient.model_validate(patient)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient
```

For now, keeping CRUD in routes is fine. When routes get complex, you extract CRUD into a separate file (covered in note 08).

## Real-Life Analogy

Think of the database connection like a hospital's central supply room:
- **Engine** = the supply room itself (always there)
- **Session** = one trip to get supplies (open → get → close)
- **Depends()** = handing each doctor (route) a key card when they need supplies

Without dependency injection, every route would build their own supply closet. With it, they all share one well-managed source.

## Environment Variables

Hardcoding your database URL is bad practice. Use a `.env` file:

```
# .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/clinical_notes_db
```

And load it with python-dotenv:

```bash
pip install python-dotenv
```

```python
# database.py
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()  # Reads .env file

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session
```

## Summary

| Concept | Code | Purpose |
|---|---|---|
| Engine | `create_engine(url)` | Connects to database, manages connection pool |
| Session | `Session(engine)` | One unit of work (add, commit, query) |
| get_session | `def get_session(): yield session` | Creates + closes sessions |
| Depends | `session = Depends(get_session)` | Injects session into routes |
| commit | `session.commit()` | Saves pending changes to DB |
| refresh | `session.refresh(obj)` | Updates obj with DB-generated values |

Next: Writing the actual CRUD operations for our routes.
