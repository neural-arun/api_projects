# 🏢 Build 09 · Multi-Tenant Healthcare SaaS

> **Your build:** One hosted product serves Clinic A, Clinic B, and a medical college while keeping each organization’s records and settings separate.

**The journey:** Identify organization → enforce isolation → serve its data and configuration

---

## 🏘️ 01 · Multi-tenancy & data isolation

**🧠 Concept** — A tenant is an organization sharing the same application. Tenant isolation ensures one organization cannot read or change another organization’s data.

**🩺 In Healthcare SaaS** — Each clinic has its own patients, users, permissions, and configuration.

**🛠 Build it**

- Choose a storage design: separate schema/database per tenant, or shared tables with a tenant ID on every row.
- Apply tenant scope on the server to every query and write.
- Check the user’s organization membership and role.
- Never trust a tenant ID supplied by the browser without verifying membership.
- Test that Clinic A cannot fetch Clinic B’s records.

~~~text
Signed-in user
├── identify organization
├── check role
└── query only that tenant’s records
~~~

---

## 🔐 02 · Tenant-specific permissions & configuration

**🧠 Concept** — Authorization determines what a user may do. Configuration supplies settings that vary by organization.

**🩺 In Healthcare SaaS** — A clinic admin may manage clinic staff; a staff member may only see permitted patient workflows. Clinics may have different branding or reminder settings.

**🛠 Build it** — Keep organization membership, roles, and tenant settings explicit. Add new tenant-specific fields deliberately; do not let configuration bypass privacy or access rules.

~~~text
Organization
├── users + roles
├── isolated records
└── settings
~~~

---

## 📦 03 · Docker & Docker Compose

**🧠 Concept** — A container packages an application with its runtime environment. Docker Compose describes and runs a group of connected containers.

**🩺 In Healthcare SaaS** — The API, database, and supporting services need a repeatable local and deployment setup.

**🛠 Build it** — Build the API image; use a Compose file for the API, database, networks, and persistent volumes. Keep secrets in environment configuration, not in the image.

~~~text
Compose application
├── API container
├── PostgreSQL container
└── network + persistent volume
~~~

---

## 🚀 04 · Linux, Nginx & CI/CD

**🧠 Concept** — A VPS is a rented Linux server. Nginx can act as a reverse proxy, forwarding public HTTPS requests to the application. CI/CD automates checks and deployment steps.

**🩺 In Healthcare SaaS** — Clinics need the service available through a stable, secure endpoint, with changes deployed consistently.

**🛠 Build it**

- Run the app and database on a managed or self-managed host.
- Put a reverse proxy in front of the API; configure HTTPS and request limits.
- Use GitHub Actions to run checks on changes and deploy only from a controlled workflow.
- Back up data and test tenant isolation before a release.

~~~text
GitHub change → CI checks → deployment
Browser → HTTPS/Nginx → API → tenant-scoped database
~~~

### 📚 Official references

- [Docker Compose overview](https://docs.docker.com/compose/)
- [GitHub Actions continuous integration](https://docs.github.com/en/actions/get-started/continuous-integration)
- [Nginx documentation](https://nginx.org/en/docs/)
