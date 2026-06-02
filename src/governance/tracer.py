import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class TraceEvent:
    name: str
    start: float = field(default_factory=time.time)
    end: Optional[float] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def stop(self):
        self.end = time.time()

    def duration_ms(self):
        if not self.end:
            return None
        return round((self.end - self.start) * 1000, 2)


class RequestTracer:
    """
    Tracks full lifecycle of a request:
    planner → router → rag → tools → llm
    """

    def __init__(self):
        self.events: Dict[str, TraceEvent] = {}

    def start(self, name: str, meta: dict = None):
        self.events[name] = TraceEvent(name=name, meta=meta or {})
        return self.events[name]

    def end(self, name: str):
        if name in self.events:
            self.events[name].stop()

    def summary(self):
        return {
            k: {
                "duration_ms": v.duration_ms(),
                "meta": v.meta,
            }
            for k, v in self.events.items()
        }
