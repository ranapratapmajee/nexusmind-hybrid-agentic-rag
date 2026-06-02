from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

# =========================================================
# 🧠 ROUTE TYPES (FINAL ARCHITECTURE ALIGNED)
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
# 🧠 ROUTER OUTPUT CONTRACT
# =========================================================
class RouterDecision(BaseModel):
    action: RouteType = Field(..., description="Execution route")
    tool: Optional[ToolType] = Field(default=None)
    optimized_query: str = Field(..., description="Clean query for downstream systems")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(...)


# =========================================================
# 🧠 MULTI-MODEL ROUTER AGENT (CORE BRAIN)
# =========================================================
class RouterAgent:
    """
    Model-agnostic routing engine.

    RULES:
    - No LLM calls here
    - No tool execution
    - ONLY decision making
    """

    def __init__(self):
        print("[Router] Initialized (Final Multi-Route Engine)")

    # =========================================================
    # FAST HEURISTIC ENGINE (PRIMARY SIGNALS)
    # =========================================================
    def _heuristic(self, query: str) -> Optional[RouterDecision]:
        q = query.lower().strip()

        # -------------------------
        # TOOL ROUTING (MATH / LOGIC)
        # -------------------------
        if any(k in q for k in ["calculate", "solve", "+", "-", "*", "/", "math"]):
            return RouterDecision(
                action="EXECUTE_TOOL",
                tool="calculator",
                optimized_query=query,
                confidence=0.95,
                reasoning="Mathematical operation detected",
            )

        # -------------------------
        # WEB / REAL-TIME SIGNALS
        # -------------------------
        if any(
            k in q
            for k in [
                "latest",
                "news",
                "today",
                "current",
                "weather",
                "price",
                "stock",
            ]
        ):
            return RouterDecision(
                action="WEB_SEARCH",
                tool="web_search",
                optimized_query=query,
                confidence=0.90,
                reasoning="Real-time / external information required",
            )

        # -------------------------
        # RAG / KNOWLEDGE SIGNALS
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
            return RouterDecision(
                action="RAG_SEARCH",
                tool=None,
                optimized_query=query,
                confidence=0.85,
                reasoning="Knowledge-intensive query detected",
            )

        # -------------------------
        # DIRECT CHAT SIGNALS
        # -------------------------
        if any(
            k in q
            for k in ["hi", "hello", "hey", "thanks", "good morning", "good evening"]
        ):
            return RouterDecision(
                action="DIRECT_ANSWER",
                tool=None,
                optimized_query=query,
                confidence=0.9,
                reasoning="Simple conversational query",
            )

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
        # 1. FAST PATH (NO MODEL CALL)
        # =====================================================
        heuristic = self._heuristic(query)
        if heuristic:
            return heuristic.model_dump()

        # =====================================================
        # 2. PLANNER-AWARE ENHANCEMENT (FUTURE READY)
        # =====================================================
        if planner_hint:
            tasks = planner_hint.get("tasks", [])

            if "RAG_SEARCH" in tasks and "USE_TOOLS" in tasks:
                return RouterDecision(
                    action="HYBRID",
                    tool="calculator",
                    optimized_query=query,
                    confidence=0.75,
                    reasoning="Planner indicates multi-step reasoning (RAG + Tools)",
                ).model_dump()

            if "RAG_SEARCH" in tasks:
                return RouterDecision(
                    action="RAG_SEARCH",
                    tool=None,
                    optimized_query=query,
                    confidence=0.7,
                    reasoning="Planner suggests knowledge retrieval",
                ).model_dump()

        # =====================================================
        # 3. SAFE DEFAULT (NEVER BLOCK SYSTEM)
        # =====================================================
        return RouterDecision(
            action="RAG_SEARCH",
            tool=None,
            optimized_query=query,
            confidence=0.55,
            reasoning="Fallback routing (safe default → RAG)",
        ).model_dump()
