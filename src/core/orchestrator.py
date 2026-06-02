import time
from typing import Any, Dict

from src.core.planner import Planner
from src.core.router import RouterAgent
from src.llm.gateway import LLMGateway
from src.memory.sqlite_memory import SQLiteMemory
from src.rag.ranking import ResultRanker
from src.rag.retriever import Retriever
from src.tools.registry import ToolRegistry


class Orchestrator:
    """
    🧠 NexusMind Execution Engine v4 (FINAL)

    FLOW:
    User → Planner → Router → Intelligence Layer → Context Builder → Gateway → Response
    """

    def __init__(self):
        print("[Orchestrator] Initializing NexusMind Core v4 (Execution Engine)")

        # =========================
        # CORE BRAIN LAYERS
        # =========================
        self.planner = Planner()
        self.router = RouterAgent()

        # =========================
        # MEMORY SYSTEM
        # =========================
        self.memory = SQLiteMemory()

        # =========================
        # INTELLIGENCE LAYER
        # =========================
        self.retriever = Retriever()
        self.ranker = ResultRanker(mode="simple")
        self.tools = ToolRegistry()

        # =========================
        # LLM GATEWAY (ONLY ENTRY POINT)
        # =========================
        self.llm = LLMGateway()

        print("[Orchestrator] Ready.")

    # =========================================================
    # MEMORY
    # =========================================================
    def _load_memory(self, session_id: str, limit: int = 20):
        chat_history = self.memory.format_for_llm(session_id, limit=limit)
        raw_messages = self.memory.get_messages(session_id, limit=limit)
        return chat_history, raw_messages

    # =========================================================
    # MAIN EXECUTION FLOW (FULL TRACE MODE)
    # =========================================================
    def run(self, query: str, session_id: str) -> Dict[str, Any]:

        start_time = time.time()

        print(f"\n[Session {session_id}] Query: {query}")

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
        }

        # =====================================================
        # 1. STORE USER INPUT
        # =====================================================
        self.memory.add_message(session_id, "user", query)

        # =====================================================
        # 2. LOAD MEMORY
        # =====================================================
        chat_history, raw_messages = self._load_memory(session_id)

        # =====================================================
        # 3. PLANNER
        # =====================================================
        plan = self.planner.create_plan(query=query, memory=chat_history)
        trace["planner"] = plan

        # =====================================================
        # 4. ROUTER
        # =====================================================
        route = self.router.route(query)
        trace["route"] = route

        action = route["action"]
        optimized_query = route.get("optimized_query", query)

        rag_context = ""
        tool_context = ""
        web_context = ""

        # =====================================================
        # 5. INTELLIGENCE LAYER
        # =====================================================

        # -------------------------
        # RAG PIPELINE
        # -------------------------
        if action in ["RAG_SEARCH", "HYBRID"]:
            docs = self.retriever.retrieve(
                query=optimized_query,
                top_k=5,
            )

            ranked = self.ranker.rank(docs, query=query)
            texts = [d.get("text", "") for d in ranked if d.get("text")]

            rag_context = "\n\n".join(texts[-6:])
            trace["rag"] = rag_context

        # -------------------------
        # TOOL PIPELINE
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
        # WEB PIPELINE (FUTURE READY)
        # -------------------------
        if action in ["WEB_SEARCH", "HYBRID"]:
            web_context = "[Web Search Not Implemented]"
            trace["web"] = web_context

        # =====================================================
        # 6. CONTEXT FUSION (DIRECT, NO EXTRA CLASS DEPENDENCY)
        # =====================================================
        final_context = self._build_context(
            memory=chat_history,
            rag=rag_context,
            tool=tool_context,
            web=web_context,
        )

        trace["context"] = final_context

        # =====================================================
        # 7. LLM GATEWAY (SINGLE ENTRY POINT)
        # =====================================================
        response = self.llm.generate(
            query=query,
            context=final_context,
            route=route,
            plan=plan,
        )

        trace["response"] = response

        # =====================================================
        # 8. STORE RESPONSE
        # =====================================================
        self.memory.add_message(session_id, "assistant", response)

        # =====================================================
        # 9. LATENCY TRACKING
        # =====================================================
        trace["latency_ms"] = round((time.time() - start_time) * 1000, 2)

        return trace

    # =========================================================
    # STREAMING MODE (GATEWAY POWERED)
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
                    yield token
            except Exception as e:
                yield f"[Stream Error] {str(e)}"

        return generator(), trace

    # =========================================================
    # INTERNAL CONTEXT BUILDER (NO EXTERNAL DEPENDENCY)
    # =========================================================
    def _build_context(self, memory="", rag="", tool="", web="") -> str:

        sections = []

        if memory:
            sections.append("### MEMORY\n" + memory)

        if rag:
            sections.append("### KNOWLEDGE\n" + rag)

        if tool:
            sections.append("### TOOL OUTPUT\n" + tool)

        if web:
            sections.append("### WEB\n" + web)

        return "\n\n".join(sections).strip()
