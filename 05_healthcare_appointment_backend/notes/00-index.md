# Build 5 — Healthcare Appointment Backend: Study Notes

## How To Use These Notes

Read them in order. Each file builds on the previous one. Code examples are progressive.

## Files

| # | File | What You'll Learn |
|---|---|---|
| 01 | `01-project-structure-and-architecture.md` | Service layer pattern, app/ package structure |
| 02 | `02-environment-and-config.md` | .env files, pydantic-settings, BaseSettings |
| 03 | `03-service-layer-pattern.md` | Business logic in services, Depends() injection |
| 04 | `04-transactions-and-data-integrity.md` | ACID, commit/rollback, savepoints |
| 05 | `05-logging-and-monitoring.md` | Python logging, JSON logs, request IDs |
| 06 | `06-testing-with-pytest.md` | TestClient, test DB, mocking |
| 07 | `07-building-the-appointment-system.md` | Complete working appointment system |
| 08 | `quiz.md` | 12+ questions with answer key |

## Prerequisites

- Build 1 completed (FastAPI basics: routes, Pydantic, HTTP methods)
- Build 2 completed (SQLAlchemy/SQLModel, database CRUD, Alembic)
- Build 3 completed (auth patterns, dependency injection)
- PostgreSQL installed and running

## What You'll Learn

- Why a **service layer** keeps your code maintainable
- How **transactions** protect healthcare data integrity
- How to **structure a production FastAPI project**
- How to **test** endpoints with a real database
- How to build an **appointment booking system** with conflict detection

## Official Reference Links

- [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [pytest docs](https://docs.pytest.org/)
