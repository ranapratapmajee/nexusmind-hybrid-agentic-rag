import time

import chromadb
from chromadb.config import Settings as ChromaSettings

import config


class ChromaVectorClient:
    def __init__(self):
        # ----------------------------
        # Config (single source of truth)
        # ----------------------------
        self.host = config.CHROMA_HOST
        self.port = config.CHROMA_PORT
        self.collection_name = config.CHROMA_COLLECTION_NAME

        self.client = None
        self.collection = None

        self._connect()

    def _connect(self, max_retries: int = 5, initial_delay: int = 2):
        print(f"[DB] Connecting -> {self.host}:{self.port}")

        delay = initial_delay

        for attempt in range(max_retries):
            try:
                # ----------------------------
                # Connect to ChromaDB server
                # ----------------------------
                self.client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                    settings=ChromaSettings(anonymized_telemetry=False),
                )

                # Health check
                self.client.heartbeat()

                # ----------------------------
                # Get or create collection
                # ----------------------------
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"},
                )

                print(f"[DB] Connected. Collection: {self.collection_name}")
                return

            except Exception as e:
                print(
                    f"[DB] Retry {attempt + 1}/{max_retries} | "
                    f"Retrying in {delay}s | Error: {e}"
                )
                time.sleep(delay)
                delay *= 1.5

        raise ConnectionError("❌ Failed to connect to ChromaDB after retries")

    def get_collection(self):
        if self.collection is None:
            raise RuntimeError("Chroma collection not initialized")
        return self.collection
