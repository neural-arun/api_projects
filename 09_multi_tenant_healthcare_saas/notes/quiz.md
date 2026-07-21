# Quiz — Build 9: Multi-Tenant Healthcare SaaS

### Q1
What is the defining characteristic of a multi-tenant application?

- A) It uses multiple programming languages
- B) It serves multiple organizations from a single deployment
- C) It runs on multiple servers
- D) It has multiple databases

**Answer:** B

### Q2
**True or False:** A missing `tenant_id` filter in a database query could expose one tenant's data to another tenant.

**Answer:** True — this is the most common multi-tenant data leak.

### Q3
Which isolation strategy is easiest to implement?

- A) Separate databases per tenant
- B) Separate schemas per tenant
- C) Shared database, shared schema with tenant_id column
- D) Separate servers per tenant

**Answer:** C

### Q4
What does RLS (Row-Level Security) provide?

- A) Faster queries
- B) A database-level safety net that enforces tenant isolation
- C) Automatic password hashing
- D) Connection pooling

**Answer:** B

### Q5
What problem does Docker solve?

- A) Makes Python faster
- B) Ensures the same environment across development, testing, and production
- C) Replaces PostgreSQL
- D) Automates testing

**Answer:** B

### Q6
**True or False:** In a CI/CD pipeline, the deployment step should run before tests.

**Answer:** False — tests must pass before deployment.

### Q7
What is the purpose of health checks in production?

- A) To make the app run faster
- B) To verify the app is working correctly and route traffic accordingly
- C) To replace monitoring
- D) To test the app locally

**Answer:** B

### Q8
**Scenario:** You deploy a new version and the health check fails. What should happen?

- A) The deployment continues anyway
- B) The pipeline rolls back to the previous version
- C) The server shuts down
- D) The health check is ignored

**Answer:** B

### Q9
Why should database migrations be backward-compatible?

- A) To reduce query time
- B) So old and new code can run simultaneously during rolling deployments
- C) Because PostgreSQL requires it
- D) To simplify the schema

**Answer:** B

### Q10
**Scenario:** A tenant uploads 10,000 files per day. Another tenant uploads 10. How should rate limiting work?

- A) Same limit for all tenants
- B) Per-tenant rate limits based on their plan
- C) No rate limiting
- D) Rate limit by file size only

**Answer:** B
