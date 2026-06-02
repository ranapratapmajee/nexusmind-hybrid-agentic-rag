from removed_files.memory.sqlite_memory import SQLiteMemory
from src.core.context_manager import ContextManager
from src.core.planner import Planner
from src.core.router import RouterAgent
from src.llm.gateway import LLMGateway
from src.rag.ranking import ResultRanker
from src.rag.retriever import Retriever
from src.tools.registry import ToolRegistry


class Orchestrator:
    """
    🧠 NexusMind Core Brain (FINAL ARCHITECTURE)

    Flow:
    User → Planner → Router → Intelligence Layer → LLM Gateway → Response
    """

    def __init__(self):
        print("[Orchestrator] Initializing NexusMind Core v3")

        # =========================
        # CORE LAYERS
        # =========================
        self.planner = Planner()
        self.router = RouterAgent()

        # =========================
        # MEMORY + CONTEXT
        # =========================
        self.memory = SQLiteMemory()
        self.context_manager = ContextManager()

        # =========================
        # INTELLIGENCE LAYER
        # =========================
        self.retriever = Retriever()
        self.ranker = ResultRanker(mode="simple")
        self.tools = ToolRegistry()

        # =========================
        # MODEL GATEWAY (MULTI-LLM)
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
    # MAIN EXECUTION FLOW
    # =========================================================
    def run(self, query: str, session_id: str):

        print(f"\n[Session {session_id}] Query: {query}")

        # -------------------------
        # 1. STORE USER INPUT
        # -------------------------
        self.memory.add_message(session_id, "user", query)

        # -------------------------
        # 2. LOAD MEMORY
        # -------------------------
        chat_history, raw_messages = self._load_memory(session_id)

        # -------------------------
        # 3. PLANNER (CONTEXT ONLY)
        # -------------------------
        plan = self.planner.create_plan(query=query, memory=chat_history)

        print(f"[Planner] {plan}")

        # -------------------------
        # 4. ROUTER (TRUTH SOURCE)
        # -------------------------
        route = self.router.route(query)

        action = route["action"]
        optimized_query = route.get("optimized_query", query)

        rag_context = ""
        tool_context = ""
        web_context = ""

        # =========================================================
        # 5. INTELLIGENCE LAYER
        # =========================================================

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

            rag_context = self.context_manager.compress(texts)

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

        # -------------------------
        # WEB SEARCH PIPELINE (future-ready)
        # -------------------------
        if action in ["WEB_SEARCH", "HYBRID"]:
            web_context = "[Web Search Layer Not Implemented Yet]"

        # =========================================================
        # 6. CONTEXT FUSION
        # =========================================================
        final_context = self.context_manager.build(
            memory=chat_history or "",
            rag=rag_context or "",
            tool=tool_context or "",
            history="",
        )

        # =========================================================
        # 7. LLM GATEWAY (SINGLE ENTRY POINT)
        # =========================================================
        response = self.llm.generate(
            query=query,
            context=final_context,
            route=route,
            plan=plan,
        )

        # =========================================================
        # 8. STORE RESPONSE
        # =========================================================
        self.memory.add_message(session_id, "assistant", response)

        return {
            "response": response,
            "route": route,
            "plan": plan,
            "context_used": bool(final_context),
        }

    # =========================================================
    # STREAMING (PHASE-2 READY)
    # =========================================================
    def run_stream(self, query: str, session_id: str):

        result = self.run(query, session_id)

        def generator():
            for word in result["response"].split():
                yield word + " "

        return generator(), result
