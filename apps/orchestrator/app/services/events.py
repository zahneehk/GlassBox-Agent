"""GlassBox Orchestrator — WebSocket event bus for real-time run updates."""
import asyncio
import json
from collections import defaultdict
from fastapi import WebSocket


class EventBus:
    """Simple in-memory pub/sub for run events → WebSocket clients."""

    def __init__(self):
        self._subscribers: dict[str, list[WebSocket]] = defaultdict(list)

    def subscribe(self, run_id: str, ws: WebSocket):
        self._subscribers[run_id].append(ws)

    def unsubscribe(self, run_id: str, ws: WebSocket):
        if run_id in self._subscribers:
            self._subscribers[run_id] = [w for w in self._subscribers[run_id] if w is not ws]
            if not self._subscribers[run_id]:
                del self._subscribers[run_id]

    async def emit(self, run_id: str, event_type: str, data: dict):
        """Broadcast an event to all subscribers of a run."""
        message = json.dumps({"type": event_type, "run_id": run_id, "data": data})
        if run_id not in self._subscribers:
            return
        dead = []
        for ws in self._subscribers[run_id]:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.unsubscribe(run_id, ws)


event_bus = EventBus()
