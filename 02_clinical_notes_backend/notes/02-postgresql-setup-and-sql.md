# PostgreSQL Setup & SQL Basics

## What is PostgreSQL?

PostgreSQL (or "Postgres") is a **relational database** — it stores data in tables with rows and columns, just like a spreadsheet. But unlike Excel, it handles millions of rows, concurrent users, and complex queries.

Think of it like this:
- **PostgreSQL** = the database engine (the actual program)
- **A database** = one "file" in that engine (e.g., `clinical_notes_db`)
- **A table** = one sheet in that file (e.g., `patients`, `notes`)
- **A row** = one record (e.g., one patient)
- **A column** = one field (e.g., `name`, `age`)

## Installation

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql  # Start on boot
```

### macOS (Homebrew)

```bash
brew install postgresql@16
brew services start postgresql@16
```

### Windows

Download from [postgresql.org/download](https://www.postgresql.org/download/) and run the installer.

## Verify Installation

```bash
# Check PostgreSQL version
psql --version

# Check if service is running
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS
```

## The psql Shell

`psql` is the command-line tool to interact with PostgreSQL. Let's create our Clinical Notes database.

```bash
# Switch to postgres user (Linux)
sudo -u postgres psql

# On macOS, you can usually just run:
psql postgres
```

Once inside `psql`, your prompt looks like: `postgres=#`

### Create a Database

```sql
CREATE DATABASE clinical_notes_db;
```

To connect to it:
```sql
\c clinical_notes_db;
```

Your prompt changes to: `clinical_notes_db=#`

## SQL Basics — The 4 Operations You Need

SQL (Structured Query Language) is how you talk to databases. You only need **4 operations** to start:

### CREATE TABLE — Define a structure

Think of this as designing a form with labeled fields:

```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

What each piece means:
- `SERIAL` — auto-incrementing integer (like `next_id` in Build 1)
- `PRIMARY KEY` — unique identifier for each row
- `VARCHAR(100)` — text, max 100 characters
- `NOT NULL` — this field is required
- `DEFAULT NOW()` — if not provided, use current time

**Real-life analogy:** You're creating a blank patient intake form with fields: ID number, patient name, age, and timestamp.

### INSERT — Add a row

```sql
INSERT INTO patients (name, age) VALUES ('Ravi Kumar', 45);
```

**Analogy:** Filling out that form and filing it.

### SELECT — Read rows

```sql
-- Get all patients
SELECT * FROM patients;

-- Get specific columns
SELECT name, age FROM patients;

-- Get filtered results
SELECT * FROM patients WHERE age > 40;

-- Get with ordering
SELECT * FROM patients ORDER BY created_at DESC;
```

**Analogy:** Opening the filing cabinet and looking up patients.

### UPDATE — Modify a row

```sql
UPDATE patients SET age = 46 WHERE id = 1;
```

Always use `WHERE` — otherwise you update every row!

**Analogy:** Correcting a mistake on the intake form.

### DELETE — Remove a row

```sql
DELETE FROM patients WHERE id = 1;
```

Again, `WHERE` is crucial. Without it, you empty the entire table.

## Our Clinical Notes Tables

Here's the SQL for our two tables:

```sql
-- The patients table
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- The notes table (each note belongs to a patient)
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

The key line: `REFERENCES patients(id) ON DELETE CASCADE`

This is a **foreign key**. It means:
- Every note must belong to an existing patient
- If that patient is deleted, all their notes are automatically deleted too

Think of sticky notes on a patient's file folder — when the folder is thrown away, the sticky notes go with it.

## Try It Yourself

In psql connected to `clinical_notes_db`:

```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add a patient
INSERT INTO patients (name, age, gender) VALUES ('Priya Sharma', 32, 'Female');

-- Add notes for that patient
INSERT INTO notes (patient_id, title, content)
VALUES (1, 'Initial Consultation', 'Patient complains of persistent headache for 3 days. Prescribed paracetamol.');

INSERT INTO notes (patient_id, title, content)
VALUES (1, 'Follow-up Visit', 'Headache reduced. Advised to continue medication for 2 more days.');

-- View patient with their notes
SELECT * FROM patients WHERE id = 1;
SELECT * FROM notes WHERE patient_id = 1;

-- View notes in chronological order
SELECT * FROM notes WHERE patient_id = 1 ORDER BY created_at DESC;
```

## The JOIN — Connect Related Tables

This is SQL's superpower. It lets you combine data from multiple tables:

```sql
-- Get notes with patient name (instead of just patient_id)
SELECT
    notes.id,
    notes.title,
    notes.content,
    patients.name AS patient_name,
    notes.created_at
FROM notes
JOIN patients ON notes.patient_id = patients.id;
```

Result looks like:
```
id | title | content | patient_name | created_at
---|-------|---------|--------------|-----------
1  | Initial... | Patient com... | Priya Sharma | 2024-...
2  | Follow-up.. | Headache r... | Priya Sharma | 2024-...
```

No more guessing what `patient_id = 1` means — the name is right there.

## Summary

| SQL Command | What It Does | CRUD Equivalent |
|---|---|---|
| `CREATE TABLE` | Define a table structure | — |
| `INSERT` | Add a row | Create |
| `SELECT` | Read rows | Read |
| `UPDATE` | Modify rows | Update |
| `DELETE` | Remove rows | Delete |
| `JOIN` | Combine related tables | — |

## What You DON'T Need to Memorize

- All SQL syntax — you'll mostly use the ORM (next notes)
- Complex joins — just the basic `JOIN ... ON`
- Indexes, views, procedures — come later

You just need to understand what SQL is doing so that when the ORM generates SQL, it's not magic.

Next: What is an ORM and why use it?
