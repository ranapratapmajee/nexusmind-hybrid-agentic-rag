# ingest_book.py
import os
import sys
import logging
from pypdf import PdfReader

from app.services.chroma_service import ChromaService
from app.services.neo4j_service import Neo4jService
from app.services.llm_service import LLMService
from app.ingestion.vector_ingestor import VectorIngestor
from app.ingestion.graph_ingestor import GraphIngestor

# Setup clean logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

def ingest_pdf_book(relative_path: str):
    if not os.path.exists(relative_path):
        logger.error(f"Target file not found at: {relative_path}")
        sys.exit(1)

    filename = os.path.basename(relative_path)
    logger.info(f"📚 Starting Extraction Sequence for: {filename}")

    reader = PdfReader(relative_path)
    raw_chunks = []
    
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text or len(text.strip()) < 10:
            continue
            
        raw_chunks.append({
            "text": text,
            "metadata": {
                "page_number": idx + 1,
                "chunk_index": idx
            }
        })

    logger.info(f"Extracted {len(raw_chunks)} raw structural windows.")

    # Initialize Services
    logger.info("Connecting to core database service clusters...")
    chroma_service = ChromaService()
    neo4j_service = Neo4jService()
    llm_service = LLMService()

    # EmbeddingService instantiation is dropped here; vectorizer runs natively inside ChromaDB
    vector_ingestor = VectorIngestor(chroma_service)
    graph_ingestor = GraphIngestor(neo4j_service)

    # 1. Vector Space Ingestion (ChromaDB)
    logger.info("Processing document chunk transfer -> ChromaDB container automated embedding...")
    vector_count = vector_ingestor.ingest_document_chunks(raw_chunks, filename)
    logger.info(f"✅ Successfully committed {vector_count} text fragments into ChromaDB via Ollama.")

    # 2. Dynamic Graph Extraction (Neo4j)
    logger.info("Starting automated AI Graph Extraction Loop...")
    total_graph_links = 0
    
    # We will sample pages throughout the text to build a rapid, rich concept network
    # Processing every single page of a 252-page book can take a long time, so we will pace it 
    # by parsing every 5th page for this optimization run.
    for i in range(0, len(raw_chunks), 5):
        chunk = raw_chunks[i]
        page_num = chunk["metadata"]["page_number"]
        logger.info(f"Analyzing semantic connections on Page {page_num}...")
        
        # Call our updated strict-schema extraction method via Gemini Cloud
        triplets = llm_service.extract_triplets_from_text(chunk["text"])
        if triplets:
            committed = graph_ingestor.ingest_triplets(triplets, filename)
            total_graph_links += committed
            logger.info(f"   Harvested and linked {committed} nodes from Page {page_num}")

    logger.info(f"✅ Graph linking phase completed. Seeded {total_graph_links} new relational links into Neo4j!")

if __name__ == "__main__":
    TARGET_BOOK = "data/A Simple Guide to Retrieval Augmented Generation{Abhinav Kimothi}(2025 July 15, MANNING Publications){108189219} libgen.li.pdf"
    ingest_pdf_book(TARGET_BOOK)
