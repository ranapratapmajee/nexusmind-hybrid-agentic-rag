# app/agents/research_agent.py

import asyncio
from app.retrieval.hybrid_retriever import HybridRetriever
from app.services.llm_service import LLMService
from app.control.router import ControlRouter

class NexusResearchAgent:
    def __init__(self, hybrid_retriever: HybridRetriever, llm_service: LLMService, router: ControlRouter):
        self.retriever = hybrid_retriever
        self.llm = llm_service
        self.router = router

    def execute_research_flow(self, user_query: str) -> dict:
        # Step 1: Run a deterministic routing check on the prompt intent
        route_intent = self.router.deterministic_route_check(user_query)
        
        # BYPASS RETRIEVAL PIPELINE ON CASUAL INTENTS
        if route_intent == "CASUAL_CHITCHAT":
            system_instruction = "You are a helpful local AI assistant named Nexa. Greet the user naturally and concisely."
            final_response = self.llm.generate_local(user_query, system_instruction)
            return {
                "answer": final_response,
                "engine": "Ollama Local Engine (Direct Route)",
                "vector_sources_count": 0,
                "graph_triplets_count": 0
            }
        
        # Step 2: Parallel Context Fetch (Vector & Graph running simultaneously via Asyncio)
        context_data = asyncio.run(self.retriever.retrieve(user_query))
        
        # Step 3: Fused formatting across multi-modal retrieval pipelines
        text_chunks = context_data["retrieved_text_chunks"]
        graph_edges = context_data["graph_topology"]
        
        fused_context = "=== VECTOR CONTEXT ===\n"
        for idx, chunk in enumerate(text_chunks):
            fused_context += f"[{idx+1}] (File: {chunk['metadata'].get('source_file')}): {chunk['text']}\n"
            
        fused_context += "\n=== GRAPH ASSERTIONS ===\n"
        for edge in graph_edges:
            fused_context += f"({edge['source']}) -> [{edge['relation']}] -> ({edge['target']})\n"

        system_instruction = (
            "Synthesize a structured explanation grounded strictly in the provided contexts. "
            "If the context does not contain relevant information, state that clearly."
        )
        generation_prompt = f"Contexts:\n{fused_context}\n\nQuery: {user_query}"

        # Step 4: Route compute footprints based on topology data structural limits
        compute_target = self.router.determine_compute_target({
            "complexity": "HIGH" if (len(graph_edges) > 5 or route_intent == "GRAPH_SEARCH") else "LOW"
        })

        if compute_target == "GEMINI_CLOUD":
            final_response = self.llm.generate_cloud(generation_prompt, system_instruction)
            engine = "Gemini 2.5 Cloud Reasoning"
        else:
            final_response = self.llm.generate_local(generation_prompt, system_instruction)
            engine = f"Ollama Local Engine ({self.router.settings.local_llm.model})"

        return {
            "answer": final_response,
            "engine": engine,
            "vector_sources_count": len(text_chunks),
            "graph_triplets_count": len(graph_edges)
        }
