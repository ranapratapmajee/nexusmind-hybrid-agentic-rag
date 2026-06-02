import time
from typing import Any, Dict

from removed_files.tools.registry import ToolRegistry
from src.core.memory import SQLiteMemory
from src.core.planner import Planner
from src.core.router import RouterAgent
from src.intelligence.rag import RAG
from src.llm.gateway import LLMGateway


class Orchestrator:
    """
    🧠 NexusMind Execution Engine v4 (FINAL LOCKED)

    FLOW:
    User → Planner → Router → RAG/Tools → Memory Context → Gateway → Response
    """

    def __init__(self):
        print("[Orchestrator] Initializing NexusMind Core v4")

        self.planner = Planner()
        self.router = RouterAgent()
        self.memory = SQLiteMemory()

        self.rag = RAG()
        self.tools = ToolRegistry()
        self.llm = LLMGateway()

        print("[Orchestrator] Ready.")

    # =========================================================
    # MEMORY
    # =========================================================
    def _load_memory(self, session_id: str, limit: int = 20):
        return self.memory.format_for_llm(session_id, limit=limit)

    # =========================================================
    # MAIN FLOW
    # =========================================================
    def run(self, query: str, session_id: str) -> Dict[str, Any]:

        start_time = time.time()

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

        # 1. MEMORY STORE (USER)
        self.memory.add_message(session_id, "user", query)

        # 2. MEMORY LOAD
        chat_history = self._load_memory(session_id)

        # 3. PLANNER
        plan = self.planner.create_plan(query=query, memory=chat_history)
        trace["planner"] = plan

        # 4. ROUTER
        route = self.router.route(query)
        trace["route"] = route

        action = route["action"]
        optimized_query = route.get("optimized_query", query)

        rag_context = ""
        tool_context = ""
        web_context = ""

        # =========================================================
        # 5. INTELLIGENCE LAYER
        # =========================================================

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
        # 6. CONTEXT FUSION
        # =========================================================
        final_context = self._build_context(
            memory=chat_history or "",
            rag=rag_context or "",
            tool=tool_context or "",
            web=web_context or "",
        )

        trace["context"] = final_context

        # =========================================================
        # 7. LLM GENERATION
        # =========================================================
        response = self.llm.generate(
            query=query,
            context=final_context,
            route=route,
            plan=plan,
        )

        trace["response"] = response

        # 8. MEMORY STORE (ASSISTANT)
        self.memory.add_message(session_id, "assistant", response)

        # 9. LATENCY
        trace["latency_ms"] = round((time.time() - start_time) * 1000, 2)

        return trace

    # =========================================================
    # STREAMING
    # =========================================================
    def run_stream(self, query: str, session_id: str):

        trace = self.run(query, session_id)

        def generator():
            try:
                yield from self.llm.stream(
                    query=query,
                    context=trace["context"] or "",
                    route=trace["route"],
                    plan=trace["planner"],
                )
            except Exception as e:
                yield f"[Stream Error] {str(e)}"

        return generator(), trace

    # =========================================================
    # CONTEXT BUILDER (FINAL ORDER)
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
