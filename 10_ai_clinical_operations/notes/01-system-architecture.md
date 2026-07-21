# System Architecture

## The Clinical Ops Pipeline

```
Patient Intake ──→ AI Processing ──→ Human Review ──→ Action
                        │                  │
                        ▼                  ▼
                   Assessment          Doctor confirms
                   + Triage            + Prescribes
                   + Education         + Schedules
```

This is not a single API. It's a **system of systems** — multiple services, queues, and AI components working together.

## High-Level Architecture

```
                        ┌──────────────┐
                        │  Frontend    │
                        │  (Patient &  │
                        │   Doctor UI) │
                        └──────┬───────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────┐
│                  API Gateway                         │
│  Auth (B3) │ Rate Limit │ Tenant (B9) │ Routing     │
└─────────────────────┬───────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ Patient  │  │ Clinical │  │ AI Service   │
│ Service  │  │ Notes    │  │ (RAG - B8)   │
│ (B1/B5)  │  │ (B2)     │  │ (Chat - B6)  │
└──────────┘  └──────────┘  └──────┬───────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │  Queue (B7)      │
                          │  Celery + Redis  │
                          └────────┬─────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     │                           │
                     ▼                           ▼
              ┌──────────────┐          ┌──────────────┐
              │ Document     │          │ Notification │
              │ Processor    │          │ Service      │
              └──────────────┘          └──────────────┘
```

## Data Flow (End to End)

```
1. Patient submits symptom form → Frontend
2. Frontend → API Gateway → Patient Service
3. Patient Service stores data → PostgreSQL
4. Patient Service emits event: "patient.intaked"
5. AI Service picks up event → Runs RAG triage
6. AI assessment stored → Clinical Notes Service
7. Notification sent to doctor → "New patient needs review"
8. Doctor reviews → Approves / Modifies
9. Action taken: prescription, appointment, education resources
```

## Service Boundaries

| Service | Responsibility | Build Origin |
|---|---|---|
| Patient Service | Patient CRUD, task management | Build 1, 5 |
| Clinical Notes | Notes, visit history | Build 2 |
| Auth Service | Login, roles, permissions | Build 3 |
| Upload Service | File handling, document storage | Build 4 |
| Queue Service | Async processing, document pipeline | Build 7 |
| RAG Service | Medical knowledge retrieval | Build 8 |
| Chat Service | Real-time tutor communication | Build 6 |

## Monolith vs Microservices

For this project, start as a **modular monolith**:
- Single deployable unit
- Clear internal module boundaries
- Can split into microservices later

```
Monolith:               Microservices:
┌──────────────┐        ┌──┐ ┌──┐ ┌──┐
│ Patient      │        │P │ │C │ │AI│
│ Clinical     │        │  │ │  │ │  │
│ Auth         │        └──┘ └──┘ └──┘
│ AI           │        └──┘ └──┘ └──┘
└──────────────┘
```

Build 10 is a modular monolith with clear interfaces between modules.

## Key Insight

This architecture is the **composition** of everything you've built. Each previous build is a module in this system. The "new" thing in Build 10 is not a new technology — it's the **integration** of all the pieces into a coherent clinical workflow.
