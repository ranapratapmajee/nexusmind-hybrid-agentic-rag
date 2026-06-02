import time
from typing import Any, Dict

from src.core.memory import Memory
from src.core.planner import Planner
from src.core.router import RouterAgent
from src.governance.guardrails import Guardrails
from src.intelligence.rag import RAG
from src.intelligence.tools import ToolRegistry
from src.llm.gateway import LLMGateway


class Orchestrator:
    """
    🧠 NexusMind Execution Engine v7 (TRACE + UI READY + STREAM FIXED)

    DESIGN GOALS:
    - Clean execution pipeline
    - UI-friendly trace structure
    - Separate execution vs streaming
    """

    def __init__(self):
        print("[Orchestrator] Initializing NexusMind Core v7 (TRACE UI READY)")

        # CORE
        self.planner = Planner()
        self.router = RouterAgent()
        self.memory = Memory()

        # INTELLIGENCE
        self.rag = RAG()
        self.tools = ToolRegistry()
        self.llm = LLMGateway()

        # SAFETY
        self.guardrails = Guardrails()

        print("[Orchestrator] Ready.")

    # =========================================================
    # MEMORY
    # =========================================================
    def _load_memory(self, session_id: str, limit: int = 20):
        return self.memory.format_history(session_id, limit=limit)

    # =========================================================
    # TRACE BUILDER (UI READY FORMAT)
    # =========================================================
    def _step(self, trace: Dict, step: str, stage: str, data: Any = None):
        trace["timeline"].append(
            {
                "step": step,
                "stage": stage,  # planning | routing | rag | tool | llm
                "timestamp": time.time(),
                "data": data,
            }
        )

    # =========================================================
    # MAIN EXECUTION PIPELINE
    # =========================================================
    def run(self, query: str, session_id: str) -> Dict[str, Any]:

        query = (query or "").strip()

        trace = {
            "query": query,
            "session_id": session_id,
            "timeline": [],
            "tokens": {
                "rag_tokens": 0,
                "tool_tokens": 0,
                "llm_tokens": 0,
            },
            "route": None,
            "planner": None,
            "context": "",
            "response": None,
        }

        start_time = time.time()

        # =========================================================
        # 1. GUARDRAILS
        # =========================================================
        guard = self.guardrails.validate_query(query)
        if not guard["safe"]:
            trace["blocked"] = True
            trace["reason"] = guard["reason"]
            return trace

        self._step(trace, "guardrails_passed", "safety", guard)

        # =========================================================
        # 2. MEMORY
        # =========================================================
        self.memory.add_message(session_id, "user", query)
        history = self._load_memory(session_id)
        self._step(trace, "memory_loaded", "memory", len(history))

        # =========================================================
        # 3. PLANNER
        # =========================================================
        plan = self.planner.create_plan(query)
        trace["planner"] = plan
        self._step(trace, "plan_created", "planning", plan)

        # =========================================================
        # 4. ROUTER
        # =========================================================
        route = self.router.route(query)
        trace["route"] = route
        self._step(trace, "route_decided", "routing", route)

        action = route["action"]
        optimized_query = route.get("optimized_query", query)

        # =========================================================
        # 5. RAG
        # =========================================================
        rag_context = ""
        if action in ["RAG_SEARCH", "HYBRID"]:
            rag_result = self.rag.retrieve(optimized_query, top_k=5)
            rag_context = rag_result.get("context", "")

            trace["tokens"]["rag_tokens"] = len(rag_context.split())
            self._step(trace, "rag_completed", "rag", rag_result)

        # =========================================================
        # 6. TOOL
        # =========================================================
        tool_context = ""
        if action in ["EXECUTE_TOOL", "HYBRID"]:
            tool_name = route.get("tool") or self.tools.detect(query)

            tool_output = self.tools.execute(tool_name, query)
            tool_context = str(tool_output)

            trace["tokens"]["tool_tokens"] = len(tool_context.split())
            self._step(trace, "tool_completed", "tool", tool_name)

        # =========================================================
        # 7. CONTEXT FUSION
        # =========================================================
        context = self._build_context(
            memory=history,
            rag=rag_context,
            tool=tool_context,
        )

        trace["context"] = context
        self._step(trace, "context_built", "fusion", len(context.split()))

        # =========================================================
        # 8. LLM GENERATION
        # =========================================================
        response = self.llm.generate(
            query=query,
            context=context,
            route=route,
            plan=plan,
        )

        trace["response"] = response
        trace["tokens"]["llm_tokens"] = len(response.split())

        self._step(trace, "llm_completed", "llm", response[:120])

        # =========================================================
        # 9. MEMORY SAVE
        # =========================================================
        self.memory.add_message(session_id, "assistant", response)

        trace["latency_ms"] = round((time.time() - start_time) * 1000, 2)

        return trace

    # =========================================================
    # STREAMING (FIXED CLEAN DESIGN)
    # =========================================================
    def run_stream(self, query: str, session_id: str):

        query = query.strip()

        trace = {
            "query": query,
            "timeline": [],
            "tokens": {"rag": 0, "tool": 0, "llm": 0},
            "latency_ms": 0,
        }

        def event(step: str):
            trace["timeline"].append(step)
            return f"EVENT|THINK|{step}\n"

        start = time.time()

        # 1. Guardrails
        guard = self.guardrails.validate_query(query)
        if not guard["safe"]:
            yield "EVENT|BLOCKED|true\n"
            return

        yield event("guardrails_passed")

        # 2. Memory
        history = self._load_memory(session_id)
        yield event("memory_loaded")

        # 3. Planner
        plan = self.planner.create_plan(query)
        yield event("plan_created")

        # 4. Router
        route = self.router.route(query)
        yield event("route_decided")

        action = route["action"]
        optimized_query = route.get("optimized_query", query)

        # 5. RAG
        rag_context = ""
        if action in ["RAG_SEARCH", "HYBRID"]:
            yield event("rag_started")

            rag_result = self.rag.retrieve(optimized_query)
            rag_context = rag_result.get("context", "")

            trace["tokens"]["rag"] = len(rag_context.split())
            yield event("rag_completed")

        # 6. TOOL
        tool_context = ""
        if action in ["EXECUTE_TOOL", "HYBRID"]:
            yield event("tool_started")

            tool_name = self.tools.detect(query)
            tool_output = self.tools.execute(tool_name, query)

            tool_context = str(tool_output)
            trace["tokens"]["tool"] = len(tool_context.split())

            yield event("tool_completed")

        # 7. CONTEXT
        context = self._build_context(history, rag_context, tool_context)
        yield event("context_built")

        # 8. LLM STREAM (REAL LIVE ANSWER)
        yield event("llm_started")

        full = ""

        for token in self.llm.stream(
            query=query,
            context=context,
            route=route,
            plan=plan,
        ):
            full += token
            trace["tokens"]["llm"] += 1
            yield f"TOKEN|{token}"

        trace["response"] = full
        trace["latency_ms"] = round((time.time() - start) * 1000, 2)

        yield f"\nTRACE|{trace}\n"

    # =========================================================
    # CONTEXT BUILDER
    # =========================================================
    def _build_context(self, memory="", rag="", tool="") -> str:
        sections = []

        if tool:
            sections.append("### TOOL OUTPUT\n" + tool)

        if rag:
            sections.append("### KNOWLEDGE\n" + rag)

        if memory:
            sections.append("### MEMORY\n" + memory)

        return "\n\n".join(sections).strip()
