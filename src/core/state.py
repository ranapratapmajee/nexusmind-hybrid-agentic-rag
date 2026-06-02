import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class NexaState:
    query: str
    context: List[str] = field(default_factory=list)

    route: Optional[str] = None
    response: Optional[str] = None

    tool_used: Optional[str] = None
    rag_used: bool = False

    retrieved_docs: Optional[list] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    start_time: float = field(default_factory=time.time)
    latency: Optional[float] = None

    def finalize(self):
        self.latency = time.time() - self.start_time
        return self
