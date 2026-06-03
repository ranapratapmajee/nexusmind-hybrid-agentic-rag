import time
import uuid
from collections import defaultdict
from typing import Any, Callable, Dict, Generator, List


class EventBus:
    """
    🌐 Universal Event Streaming Bus (UESB) — NexusMind Core

    DESIGN GOALS:
    - Single source of truth for ALL events
    - Supports streaming + replay
    - Supports future multi-agent subscriptions
    - Lightweight (no external infra)
    """

    def __init__(self):
        # session_id → event list buffer
        self._streams: Dict[str, List[Dict]] = defaultdict(list)

        # optional subscribers (future agents / UI / logger)
        self._subscribers: List[Callable[[Dict], None]] = []

    # =========================================================
    # CORE EVENT CREATION
    # =========================================================
    def emit(
        self,
        session_id: str,
        event_type: str,
        source: str,
        content: Any,
        meta: Dict = None,
    ) -> Dict:
        """
        Create + store event in stream buffer
        """

        event = {
            "event_id": str(uuid.uuid4()),
            "type": event_type,  # EVENT | TOKEN | FINAL
            "source": source,  # router | rag | llm | tool
            "content": content,
            "meta": meta or {},
            "timestamp": time.time(),
            "session_id": session_id,
        }

        # store in session buffer
        self._streams[session_id].append(event)

        # push to subscribers (future agents / logger)
        for sub in self._subscribers:
            try:
                sub(event)
            except Exception:
                pass

        return event

    # =========================================================
    # STREAM CONSUMPTION (UI USES THIS)
    # =========================================================
    def stream(self, session_id: str) -> Generator[str, None, None]:
        """
        Returns ALL buffered + future events for a session.
        Stops automatically after FINAL event.
        """

        sent = 0

        while True:
            events = self._streams.get(session_id, [])

            # send new events only
            while sent < len(events):
                event = events[sent]
                sent += 1

                yield self._format(event)

                # ✅ CRITICAL FIX: STOP AFTER FINAL
                if event["type"] == "FINAL":
                    return

            time.sleep(0.01)  # prevents CPU spin

    # =========================================================
    # FORMAT FOR FRONTEND (STRICT CONTRACT)
    # =========================================================
    def _format(self, event: Dict) -> str:
        """
        Converts event → stream string
        """
        return f"{event['type']}|{event['source']}|{event['content']}\n"

    # =========================================================
    # SUBSCRIPTION SYSTEM (FOR FUTURE AGENTS)
    # =========================================================
    def subscribe(self, callback: Callable[[Dict], None]):
        """
        Agents / loggers can subscribe to all events
        """
        self._subscribers.append(callback)

    # =========================================================
    # UTILITY
    # =========================================================
    def clear(self, session_id: str):
        """
        Reset session stream (important for new chats)
        """
        if session_id in self._streams:
            del self._streams[session_id]


# =========================================================
# ✅ SINGLETON INSTANCE (VERY IMPORTANT)
# =========================================================
event_bus = EventBus()
