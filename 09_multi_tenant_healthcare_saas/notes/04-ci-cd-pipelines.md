# CI/CD Pipelines

## What is CI/CD?

**Continuous Integration / Continuous Deployment** — automate the process from code change to production.

```
Developer pushes code
    │
    ▼
CI: Build & Test (automated)
    │
    ▼
CD: Deploy (automated)
    │
    ▼
Production
```

## Continuous Integration (CI)

Every time you push code, the CI server:
1. Checks out your code
2. Builds the Docker image
3. Runs tests (unit, integration, linting)
4. Reports results

```
git push → GitHub detects change → CI runner starts:
    
    Step 1: Checkout code
    Step 2: Install dependencies  
    Step 3: Run linter (ruff)
    Step 4: Run tests (pytest)
    Step 5: Build Docker image
    Step 6: Push image to registry
    Step 7: Notify team (pass/fail)
```

If any step fails, the pipeline stops. Bad code never reaches production.

## Continuous Deployment (CD)

After CI passes, CD automatically deploys:

```
CI passes ✅
    │
    ▼
CD starts:
    │
    ├── Pull latest Docker image
    ├── Run database migrations
    ├── Health check old version
    ├── Deploy new version (rolling update)
    ├── Health check new version
    └── Rollback if health check fails
```

## GitHub Actions (Example)

A pipeline definition file (`.github/workflows/deploy.yml`):

```
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          ssh server "docker compose pull && docker compose up -d"
```

## Deployment Strategies

| Strategy | How | Risk |
|---|---|---|
| Rolling | Replace containers one by one | Low — always some instances running |
| Blue-green | Two identical environments, switch traffic | Very low — instant rollback |
| Canary | Deploy to 10% of users first | Low — limit blast radius |

For healthcare SaaS, **blue-green** or **rolling** with health checks is standard. Never do a hard cut-over.

## Database Migrations in CI/CD

Migrations are the riskiest part of deployment:

```
MUST run before new code:   adding a nullable column
MUST run after new code:    removing a column
MUST be backward-compatible: renaming a column
```

Rules:
- **Additive changes** (new table, nullable column) — safe to run before deploy
- **Destructive changes** (drop column, remove table) — run after deploy, when old code is gone
- **Renames** — create new column + backfill + switch code + drop old (4-step process)

## The Complete Pipeline

```
Development → Push → CI (tests pass) → CD (deploy)
                                                  │
                                                  ▼
                                         Health checks pass?
                                              ├── Yes → Done ✅
                                              └── No  → Auto-rollback 🔄
```

## Key Insight

CI/CD is not about speed — it's about **confidence**. Every change goes through the same automated process. Manual deployments are error-prone; automated deployments are repeatable and auditable. For a medical SaaS, this audit trail is critical for compliance.
