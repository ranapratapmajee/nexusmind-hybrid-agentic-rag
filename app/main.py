# app/main.py

import sys
from pathlib import Path

# Fix module loading paths across flat container structures
sys.path.append(str(Path(__file__).resolve().parent))

from app.services.chroma_service import ChromaService
from app.services.neo4j_service import Neo4jService
from app.services.llm_service import LLMService
from app.retrieval.vector_retriever import VectorRetriever
from app.retrieval.graph_retriever import GraphRetriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.control.router import ControlRouter
from app.agents.research_agent import NexusResearchAgent

def initialize_nexus_system() -> NexusResearchAgent:
    """
    Dependency injection framework constructor.
    Wires all service layers, databases, routers, and agents into a running runner environment.
    """
    # 1. Initialize core infrastructure connections
    chroma_service = ChromaService()
    neo4j_service = Neo4jService()
    llm_service = LLMService()
    
    # 2. Wire retrievers (EmbeddingService is dropped; Chroma handles vectorization natively)
    vector_retriever = VectorRetriever(chroma_service)
    graph_retriever = GraphRetriever(neo4j_service)
    hybrid_retriever = HybridRetriever(vector_retriever, graph_retriever)
    
    # 3. Construct orchestration control routers
    router = ControlRouter()
    
    # 4. Return complete agent controller
    return NexusResearchAgent(
        hybrid_retriever=hybrid_retriever,
        llm_service=llm_service,
        router=router
    )

if __name__ == "__main__":
    print("Initializing NexusResearch Orchestration Core...")
    agent = initialize_nexus_system()
    
    # Sample test inquiry run via terminal interface execution
    sample_query = "How does ChromaDB interact with GraphRAG structures?"
    print(f"\nExecuting Sample Run: '{sample_query}'")
    
    result = agent.execute_research_flow(sample_query)
    print(f"\n[Execution Engine Target]: {result['engine']}")
    print(f"[Vector Chunks Retrieved]: {result['vector_sources_count']}")
    print(f"[Graph Relations Traversed]: {result['graph_triplets_count']}")
    print(f"\n[System Output Synthesis]:\n{result['answer']}")
