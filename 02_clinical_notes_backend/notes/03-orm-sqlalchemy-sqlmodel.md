# ORMs: SQLAlchemy vs SQLModel

## The Problem With Raw SQL

In the last note, you wrote SQL like this:

```sql
SELECT * FROM patients WHERE age > 40;
```

That works. But in a Python app, you'd have to:
1. Write SQL as strings: `"SELECT * FROM patients WHERE age > %s"`
2. Pass parameters carefully to avoid injection
3. Parse results back into Python objects manually
4. Repeat for every query

It gets messy fast:

```python
# Raw SQL in Python — ugly and error-prone
cursor.execute("SELECT * FROM patients WHERE age > %s", (40,))
rows = cursor.fetchall()
patients = []
for row in rows:
    patients.append({"id": row[0], "name": row[1], "age": row[2]})
```

## What is an ORM?

**ORM = Object Relational Mapping**

It lets you write Python classes instead of SQL tables, and Python method calls instead of SQL queries.

### Without ORM (raw SQL):
```sql
INSERT INTO patients (name, age) VALUES ('Ravi', 45);
```

### With ORM (Python):
```python
patient = Patient(name="Ravi", age=45)
session.add(patient)
session.commit()
```

The ORM translates the Python code into the SQL query automatically.

## Real-Life Analogy

Think of SQL as speaking directly to the database in its native language.

An ORM is like having a translator:
- You speak Python (your language)
- ORM translates to SQL (database language)
- Database responds with raw data
- ORM converts back to Python objects

You don't always *need* the translator, but it makes life much easier.

## Two Options: SQLAlchemy vs SQLModel

### SQLAlchemy

The veteran. Been around for 15+ years. Used by most Python web frameworks.

```python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
```

Then for validation in FastAPI, you also need a separate Pydantic model:

```python
from pydantic import BaseModel

class PatientCreate(BaseModel):
    name: str
    age: int | None = None
```

**Problem:** You define the Patient *twice* — once for the database (SQLAlchemy), once for validation (Pydantic). Duplicate work.

### SQLModel (Recommended for This Build)

Created by the same person who built FastAPI (Sebastián Ramírez / tiangolo). It combines SQLAlchemy + Pydantic into one.

```python
from sqlmodel import SQLModel, Field

class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    age: int | None = None
```

**One class, two jobs:**
- Database table definition (because `table=True`)
- Pydantic validation (because it inherits from `SQLModel`, which is built on Pydantic)

## Why SQLModel Wins for FastAPI

| Feature | SQLAlchemy | SQLModel |
|---|---|---|
| Database models | ✅ | ✅ |
| Pydantic validation | ❌ Separate model needed | ✅ Built-in |
| Request/response schemas | ❌ Separate model needed | ✅ Built-in |
| Less code | ❌ | ✅ |
| Works with FastAPI natively | It works, but more manual | Perfect integration |
| Maturity | ✅ Very mature | ✅ Built on SQLAlchemy |

## The One SQLModel Pattern You Need

SQLModel uses **type hints** to define columns — same syntax you already know from Python:

```python
# Regular Python type | What it means in the database
# -------------------|-------------------------------
int                  → INTEGER (or SERIAL for primary key)
str                  → VARCHAR / TEXT
float                → FLOAT / DOUBLE
bool                 → BOOLEAN
datetime             → TIMESTAMP
list[int]            → (used for relationships, not columns)
```

Special SQLModel fields:

```python
# Primary key — auto-incrementing
id: int | None = Field(default=None, primary_key=True)

# Required string with max length
name: str = Field(max_length=100)

# Optional field (nullable in DB)
age: int | None = None

# Default value
created_at: datetime = Field(default_factory=datetime.now)

# Unique column
email: str = Field(unique=True)

# Foreign key (points to another table's column)
patient_id: int = Field(foreign_key="patients.id")
```

## Let's See It In Action

Here's a complete example of defining and using SQLModel:

```python
from sqlmodel import SQLModel, Field, create_engine, Session

# Step 1: Define the model
class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    age: int | None = None

# Step 2: Create database engine (connection)
engine = create_engine("postgresql://user:pass@localhost:5432/clinical_notes_db")

# Step 3: Create tables (runs CREATE TABLE if not exists)
SQLModel.metadata.create_all(engine)

# Step 4: Create a session and add data
with Session(engine) as session:
    patient = Patient(name="Ravi Kumar", age=45)
    session.add(patient)
    session.commit()
    print(f"Created patient with id: {patient.id}")
```

That's it. Define → connect → create. You don't write a single SQL string.

## How SQLModel Handles Build 1's Pydantic Models

Remember your Build 1 setup:

```python
# Build 1: Separate models for different operations
class TaskCreate(BaseModel):       # For POST request body
    title: str
    description: str | None = None

class TaskUpdate(BaseModel):       # For PUT request body
    title: str | None = None
    description: str | None = None

class Task(BaseModel):             # For response
    id: int
    title: str
    description: str | None = None
    is_completed: bool
```

With SQLModel, you can do this more elegantly:

```python
from sqlmodel import SQLModel, Field

# Reusable base
class PatientBase(SQLModel):
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)

# For database
class Patient(PatientBase, table=True):
    __tablename__ = "patients"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)

# For creating (no id, no created_at)
class PatientCreate(PatientBase):
    pass

# For response (includes id)
class PatientResponse(PatientBase):
    id: int
```

## Summary

- **ORM** = Write Python, get SQL automatically
- **SQLAlchemy** = Mature but needs separate Pydantic models
- **SQLModel** = One model for DB + validation (built on SQLAlchemy)
- **Use SQLModel** for this build — less code, better FastAPI integration

Next: Defining our Patient and Note models with proper relationships.
