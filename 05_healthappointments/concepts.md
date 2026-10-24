# 📅 Build 05 · Healthcare Appointment Backend

> **Your build:** Patients find a doctor’s open time slot, book it, and review visit history. The system must prevent two patients from booking the same slot.

**The journey:** Find slot → request booking → confirm once → record visit

---

## 🧱 01 · Project structure & service layer

**🧠 Concept** — Project structure separates responsibilities. Routes handle HTTP; services contain application decisions; models and database modules handle stored data; configuration lives outside business logic.

**🩺 In Appointments** — Booking involves patients, doctors, slots, and appointments. Putting all rules inside one route makes changes hard to follow.

**🛠 Build it** — Organize modules such as api/, services/, models/, schemas/, db/, and config/. Keep the route thin: validate the request, call a booking service, return the result.

~~~text
HTTP route → booking service → database
                    ↓
          slot and booking rules
~~~

---

## 🔒 02 · Transactions & scheduling

**🧠 Concept** — A transaction groups related database changes. It either commits all of them or rolls them back. Scheduling also requires representing times consistently, including time zones.

**🩺 In Appointments** — Check a slot and create its appointment as one transaction. Otherwise, two requests arriving together could both see the slot as open and book it.

**🛠 Build it**

- Store a clear start/end time and the relevant time zone.
- Enforce a database constraint that prevents duplicate active bookings for the same slot.
- In one transaction, verify availability, create the appointment, and mark the slot booked.
- If the operation fails, roll it back and return a conflict.

~~~text
Booking transaction
├── slot still open?
├── create appointment
├── reserve slot
└── commit together or rollback
~~~

---

## 🧾 03 · Configuration, logging & request IDs

**🧠 Concept** — Configuration supplies environment-specific values; structured logs record events as searchable fields. A request ID links logs from one API call.

**🩺 In Appointments** — When a booking fails, staff need to find the relevant event without exposing patient details in logs.

**🛠 Build it** — Keep database URLs and secrets in environment configuration. Log a request ID, operation, outcome, and timing; avoid logging clinical note content or access tokens.

~~~text
Request ID
├── API log
├── booking service log
└── database/error log
~~~

---

## 🧪 04 · Tests — pytest & TestClient

**🧠 Concept** — Unit tests check one piece of logic. Integration tests check several parts working together. FastAPI TestClient sends test requests to the app without a real browser.

**🩺 In Appointments** — Test the booking rules and the full request path, especially that a slot cannot be double-booked.

**🛠 Build it**

- Unit-test slot availability and time rules.
- Use TestClient to test create, read, update, and booking endpoints.
- Integration-test two booking attempts for the same slot; only one should succeed.
- Keep test data separate from real patient information.

~~~text
Unit test → one rule
TestClient → API behavior
Integration test → API + database + transaction
~~~

### 📚 Official references

- [FastAPI project testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest getting started](https://docs.pytest.org/en/stable/getting-started.html)
- [SQLAlchemy sessions and transactions](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
