# Quiz — Notes 01 to 04 (Answer Key with Explanations)

---

### Q1

You're building a clinical notes system for a hospital with 50 concurrent doctors writing notes all day. Your junior dev suggests using a JSON file on a shared drive instead of PostgreSQL. What's the most critical problem with this?

- C) Two doctors writing at the same moment will corrupt the file

**Why C is correct:** JSON files have no built-in concurrency control. If Doctor A writes to the file at the exact moment Doctor B writes, one write will overwrite the other or the file will become a mix of both — corrupted. PostgreSQL handles this with transactions and row-level locking.

**Why the others are wrong:**
- A) JSON supports UTF-8 — that's not a problem
- B) JSON can store datetime as strings — it's just less convenient
- D) JSON is slower for complex queries, but "critical" problem is data corruption, not speed


### Q2

```sql
SELECT p.name, COUNT(n.id) as note_count
FROM patients p
LEFT JOIN notes n ON p.id = n.patient_id
GROUP BY p.name;
```

- D) All patients with their note count — zero-note patients show 0

**Why D is correct:** `LEFT JOIN` means "keep ALL rows from the `patients` table (left side), and match notes where possible." For patients with no notes, the note columns are NULL. `COUNT(n.id)` counts non-NULL values — since n.id is NULL for non-matching rows, those patients get `0`.

**Why A is wrong:** A is what `INNER JOIN` does — it excludes patients without notes. `LEFT JOIN` is different — it keeps everything from the left table.

**Mental model:** LEFT JOIN = "Give me everything from the left table, plus whatever matches on the right. If nothing matches, show NULLs."


### Q3

In SQLModel, `SQLModel.metadata.create_all(engine)` is called. The table already exists from a previous run. What happens?

- C) Nothing — `create_all` skips existing tables

**Why C is correct:** `create_all` checks `IF NOT EXISTS` for every table before creating it. If the table already exists, it's skipped. No data loss, no error.

**Why D is wrong:** `create_all` does NOT modify existing tables. If you add a new column to your model, `create_all` will NOT add it to the existing table. That's what Alembic migrations are for (covered in Note 07).

**Real-life analogy:** Think of `create_all` like checking a warehouse. "Is there a shelf labeled 'patients'? Yes? Okay, moving on." It never rearranges existing shelves.


### Q4

A doctor creates a patient, then 3 notes for that patient. The doctor notices a typo in the patient's name and tries to delete the patient — but it fails because notes reference the patient. Which SQL clause makes deletion work?

- B) ON DELETE CASCADE

**Why B is correct:** `ON DELETE CASCADE` tells PostgreSQL: "When a patient is deleted, automatically delete all their notes too." Without it, PostgreSQL prevents deleting a patient who still has notes (to prevent orphaned records).

**Why A is wrong:** `RESTRICT` is actually the default behavior — it BLOCKS the deletion. That's why the doctor couldn't delete in the first place.

**Why C is wrong:** `SET NULL` would set `patient_id` in notes to NULL instead of deleting them. That creates orphaned notes (notes that belong to no one).


### Q5

What does a PRIMARY KEY guarantee that a UNIQUE constraint does NOT?

- C) The column cannot contain NULL

**Why C is correct:** This is a common interview question. Both PRIMARY KEY and UNIQUE guarantee unique values. Both create indexes. But PRIMARY KEY additionally guarantees `NOT NULL` — a primary key column can never be NULL. A UNIQUE column CAN be NULL (in PostgreSQL, multiple NULLs are allowed).

**Real-life analogy:** PRIMARY KEY = Aadhaar number (every citizen gets one, no one can have the same, and everyone MUST have one). UNIQUE = Email address (no two people can have the same, but a person without email is allowed).


### Q6

```python
class Note(SQLModel, table=True):
    content: str
    patient_id: int = Field(foreign_key="patients.id")
```

Without `Relationship` defined, which of these can you NOT do?

- B) Access `note.patient.name` from a Note object

**Why B is correct:** The `Relationship()` attribute (`note.patient`) is a Python-level convenience. It lets you navigate from a Note to its Patient object directly in code. Without it, the foreign key still exists at the database level (PostgreSQL enforces it), but you can't do `note.patient`. You'd have to manually query: `session.get(Patient, note.patient_id)`.

**What still works without Relationship:**
- A) You can query notes by patient_id — `select(Note).where(Note.patient_id == 1)`
- C) You can create notes linked to patients — foreign key constraint still works
- D) The foreign key constraint is still created — `Field(foreign_key=...)` does this


### Q7

```python
session = Session(engine)
patient = Patient(name="Test")
session.add(patient)
session.commit()
print(patient.id)  # Still None — why?
```

