# Conceptual Quiz — Notes 01 to 04 (Mixed Format)

Mark each as **True** or **False**, or pick the best option. Then come back to me.

---

### Q1

**True or False:** If you save data to a JSON file on disk every time your program makes a change, your data is just as safe as using PostgreSQL.

**Your answer:** ________False

---

### Q2

Two people open the same patient record and click "Save" at the exact same time.

**True or False:** With a JSON file, one person's changes will silently overwrite the other's.

**Your answer:** _______ ttrue

---

### Q3

You have two tables: `doctors` and `patients`. A doctor can see many patients. A patient can see many doctors.

Which table structure correctly models this?

- A) Add `doctor_id` to the `patients` table
- B) Add `patient_id` to the `doctors` table
- C) Create a third table called `appointments` or `doctor_patient` that has both `doctor_id` and `patient_id`
- D) Create two separate databases, one for doctors and one for patients

**Your answer:** ________c

---

### Q4

```python
class Patient(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
```

**True or False:** The `| None` makes the database column allow NULL values.

**Your answer:** ________no it does if it is not filled it will be automatically filled.

---

### Q5

You define a model with `table=True` and run `create_all`. Later, you add a new column to the model and run `create_all` again.

What happens to the existing data?

- A) The new column is added to the existing table, existing rows get NULL for it
- B) Nothing — `create_all` skips existing tables, the new column is NOT added
- C) The table is dropped and recreated, all data is lost
- D) An error is thrown because the table already exists

**Your answer:** ________a

---

### Q6

You have Patient → Note (one-to-many). You try to delete a Patient who has 10 notes, but the delete fails.

**True or False:** The delete fails because you didn't call `session.refresh()`.

**Your answer:** ________False

---

### Q7

A junior developer writes:

```python
session = Session(engine)
p = Patient(name="Test")
session.add(p)
session.commit()
print(p.id)  # Wants the database-generated ID
```

The print shows `None`.

Which fix is needed?

- A) Change `int | None` to `int` in the model
- B) Call `session.refresh(p)` after `commit()`
- C) Call `session.flush()` instead of `commit()`
- D) The ID is never available until you restart the server

**Your answer:** ________b

---

### Q8

**True or False:** A `UNIQUE` constraint in PostgreSQL allows one NULL value, but a `PRIMARY KEY` constraint does NOT allow any NULL values.

**Your answer:** ________True

---

### Q9

```python
class Note(SQLModel, table=True):
    content: str
    patient_id: int = Field(foreign_key="patients.id")
```

Without any `Relationship` defined, which of these will work?

- A) `note.patient.name` — accessing the patient's name from a note
- B) `patient.notes` — accessing all notes of a patient
- C) Creating a note with a valid `patient_id` and having PostgreSQL enforce the link
- D) Both A and B

**Your answer:** ________c

---

### Q10

**True or False:** Lazy loading means SQLModel sends one big query upfront to load everything you might need.

**Your answer:** ________False

---

### Q11

**True or False:** Lazy loading is GOOD when you have a list of 1000 patients but only need to view their names, not their notes.

**Your answer:** ________true

---

### Q12

A note has:

```python
created_at: datetime = Field(default_factory=datetime.now)
updated_at: datetime = Field(default_factory=datetime.now)
```

The note is created at 9 AM. At 5 PM, someone edits the note's content.

What is `updated_at` after the edit?

- A) 5 PM — because `default_factory` re-runs on every save
- B) 9 AM — because `default_factory` only runs once at creation and nothing in the code updates `updated_at`
- C) NULL — because `default_factory` doesn't work with datetime
- D) The server crashes

**Your answer:** ________a

---

### Q13

A developer says: "I'll use `SQLModel.metadata.create_all(engine)` in production. If a table already exists, it'll just add any new columns I've defined."

**True or False:** The developer is correct.

**Your answer:** ________True

---

### Q14

Which of these best describes what a `Session` is in SQLModel?

- A) A permanent connection to the database that lives for the entire lifetime of the server
- B) A temporary workspace for a single unit of work — you open it, do operations, commit or rollback, then close it
- C) A configuration file that stores your database URL
- D) A tool for generating migration files

**Your answer:** ________b

---

### Q15

**True or False:** If you call `session.add(patient)` but never call `session.commit()`, then close the session — the patient IS saved to the database because `add()` sends data immediately.

**Your answer:** ________false

---

### Q16

Model files reference each other: Patient has `list["Note"]` and Note has `Optional["Patient"]`.

Why are strings used instead of the actual class names?

- A) Python can't handle classes that reference each other directly — circular import error
- B) Strings are faster to process
- C) SQLModel only works with string references
- D) FastAPI requires strings for JSON serialization

**Your answer:** ________do not know

---

### Q17

**Scenario:** A hospital has 2 million patient records. The `patients` table has a `name` column. Someone runs: `SELECT * FROM patients WHERE name ILIKE '%sharma%';`

**True or False:** This query will be fast because PostgreSQL automatically optimizes all text searches.

**Your answer:** ________true

---

### Q18

A student table has `email` with `unique=True`. Someone tries to insert two students with `email = NULL`.

**True or False:** PostgreSQL rejects the second NULL because UNIQUE means no duplicates, and NULL is treated as a value.

**Your answer:** ________True

---

### Q19

A Patient has many Notes. You write:

```python
patient = session.get(Patient, 1)
# AT THIS POINT: how many SQL queries have run?
print(len(patient.notes))
# AT THIS POINT: how many SQL queries have run?
```

How many SQL queries have executed at each marked point?

- A) 1 at first point, 2 at second point
- B) 0 at first point, 1 at second point
- C) 1 at both points
- D) 2 at first point, 2 at second point

**Your answer:** ________a

---

### Q20

**True or False:** Two transactions updating different rows of the same table will NEVER conflict with each other in PostgreSQL.

**Your answer:** ________True

---

When done, come back to me with your answers. I'll explain the ones you get wrong. No scores. Just understanding.
