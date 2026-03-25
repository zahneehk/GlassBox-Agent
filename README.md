# 📦 GlassBox-Agent

[English](#english-version) | [中文版](#chinese-version)

---

<a name="english-version"></a>
## 🇬🇧 English Version

**A transparent, agent-driven visual execution system.**

GlassBox-Agent is a "white-box" execution engine designed for the next generation of AI applications. 

Traditional LLM automation tools often operate as a black box where users can only wait for the final output. GlassBox-Agent aims to break this paradigm. It strictly decouples the "decision-making brain" (e.g., OpenClaw) from the "executing limbs" (Playwright), introducing a powerful Orchestrator layer in between. 

In this system, every Agent runs in a fully isolated Docker container. Through integrated `x11vnc` and `noVNC` technologies, users can watch real-time, live-stream-like execution of multiple Agents operating on actual web pages via a custom Web UI. This not only physicalizes LLM capabilities but also ensures the safety of high-risk tasks through system-level Human-in-the-loop (HITL) mechanisms.

### ✨ Value Proposition
1. **Capability Transformation**: Converts an LLM's text-generation ability into executable actions in the digital world.
2. **White-Box Observability**: Transforms black-box automation into a transparent system that is observable, interruptible, and replayable.
3. **Architectural Decoupling**: The upper-layer LLM handles uncertain reasoning, the lower-layer Playwright handles deterministic execution, and the Orchestrator manages isolation and scheduling.

### 🏗️ High-Level Architecture

```text
[ Custom Web UI ]  <-- (Renders noVNC stream & receives user input)
       │
[ Nginx / API Gateway ] <-- (HTTP Routing & WebSocket Dynamic Proxying)
       │
===================================================================
       │
[ OpenClaw (Agent Layer) ] <-- (Multi-Agent Collaboration / Planner / Executor / Reviewer)
       │    └─ Outputs structured JSON Plans
       ▼
[ Orchestrator (Scheduling) ] <-- (FastAPI + Redis + PostgreSQL)
       │    ├─ Task breakdown & dispatching
       │    ├─ State machine management & Policy interception
       │    └─ Container Lifecycle Management (GC)
       ▼
===================================================================
       │
[ Container Workspace ] <-- (Isolated Docker Container Cluster)
       │    ├─ Node.js Runner 
       │    ├─ Playwright (Browser Automation)
       │    └─ Xvfb + x11vnc + noVNC (Desktop Environment & Streaming)
       ▼
[ Target Web Environment ]
