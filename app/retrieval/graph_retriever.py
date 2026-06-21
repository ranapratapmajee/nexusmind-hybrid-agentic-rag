# app/retrieval/graph_retriever.py

from typing import List, Dict, Any
from app.services.neo4j_service import Neo4jService

class GraphRetriever:
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service

    def retrieve_subgraph(self, entities: List[str]) -> List[Dict[str, Any]]:
        """
        Queries Neo4j to pull structural multi-hop connections for specific terms.
        Applies a case-insensitive comparison layer to prevent token matching failures.
        """
        if not entities:
            return []

        # We normalize strings to uppercase directly inside the database query evaluation loop
        cypher_query = """
        MATCH (n:Entity)-[r]->(m:Entity)
        WHERE toUpper(n.name) IN $entity_list OR toUpper(m.name) IN $entity_list
        RETURN n.name AS source, type(r) AS relation, m.name AS target
        LIMIT 15
        """
        
        # Pass a cleanly scrubbed lowercase/uppercase list down to the Bolt connection runner
        # This allows the database engine to compare normalized targets efficiently
        normalized_entities = [str(e).strip().upper() for e in entities if e]
        
        return self.neo4j.run_query(cypher_query, {"entity_list": normalized_entities})
