"""
Vector Store for RAG System using pgvector
Manages document embeddings and semantic search
"""

import logging
from typing import List, Optional, Tuple

import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from .config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store using PostgreSQL with pgvector extension"""

    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self._ensure_extension()
        self._create_tables()

    def _ensure_extension(self):
        """Ensure pgvector extension is installed"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
                logger.info("pgvector extension enabled")
        except Exception as e:
            logger.error(f"Failed to enable pgvector: {e}")
            raise

    def _create_tables(self, dimension: int = 384):
        """Create vector storage tables if they don't exist

        Args:
            dimension: Vector embedding dimension (384 for MiniLM, 1536 for OpenAI)
        """
        create_table_sql = text(f"""
            CREATE TABLE IF NOT EXISTS medical_documents (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector({dimension}),
                metadata JSONB,
                source TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS medical_documents_embedding_idx
            ON medical_documents USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);

            CREATE INDEX IF NOT EXISTS medical_documents_category_idx
            ON medical_documents(category);

            CREATE INDEX IF NOT EXISTS medical_documents_metadata_idx
            ON medical_documents USING gin(metadata);
        """)

        try:
            with self.engine.connect() as conn:
                conn.execute(create_table_sql)
                conn.commit()
                logger.info("Vector store tables created")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    def add_document(
        self,
        content: str,
        embedding: np.ndarray,
        metadata: dict,
        source: str,
        category: str,
    ) -> int:
        """
        Add a document with its embedding to the vector store

        Args:
            content: Document text content
            embedding: Document embedding vector
            metadata: Additional metadata (dict)
            source: Source identifier
            category: Document category (drug, disease, guideline, etc.)

        Returns:
            Document ID
        """
        insert_sql = text("""
            INSERT INTO medical_documents
            (content, embedding, metadata, source, category)
            VALUES (:content, CAST(:embedding AS vector), CAST(:metadata AS jsonb), :source, :category)
            RETURNING id
        """)

        try:
            import json
            with self.engine.connect() as conn:
                result = conn.execute(
                    insert_sql,
                    {
                        "content": content,
                        "embedding": str(embedding.tolist()),
                        "metadata": json.dumps(metadata),
                        "source": source,
                        "category": category,
                    },
                )
                conn.commit()
                doc_id = result.fetchone()[0]
                logger.info(f"Added document {doc_id} to vector store")
                return doc_id
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise

    def add_documents_batch(
        self,
        documents: List[Tuple[str, np.ndarray, dict, str, str]],
    ) -> List[int]:
        """
        Add multiple documents in batch

        Args:
            documents: List of (content, embedding, metadata, source, category) tuples

        Returns:
            List of document IDs
        """
        insert_sql = text("""
            INSERT INTO medical_documents
            (content, embedding, metadata, source, category)
            VALUES (:content, CAST(:embedding AS vector), CAST(:metadata AS jsonb), :source, :category)
            RETURNING id
        """)

        doc_ids = []
        try:
            import json
            with self.engine.connect() as conn:
                for content, embedding, metadata, source, category in documents:
                    result = conn.execute(
                        insert_sql,
                        {
                            "content": content,
                            "embedding": str(embedding.tolist()),
                            "metadata": json.dumps(metadata),
                            "source": source,
                            "category": category,
                        },
                    )
                    doc_ids.append(result.fetchone()[0])
                conn.commit()
                logger.info(f"Added {len(doc_ids)} documents to vector store")
                return doc_ids
        except Exception as e:
            logger.error(f"Failed to add documents batch: {e}")
            raise

    def search_similar(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        category: Optional[str] = None,
        min_similarity: float = 0.7,
    ) -> List[dict]:
        """
        Search for similar documents using cosine similarity

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            category: Filter by category (optional)
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of similar documents with metadata
        """
        # Build query with optional category filter
        embedding_str = str(query_embedding.tolist())
        if category:
            search_sql = text("""
                SELECT
                    id,
                    content,
                    metadata,
                    source,
                    category,
                    1 - (embedding <=> CAST(:embedding AS vector)) as similarity
                FROM medical_documents
                WHERE category = :category
                    AND 1 - (embedding <=> CAST(:embedding AS vector)) >= :min_similarity
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
            """)
            params = {
                "embedding": embedding_str,
                "category": category,
                "top_k": top_k,
                "min_similarity": min_similarity,
            }
        else:
            search_sql = text("""
                SELECT
                    id,
                    content,
                    metadata,
                    source,
                    category,
                    1 - (embedding <=> CAST(:embedding AS vector)) as similarity
                FROM medical_documents
                WHERE 1 - (embedding <=> CAST(:embedding AS vector)) >= :min_similarity
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
            """)
            params = {
                "embedding": embedding_str,
                "top_k": top_k,
                "min_similarity": min_similarity,
            }

        try:
            with self.engine.connect() as conn:
                result = conn.execute(search_sql, params)
                documents = []
                for row in result:
                    documents.append(
                        {
                            "id": row[0],
                            "content": row[1],
                            "metadata": row[2],
                            "source": row[3],
                            "category": row[4],
                            "similarity": float(row[5]),
                        }
                    )
                logger.info(f"Found {len(documents)} similar documents")
                return documents
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            raise

    def hybrid_search(
        self,
        query_embedding: np.ndarray,
        query_text: str,
        top_k: int = 5,
        category: Optional[str] = None,
        semantic_weight: float = 0.7,
    ) -> List[dict]:
        """
        Hybrid search combining semantic (vector) and keyword (full-text) search

        Args:
            query_embedding: Query embedding vector
            query_text: Query text for keyword search
            top_k: Number of results to return
            category: Filter by category (optional)
            semantic_weight: Weight for semantic search (0-1), keyword weight = 1 - semantic_weight

        Returns:
            List of documents ranked by hybrid score
        """
        keyword_weight = 1 - semantic_weight
        embedding_str = str(query_embedding.tolist())

        if category:
            hybrid_sql = text("""
                WITH semantic_results AS (
                    SELECT
                        id,
                        content,
                        metadata,
                        source,
                        category,
                        (1 - (embedding <=> CAST(:embedding AS vector))) * :semantic_weight as semantic_score
                    FROM medical_documents
                    WHERE category = :category
                ),
                keyword_results AS (
                    SELECT
                        id,
                        ts_rank(
                            to_tsvector('english', content),
                            plainto_tsquery('english', :query_text)
                        ) * :keyword_weight as keyword_score
                    FROM medical_documents
                    WHERE category = :category
                        AND to_tsvector('english', content) @@ plainto_tsquery('english', :query_text)
                )
                SELECT
                    s.id,
                    s.content,
                    s.metadata,
                    s.source,
                    s.category,
                    COALESCE(s.semantic_score, 0) + COALESCE(k.keyword_score, 0) as hybrid_score,
                    s.semantic_score,
                    k.keyword_score
                FROM semantic_results s
                LEFT JOIN keyword_results k ON s.id = k.id
                WHERE COALESCE(s.semantic_score, 0) + COALESCE(k.keyword_score, 0) > 0
                ORDER BY hybrid_score DESC
                LIMIT :top_k
            """)
            params = {
                "embedding": embedding_str,
                "query_text": query_text,
                "category": category,
                "semantic_weight": semantic_weight,
                "keyword_weight": keyword_weight,
                "top_k": top_k,
            }
        else:
            hybrid_sql = text("""
                WITH semantic_results AS (
                    SELECT
                        id,
                        content,
                        metadata,
                        source,
                        category,
                        (1 - (embedding <=> CAST(:embedding AS vector))) * :semantic_weight as semantic_score
                    FROM medical_documents
                ),
                keyword_results AS (
                    SELECT
                        id,
                        ts_rank(
                            to_tsvector('english', content),
                            plainto_tsquery('english', :query_text)
                        ) * :keyword_weight as keyword_score
                    FROM medical_documents
                    WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :query_text)
                )
                SELECT
                    s.id,
                    s.content,
                    s.metadata,
                    s.source,
                    s.category,
                    COALESCE(s.semantic_score, 0) + COALESCE(k.keyword_score, 0) as hybrid_score,
                    s.semantic_score,
                    k.keyword_score
                FROM semantic_results s
                LEFT JOIN keyword_results k ON s.id = k.id
                WHERE COALESCE(s.semantic_score, 0) + COALESCE(k.keyword_score, 0) > 0
                ORDER BY hybrid_score DESC
                LIMIT :top_k
            """)
            params = {
                "embedding": embedding_str,
                "query_text": query_text,
                "semantic_weight": semantic_weight,
                "keyword_weight": keyword_weight,
                "top_k": top_k,
            }

        try:
            with self.engine.connect() as conn:
                result = conn.execute(hybrid_sql, params)
                documents = []
                for row in result:
                    documents.append(
                        {
                            "id": row[0],
                            "content": row[1],
                            "metadata": row[2],
                            "source": row[3],
                            "category": row[4],
                            "hybrid_score": float(row[5]),
                            "semantic_score": float(row[6]) if row[6] else 0.0,
                            "keyword_score": float(row[7]) if row[7] else 0.0,
                        }
                    )
                logger.info(f"Found {len(documents)} documents via hybrid search")
                return documents
        except Exception as e:
            logger.error(f"Failed to perform hybrid search: {e}")
            raise

    def get_document_count(self, category: Optional[str] = None) -> int:
        """Get total number of documents in the store"""
        if category:
            count_sql = text(
                "SELECT COUNT(*) FROM medical_documents WHERE category = :category"
            )
            params = {"category": category}
        else:
            count_sql = text("SELECT COUNT(*) FROM medical_documents")
            params = {}

        try:
            with self.engine.connect() as conn:
                result = conn.execute(count_sql, params)
                count = result.fetchone()[0]
                return count
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            raise

    def delete_all_documents(self):
        """Delete all documents (use with caution!)"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("TRUNCATE TABLE medical_documents"))
                conn.commit()
                logger.warning("All documents deleted from vector store")
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise
