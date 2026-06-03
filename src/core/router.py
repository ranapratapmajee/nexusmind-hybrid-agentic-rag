from typing import Any, Dict, Literal, Optional

# =========================================================
# 🧠 ROUTE TYPES
# =========================================================
RouteType = Literal[
    "DIRECT_ANSWER",
    "RAG_SEARCH",
    "EXECUTE_TOOL",
    "WEB_SEARCH",
    "HYBRID",
]

ToolType = Literal["calculator", "web_search", "none"]


# =========================================================
# 🧠 ROUTER ENGINE
# =========================================================
class RouterAgent:
    """
    NexusMind Routing Brain (EventBus Compatible)

    RULES:
    - No LLM calls
    - No side effects
    - No verbose reasoning output
    - ONLY structured decision
    """

    def __init__(self):
        print("[Router] Initialized (EventBus-safe mode)")

    # =========================================================
    # HEURISTIC ENGINE
    # =========================================================
    def _heuristic(self, query: str) -> Optional[Dict[str, Any]]:
        q = query.lower().strip()

        # -------------------------
        # TOOL: CALCULATOR
        # -------------------------
        if any(k in q for k in ["calculate", "solve", "+", "-", "*", "/", "math"]):
            return {
                "action": "EXECUTE_TOOL",
                "tool": "calculator",
                "optimized_query": query,
                "confidence": 0.95,
            }

        # -------------------------
        # WEB / REAL-TIME
        # -------------------------
        if any(
            k in q
            for k in ["latest", "news", "today", "current", "weather", "price", "stock"]
        ):
            return {
                "action": "WEB_SEARCH",
                "tool": "web_search",
                "optimized_query": query,
                "confidence": 0.90,
            }

        # -------------------------
        # RAG / KNOWLEDGE
        # -------------------------
        if any(
            k in q
            for k in [
                "what is",
                "explain",
                "how does",
                "architecture",
                "rag",
                "vector",
                "embedding",
                "difference",
            ]
        ):
            return {
                "action": "RAG_SEARCH",
                "tool": None,
                "optimized_query": query,
                "confidence": 0.85,
            }

        # -------------------------
        # DIRECT CHAT
        # -------------------------
        if any(
            k in q
            for k in ["hi", "hello", "hey", "thanks", "good morning", "good evening"]
        ):
            return {
                "action": "DIRECT_ANSWER",
                "tool": None,
                "optimized_query": query,
                "confidence": 0.9,
            }

        return None

    # =========================================================
    # MAIN ROUTE FUNCTION
    # =========================================================
    def route(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        planner_hint: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        context = context or {}

        # =====================================================
        # 1. FAST HEURISTIC PATH
        # =====================================================
        result = self._heuristic(query)
        if result:
            return result

        # =====================================================
        # 2. PLANNER-AWARE MODE (FUTURE READY)
        # =====================================================
        if planner_hint:
            tasks = planner_hint.get("tasks", [])

            if "RAG_SEARCH" in tasks and "USE_TOOLS" in tasks:
                return {
                    "action": "HYBRID",
                    "tool": "calculator",
                    "optimized_query": query,
                    "confidence": 0.75,
                }

            if "RAG_SEARCH" in tasks:
                return {
                    "action": "RAG_SEARCH",
                    "tool": None,
                    "optimized_query": query,
                    "confidence": 0.7,
                }

        # =====================================================
        # 3. SAFE DEFAULT (NEVER FAIL SYSTEM)
        # =====================================================
        return {
            "action": "RAG_SEARCH",
            "tool": None,
            "optimized_query": query,
            "confidence": 0.55,
        }
