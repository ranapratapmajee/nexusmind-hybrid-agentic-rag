import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


# =========================================================
# TRACE EVENT
# =========================================================
@dataclass
class TraceEvent:
    name: str
    start: float = field(default_factory=time.time)
    end: Optional[float] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def stop(self):
        self.end = time.time()

    def duration_ms(self):
        if self.end is None:
            return None
        return round((self.end - self.start) * 1000, 2)


# =========================================================
# REQUEST TRACER (EVENTBUS SAFE)
# =========================================================
class RequestTracer:
    """
    Tracks lifecycle of a request:
    planner → router → rag → tools → llm

    RULES:
    - No prints
    - No streaming
    - No side effects
    - Only returns structured data
    """

    def __init__(self):
        self.events: Dict[str, TraceEvent] = {}

    # -------------------------
    # START EVENT
    # -------------------------
    def start(self, name: str, meta: Dict[str, Any] = None):
        self.events[name] = TraceEvent(name=name, meta=meta or {})

    # -------------------------
    # END EVENT
    # -------------------------
    def end(self, name: str):
        if name in self.events:
            self.events[name].stop()

    # -------------------------
    # EXPORT SUMMARY
    # -------------------------
    def summary(self) -> Dict[str, Any]:
        return {
            name: {
                "duration_ms": event.duration_ms(),
                "meta": event.meta,
            }
            for name, event in self.events.items()
        }
