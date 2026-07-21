# Event-Driven Architecture

## What is Event-Driven?

Instead of Service A calling Service B directly, Service A **emits an event** when something happens. Any interested service can react.

```
DIRECT (sync):
Upload Service ──POST /ai──▶ AI Service
    │                        │
    │◀───── Response ────────│
    │  (waits 30 seconds!)   │

EVENT-DRIVEN (async):
Upload Service ──emit("document.uploaded")──▶ Event Bus
    │                                          │
    │  (returns immediately)                   │
    │                                          ▼
    │                               ┌──────────────────┐
    │                               │ AI Service picks  │
    │                               │ up event          │
    │                               └──────────────────┘
    │                                          │
    │                                          ▼
    │                               ┌──────────────────┐
    │                               │ Notification      │
    │                               │ picks up "done"   │
    │                               └──────────────────┘
```

## Events vs Commands

| | Event | Command |
|---|---|---|
| What | Something happened | Do something |
| Sender | Doesn't care who reacts | Expects a result |
| Example | "patient.created" | "send.email" |
| Coupling | Loose | Tight |

Events are past tense. Commands are requests for action.

## Clinical Events

In a clinical operations system, events might be:

```
patient.registered       → Patient signs up
patient.intaked          → Symptoms submitted
triage.completed         → AI assessed urgency
doctor.reviewed          → Doctor approved plan
medication.prescribed    → Prescription issued
appointment.scheduled    → Follow-up booked
critical.alert           → Abnormal results detected
```

Each event can trigger multiple reactions independently.

## The Event Bus

In FastAPI, the simplest event bus is Redis Pub/Sub or a Celery task that fans out to multiple handlers:

```
event_bus.publish("patient.intaked", patient_data)
    │
    ├── AI Service: Run triage
    ├── Notification Service: Notify doctor
    └── Audit Service: Log the event
```

Each handler runs independently. If AI Service fails, Notification Service still works.

## Why Event-Driven for Clinical Ops

| Benefit | Why it matters |
|---|---|
| Decoupling | Failures don't cascade |
| Scalability | Each handler can scale independently |
| Audit trail | Every event is logged |
| Extensibility | Add new handlers without changing existing code |
| Resilience | Events can be replayed if processing fails |

## Choreography vs Orchestration

**Choreography:** Services react to events independently. Like dancers following the music.

```
Patient Service emits "patient.intaked"
    → AI Service picks up, emits "triage.completed"
        → Notes Service picks up, stores assessment
            → Notification Service picks up, alerts doctor
```

**Orchestration:** A central coordinator tells services what to do.

```
Workflow Engine:
    1. Call Patient Service → intake patient
    2. Call AI Service → triage
    3. Call Notes Service → store
    4. Call Notification → alert doctor
```

For clinical ops, **choreography** is simpler and more flexible. Orchestration adds complexity but provides more control for complex workflows.

## Key Insight

Event-driven architecture transforms your system from a **chain of dependencies** (A→B→C) into a **web of reactions** (A→event→B, A→event→C). This is how you build systems that don't fall over when one component fails.
