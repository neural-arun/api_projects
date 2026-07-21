# Transactions and Data Integrity

## What Are Database Transactions?

A transaction is a unit of work that must complete **fully or not at all**.

Imagine booking an appointment:
1. Check if slot is free
2. Create the appointment record
3. Send a notification

If step 3 fails, but step 2 already saved — now you have an appointment the patient doesn't know about. A transaction ensures steps 1-3 all succeed together, or none apply.

## ACID Properties

Healthcare data needs ACID compliance.

| Property | Meaning | Healthcare Example |
|---|---|---|
| **Atomicity** | All or nothing | Can't save appointment without checking conflict |
| **Consistency** | Data follows rules | No appointment for a deleted patient |
| **Isolation** | Concurrent bookings don't interfere | Two receptionists can't double-book |
| **Durability** | Committed data survives crashes | Power outage doesn't lose the booking |

## SQLAlchemy Session as Transaction Boundary

Every SQLAlchemy `Session` starts a transaction when you use it.

```python
session = Session(engine)   # implicit BEGIN
session.add(some_object)    # staged, not saved
session.commit()            # writes everything or ROLLBACK
```

```python
from sqlmodel import Session

with Session(engine) as session:
    # Inside this block = one transaction
    session.add(appointment)
    session.commit()  # If this fails → automatic rollback
```

## commit() and rollback()

```python
# app/services/appointment_service.py
def create_appointment(self, data: AppointmentCreate) -> Appointment:
    start = data.start_time
    end = start + timedelta(minutes=data.duration_minutes)

    if self.check_conflict(data.doctor_id, start, end):
        raise ValueError("Time slot already booked")

    try:
        apt = Appointment(...)
        self.session.add(apt)
        self.session.commit()         # Save to database
        self.session.refresh(apt)     # Get generated ID
        return apt
    except Exception:
        self.session.rollback()       # Undo everything
        raise
```

**Warning:** If you `raise` before `commit()`, the transaction remains open. Always `commit()` or `rollback()`.

## The get_session Generator

```python
# app/database.py
from sqlmodel import Session, create_engine
from app.config import settings

engine = create_engine(settings.database_url)


def get_session():
    with Session(engine) as session:
        yield session  # FastAPI handles commit/rollback
```

FastAPI calls `next(get_session())` to get the session. When the request finishes, the `with` block exits and the session closes. If an exception occurred, `Session.__exit__` calls `rollback()`.

## Nested Transactions and Savepoints

Savepoints let you roll back part of a transaction.

```python
# Create a savepoint
sp = session.begin_nested()
try:
    session.add(some_record)
    sp.commit()  # commits just this savepoint
except:
    sp.rollback()  # rolls back just this savepoint
    # Outer transaction continues normally
```

Useful when one service calls another and you want partial rollback.

## Healthcare Scenario: Booking an Appointment

```
1. BEGIN TRANSACTION
2. SELECT * FROM appointments WHERE doctor_id=1 AND time overlaps
3. → No conflict found
4. INSERT INTO appointments (patient_id, doctor_id, start, end)
5. UPDATE doctor_schedule SET booked = true
6. COMMIT

If INSERT succeeds but UPDATE fails:
    ROLLBACK — appointment is NOT saved
```

## References

- [SQLAlchemy Sessions](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [SQLAlchemy commit/rollback](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.commit)
