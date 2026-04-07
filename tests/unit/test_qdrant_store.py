"""
Unit tests for Qdrant Vector Store
Tests vector storage and similarity search
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
import numpy as np


class TestQdrantVectorStoreInit:
    """Tests for QdrantVectorStore initialization"""

    @patch('api.core.qdrant_store.QdrantClient')
    def test_init_success(self, mock_client_class):
        """Test successful initialization"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        assert store.client is not None
        assert store.url == "http://localhost:6333"
        assert store.collection_name == "medical_knowledge"

    @patch('api.core.qdrant_store.QdrantClient')
    def test_init_with_custom_collection_name(self, mock_client_class):
        """Test initialization with custom collection name"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(
            url="http://localhost:6333",
            collection_name="custom_collection"
        )

        assert store.collection_name == "custom_collection"

    @patch('api.core.qdrant_store.QdrantClient')
    def test_init_failure_sets_client_to_none(self, mock_client_class):
        """Test initialization failure sets client to None"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client_class.side_effect = Exception("Connection failed")

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        assert store.client is None

    @patch('api.core.qdrant_store.QdrantClient')
    def test_init_with_api_key(self, mock_client_class):
        """Test initialization with API key"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(
            url="https://cloud.qdrant.io",
            api_key="test_key"
        )

        mock_client_class.assert_called_once_with(
            url="https://cloud.qdrant.io",
            api_key="test_key",
            timeout=10
        )


class TestInitCollection:
    """Tests for _init_collection method"""

    @patch('api.core.qdrant_store.QdrantClient')
    def test_init_collection_creates_new_collection(self, mock_client_class):
        """Test _init_collection creates collection if not exists"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        mock_client.create_collection.assert_called_once()

    @patch('api.core.qdrant_store.QdrantClient')
    def test_init_collection_skips_if_exists(self, mock_client_class):
        """Test _init_collection skips creation if collection exists"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collection = Mock()
        mock_collection.name = "medical_knowledge"
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_client.get_collections.return_value = mock_collections
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        mock_client.create_collection.assert_not_called()

    @patch('api.core.qdrant_store.QdrantClient')
    def test_init_collection_error_sets_client_none(self, mock_client_class):
        """Test _init_collection error sets client to None"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_client.get_collections.side_effect = Exception("Collection error")
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        # Exception is caught internally and client is set to None
        assert store.client is None

    @patch('api.core.qdrant_store.QdrantClient')
    def test_init_collection_returns_if_no_client(self, mock_client_class):
        """Test _init_collection returns early if client is None"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client_class.side_effect = Exception("Connection failed")

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        assert store.client is None


class TestAddDocuments:
    """Tests for add_documents method"""

    @patch('api.core.qdrant_store.QdrantClient')
    def test_add_documents_success(self, mock_client_class):
        """Test successful document addition"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        documents = [
            {
                "content": "Test document 1",
                "embedding": np.random.random(384).tolist(),
                "source": "test_source",
                "category": "medical"
            }
        ]

        count = store.add_documents(documents)

        assert count == 1
        mock_client.upsert.assert_called_once()

    @patch('api.core.qdrant_store.QdrantClient')
    def test_add_documents_batch_processing(self, mock_client_class):
        """Test batch processing of documents"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        documents = [
            {
                "content": f"Document {i}",
                "embedding": np.random.random(384).tolist(),
                "source": "test",
                "category": "medical"
            }
            for i in range(250)
        ]

        count = store.add_documents(documents, batch_size=100)

        assert count == 250
        assert mock_client.upsert.call_count == 3

    @patch('api.core.qdrant_store.QdrantClient')
    def test_add_documents_with_metadata(self, mock_client_class):
        """Test adding documents with metadata"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        documents = [
            {
                "content": "Test document",
                "embedding": np.random.random(384).tolist(),
                "source": "pubmed",
                "category": "clinical",
                "metadata": {"authors": ["Dr. Smith"], "year": 2023}
            }
        ]

        count = store.add_documents(documents)

        assert count == 1

    @patch('api.core.qdrant_store.QdrantClient')
    def test_add_documents_no_client(self, mock_client_class):
        """Test add_documents when client is None"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client_class.side_effect = Exception("No connection")

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        documents = [{"content": "Test", "embedding": [0.1] * 384}]
        count = store.add_documents(documents)

        assert count == 0

    @patch('api.core.qdrant_store.QdrantClient')
    def test_add_documents_exception_handling(self, mock_client_class):
        """Test exception handling in add_documents"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client.upsert.side_effect = Exception("Upsert failed")
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        documents = [
            {
                "content": "Test",
                "embedding": np.random.random(384).tolist()
            }
        ]

        count = store.add_documents(documents)

        assert count == 0


