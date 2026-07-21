# Isolation Strategies

## The Isolation Spectrum

How much do tenants share? There are three main approaches:

```
Low isolation ──────────────────────────→ High isolation
(cheaper, less secure)          (costlier, more secure)

Shared DB    →  Shared Schema   →  Separate DB
Sharing      →  Shared DB,      →  Each tenant
everything     separate schemas    gets own DB
```

## Strategy 1: Shared Database, Shared Schema (Discriminator Column)

All tenants share one database and one set of tables. Each row has a `tenant_id`.

```
patients table:
┌────┬───────────┬───────────┐
│ id │ tenant_id  │ name     │
├────┼───────────┼───────────┤
│ 1  │ clinic_a  │ Ravi     │
│ 2  │ clinic_b  │ Priya    │
│ 3  │ clinic_a  │ Arun     │
└────┴───────────┴───────────┘
```

**Pros:** Simplest to implement, lowest cost, easiest to scale
**Cons:** Must add `WHERE tenant_id = ?` to every query, risk of data leaks

**Best for:** Early-stage SaaS, low-compliance data

## Strategy 2: Shared Database, Separate Schemas

Each tenant gets their own schema (namespace) in the same database.

```
Database: medapp
├── schema: clinic_a
│   ├── patients
│   └── notes
├── schema: clinic_b
│   ├── patients
│   └── notes
└── schema: clinic_c
    ├── patients
    └── notes
```

**Pros:** Better isolation (no risk of missing WHERE clause), can backup/restore per tenant
**Cons:** More complex migrations (run per schema), more database connections

**Best for:** Mid-stage SaaS, healthcare data with moderate compliance needs

## Strategy 3: Separate Databases

Each tenant gets their own PostgreSQL database.

```
PostgreSQL server:
├── database: medapp_clinic_a
│   ├── patients
│   └── notes
├── database: medapp_clinic_b
│   ├── patients
│   └── notes
└── database: medapp_clinic_c
    ├── patients
    └── notes
```

**Pros:** Strongest isolation, per-tenant performance tuning, true data separation
**Cons:** Highest cost, connection management, complex migrations

**Best for:** Enterprise healthcare, strict compliance (HIPAA), large tenants

## Comparing Strategies

| Aspect | Shared Schema | Separate Schema | Separate DB |
|---|---|---|---|
| Data isolation | Weak | Strong | Strongest |
| Query complexity | Must include tenant_id | Automatic (schema per tenant) | Automatic |
| Migration complexity | Single migration | Run N migrations | Run N migrations |
| Cost | Lowest | Medium | Highest |
| Backup/restore | All tenants at once | Per tenant | Per tenant |
| Compliance | Low | Medium | High |

## Healthcare Recommendation

For healthcare SaaS:
- **Start with shared schema** (faster development)
- **Add tenant_id checks** via middleware (cannot be forgotten)
- **Migrate to separate schemas** when compliance requires it
- **Separate databases** only for enterprise clients with specific requirements

## The Middleware Solution

To prevent accidental data leaks in shared schema mode:

```
@app.middleware("http")
async def add_tenant_context(request, call_next):
    tenant_id = extract_tenant(request)
    
    # Store in request state (accessible in all dependencies)
    request.state.tenant_id = tenant_id
    
    response = await call_next(request)
    return response
```

Then in database queries, never query without tenant context.
