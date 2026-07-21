# Deployment Architecture

## Production Stack

```
                           ┌──────────────┐
                           │  DNS         │
                           │  medapp.com  │
                           └──────┬───────┘
                                  │
                           ┌──────▼───────┐
                           │  HTTPS       │
                           │  (Let's Encrypt)│
                           └──────┬───────┘
                                  │
                           ┌──────▼───────┐
                           │  Reverse     │
                           │  Proxy       │
                           │  (Nginx)     │
                           └──────┬───────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
        ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
        │  FastAPI  │      │  FastAPI  │      │  FastAPI  │
        │  Instance │      │  Instance │      │  Instance │
        │  1        │      │  2        │      │  3        │
        └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │  PostgreSQL (Primary +     │
                    │  Read Replica)             │
                    └───────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │  Redis (Cache + Queue)     │
                    └───────────────────────────┘
```

## Reverse Proxy (Nginx)

Nginx sits in front of your API instances. It handles:

| Function | What it does |
|---|---|
| TLS termination | Handles HTTPS, passes HTTP to your API |
| Load balancing | Distributes requests across API instances |
| Static files | Serves uploaded files directly (fast) |
| Rate limiting | Blocks excessive requests before they hit your API |
| Request buffering | Handles large uploads gracefully |

```
server {
    listen 443 ssl;
    server_name clinic-a.medapp.com;
    
    location /api/ {
        proxy_pass http://api_cluster;
        proxy_set_header Host $host;
    }
    
    location /static/ {
        alias /data/uploads/;  # Served directly by Nginx
    }
}
```

## HTTPS with Let's Encrypt

All traffic must be encrypted. Let's Encrypt provides free TLS certificates:

```
# Certbot automates certificate issuance and renewal
certbot --nginx -d medapp.com -d clinic-a.medapp.com
```

Certificates auto-renew every 90 days. No manual intervention.

## Environment Configuration

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/medapp
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}  # From .env file or secrets manager
      - ENVIRONMENT=production
      - LOG_LEVEL=info
```

Never hardcode secrets. Use:
- `.env` files locally
- Secrets manager in production (AWS Secrets Manager, HashiCorp Vault)

## Health Checks

Production deployments need health check endpoints:

```
GET /health → {"status": "ok", "db": "connected", "redis": "connected"}
```

Used by:
- Load balancer (don't send traffic to unhealthy instances)
- CI/CD pipeline (verify deployment succeeded)
- Monitoring (alert if health check fails)

## Monitoring Stack

```
┌──────────┐   ┌──────────┐   ┌──────────┐
│ FastAPI  │──▶│ Metrics  │──▶│ Grafana  │
│ Metrics  │   │(Prometheus)│  │ Dashboard│
└──────────┘   └──────────┘   └──────────┘

┌──────────┐   ┌──────────┐
│ Logs     │──▶│ Log      │  Centralized log viewer
│ (JSON)   │   │ Aggregator│
└──────────┘   └──────────┘

┌──────────┐   ┌──────────┐
│ Alerts   │──▶│ Pager    │  When something breaks
│ Rules    │   │ (Slack)  │
└──────────┘   └──────────┘
```

## Key Insight

Deployment is not a one-time setup — it's a **system** that must be maintained. The goal is to make deployment boring: push code, pipeline runs, app updates, no one panics. Boring deployments = reliable systems.
