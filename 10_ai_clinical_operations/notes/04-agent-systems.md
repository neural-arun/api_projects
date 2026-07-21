# Agent Systems

## What is an AI Agent?

An agent is not a simple LLM call. It's an LLM **with tools, memory, and autonomy**:

```
┌─────────────────────────────┐
│         Agent               │
│                             │
│  ┌─────────────────────┐    │
│  │  LLM (Brain)        │    │
│  │  + System Prompt    │    │
│  │  + Conversation     │    │
│  │  History            │    │
│  └──────────┬──────────┘    │
│             │               │
│    ┌────────┴────────┐     │
│    │    Tools         │     │
│    │                 │     │
│    │ - Search RAG    │     │
│    │ - Query DB      │     │
│    │ - Create Note   │     │
│    │ - Schedule Appt │     │
│    │ - Send Message  │     │
│    └────────────────┘     │
└─────────────────────────────┘
```

The agent doesn't just answer questions — it takes **actions** in the system.

## Medical Tutor Agent

A student asks a question. The agent decides what to do:

```
Student: "I'm confused about ACE inhibitors. Can you help?"

Agent thinks:
1. I need to check what the student already knows
→ Tool: query_knowledge_base("ACE inhibitors curriculum")

2. I should find relevant lecture content
→ Tool: search_rag("ACE inhibitors mechanism side effects")

3. Let me create a study plan
→ Tool: create_study_session(student_id, topic="ACE inhibitors")

4. Let me schedule a follow-up
→ Tool: schedule_quiz(student_id, topic="ACE inhibitors", date=tomorrow)

Agent responds:
"Let me check what we've covered... According to your lectures,
ACE inhibitors work by blocking angiotensin-converting enzyme.
I've created a study session for you with practice questions tomorrow."
```

## Triage Agent

A patient submits symptoms. The agent processes them:

```
Patient: "I have chest pain and shortness of breath"

Agent:
1. Check urgency → Tool: assess_severity("chest pain, shortness of breath")
   Result: HIGH — potential cardiac issue

2. Search for relevant information
   → Tool: search_rag("chest pain emergency protocol")

3. Create triage note for doctor
   → Tool: create_note(patient_id, "URGENT: Chest pain + SOB, seen at 10:30")

4. Notify doctor
   → Tool: send_alert(doctor_id, "URGENT: Patient with chest pain needs immediate review")
```

## Components of an Agent

| Component | Purpose | Example |
|---|---|---|
| System prompt | Defines role, boundaries, behavior | "You are a medical triage assistant..." |
| Tools | Actions the agent can take | search_rag, create_note, send_alert |
| Memory | Conversation history, context | Previous questions, patient history |
| Orchestrator | Decides which tool to call and when | LLM generates tool calls |
| Guardrails | Safety constraints | "Never diagnose, only summarize" |

## Tool Definition

Tools are functions the LLM can call. They're registered with a name, description, and parameters:

```
Tool: search_rag
Description: Search medical knowledge base for relevant information
Parameters:
  - query: str (the search query)
  - top_k: int (number of results, default 5)

Tool: create_note
Description: Create a clinical note for a patient
Parameters:
  - patient_id: str
  - content: str
  - urgency: "low" | "medium" | "high"

Tool: send_alert
Description: Send an urgent notification to a doctor
Parameters:
  - doctor_id: str
  - message: str
  - priority: int (1-5)
```

## Safety & Guardrails

In healthcare, agent autonomy must be constrained:

| Guardrail | Implementation |
|---|---|
| No diagnosis | System prompt: "Only summarize, never diagnose" |
| Human-in-loop | Critical actions require doctor approval |
| Audit trail | Every agent action is logged |
| Rate limits | Max 5 tool calls per query |
| Escalation | If confidence < 0.8, escalate to human |

## Agent vs Simple API

```
Simple API: "Tell me about ACE inhibitors"
    → Search RAG → Return result
    → Done

Agent: "I'm confused about ACE inhibitors"
    → Search RAG → Check what student knows → Create study plan
    → Schedule quiz → Send reminder → Return personalized response
    → Done (with multiple system actions taken)
```

The agent **orchestrates** multiple actions toward a goal. This is the difference between a chatbot and an AI assistant.
