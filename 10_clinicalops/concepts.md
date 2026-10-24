# 🏥 Build 10 · AI Clinical Operations Platform

> **Your build:** Turn a slow manual workflow into a trackable process: patient intake → AI assistance → human review → documented action.

**The rule:** AI prepares or organizes work; an authorized human reviews clinical decisions before action.

---

## 🧭 01 · Workflow architecture

**🧠 Concept**

- **Architecture:** The components in a system, their responsibilities, and how they exchange data.
- **Workflow state:** A named step in a process, such as `received`, `processing`, `needs_review`, or `completed`.
- **Monolith:** One application that can be deployed as a unit. It can still have well-separated internal modules.
- **Event-driven system:** Components publish events, such as `DocumentUploaded`, and other components handle them asynchronously.
- Events help separate slow or independent work, but require explicit handling for retries, ordering, and failures.

**⚠️ Important to remember**

- Start with a clear modular application unless separate deployment or workload needs are real. Microservices add network failures, deployment work, and operational overhead.
- Event delivery may happen more than once. Make event handlers safe to retry and record state transitions so a workflow can recover.

**🩺 In Clinical Operations**

- Intake, AI processing, review, and action each need clear ownership and a record of state changes.
- A saved state makes it possible to see whether an item is waiting for AI, waiting for a person, approved, or complete.

**🛠 Build it**

- Model the workflow with explicit states such as received, processing, needs review, approved, and completed.
- Start with clear modules in one app; add events or queues where slow work or independent scaling requires them.
- Record valid state transitions and who or what caused each transition.

![Mind map: Clinical workflow](assets/mindmaps/01-workflow-architecture.svg)

---

## 🤖 02 · Agents, queues & human review

**🧠 Concept**

- **Agent:** A model-driven process that can choose among permitted steps or tools to work toward a goal.
- **Tool:** A specific action the agent is allowed to call, such as retrieving an approved document or drafting a summary.
- **Queue:** A place for work that must wait for a worker or reviewer.
- **Human review:** A checkpoint where an authorized person examines the proposal and accepts, edits, or rejects it.
- Keep AI proposals separate from approved actions so the system can show exactly what a person reviewed.

**⚠️ Important to remember**

- “Human in the loop” only helps if the reviewer sees the evidence, uncertainty, and proposed action and has time and authority to reject it.
- Treat model output as untrusted input. Restrict tools and data, and do not let the agent perform a high-impact clinical action without the required approval.

**🩺 In Clinical Operations**

- An AI assistant may summarize intake or prepare a triage suggestion.
- A clinician reviews the proposal and records whether it was accepted, changed, or rejected before action.

**🛠 Build it**

- Limit the agent to defined tools and data.
- Keep proposed output separate from approved action.
- Put review-required cases into a queue with clear status and ownership.
- Record who reviewed the output, what changed, and what action followed.
- Handle timeouts and failures without losing the intake record or leaving it falsely marked complete.

![Mind map: Human-reviewed AI](assets/mindmaps/02-agents-human-review.svg)

---

## 📊 03 · Observability: metrics, logs, traces

**🧠 Concept**

- **Observability:** Signals that help explain the system’s behavior from what it reports while running.
- **Metrics:** Numbers tracked over time, such as queue depth or request duration.
- **Logs:** Individual event records, such as “job 81 failed to process.”
- **Traces:** A timeline following one request as it passes through API, queue, worker, and database.
- **Request ID:** A shared identifier that helps connect logs and traces from one operation.

**⚠️ Important to remember**

- Do not put patient names, note text, tokens, or other protected health information in metric labels or routine logs.
- Observability helps diagnose operations; it is not an audit trail. Record important clinical and permission-related actions in a separate access-controlled audit log.

**🩺 In Clinical Operations**

- Teams need to notice rising processing delays, failed jobs, or reviews waiting too long.
- Request IDs connect operational details while patient content stays out of routine logs.

**🛠 Build it**

- Track request duration, queue depth, processing failures, and review wait time.
- Use Prometheus to store/query metrics and Grafana to display dashboards and alerts.
- Use request IDs to connect logs and traces; keep protected health information out of metric labels and routine logs.
- Keep a distinct audit log for who accessed, reviewed, or changed a case.

![Mind map: System health](assets/mindmaps/03-observability.svg)

---

## 📈 04 · Production scaling & tradeoffs

**🧠 Concept**

- **Scaling up:** Give one server more resources. **Scaling out:** Run more copies of a service.
- **Bottleneck:** The slow or capacity-limited step that holds back the full workflow.
- **Queue and worker:** Let the API accept work quickly while workers process it at a controlled rate.
- A monolith is often simpler; event-driven services can isolate workloads but add network, delivery, and monitoring complexity.

**⚠️ Important to remember**

- Measure before splitting services or adding capacity. The bottleneck may be human review, a database, or a model provider—not the API server.
- A queue smooths bursts but does not create unlimited capacity. Watch queue age and define a safe fallback when workers or AI services fail.

**🩺 In Clinical Operations**

- Intake may be fast, while AI processing or human review takes longer and has different capacity limits.
- A growing queue or longer review wait may signal a staffing or workflow bottleneck, not just a need for more API servers.

**🛠 Build it**

- Measure slow steps before changing architecture.
- Move long AI or document jobs to workers; keep APIs stateless where possible; use queues for work that can wait.
- Define alerts and a safe fallback when AI or downstream services fail.
- Track time from intake to human review as well as API response time.

![Mind map: Scale by evidence](assets/mindmaps/04-scaling-tradeoffs.svg)

### 📚 Official references

- [Prometheus overview](https://prometheus.io/docs/introduction/overview/)
- [Grafana getting started](https://grafana.com/docs/grafana/latest/fundamentals/getting-started/)
- [GitHub Actions workflows](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows)
