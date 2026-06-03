from typing import Generator

from src.core.event_bus import EventBus
from src.core.memory import Memory
from src.core.planner import Planner
from src.core.router import RouterAgent
from src.governance.cost_manager import BudgetManager, CostTracker
from src.governance.guardrails import Guardrails
from src.governance.latency import LatencyTracker
from src.intelligence.rag import RAG
from src.intelligence.tools import ToolRegistry
from src.llm.gateway import LLMGateway


class Orchestrator:
    """
    🧠 NexusMind Orchestrator v11 (FINAL)

    Integrated:
    - EventBus (streaming backbone)
    - Guardrails (input safety)
    - Latency (TTFT + total)
    - BudgetManager (pre-check)
    - CostTracker (post usage)
    """

    def __init__(self):
        self.planner = Planner()
        self.router = RouterAgent()
        self.memory = Memory()

        self.rag = RAG()
        self.tools = ToolRegistry()
        self.llm = LLMGateway()

        self.guardrails = Guardrails()

        # ✅ Governance
        self.budget = BudgetManager()
        self.cost = CostTracker()

    # =========================================================
    def _load_memory(self, session_id: str, limit: int = 20):
        return self.memory.format_history(session_id, limit=limit)

    # =========================================================
    def _build_context(self, memory="", rag_docs=None, tool_output=None) -> str:
        parts = []

        if tool_output:
            parts.append("### TOOL OUTPUT\n" + str(tool_output))

        if rag_docs:
            rag_text = "\n\n".join([d.get("text", "") for d in rag_docs])
            parts.append("### KNOWLEDGE\n" + rag_text)

        if memory:
            parts.append("### MEMORY\n" + memory)

        return "\n\n".join(parts).strip()

    # =========================================================
    # STREAMING PIPELINE (PRIMARY)
    # =========================================================
    def run_stream(self, query: str, session_id: str) -> Generator[str, None, None]:

        bus = EventBus()
        latency = LatencyTracker()

        query = (query or "").strip()
        latency.start()

        # =====================================================
        # 1. GUARDRAILS
        # =====================================================
        guard = self.guardrails.validate_query(query)
        if not guard["safe"]:
            bus.emit(session_id, "EVENT", "guardrails", guard["reason"])
            yield from bus.stream(session_id)
            return

        bus.emit(session_id, "EVENT", "guardrails", "passed")

        # =====================================================
        # 2. MEMORY (SAVE USER)
        # =====================================================
        self.memory.add_message(session_id, "user", query)
        history = self._load_memory(session_id)

        bus.emit(session_id, "EVENT", "memory", "loaded")

        # =====================================================
        # 3. PLANNER
        # =====================================================
        plan = self.planner.create_plan(query)
        bus.emit(session_id, "EVENT", "planner", plan["tasks"])

        # =====================================================
        # 4. ROUTER
        # =====================================================
        route = self.router.route(query)
        action = route["action"]
        optimized_query = route.get("optimized_query", query)

        bus.emit(session_id, "EVENT", "router", action)

        # =====================================================
        # 5. RAG
        # =====================================================
        rag_docs = []

        if action in ["RAG_SEARCH", "HYBRID"]:
            bus.emit(session_id, "EVENT", "rag", "started")

            rag_result = self.rag.retrieve(optimized_query)
            rag_docs = rag_result.get("documents", [])

            bus.emit(session_id, "EVENT", "rag", f"{len(rag_docs)} docs")

        # =====================================================
        # 6. TOOL
        # =====================================================
        tool_output = None

        if action in ["EXECUTE_TOOL", "HYBRID"]:
            bus.emit(session_id, "EVENT", "tool", "started")

            tool_name = route.get("tool") or "calculator"
            tool_output = self.tools.execute(tool_name, query)

            bus.emit(session_id, "EVENT", "tool", tool_name)

        # =====================================================
        # 7. CONTEXT
        # =====================================================
        context = self._build_context(history, rag_docs, tool_output)
        bus.emit(session_id, "EVENT", "context", "built")

        # =====================================================
        # 8. BUDGET CHECK (CRITICAL)
        # =====================================================
        budget_check = self.budget.can_proceed(context + query, estimated_cost=0.001)

        if not budget_check["allowed"]:
            bus.emit(session_id, "EVENT", "budget", budget_check["reason"])
            bus.emit(session_id, "FINAL", "response", "⚠️ Budget exceeded.")
            yield from bus.stream(session_id)
            return

        bus.emit(session_id, "EVENT", "budget", "approved")

        # =====================================================
        # 9. LLM STREAM
        # =====================================================
        bus.emit(session_id, "EVENT", "llm", "started")

        full_response = ""

        for token in self.llm.stream(
            query=query,
            context=context,
            route=route,
            plan=plan,
        ):
            if not full_response:
                latency.mark_first_token()

            full_response += token
            bus.emit(session_id, "TOKEN", "llm", token)

        # =====================================================
        # 10. COST TRACKING
        # =====================================================
        usage = self.cost.add_usage("ollama", full_response)
        self.budget.update_usage(full_response, usage["cost"])

        # =====================================================
        # 11. FINAL EVENTS
        # =====================================================
        bus.emit(session_id, "EVENT", "llm", "completed")

        bus.emit(
            session_id,
            "FINAL",
            "response",
            full_response,
            meta={
                "latency_ms": latency.total_latency_ms(),
                "ttft_ms": latency.ttft_ms(),
                "tokens": usage["tokens"],
                "cost": usage["cost"],
            },
        )

        # =====================================================
        # 12. MEMORY SAVE (ASSISTANT)
        # =====================================================
        self.memory.add_message(session_id, "assistant", full_response)

        # =====================================================
        # STREAM OUTPUT
        # =====================================================
        yield from bus.stream(session_id)
