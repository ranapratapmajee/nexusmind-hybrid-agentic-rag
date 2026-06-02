from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

# =========================================================
# 🧠 ROUTE TYPES (ALIGNED WITH FINAL SYSTEM ARCHITECTURE)
# =========================================================
RouteType = Literal[
    "DIRECT_ANSWER",  # simple LLM response
    "RAG_SEARCH",  # vector DB retrieval
    "EXECUTE_TOOL",  # calculator / functions
    "WEB_SEARCH",  # external / scraping
    "HYBRID",  # multi-step pipeline
]

ToolType = Literal["calculator", "web_search", "none"]


# =========================================================
# 🧠 ROUTER OUTPUT CONTRACT (MODEL-AGNOSTIC)
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

    IMPORTANT:
    - Does NOT depend on Ollama/Gemini/OpenAI
    - Only produces structured decisions
    - Execution is handled by LLM Gateway + Orchestrator
    """

    def __init__(self):
        print("[Router] Initialized (Multi-Model Mode)")

    # -----------------------------------------------------
    # FAST HEURISTIC ENGINE (COST-FREE ROUTING)
    # -----------------------------------------------------
    def _heuristic(self, query: str) -> Optional[RouterDecision]:
        q = query.lower().strip()

        # TOOL: mathematical operations
        if any(k in q for k in ["calculate", "solve", "+", "-", "*", "/", "math"]):
            return RouterDecision(
                action="EXECUTE_TOOL",
                tool="calculator",
                optimized_query=query,
                confidence=0.95,
                reasoning="Mathematical operation detected",
            )

        # WEB: real-world / temporal queries
        if any(
            k in q for k in ["latest", "news", "today", "price", "current", "weather"]
        ):
            return RouterDecision(
                action="WEB_SEARCH",
                tool="web_search",
                optimized_query=query,
                confidence=0.85,
                reasoning="Real-time information required",
            )

        # RAG: knowledge / docs / explanations
        if any(
            k in q
            for k in ["what is", "explain", "architecture", "how does", "rag", "vector"]
        ):
            return RouterDecision(
                action="RAG_SEARCH",
                tool=None,
                optimized_query=query,
                confidence=0.80,
                reasoning="Knowledge-intensive query detected",
            )

        return None

    # -----------------------------------------------------
    # MAIN ROUTE FUNCTION (MODEL-AGNOSTIC)
    # -----------------------------------------------------
    def route(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        context = context or {}

        # 1. FAST PATH (NO MODEL CALL)
        heuristic = self._heuristic(query)
        if heuristic:
            return heuristic.model_dump()

        # 2. DEFAULT FALLBACK STRATEGY (SAFE)
        # Router NEVER blocks system — always returns valid decision

        return RouterDecision(
            action="RAG_SEARCH",  # safest default for unknown queries
            tool=None,
            optimized_query=query,
            confidence=0.55,
            reasoning="Fallback routing (uncertain intent → RAG default)",
        ).model_dump()
