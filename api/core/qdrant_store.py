"""
Qdrant Cloud Vector Store Integration

Provides vector database functionality using Qdrant Cloud (1GB free tier).
Replaces PostgreSQL + pgvector for medical knowledge retrieval.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """
    Vector store using Qdrant Cloud for medical knowledge retrieval.

    Features:
    - 384-dimensional embeddings (all-MiniLM-L6-v2)
    - Cosine similarity search
    - Metadata filtering by category, source, etc.
    - Batch upsert for efficient indexing
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: str = "medical_knowledge",
    ):
        """
        Initialize Qdrant client and collection.

        Args:
            url: Qdrant Cloud URL (default: env QDRANT_URL)
            api_key: Qdrant API key (default: env QDRANT_API_KEY)
            collection_name: Collection name for medical documents
        """
        self.url = url or os.getenv("QDRANT_URL")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name

        if not self.url or not self.api_key:
            logger.warning(
                "Qdrant credentials not configured. Vector search will be disabled."
            )
            self.client = None
            return

        try:
            self.client = QdrantClient(url=self.url, api_key=self.api_key, timeout=10)
            self._init_collection()
            logger.info(f"Qdrant client initialized for collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            self.client = None

    def _init_collection(self):
        """Create collection if it doesn't exist."""
        if not self.client:
            return

        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                # Create collection with 384-dim vectors (all-MiniLM-L6-v2)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # Sentence transformer dimension
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection already exists: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise

    def add_documents(
        self, documents: List[Dict[str, Any]], batch_size: int = 100
    ) -> int:
        """
        Add documents to Qdrant collection.

        Args:
            documents: List of dicts with keys:
                - content (str): Document text
                - embedding (List[float]): 384-dim vector
                - source (str): Document source
                - category (str): Document category
                - metadata (Dict): Additional metadata
            batch_size: Batch size for upsert operations

        Returns:
            Number of documents added
        """
        if not self.client:
            logger.warning("Qdrant client not initialized. Skipping add_documents.")
            return 0

        try:
            total_added = 0

            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]

                points = [
                    PointStruct(
                        id=hash(doc["content"]),  # Use content hash as ID
                        vector=doc["embedding"],
                        payload={
                            "content": doc["content"],
                            "source": doc.get("source", "Unknown"),
                            "category": doc.get("category", "general"),
                            "metadata": doc.get("metadata", {}),
                        },
                    )
                    for doc in batch
                ]

                self.client.upsert(collection_name=self.collection_name, points=points)
                total_added += len(points)

            logger.info(f"Added {total_added} documents to Qdrant")
            return total_added

        except Exception as e:
            logger.error(f"Failed to add documents to Qdrant: {e}")
            return 0

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        category_filter: Optional[str] = None,
        score_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.

        Args:
            query_embedding: 384-dim query vector
            top_k: Number of results to return
            category_filter: Optional category to filter by
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of dicts with keys:
                - content (str): Document text
                - source (str): Document source
                - category (str): Document category
                - score (float): Similarity score
                - metadata (Dict): Additional metadata
        """
        if not self.client:
            logger.warning("Qdrant client not initialized. Returning empty results.")
            return []

        try:
            # Build filter if category specified
            search_filter = None
            if category_filter:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="category", match=MatchValue(value=category_filter)
                        )
                    ]
                )

            # Execute search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=search_filter,
                score_threshold=score_threshold,
            )

            # Format results
            formatted_results = [
                {
                    "content": hit.payload["content"],
                    "source": hit.payload["source"],
                    "category": hit.payload["category"],
                    "score": hit.score,
                    "metadata": hit.payload.get("metadata", {}),
                }
                for hit in results
            ]

            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results

        except Exception as e:
            logger.error(f"Failed to search Qdrant: {e}")
            return []

    def delete_collection(self):
        """Delete the collection (use with caution)."""
        if not self.client:
            logger.warning("Qdrant client not initialized.")
            return

        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")

    def get_collection_info(self) -> Optional[Dict[str, Any]]:
        """Get collection statistics."""
        if not self.client:
            return None

        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return None

    def health_check(self) -> bool:
        """Check if Qdrant is accessible."""
        if not self.client:
            return False

        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False
