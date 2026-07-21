# SaaS Security & Scaling

## Cross-Tenant Security

The #1 rule: **Tenant A can never see Tenant B's data.**

```
Common vulnerabilities:
❌ Missing tenant_id in query → leaks all tenants' data
❌ Caching without tenant key → returns wrong tenant's data
❌ Shared file storage → Tenant A accesses Tenant B's files
❌ Session confusion → wrong user switches tenants
```

## The Defense Layers

```
Layer 1: Middleware
Every request → extract & validate tenant_id

Layer 2: Query Filtering
Every DB query → WHERE tenant_id = ?

Layer 3: Row-Level Security (RLS)
PostgreSQL enforces tenant isolation at database level

Layer 4: Testing
Automated tests verify tenant isolation
```

## PostgreSQL Row-Level Security

RLS makes the database itself enforce tenant isolation:

```
CREATE POLICY tenant_isolation ON patients
    USING (tenant_id = current_setting('app.tenant_id'));

ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
```

Even if a query forgets the WHERE clause, RLS blocks cross-tenant access. This is a **safety net**, not a replacement for proper query filtering.

## Rate Limiting Per Tenant

One tenant shouldn't be able to overwhelm the system for others.

```
Rate limit key: "rate_limit:{tenant_id}:{endpoint}"
Limit: 1000 requests/minute per tenant
```

Store in Redis with TTL. If exceeded, return 429 Too Many Requests.

## Backups & Disaster Recovery

| Component | Backup strategy | Recovery time |
|---|---|---|
| PostgreSQL | Daily snapshots + WAL streaming | Minutes |
| Uploaded files | S3 with versioning | Instant |
| Redis | Periodic RDB snapshots | Minutes |

For multi-tenant SaaS, test restores **quarterly**. A backup nobody has tested isn't a backup.

## Scaling Dimensions

| Component | Scales by | Bottleneck |
|---|---|---|
| API instances | Add more containers | Database connections |
| PostgreSQL | Read replicas, connection pooling | Write throughput |
| Redis | Cluster mode | Memory |
| File storage | S3 (essentially unlimited) | Bandwidth |
| Workers | Add more worker containers | Queue throughput |

## The SaaS Maturity Model

```
Stage 1: Single tenant, single server
    → One client, everything on one VPS

Stage 2: Multi-tenant, single server
    → Multiple clients, shared infrastructure

Stage 3: Multi-tenant, scaled
    → Multiple API instances, read replicas, queues

Stage 4: Multi-region
    → Data residency (EU data in EU, India data in India)
```

Each stage adds complexity. Only build what you need today.

## Key Insight

A multi-tenant SaaS is not "an app" — it's a **platform**. Your customers depend on it being available, fast, and secure. Every architectural decision should prioritize tenant isolation, system reliability, and operational simplicity.
