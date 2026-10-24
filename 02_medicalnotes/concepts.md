# 🩺 Build 02 · Clinical Notes Backend

> **Your build:** A doctor creates and edits notes for a patient, searches them, and reviews visit history. Notes are sensitive records, so each note must stay connected to the correct patient and be shown only to authorized users.

**The journey:** Patient → Visit → Note → Search/history

---

## 🗃️ 01 · PostgreSQL & SQL  
### Give notes a reliable home

**🧠 Concept** — PostgreSQL is a relational database: it stores structured records in tables. SQL is the language used to create, read, update, and delete those records.

**🩺 In Clinical Notes** — Keep patients in one table and visit notes in another. A note belongs to a patient, and a patient can have many notes.

**🛠 Build it** — Create patient and note tables. Use a patient ID on each note, then query by patient, visit date, or search text.

~~~text
Patient table 1 ───── many Note rows
patient_id                  patient_id
name                        visit_date
                            note_text
~~~

---

## 🧱 02 · SQLAlchemy, SQLModel & sessions  
### Work with database rows in Python

**🧠 Concept** — An ORM maps database tables to Python objects. SQLAlchemy provides the ORM and database session. SQLModel builds on SQLAlchemy and Pydantic, using type-annotated models for both data validation and database mapping.

**🩺 In Clinical Notes** — A Patient object and a Note object represent the database rows your API creates and searches.

**🛠 Build it**

- Learn the SQLAlchemy model, query, and session flow first.
- Use a session to query or change rows; commit successful changes and close the session after the request.
- Try SQLModel as a concise way to define models. Keep request/response models distinct when the API needs different fields.

~~~text
API operation
    ↓
database session
    ├── query patient / notes
    ├── add or edit note
    └── commit or rollback
~~~

---

## 🔗 03 · Relationships, CRUD & transactions  
### Keep patient history consistent

**🧠 Concept** — A foreign key links a row to another table. An ORM relationship makes that link easier to navigate. A transaction groups database changes so they succeed together or are rolled back together.

**🩺 In Clinical Notes** — A note must reference a real patient. Saving a visit and its note should not leave a half-created record if one step fails.

**🛠 Build it**

- Link each note to a patient with a foreign key.
- Implement create, read, update, and delete using database queries.
- Search notes through the patient relationship.
- Use a transaction when one user action changes multiple related rows.

~~~text
Create note
├── verify patient
├── save visit + note
└── commit together
    └── on failure → rollback
~~~

---

## 🧰 04 · Dependency injection, Alembic & project structure  
### Keep the backend maintainable

**🧠 Concept** — Dependency injection supplies shared resources to an operation. Alembic tracks database schema changes as versioned migrations.

**🩺 In Clinical Notes** — Each request needs a database session. As the patient and note tables evolve, existing databases need a safe way to upgrade.

**🛠 Build it**

- Use FastAPI Depends() to provide and close a session per request.
- Put routes, models, schemas, and database setup in separate modules.
- Create an Alembic migration when the schema changes; practice upgrade and rollback.
- Keep clinical content out of routine logs.

~~~text
api/       routes and HTTP
models/    database tables
schemas/   API input/output
db/        engine and sessions
migrations/ schema history
~~~

### 📚 Official references

- [PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial.html)
- [SQLAlchemy ORM quick start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html) · [Sessions](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [SQLModel tutorial](https://sqlmodel.tiangolo.com/tutorial/) · [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
