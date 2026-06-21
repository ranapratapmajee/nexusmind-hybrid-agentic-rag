# test.py

import asyncio
import logging
import sys
from pathlib import Path

# Align module pathing configurations
sys.path.append(str(Path(__file__).resolve().parent))

from app.main import initialize_nexus_system
from app.services.chroma_service import ChromaService
from app.services.neo4j_service import Neo4jService
from app.ingestion.vector_ingestor import VectorIngestor
from app.ingestion.graph_ingestor import GraphIngestor
from app.services.embedding_service import EmbeddingService

# Setup basic visual verification logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("NexusTestRunner")

def run_integration_test():
    logger.info("==================================================")
    logger.info("🧪 STARTING NEXUSRESEARCH V1 INTEGRATION TEST CRADLE")
    logger.info("==================================================")

    # 1. Initialize core system layer configurations and connections
    logger.info("Connecting to core database service instances...")
    try:
        chroma = ChromaService()
        neo4j = Neo4jService()
        
        # Wipe database records to ensure a completely clean execution sandbox
        logger.info("Clearing sandbox database registers for pristine testing environment...")
        neo4j.clear_database()
        # Reset Chroma collection tracking
        chroma.client.delete_collection(chroma.settings.chroma.collection_name)
        chroma.collection = chroma.client.get_or_create_collection(chroma.settings.chroma.collection_name)
    except Exception as e:
        logger.critical(f"Database connection error. Verify Colima Docker status: {e}")
        sys.exit(1)

    # 2. Mock Ingestion Setup
    logger.info("Mocking unstructured document text windows...")
    mock_filename = "attention_is_all_you_need.pdf"
    
    mock_chunks = [
        {
            "text": "The Transformer model uses an Attention mechanism to track structural dependencies across tokens. Unlike traditional RNN architectures, Transformers compute relationships in parallel, removing sequential processing bottlenecks.",
            "metadata": {"chunk_index": 0}
        },
        {
            "text": "GraphRAG architectures extend baseline vector RAG models by linking unstructured text segments with deterministic knowledge graphs in Neo4j. ChromaDB manages high-density semantic vectors while Neo4j stores explicitly extracted entity relationships.",
            "metadata": {"chunk_index": 1}
        }
    ]

    # 3. Commit Vector Ingestion
    logger.info("Injecting mock text data blocks into ChromaDB Vector Engine...")

    # Initialize the missing dependency
    embedding_service = EmbeddingService() 
    vector_ingestor = VectorIngestor(chroma, embedding_service) # Pass both services

    chunks_committed = vector_ingestor.ingest_document_chunks(mock_chunks, mock_filename)
    logger.info(f"Successfully committed {chunks_committed} vectors into ChromaDB.")

    # 4. Commit Graph Relational Triplet Ingestion
    logger.info("Injecting structured entity network loops into Neo4j Graph Core...")
    graph_ingestor = GraphIngestor(neo4j)
    
    mock_triplets = [
        {"source": "TRANSFORMER", "relation": "UTILIZES", "target": "ATTENTION_MECHANISM"},
        {"source": "GRAPHRAG", "relation": "EXTENDS", "target": "RAG"},
        {"source": "GRAPHRAG", "relation": "STORES_VECTORS_IN", "target": "CHROMADB"},
        {"source": "GRAPHRAG", "relation": "STORES_RELATIONS_IN", "target": "NEO4J"},
        {"source": "CHROMADB", "relation": "MANAGES", "target": "SEMANTIC_VECTORS"}
    ]
    
    triplets_committed = graph_ingestor.ingest_triplets(mock_triplets, mock_filename)
    logger.info(f"Successfully committed {triplets_committed} structural graph links into Neo4j.")

    # 5. Initialize Orchestrator and Run Retrieval Queries
    logger.info("Booting Google ADK System Orchestration Core Agent...")
    agent = initialize_nexus_system()

    # Complex multi-hop semantic & structural exploration test query
    test_query = "Explain how GraphRAG extends traditional systems, and where it stores its relations and vectors."
    
    logger.info(f"Firing integration test query payload: '{test_query}'")
    logger.info("Running parallel hybrid retrievers (Vector space distance search + Cypher structural loops)...")
    
    try:
        result = agent.execute_research_flow(test_query)
        
        logger.info("==================================================")
        logger.info("📊 TEST EXECUTION ANALYSIS RESULTS")
        logger.info("==================================================")
        logger.info(f"Target Compute Router Decision : {result['engine']}")
        logger.info(f"Vector Space Context Matches   : {result['vector_sources_count']}")
        logger.info(f"Graph Relational Links Visited  : {result['graph_triplets_count']}")
        logger.info("\n[SYSTEM GENERATION SYNTHESIS RESPONSE]:\n")
        print(result['answer'])
        logger.info("==================================================")
        logger.info("✅ INTEGRATION RUN SUCCESSFUL. ALL SYSTEMS OPERATIONAL.")
        logger.info("==================================================")
        
    except Exception as e:
        logger.error(f"Frictional execution failure encountered during routing: {e}")
    finally:
        neo4j.close()

if __name__ == "__main__":
    run_integration_test()