class TestSearch:
    """Tests for search method"""

    @patch('api.core.qdrant_store.QdrantClient')
    def test_search_success(self, mock_client_class):
        """Test successful search"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections

        mock_hit = Mock()
        mock_hit.payload = {
            "content": "Test result",
            "source": "pubmed",
            "category": "medical",
            "metadata": {}
        }
        mock_hit.score = 0.95
        mock_client.search.return_value = [mock_hit]

        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        query_vector = np.random.random(384).tolist()
        results = store.search(query_vector, top_k=5)

        assert len(results) == 1
        assert results[0]["content"] == "Test result"
        assert results[0]["score"] == 0.95

    @patch('api.core.qdrant_store.QdrantClient')
    def test_search_with_category_filter(self, mock_client_class):
        """Test search with category filter"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client.search.return_value = []
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        query_vector = np.random.random(384).tolist()
        results = store.search(
            query_vector,
            top_k=5,
            category_filter="clinical"
        )

        assert isinstance(results, list)
        call_kwargs = mock_client.search.call_args[1]
        assert call_kwargs["query_filter"] is not None

    @patch('api.core.qdrant_store.QdrantClient')
    def test_search_with_score_threshold(self, mock_client_class):
        """Test search with score threshold"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client.search.return_value = []
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        query_vector = np.random.random(384).tolist()
        results = store.search(
            query_vector,
            top_k=5,
            score_threshold=0.7
        )

        call_kwargs = mock_client.search.call_args[1]
        assert call_kwargs["score_threshold"] == 0.7

    @patch('api.core.qdrant_store.QdrantClient')
    def test_search_no_client(self, mock_client_class):
        """Test search when client is None"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client_class.side_effect = Exception("No connection")

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        query_vector = np.random.random(384).tolist()
        results = store.search(query_vector)

        assert results == []

    @patch('api.core.qdrant_store.QdrantClient')
    def test_search_exception_handling(self, mock_client_class):
        """Test exception handling in search"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client.search.side_effect = Exception("Search failed")
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        query_vector = np.random.random(384).tolist()
        results = store.search(query_vector)

        assert results == []

    @patch('api.core.qdrant_store.QdrantClient')
    def test_search_multiple_results(self, mock_client_class):
        """Test search with multiple results"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections

        mock_hits = []
        for i in range(3):
            mock_hit = Mock()
            mock_hit.payload = {
                "content": f"Result {i}",
                "source": "test",
                "category": "medical",
                "metadata": {"index": i}
            }
            mock_hit.score = 0.9 - (i * 0.1)
            mock_hits.append(mock_hit)

        mock_client.search.return_value = mock_hits
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        query_vector = np.random.random(384).tolist()
        results = store.search(query_vector, top_k=3)

        assert len(results) == 3
        assert results[0]["score"] == 0.9
        assert results[2]["metadata"]["index"] == 2


class TestDeleteCollection:
    """Tests for delete_collection method"""

    @patch('api.core.qdrant_store.QdrantClient')
    def test_delete_collection_success(self, mock_client_class):
        """Test successful collection deletion"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        store.delete_collection()

        mock_client.delete_collection.assert_called_once_with(
            collection_name="medical_knowledge"
        )

    @patch('api.core.qdrant_store.QdrantClient')
    def test_delete_collection_no_client(self, mock_client_class):
        """Test delete_collection when client is None"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client_class.side_effect = Exception("No connection")

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        # Should not raise exception
        store.delete_collection()

    @patch('api.core.qdrant_store.QdrantClient')
    def test_delete_collection_exception_handling(self, mock_client_class):
        """Test exception handling in delete_collection"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client.delete_collection.side_effect = Exception("Delete failed")
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        # Should not raise exception
        store.delete_collection()


class TestGetCollectionInfo:
    """Tests for get_collection_info method"""

    @patch('api.core.qdrant_store.QdrantClient')
    def test_get_collection_info_success(self, mock_client_class):
        """Test successful collection info retrieval"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections

        mock_info = Mock()
        mock_info.vectors_count = 1000
        mock_info.indexed_vectors_count = 1000
        mock_info.points_count = 1000
        mock_info.status = "green"
        mock_client.get_collection.return_value = mock_info

        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        info = store.get_collection_info()

        assert info is not None
        assert info["name"] == "medical_knowledge"
        assert info["vectors_count"] == 1000
        assert info["points_count"] == 1000
        assert info["status"] == "green"

    @patch('api.core.qdrant_store.QdrantClient')
    def test_get_collection_info_no_client(self, mock_client_class):
        """Test get_collection_info when client is None"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client_class.side_effect = Exception("No connection")

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        info = store.get_collection_info()

        assert info is None

    @patch('api.core.qdrant_store.QdrantClient')
    def test_get_collection_info_exception_handling(self, mock_client_class):
        """Test exception handling in get_collection_info"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client.get_collection.side_effect = Exception("Get info failed")
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        info = store.get_collection_info()

        assert info is None


class TestHealthCheck:
    """Tests for health_check method"""

    @patch('api.core.qdrant_store.QdrantClient')
    def test_health_check_success(self, mock_client_class):
        """Test successful health check"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        status = store.health_check()

        assert status is True

    @patch('api.core.qdrant_store.QdrantClient')
    def test_health_check_no_client(self, mock_client_class):
        """Test health check when client is None"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client_class.side_effect = Exception("No connection")

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        status = store.health_check()

        assert status is False

    @patch('api.core.qdrant_store.QdrantClient')
    def test_health_check_failure(self, mock_client_class):
        """Test health check failure"""
        from api.core.qdrant_store import QdrantVectorStore

        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections
        mock_client_class.return_value = mock_client

        store = QdrantVectorStore(url="http://localhost:6333", api_key="test_key")

        # Make health check fail
        mock_client.get_collections.side_effect = Exception("Connection failed")

        status = store.health_check()

        assert status is False
