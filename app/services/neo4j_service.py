# app/services/neo4j_service.py

from neo4j import GraphDatabase
from config.settings import get_settings

class Neo4jService:
    def __init__(self):
        self.settings = get_settings()
        self.driver = GraphDatabase.driver(
            self.settings.neo4j.uri,
            auth=(self.settings.neo4j.username, self.settings.neo4j.password)
        )

    def close(self):
        """Gracefully tears down the Bolt connection pool."""
        self.driver.close()

    def run_query(self, cypher_query: str, parameters: dict = None) -> list[dict]:
        """
        Executes a deterministic relational Cypher query transactional block.
        Perfect layout for production multi-hop assertions.
        """
        with self.driver.session(database=self.settings.neo4j.database) as session:
            result = session.run(cypher_query, parameters)
            return [record.data() for record in result]

    def clear_database(self):
        """Wipes out all structural nodes and relations (useful for re-indexing data)."""
        query = "MATCH (n) DETACH DELETE n"
        self.run_query(query)

    def create_vector_index(self, index_name: str, node_label: str, embedding_property: str, dimensions: int = 768):
        """
        Creates a native vector index inside Neo4j for hybrid GraphRAG tracking.
        Defaults to 768 dimensions to align perfectly with your nomic-embed-text vectors.
        """
        query = f"""
        CREATE VECTOR INDEX {index_name} IF NOT EXISTS
        FOR (n:{node_label}) ON (n.{embedding_property})
        OPTIONS {{
          indexConfig: {{
            `vector.dimensions`: {dimensions},
            `vector.similarity_function`: 'cosine'
          }}
        }}
        """
        self.run_query(query)

    def query_similarity_by_vector(self, index_name: str, query_vector: list[float], top_k: int = 5) -> list[dict]:
        """
        Queries Neo4j nodes using a raw text embedding vector generated via Ollama.
        Combines semantic similarity retrieval with contextual graph lookups.
        """
        query = f"""
        CALL db.index.vector.queryNodes($index, $top_k, $vector) 
        YIELD node, score
        RETURN node.text AS text, score, properties(node) AS properties
        """
        params = {
            "index": index_name,
            "top_k": top_k,
            "vector": query_vector
        }
        return self.run_query(query, params)
