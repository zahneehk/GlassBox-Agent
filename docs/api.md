# GlassBox-Agent API Reference

## Orchestrator API (FastAPI, port 8000)

### Health
- `GET /health` → `{ "status": "ok" }`

### Runs (Task Lifecycle)
- `POST /api/runs` — Create a new run
- `GET /api/runs` — List runs
- `GET /api/runs/{run_id}` — Get run detail + steps
- `POST /api/runs/{run_id}/approve` — Approve a paused HITL step
- `POST /api/runs/{run_id}/cancel` — Cancel a run

### Containers
- `GET /api/containers` — List active containers
- `GET /api/containers/{container_id}/vnc` — Get noVNC URL

### WebSocket
- `WS /ws/runs/{run_id}` — Real-time run events (step_started, step_completed, hitl_pause, etc.)

---

## Runner API (Node.js, port 3001, container-internal)

### Actions
- `POST /actions/execute` — Execute a single action
  ```json
  {
    "action": "goto",
    "params": { "url": "https://example.com" }
  }
  ```
- `GET /status` — Runner health + current page info
- `GET /screenshot` — Current page screenshot (PNG)
