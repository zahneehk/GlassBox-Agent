# Security Policy

## Container Isolation
- Each run gets a dedicated Docker container
- No shared state between containers (Cookie, Session, Storage, Profile)
- CPU/Memory limits enforced per container
- Containers are destroyed after run completion (GC)

## Human-in-the-Loop (HITL)
- Steps with `risk == "high"` trigger automatic pause
- Orchestrator sends WebSocket notification to UI
- Execution resumes ONLY after explicit human approval
- Timeout: unapproved steps auto-cancel after configurable duration

## Risk Classification (v1 — Static)
- `goto`: low risk (unless navigating to sensitive domains)
- `click`: medium risk (depends on target element context)
- `type`: high risk when input fields are password/payment related

## Network Isolation
- Runner containers have restricted network access by default
- Only Orchestrator can communicate with Runner (internal Docker network)
- noVNC stream exposed only through Nginx proxy

## Secrets
- No credentials stored in containers
- Credentials injected at runtime via Orchestrator environment variables
- Orchestrator secrets managed via environment / vault
