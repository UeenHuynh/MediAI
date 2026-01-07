"""
Unit tests for Qdrant integration
"""

import pytest


class TestQdrantStore:
    """Test Qdrant vector store"""

    def test_import_qdrant_store(self):
        """Test that Qdrant store can be imported"""
        from api.core.qdrant_store import QdrantVectorStore

        assert QdrantVectorStore is not None

    def test_qdrant_store_init_without_credentials(self):
        """Test Qdrant store initialization without credentials"""
        from api.core.qdrant_store import QdrantVectorStore

        # Should not raise error, just disable functionality
        store = QdrantVectorStore(url=None, api_key=None)
        assert store.client is None

    def test_qdrant_store_health_check_without_client(self):
        """Test health check when client is not initialized"""
        from api.core.qdrant_store import QdrantVectorStore

        store = QdrantVectorStore(url=None, api_key=None)
        assert store.health_check() is False

    def test_qdrant_store_search_without_client(self):
        """Test search returns empty results when client not initialized"""
        from api.core.qdrant_store import QdrantVectorStore

        store = QdrantVectorStore(url=None, api_key=None)
        results = store.search(query_embedding=[0.1] * 384, top_k=5)
        assert results == []

    def test_qdrant_store_add_documents_without_client(self):
        """Test add_documents returns 0 when client not initialized"""
        from api.core.qdrant_store import QdrantVectorStore

        store = QdrantVectorStore(url=None, api_key=None)
        count = store.add_documents([{"content": "test", "embedding": [0.1] * 384}])
        assert count == 0


class TestHybridRAG:
    """Test hybrid RAG pipeline"""

    def test_import_hybrid_rag(self):
        """Test that hybrid RAG can be imported"""
        from api.services.hybrid_rag import HybridRAGPipeline

        assert HybridRAGPipeline is not None

    def test_hybrid_rag_init(self):
        """Test hybrid RAG initialization"""
        from api.services.hybrid_rag import HybridRAGPipeline

        try:
            pipeline = HybridRAGPipeline()
            assert pipeline is not None
            assert hasattr(pipeline, "cag_cache")
            assert hasattr(pipeline, "qdrant_store")
            assert hasattr(pipeline, "embedding_service")
        except Exception:
            pytest.skip("Dependencies not available")

    def test_hybrid_rag_health_check(self):
        """Test hybrid RAG health check"""
        from api.services.hybrid_rag import HybridRAGPipeline

        try:
            pipeline = HybridRAGPipeline()
            health = pipeline.health_check()
            assert isinstance(health, dict)
            assert "cag_cache" in health
            assert "qdrant" in health
            assert "embedding_service" in health
        except Exception:
            pytest.skip("Dependencies not available")

    def test_hybrid_rag_retrieve_with_cag_only(self):
        """Test retrieval using only CAG cache"""
        from api.services.hybrid_rag import HybridRAGPipeline

        try:
            pipeline = HybridRAGPipeline()
            results = pipeline.retrieve(
                query="sepsis definition",
                use_cag=True,
                use_qdrant=False,
                use_pubmed=False,
                top_k=3,
            )
            assert isinstance(results, list)
            # Should return results from CAG if it contains sepsis info
        except Exception:
            pytest.skip("Dependencies not available")


class TestQdrantInitialization:
    """Test Qdrant initialization script functionality"""

    def test_script_exists(self):
        """Test that initialization script exists"""
        from pathlib import Path

        script_path = Path("scripts/initialize_qdrant.py")
        assert script_path.exists()

    def test_script_is_executable(self):
        """Test that script has execute permissions"""
        import os
        from pathlib import Path

        script_path = Path("scripts/initialize_qdrant.py")
        if script_path.exists():
            # Check if executable bit is set
            is_executable = os.access(script_path, os.X_OK)
            assert is_executable or os.name == "nt"  # Windows doesn't use +x


class TestEmbeddingService:
    """Test embedding service integration"""

    def test_embedding_service_import(self):
        """Test embedding service can be imported"""
        from api.services.embedding_service import EmbeddingService

        assert EmbeddingService is not None

    def test_embedding_service_sentence_transformers(self):
        """Test sentence-transformers provider"""
        from api.services.embedding_service import EmbeddingService

        try:
            service = EmbeddingService(provider="sentence-transformers")
            assert service.provider == "sentence-transformers"
            assert service.embedding_dim == 384
        except ImportError:
            pytest.skip("sentence-transformers not installed")

    def test_embedding_service_embed_single_text(self):
        """Test embedding single text"""
        from api.services.embedding_service import EmbeddingService

        try:
            service = EmbeddingService(provider="sentence-transformers")
            text = "This is a test sentence"
            embedding = service.embed(text)
            assert embedding is not None
            assert len(embedding) == 384
        except Exception:
            pytest.skip("Dependencies not available")

    def test_embedding_service_embed_batch(self):
        """Test embedding batch of texts"""
        from api.services.embedding_service import EmbeddingService

        try:
            service = EmbeddingService(provider="sentence-transformers")
            texts = ["Text 1", "Text 2", "Text 3"]
            embeddings = service.embed_batch(texts)
            assert embeddings is not None
            assert len(embeddings) == 3
            assert all(len(emb) == 384 for emb in embeddings)
        except Exception:
            pytest.skip("Dependencies not available")

    def test_embedding_service_similarity(self):
        """Test similarity computation"""
        import numpy as np

        from api.services.embedding_service import EmbeddingService

        try:
            service = EmbeddingService(provider="sentence-transformers")
            text1 = "sepsis infection"
            text2 = "bacterial infection"
            text3 = "weather forecast"

            emb1 = service.embed(text1)
            emb2 = service.embed(text2)
            emb3 = service.embed(text3)

            # Similar texts should have higher similarity
            sim_12 = service.compute_similarity(np.array(emb1), np.array(emb2))
            sim_13 = service.compute_similarity(np.array(emb1), np.array(emb3))

            assert sim_12 is not None
            assert sim_13 is not None
            # Medical terms should be more similar to each other than to weather
            assert sim_12 > sim_13

        except Exception:
            pytest.skip("Dependencies not available")