- B) `session.refresh(patient)` is needed after commit to load the DB-generated id

**Why B is correct:** `commit()` sends the data to PostgreSQL and generates the ID on the database server. But the Python object `patient` still has its old value of `None` for `id`. `refresh()` tells SQLAlchemy to go back to the database and reload the object, picking up the generated ID.

**The full pattern:** `add() → commit() → refresh()`. All three are needed to get the ID back.


### Q8

```python
patient = session.get(Patient, 1)
notes = patient.notes  # Triggers a second SQL query
```

Why does accessing `patient.notes` hit the database again?

- A) SQLModel uses lazy loading — related data is fetched only when accessed

**Why A is correct:** SQLModel/SQLAlchemy doesn't load everything at once. The first query only loads the Patient row. When you access `patient.notes`, SQLModel sees "I haven't loaded the notes yet" and sends a second query: `SELECT * FROM notes WHERE patient_id = 1`.

**Why B is wrong:** `session.get()` CAN load relationships — it just doesn't unless you tell it to (using `selectinload` or similar).

**Why this is good:** If you have 1000 patients and only need their names, lazy loading saves 1000 unnecessary queries.


### Q9

```python
class Note(SQLModel, table=True):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

A note is created at 10:00 AM. At 11:00 AM, the note's content is updated via SQLModel. What is `updated_at` after the update?

- C) 10:00 AM — `default_factory` only sets the initial value, and the code doesn't manually update `updated_at`

**Why C is correct:** `default_factory=datetime.now` is a Python-level default. It runs ONCE when you create the Note object in Python. When you later update the note's content, `updated_at` is NOT automatically changed — nothing in this code updates `updated_at` at 11:00 AM.

**How to fix it:** When updating the note, you must explicitly set `updated_at`:
```python
db_note.updated_at = datetime.now()
```

**Why `created_at` is fine:** `created_at` should only be set at creation time and never change. So `default_factory` works perfectly for it.


### Q10

```sql
DELETE FROM patients WHERE age > 150;
```

This runs successfully but no rows are deleted. The most likely reason is:

- B) No patient has age greater than 150

**Why B is correct:** The SQL syntax is valid. It ran without error. The WHERE condition just didn't match any rows. No rows to delete = nothing happens.

**Why A is wrong:** PostgreSQL has no LIMIT requirement for DELETE.

**Key insight:** SQL commands that affect 0 rows are not errors. `DELETE`, `UPDATE`, `SELECT` can all return zero results without any problem.


### Q11

```python
class Medication(SQLModel, table=True):
    name: str
    dosage_mg: float
```

5 medications exist in the table. You add a `patient_id` foreign key field to the model and run `create_all`. What happens to the 5 existing rows?

- C) Existing rows remain, with `patient_id = NULL`

**Why C is correct:** When you add a new nullable column to a model and call `create_all`, it does `ALTER TABLE medications ADD COLUMN patient_id INTEGER`. For existing rows, PostgreSQL sets the new column to NULL (since no value was provided).

**Why A is wrong:** `create_all` does NOT modify existing tables when the table already exists. It only creates tables that don't exist. So adding `patient_id` to the model doesn't even run the ALTER TABLE — you need Alembic for that.

**This reveals a limitation:** `create_all` can't add columns to existing tables. That's exactly why you need Alembic (Note 07).


### Q12

In SQLModel/PostgreSQL, what does `Session` represent?

- D) A single unit of work — a transactional workspace for DB operations

**Why D is correct:** A Session is a workspace where you stage operations (add, delete, modify) before sending them to the database with `commit()`. If something goes wrong, you call `rollback()` and nothing is saved. This is the "unit of work" pattern.

**Others:**
- A) The engine manages the connection pool, not the Session
- B) Alembic tracks migration history, not Session
- C) Sessions are short-lived and created per-request. They are NOT persistent connections.


### Q13

```python
class Patient(SQLModel, table=True):
    age: int | None = None
