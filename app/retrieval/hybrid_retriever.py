# app/retrieval/hybrid_retriever.py

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List
from app.retrieval.vector_retriever import VectorRetriever
from app.retrieval.graph_retriever import GraphRetriever

class HybridRetriever:
    def __init__(self, vector_retriever: VectorRetriever, graph_retriever: GraphRetriever):
        self.vector_retriever = vector_retriever
        self.graph_retriever = graph_retriever
        # Explicit worker pool thread allocation to handle rapid local Docker I/O workloads safely
        self._executor = ThreadPoolExecutor(max_workers=8)

    def _extract_heuristic_entities(self, query: str) -> List[str]:
        """Extracts candidate words as entity tags for high-speed graph lookup."""
        words = query.split()
        return [w.strip("?,.!") for w in words if len(w) > 2]

    async def retrieve(self, query: str) -> Dict[str, Any]:
        """
        Executes parallel Vector space queries and relational Graph traversals.
        Uses graph structural context to perform a secondary vector amplification phase.
        """
        loop = asyncio.get_running_loop()
        candidate_entities = self._extract_heuristic_entities(query)

        # Step 1: Fire off both retrieval branches simultaneously to minimize latency
        vector_task = loop.run_in_executor(self._executor, self.vector_retriever.retrieve_context, query, 3)
        graph_task = loop.run_in_executor(self._executor, self.graph_retriever.retrieve_subgraph, candidate_entities)

        primary_chunks, graph_relations = await asyncio.gather(vector_task, graph_task)

        # Ensure primary_chunks is evaluated safely as a list structure
        if not primary_chunks:
            primary_chunks = []

        # Step 2: Graph-Driven Vector Amplification
        # Extract unique entities discovered from the structural graph sweep
        discovered_nodes = set()
        for edge in graph_relations:
            if "source" in edge and "target" in edge:
                discovered_nodes.add(edge["source"])
                discovered_nodes.add(edge["target"])

        secondary_chunks = []
        if discovered_nodes:
            # Query the vector base again using the graph's discovered terminology
            expansion_query = " ".join(list(discovered_nodes))
            secondary_chunks = await loop.run_in_executor(
                self._executor, self.vector_retriever.retrieve_context, expansion_query, 2
            )
            
        if not secondary_chunks:
            secondary_chunks = []

        # Step 3: De-duplicate chunks matching the same structural ID
        seen_ids = set()
        fused_chunks = []
        
        for chunk in (primary_chunks + secondary_chunks):
            # Guard checking to prevent parsing crashes from empty index results
            if isinstance(chunk, dict) and "id" in chunk:
                if chunk["id"] not in seen_ids:
                    fused_chunks.append(chunk)
                    seen_ids.add(chunk["id"])

        return {
            "retrieved_text_chunks": fused_chunks,
            "graph_topology": graph_relations
        }

    def shutdown(self):
        """Clean closure hooks for thread lifecycle destruction."""
        self._executor.shutdown(wait=True)
