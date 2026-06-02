import time
from typing import Any, Dict

from src.core.memory import Memory
from src.core.planner import Planner
from src.core.router import RouterAgent
from src.governance.budget import BudgetManager

# =========================
# GOVERNANCE LAYER
# =========================
from src.governance.guardrails import Guardrails
from src.governance.latency import LatencyTracker
from src.governance.tracer import RequestTracer

# =========================
# INTELLIGENCE LAYER
# =========================
from src.intelligence.rag import RAG
from src.llm.gateway import LLMGateway
from src.tools.registry import ToolRegistry


class Orchestrator:
    """
    🧠 NexusMind Execution Engine v5 (GOVERNANCE ACTIVATED)

    FLOW:
    User → Guardrails → Budget → Planner → Router → RAG/Tools
         → Memory Context → LLM → Governance Logging → Response
    """

    def __init__(self):
        print("[Orchestrator] Initializing NexusMind Core v5 (GOVERNED)")

        # =========================
        # CORE
        # =========================
        self.planner = Planner()
        self.router = RouterAgent()
        self.memory = Memory()

        # =========================
        # INTELLIGENCE
        # =========================
        self.rag = RAG()
        self.tools = ToolRegistry()
        self.llm = LLMGateway()

        # =========================
        # GOVERNANCE
        # =========================
        self.guardrails = Guardrails()
        self.budget = BudgetManager()
        self.tracer = RequestTracer()
        self.latency = LatencyTracker()

        print("[Orchestrator] Ready.")

    # =========================================================
    # MEMORY
    # =========================================================
    def _load_memory(self, session_id: str, limit: int = 20):
        return self.memory.format_history(session_id, limit=limit)

    # =========================================================
    # MAIN FLOW
    # =========================================================
    def run(self, query: str, session_id: str) -> Dict[str, Any]:

        start_time = time.time()
        self.latency.start()

        trace = {
            "query": query,
            "session_id": session_id,
            "planner": None,
            "route": None,
            "rag": None,
            "tool": None,
            "web": None,
            "context": None,
            "response": None,
            "latency_ms": None,
            "governance": {},
        }

        # =========================================================
        # 1. GUARDRAILS (INPUT SAFETY)
        # =========================================================
        guard = self.guardrails.validate_query(query)
        if not guard["safe"]:
            return {
                "error": "Blocked by guardrails",
                "reason": guard["reason"],
            }

        # =========================================================
        # 2. MEMORY STORE (USER)
        # =========================================================
        self.memory.add_message(session_id, "user", query)

        # =========================================================
        # 3. MEMORY LOAD
        # =========================================================
        chat_history = self._load_memory(session_id)

        # =========================================================
        # 4. PLANNER
        # =========================================================
        plan = self.planner.create_plan(query=query, memory=chat_history)
        trace["planner"] = plan

        # =========================================================
        # 5. ROUTER
        # =========================================================
        route = self.router.route(query)
        trace["route"] = route

        action = route["action"]
        optimized_query = route.get("optimized_query", query)

        # =========================================================
        # 6. INTELLIGENCE LAYER
        # =========================================================
        rag_context = ""
        tool_context = ""
        web_context = ""

        # -------------------------
        # RAG
        # -------------------------
        if action in ["RAG_SEARCH", "HYBRID"]:
            rag_result = self.rag.retrieve(
                query=optimized_query,
                top_k=5,
            )

            rag_context = (
                rag_result.get("context", "")
                if isinstance(rag_result, dict)
                else str(rag_result)
            )

            trace["rag"] = rag_context

        # -------------------------
        # TOOLS
        # -------------------------
        if action in ["EXECUTE_TOOL", "HYBRID"]:
            tool_name = route.get("tool") or self.tools.detect(query)

            try:
                tool_output = self.tools.execute(tool_name, query)
                tool_context = str(tool_output)
            except Exception as e:
                tool_context = f"[Tool Error] {str(e)}"

            trace["tool"] = tool_context

        # -------------------------
        # WEB (RESERVED)
        # -------------------------
        if action in ["WEB_SEARCH", "HYBRID"]:
            web_context = "[WEB LAYER RESERVED - NOT IMPLEMENTED]"
            trace["web"] = web_context

        # =========================================================
        # 7. CONTEXT FUSION
        # =========================================================
        final_context = self._build_context(
            memory=chat_history or "",
            rag=rag_context or "",
            tool=tool_context or "",
            web=web_context or "",
        )

        trace["context"] = final_context

        # =========================================================
        # 8. BUDGET CHECK (BEFORE LLM)
        # =========================================================
        budget_check = self.budget.can_proceed(
            text=final_context,
            estimated_cost=0.001,
        )

        if not budget_check["allowed"]:
            return {
                "error": "Blocked by budget manager",
                "reason": budget_check["reason"],
            }

        # =========================================================
        # 9. LLM GENERATION
        # =========================================================
        response = self.llm.generate(
            query=query,
            context=final_context,
            route=route,
            plan=plan,
        )

        trace["response"] = response

        # =========================================================
        # 10. MEMORY STORE (ASSISTANT)
        # =========================================================
        self.memory.add_message(session_id, "assistant", response)

        # =========================================================
        # 11. LATENCY TRACKING
        # =========================================================
        trace["latency_ms"] = round((time.time() - start_time) * 1000, 2)
        self.latency.mark_first_token()

        # =========================================================
        # 12. GOVERNANCE LOGGING
        # =========================================================
        trace["governance"] = {
            "guardrails": guard,
            "budget": self.budget.summary(),
            "latency": self.latency.total_latency_ms(),
        }

        return trace

    # =========================================================
    # STREAMING
    # =========================================================
    def run_stream(self, query: str, session_id: str):

        trace = self.run(query, session_id)

        def generator():
            try:
                for token in self.llm.stream(
                    query=query,
                    context=trace["context"] or "",
                    route=trace["route"],
                    plan=trace["planner"],
                ):
                    self.latency.mark_first_token()
                    yield token
            except Exception as e:
                yield f"[Stream Error] {str(e)}"

        return generator(), trace

    # =========================================================
    # CONTEXT BUILDER
    # =========================================================
    def _build_context(self, memory="", rag="", tool="", web="") -> str:

        sections = []

        if tool:
            sections.append("### TOOL OUTPUT\n" + tool)

        if rag:
            sections.append("### KNOWLEDGE\n" + rag)

        if web:
            sections.append("### WEB\n" + web)

        if memory:
            sections.append("### MEMORY\n" + memory)

        return "\n\n".join(sections).strip()
