# Quiz — Build 10: AI Clinical Operations Platform

### Q1
What is the primary difference between monitoring and observability?

- A) They are the same thing
- B) Monitoring tells you something is wrong; observability lets you figure out why
- C) Observability is for developers; monitoring is for operations
- D) Monitoring is automated; observability is manual

**Answer:** B

### Q2
**True or False:** In an event-driven architecture, if the AI Service is down, the Upload Service cannot accept new uploads.

**Answer:** False — event-driven architecture decouples services. The Upload Service emits events regardless of whether downstream services are available.

### Q3
What makes an AI agent different from a simple LLM API call?

- A) It's faster
- B) It has tools, memory, and autonomy to take actions in the system
- C) It only works with medical data
- D) It doesn't need a prompt

**Answer:** B

### Q4
A request takes 5 seconds. The p95 response time should be under 1 second. How do you find the bottleneck?

- A) Read the error logs
- B) Check distributed traces (how much time did each service take?)
- C) Restart the server
- D) Increase timeout

**Answer:** B

### Q5
**Scenario:** An AI agent incorrectly assesses a patient's symptoms. What protection should exist?

- A) Don't use AI
- B) Human-in-the-loop — critical actions require doctor approval
- C) Use a bigger model
- D) Retry the request

**Answer:** B

### Q6
What is the correct order for rolling out a new AI feature?

- A) All users at once → shadow mode → rollback
- B) Shadow mode → A/B test → full rollout with kill switch
- C) A/B test → shadow mode → all users
- D) Full rollout → monitor → rollback

**Answer:** B

### Q7
**True or False:** In a modular monolith, all code is in one deployable unit but organized into clear internal modules.

**Answer:** True

### Q8
Why cache AI responses?

- A) To reduce storage costs
- B) Many questions repeat — caching saves money and reduces latency
- C) To improve AI quality
- D) To bypass rate limits

**Answer:** B

### Q9
What should you log for every AI action?

- A) The full patient medical record
- B) The input, output, model used, latency, cost, and whether human review is needed
- C) Nothing — AI actions don't need logging
- D) Only errors

**Answer:** B

### Q10
Build 10 is described as "not a new technology, but a new level of system thinking." What does this mean?

- A) Build 10 doesn't use any code
- B) Build 10 is the integration of all previous builds into a complete clinical workflow
- C) Build 10 uses a completely different programming language
- D) Build 10 is about documentation only

**Answer:** B
