# Alembic Migrations

## The Problem

You just created `patients` and `notes` tables. Now imagine your client says:

> "We need to add a `phone` field to patients and mark whether the note is 'urgent'."

You update your SQLModel:

```python
class Patient(SQLModel, table=True):
    ...
    phone: str | None = None  # New field
```

But the existing `patients` table in PostgreSQL still has the old columns. You'd need to run:

```sql
ALTER TABLE patients ADD COLUMN phone VARCHAR(20);
```

And remember to run it manually on every developer's machine, on staging, and on production. One mistake and columns or data get out of sync.

## What Alembic Does

Alembic is a **migration tool** — it tracks every change to your database schema:

1. Compares your current SQLModel classes to the actual database
2. Generates a Python file ("migration") with the ALTER TABLE commands
3. Lets you apply or roll back changes with a single command

Think of it like **Git for your database schema**.

## Setting Up Alembic

### Step 1: Install

```bash
pip install alembic
```

### Step 2: Initialize

```bash
alembic init alembic
```

This creates:
```
alembic/
├── env.py          # How Alembic connects to your DB and finds your models
├── script.py.mako  # Template for migration files
└── versions/       # Your migration files go here
alembic.ini         # Configuration file
```

### Step 3: Configure Connection

Edit `alembic.ini` to point to your database:

```ini
sqlalchemy.url = postgresql://postgres:password@localhost:5432/clinical_notes_db
```

Or better — load from `.env` by editing `alembic/env.py`:

```python
# alembic/env.py
import os
from dotenv import load_dotenv

load_dotenv()  # Reads .env file from project root
DATABASE_URL = os.getenv("DATABASE_URL")

# Change this line in env.py:
# from config import Config
# config.set_main_option("sqlalchemy.url", DATABASE_URL)
```

### Step 4: Tell Alembic About Your Models

In `alembic/env.py`, find the section with `target_metadata`:

```python
# alembic/env.py
from sqlmodel import SQLModel
from models import Patient, Note  # Import your models

# Change this:
target_metadata = SQLModel.metadata
```

**This is critical.** `target_metadata` tells Alembic "these are the tables I want" so it can compare them to the actual database.

## Creating Your First Migration

Make sure your database exists and your tables are created:

```bash
createdb clinical_notes_db
```

Then:

```bash
alembic revision --autogenerate -m "create patients and notes tables"
```

Alembic compares `SQLModel.metadata` (your Python models) against the actual database and generates a migration file in `alembic/versions/`:

```python
"""create patients and notes tables

Revision ID: abc123
Create Date: 2024-...
"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = None

def upgrade() -> None:
    op.create_table('patients',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('notes')
    op.drop_table('patients')
```

**`upgrade()`** — runs the migration (create tables)
**`downgrade()`** — reverses it (drop tables)

### Apply the Migration

```bash
alembic upgrade head
```

"head" means "apply all pending migrations up to the latest one."

### Check Status

```bash
alembic current        # Shows which migration is currently applied
alembic history        # Shows all migrations
```

## Making a Schema Change

Suppose we add `phone` to the patient model:

```python
class Patient(SQLModel, table=True):
    ...
    phone: str | None = Field(default=None, max_length=20)  # New
```

Generate a migration:

```bash
alembic revision --autogenerate -m "add phone to patients"
```

Alembic detects the change and generates:

```python
def upgrade() -> None:
    op.add_column('patients', sa.Column('phone', sa.String(length=20), nullable=True))

def downgrade() -> None:
    op.drop_column('patients', 'phone')
```

Apply it:

```bash
alembic upgrade head
```

Now the database has the new column without losing any existing data.

## Rolling Back

Made a mistake? Roll back the last migration:

```bash
alembic downgrade -1
```

Roll back to the beginning:

```bash
alembic downgrade base
```

## Common Workflow

```
1. Change your SQLModel (add field, change type, etc.)
2. Generate migration:  alembic revision --autogenerate -m "description"
3. Review the generated file (make sure it looks right)
4. Apply it:            alembic upgrade head
5. Repeat
```

## Important Rules

### 1. Always review generated migrations

Alembic isn't perfect. Sometimes it misses things or generates wrong SQL. Always check the file before running it.

### 2. Never edit existing migrations after they're applied

If you need to change something, create a new migration. Editing an already-applied migration is like rewriting Git history — you'll break everyone else's database.

### 3. Keep migrations in version control

Migration files belong in Git. They're the history of your schema and let other developers (or your production server) catch up.

### 4. `--autogenerate` needs context

Alembic can only detect:
- Table additions/removals
- Column additions/removals
- Column type changes
- Column nullability changes
- Index/constraint changes

It **cannot** detect:
- Table renames (it thinks old table was deleted and new one created)
- Column renames (same — sees it as drop + add)
These need manual migration edits.

## Production Tip

In development, `SQLModel.metadata.create_all(engine)` is fine. In production, use only Alembic migrations:

```python
# main.py — remove create_db_and_tables from startup
# Instead, manually run: alembic upgrade head
```

This gives you explicit control over when schema changes happen.

## Summary

| Command | What It Does |
|---|---|
| `alembic init alembic` | Create migration environment |
| `alembic revision --autogenerate -m "msg"` | Generate migration from model changes |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Roll back last migration |
| `alembic current` | See current state |
| `alembic history` | See full migration history |

Next: Organizing a real backend project with proper structure.
