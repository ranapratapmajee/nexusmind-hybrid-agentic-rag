# app/ingestion/graph_ingestor.py

from typing import List, Dict, Any
from app.services.neo4j_service import Neo4jService
import logging

logger = logging.getLogger(__name__)

class GraphIngestor:
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service

    def ingest_triplets(self, triplets: List[Dict[str, str]], source_file: str) -> int:
        """
        Accepts explicit entity relation maps and structurally commits them into Neo4j.
        Expected Triplet Schema: {'source': 'RAG', 'target': 'ChromaDB', 'relation': 'USES'}
        """
        ingested_count = 0
        
        # FIXED: Modified YIELD tracking from 'relationship' to 'rel' to align with newer APOC procedures
        cypher_query = """
        MERGE (s:Entity {name: $source})
        ON CREATE SET s.created_at = timestamp(), s.source_file = $source_file
        
        MERGE (t:Entity {name: $target})
        ON CREATE SET t.created_at = timestamp(), t.source_file = $source_file
        
        WITH s, t
        CALL apoc.merge.relationship(s, $relation, {}, {}, t, {})
        YIELD rel
        RETURN count(rel) as committed
        """

        for triplet in triplets:
            try:
                source = triplet.get("source", "").strip().upper()
                target = triplet.get("target", "").strip().upper()
                relation = triplet.get("relation", "").strip().replace(" ", "_").upper()

                if not source or not target or not relation:
                    continue

                params = {
                    "source": source,
                    "target": target,
                    "relation": relation,
                    "source_file": source_file
                }
                
                self.neo4j.run_query(cypher_query, params)
                ingested_count += 1
                
            except Exception as e:
                logger.error(f"Frictional fault writing triplet structural graph link: {e}")
                continue
                
        return ingested_count