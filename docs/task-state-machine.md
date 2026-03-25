# Task State Machine

## Run States

```
PENDING → PROVISIONING → RUNNING → COMPLETED
                           ↓          ↑
                        PAUSED ────────┘
                           ↓
                       CANCELLED
                       
                    (any) → FAILED
```

## Step States

```
PENDING → EXECUTING → COMPLETED
              ↓           ↑
          AWAITING_APPROVAL (HITL)
              ↓
          APPROVED → EXECUTING
              ↓
          REJECTED → SKIPPED
```

## Transitions

| From | To | Trigger |
|------|----|---------|
| PENDING | PROVISIONING | Container creation started |
| PROVISIONING | RUNNING | Container ready, first step dispatched |
| RUNNING | PAUSED | High-risk step encountered |
| PAUSED | RUNNING | Human approves step |
| PAUSED | CANCELLED | Human rejects / cancels |
| RUNNING | COMPLETED | All steps finished |
| * | FAILED | Unrecoverable error |