```

What SQL column type does this produce in PostgreSQL?

- A) INTEGER (allows NULL)

**Why A is correct:** `int | None = None` tells SQLModel two things:
1. `int` → the SQL type is INTEGER
2. `None` → the column is nullable (allows NULL in the database)

If you wrote `age: int` (without `| None`), it would create `INTEGER NOT NULL`.


### Q14

Find all notes created in the last 7 days. Which is correct?

- D) `select(Note).where(Note.created_at > (datetime.now() - timedelta(days=7)))`

**Why D is correct:** You need to compute "7 days ago" as a datetime object, then compare it to `created_at`. Only D does this correctly. Python evaluates `datetime.now() - timedelta(days=7)` first, then passes the result to SQLModel, which sends it as a parameter to PostgreSQL.

**Why A is wrong:** `> 7` compares a datetime to an integer — meaningless.
**Why B is wrong:** `> "7 days ago"` compares a datetime to a string — meaningless.
**Why C is wrong:** `.last_7_days()` doesn't exist in SQLModel.


### Q15

Two transactions run simultaneously:
- T1: reads Patient, changes name, saves
- T2: reads the same Patient, changes age, saves

PostgreSQL's default behavior:

- A) Row-level locking allows both changes to apply correctly

**Why A is correct:** PostgreSQL locks the specific row being modified, not the entire table. T1 locks the patient row, changes the name, and commits. T2 waits briefly, then locks the same row, changes the age, and commits. Both changes are applied.

**Contrast with Build 1:** In the in-memory list, there's no locking. Two simultaneous writes would overwrite each other or corrupt the list. PostgreSQL's row-level locking is one of the most important reasons to use a real database.


### Q16

Patient has `list["Note"]` and Note has `Optional["Patient"]`. Why are strings used instead of direct class references?

- C) To avoid circular import errors between the two model files

**Why C is correct:** If Patient imports Note, and Note imports Patient, you get a circular import error. Python can't resolve them. Using strings (`"Note"` and `"Patient"`) tells Python "resolve this name later, after all imports are done." SQLModel/SQLAlchemy resolves these strings internally.

**Why B is wrong:** FastAPI doesn't require strings for JSON serialization — it uses Pydantic's model_dump() which handles actual Python objects fine.


### Q17

```python
class User(SQLModel, table=True):
    email: str = Field(unique=True)
```

A second user is inserted with the same email as an existing user. What happens?

- D) PostgreSQL rejects the insert with a unique constraint violation

**Why D is correct:** `Field(unique=True)` creates a `UNIQUE` constraint at the PostgreSQL level. The database itself enforces this — no Python code runs between your insert and the database. If you try to violate the constraint, PostgreSQL returns an error, and SQLAlchemy raises `IntegrityError`.


### Q18

`SQLModel.metadata.create_all(engine)` runs on every server startup. A team member worries: "This could drop our production database!" Are they right?

- B) No — `create_all` only creates tables that don't exist, existing data is untouched

**Why B is correct:** `create_all` is safe by design. It runs `CREATE TABLE IF NOT EXISTS` for every model. If the table exists, it does nothing. Your data is never touched. The dangerous operation is `drop_all()` — and you don't accidentally call that.


### Q19

A Session is opened, a patient is added with `session.add()`, but `commit()` is never called. The session closes. What happens?

- D) The session rolls back the uncommitted transaction on close — nothing is saved

**Why D is correct:** A Session wraps everything in a transaction. When you call `session.add()`, the data is staged in memory — it hasn't hit the database yet. If the session closes without `commit()`, it automatically rolls back (cancels) the transaction. No data is written.

**The flow:**
1. `session.add(patient)` — stages in memory (not saved)
2. `session.commit()` — sends to database (required!)
3. Session closes — if no commit happened, rollback is automatic


### Q20

Raw SQL: `SELECT * FROM notes WHERE content ILIKE '%fever%'`. Which SQLModel query is equivalent?

- D) `select(Note).where(Note.content.ilike("%fever%"))`

**Why D is correct:** `.ilike()` is a SQLAlchemy method that generates `ILIKE` — case-insensitive pattern matching in PostgreSQL. `ILIKE` finds "fever", "Fever", "FEVER", etc.

**Why B is wrong:** `None of the above` is incorrect because option D works. The explanation in B about `contains` vs `ILIKE` is accurate, but D exists and is the correct answer.

**Important distinction:**
- `Note.content.contains("fever")` → `content LIKE '%fever%'` (case-sensitive)
- `Note.content.ilike("%fever%")` → `content ILIKE '%fever%'` (case-insensitive)

---

## Your Score: 10/20

**Conceptually correct:** Q1, Q4, Q7, Q8, Q10, Q13, Q14, Q15, Q17, Q18, Q19

**Need to review:**
- LEFT JOIN behavior (Q2)
- create_all limitations (Q3, Q11)
- PRIMARY KEY vs UNIQUE (Q5)
- What Relationship() provides vs foreign key (Q6)
- default_factory only runs on creation (Q9)
- Session vs Engine vs Connection Pool (Q12)
- Why strings in Relationship (Q16)
- .ilike() for case-insensitive search (Q20)

Go back to notes 02, 03, 04 and re-read the sections on these topics. Then you're ready to start building.
