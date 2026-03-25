# GlassBox-Agent Architecture

## Overview

GlassBox-Agent is a three-layer system: Agent → Orchestrator → Execution.

## Layers

### Agent Layer (OpenClaw)
- Reasoning and planning
- Outputs structured JSON Plans
- Does NOT touch the browser directly

### Orchestrator Layer (FastAPI)
- Task lifecycle management (create → dispatch → execute → complete)
- Container provisioning via Docker SDK
- State machine for each run/step
- HITL (Human-in-the-loop) pause/resume
- WebSocket event broadcasting

### Execution Layer (Docker Containers)
- Each run gets an isolated container
- Playwright browser automation
- Xvfb + x11vnc + noVNC for real-time visualization
- Node.js runner receives action commands via HTTP

## Data Flow

```
User submits task via Web UI
  → POST /api/runs (Orchestrator)
  → Orchestrator creates Run + Steps in PostgreSQL
  → Orchestrator provisions Docker container
  → Container starts: Xvfb → x11vnc → noVNC → Playwright → Runner HTTP server
  → Orchestrator dispatches steps to Runner: goto / click / type
  → Runner executes via Playwright, reports status back
  → noVNC streams browser screen to Web UI in real-time
  → High-risk steps trigger HITL pause → WebSocket notification → User approves → Resume
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Orchestrator | Python, FastAPI, SQLAlchemy, asyncpg |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Runner | Node.js, TypeScript, Playwright |
| Visualization | Xvfb, x11vnc, noVNC |
| Frontend | React, Vite, TypeScript |
| Containers | Docker, docker-compose |
| Gateway | Nginx |
