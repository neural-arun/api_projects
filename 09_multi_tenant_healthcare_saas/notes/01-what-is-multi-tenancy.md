# What is Multi-Tenancy?

## The Concept

A **multi-tenant** application serves multiple organizations (tenants) from a single deployment.

```
┌──────────────────────────────────────────────┐
│            Your API (one deployment)          │
│                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Clinic A │  │ Clinic B │  │ Med      │   │
│  │ (tenant) │  │ (tenant) │  │ College  │   │
│  │          │  │          │  │ (tenant) │   │
│  │ Dr. Ravi │  │ Dr. Priya│  │ Student  │   │
│  │ Patient  │  │ Patient  │  │ Records  │   │
│  │ Records  │  │ Records  │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────────────────────────────┘
```

Each tenant:
- Has their own users, patients, notes, appointments
- Cannot see other tenants' data
- Gets their own subdomain or identifier

## Why Multi-Tenancy?

| Model | Description | Example |
|---|---|---|
| Single-tenant | Each customer gets their own server instance | Hospital installs your software on-premise |
| Multi-tenant | All customers share one server, data is isolated | SaaS like Google Drive, Notion |

Multi-tenant is cheaper (share infrastructure), easier to maintain (one codebase), and scales better (add capacity to the pool).

## Tenant Identification

Each request must identify which tenant it belongs to:

```
Option 1: Subdomain
clinic-a.medapp.com/api/patients
clinic-b.medapp.com/api/patients

Option 2: Header
GET /api/patients
X-Tenant-ID: clinic-a

Option 3: Path prefix
/api/tenant/clinic-a/patients
```

Subdomains are most common for SaaS — they feel like separate apps to each tenant.

## The Tenant Context

Once identified, the tenant ID flows through the entire request:

```
Request → Middleware extracts tenant ID
    │
    ▼
Tenant ID added to request state
    │
    ▼
DB queries filtered by tenant_id
    │
    ▼
All data operations scoped to that tenant
```

Every table needs a `tenant_id` column to isolate data.

## Database Schema

```
All tables include tenant_id:

patients:
├── id
├── tenant_id ← Every row knows which tenant it belongs to
├── name
└── ...

notes:
├── id
├── tenant_id
├── patient_id
└── ...

Every query includes: WHERE tenant_id = current_tenant
```

Missing a `WHERE tenant_id = ?` is a **data leak** — tenant B sees tenant A's data. This is the #1 security risk in multi-tenant systems.

## The Tenant Lifecycle

```
1. New clinic signs up
2. System creates tenant record
3. System provisions tenant resources (DB schema, storage)
4. Tenant admin creates users
5. Users login and start working

When tenant leaves:
6. Export their data
7. Delete tenant record (cascades to all their data)
8. Reclaim resources
```

## Key Systems Insight

Multi-tenancy is a **cross-cutting concern** — it touches every part of your application. Every query, every cache key, every background task must include the tenant context. Getting it wrong = data leaking between tenants.
