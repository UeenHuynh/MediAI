"""
Unit tests for Vector Store (pgvector)
Tests PostgreSQL vector database operations
"""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch, call


class TestVectorStoreInit:
    """Tests for VectorStore initialization"""

    @patch('api.core.vector_store.create_engine')
    def test_init_creates_engine(self, mock_create_engine):
        """Test __init__ creates engine with database URL"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        mock_create_engine.assert_called_once()
        assert store.engine == mock_engine

    @patch('api.core.vector_store.create_engine')
    def test_init_calls_ensure_extension(self, mock_create_engine):
        """Test __init__ calls _ensure_extension"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension') as mock_ensure:
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        mock_ensure.assert_called_once()

    @patch('api.core.vector_store.create_engine')
    def test_init_calls_create_tables(self, mock_create_engine):
        """Test __init__ calls _create_tables"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables') as mock_create:
                store = VectorStore()

        mock_create.assert_called_once()


class TestEnsureExtension:
    """Tests for _ensure_extension method"""

    @patch('api.core.vector_store.create_engine')
    def test_ensure_extension_success(self, mock_create_engine):
        """Test _ensure_extension creates pgvector extension"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_create_tables'):
            store = VectorStore()

        # Verify extension SQL was executed
        mock_conn.execute.assert_called()
        mock_conn.commit.assert_called()

    @patch('api.core.vector_store.create_engine')
    def test_ensure_extension_raises_on_error(self, mock_create_engine):
        """Test _ensure_extension raises on database error"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("DB error")
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with pytest.raises(Exception) as exc_info:
            store = VectorStore()

        assert "DB error" in str(exc_info.value)


class TestCreateTables:
    """Tests for _create_tables method"""

    @patch('api.core.vector_store.create_engine')
    def test_create_tables_default_dimension(self, mock_create_engine):
        """Test _create_tables uses default 384 dimension"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            store = VectorStore()

        # Verify CREATE TABLE was executed
        assert mock_conn.execute.called
        mock_conn.commit.assert_called()

    @patch('api.core.vector_store.create_engine')
    def test_create_tables_raises_on_error(self, mock_create_engine):
        """Test _create_tables raises on database error"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        # First call for _ensure_extension succeeds, second call for _create_tables fails
        mock_conn.execute.side_effect = [None, Exception("Table error")]
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with pytest.raises(Exception) as exc_info:
            store = VectorStore()

        assert "Table error" in str(exc_info.value)


class TestAddDocument:
    """Tests for add_document method"""

    @patch('api.core.vector_store.create_engine')
    def test_add_document_success(self, mock_create_engine):
        """Test successful document addition"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = [42]
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        embedding = np.array([0.1, 0.2, 0.3])
        doc_id = store.add_document(
            content="Test content",
            embedding=embedding,
            metadata={"key": "value"},
            source="test_source",
            category="test_category"
        )

        assert doc_id == 42
        mock_conn.commit.assert_called()

    @patch('api.core.vector_store.create_engine')
    def test_add_document_raises_on_error(self, mock_create_engine):
        """Test add_document raises on database error"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Insert error")
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        embedding = np.array([0.1, 0.2, 0.3])

        with pytest.raises(Exception) as exc_info:
            store.add_document(
                content="Test content",
                embedding=embedding,
                metadata={},
                source="test",
                category="test"
            )

        assert "Insert error" in str(exc_info.value)


class TestAddDocumentsBatch:
    """Tests for add_documents_batch method"""

    @patch('api.core.vector_store.create_engine')
    def test_add_documents_batch_success(self, mock_create_engine):
        """Test successful batch document addition"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result1 = MagicMock()
        mock_result1.fetchone.return_value = [1]
        mock_result2 = MagicMock()
        mock_result2.fetchone.return_value = [2]
        mock_conn.execute.side_effect = [mock_result1, mock_result2]
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        embedding1 = np.array([0.1, 0.2, 0.3])
        embedding2 = np.array([0.4, 0.5, 0.6])

        documents = [
            ("Content 1", embedding1, {"key": "val1"}, "source1", "cat1"),
            ("Content 2", embedding2, {"key": "val2"}, "source2", "cat2"),
        ]

        doc_ids = store.add_documents_batch(documents)

        assert doc_ids == [1, 2]
        mock_conn.commit.assert_called()

    @patch('api.core.vector_store.create_engine')
    def test_add_documents_batch_empty_list(self, mock_create_engine):
        """Test batch addition with empty list"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        doc_ids = store.add_documents_batch([])

        assert doc_ids == []

    @patch('api.core.vector_store.create_engine')
    def test_add_documents_batch_raises_on_error(self, mock_create_engine):
        """Test batch addition raises on error"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Batch error")
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        embedding = np.array([0.1, 0.2, 0.3])
        documents = [("Content", embedding, {}, "src", "cat")]

        with pytest.raises(Exception) as exc_info:
            store.add_documents_batch(documents)

        assert "Batch error" in str(exc_info.value)


class TestSearchSimilar:
    """Tests for search_similar method"""

    @patch('api.core.vector_store.create_engine')
    def test_search_similar_no_category_filter(self, mock_create_engine):
        """Test search without category filter"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([
            (1, "Content 1", {"meta": "data"}, "source1", "cat1", 0.95),
            (2, "Content 2", {"meta": "data2"}, "source2", "cat2", 0.85),
        ]))
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        query_embedding = np.array([0.1, 0.2, 0.3])
        results = store.search_similar(query_embedding, top_k=5)

        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[0]["content"] == "Content 1"
        assert results[0]["similarity"] == 0.95

    @patch('api.core.vector_store.create_engine')
    def test_search_similar_with_category_filter(self, mock_create_engine):
        """Test search with category filter"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([
            (1, "Drug content", {}, "drug_source", "drug", 0.90),
        ]))
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        query_embedding = np.array([0.1, 0.2, 0.3])
        results = store.search_similar(query_embedding, top_k=5, category="drug")

        assert len(results) == 1
        assert results[0]["category"] == "drug"

    @patch('api.core.vector_store.create_engine')
    def test_search_similar_with_min_similarity(self, mock_create_engine):
        """Test search respects min_similarity parameter"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        query_embedding = np.array([0.1, 0.2, 0.3])
        results = store.search_similar(query_embedding, min_similarity=0.9)

        assert results == []

    @patch('api.core.vector_store.create_engine')
    def test_search_similar_raises_on_error(self, mock_create_engine):
        """Test search raises on database error"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Search error")
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        query_embedding = np.array([0.1, 0.2, 0.3])

        with pytest.raises(Exception) as exc_info:
            store.search_similar(query_embedding)

        assert "Search error" in str(exc_info.value)


class TestHybridSearch:
    """Tests for hybrid_search method"""

    @patch('api.core.vector_store.create_engine')
    def test_hybrid_search_no_category_filter(self, mock_create_engine):
        """Test hybrid search without category filter"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([
            (1, "Content 1", {}, "src1", "cat1", 0.9, 0.7, 0.2),
            (2, "Content 2", {}, "src2", "cat2", 0.8, 0.6, 0.2),
        ]))
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        query_embedding = np.array([0.1, 0.2, 0.3])
        results = store.hybrid_search(query_embedding, "test query", top_k=5)

        assert len(results) == 2
        assert results[0]["hybrid_score"] == 0.9
        assert results[0]["semantic_score"] == 0.7
        assert results[0]["keyword_score"] == 0.2

    @patch('api.core.vector_store.create_engine')
    def test_hybrid_search_with_category_filter(self, mock_create_engine):
        """Test hybrid search with category filter"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([
            (1, "Drug info", {}, "drug_src", "drug", 0.85, 0.6, 0.25),
        ]))
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        query_embedding = np.array([0.1, 0.2, 0.3])
        results = store.hybrid_search(query_embedding, "drug query", category="drug")

        assert len(results) == 1
        assert results[0]["category"] == "drug"

    @patch('api.core.vector_store.create_engine')
    def test_hybrid_search_custom_weights(self, mock_create_engine):
        """Test hybrid search with custom semantic weight"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        query_embedding = np.array([0.1, 0.2, 0.3])
        results = store.hybrid_search(
            query_embedding,
            "test",
            semantic_weight=0.5
        )

        assert results == []

    @patch('api.core.vector_store.create_engine')
    def test_hybrid_search_handles_none_scores(self, mock_create_engine):
        """Test hybrid search handles None semantic/keyword scores"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([
            (1, "Content", {}, "src", "cat", 0.5, None, None),
        ]))
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        query_embedding = np.array([0.1, 0.2, 0.3])
        results = store.hybrid_search(query_embedding, "test")

        assert len(results) == 1
        assert results[0]["semantic_score"] == 0.0
        assert results[0]["keyword_score"] == 0.0

    @patch('api.core.vector_store.create_engine')
    def test_hybrid_search_raises_on_error(self, mock_create_engine):
        """Test hybrid search raises on database error"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Hybrid search error")
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        query_embedding = np.array([0.1, 0.2, 0.3])

        with pytest.raises(Exception) as exc_info:
            store.hybrid_search(query_embedding, "test")

        assert "Hybrid search error" in str(exc_info.value)


class TestGetDocumentCount:
    """Tests for get_document_count method"""

    @patch('api.core.vector_store.create_engine')
    def test_get_document_count_no_filter(self, mock_create_engine):
        """Test get_document_count without category filter"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = [100]
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        count = store.get_document_count()

        assert count == 100

    @patch('api.core.vector_store.create_engine')
    def test_get_document_count_with_category(self, mock_create_engine):
        """Test get_document_count with category filter"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = [25]
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        count = store.get_document_count(category="drug")

        assert count == 25

    @patch('api.core.vector_store.create_engine')
    def test_get_document_count_raises_on_error(self, mock_create_engine):
        """Test get_document_count raises on database error"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Count error")
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        with pytest.raises(Exception) as exc_info:
            store.get_document_count()

        assert "Count error" in str(exc_info.value)


class TestDeleteAllDocuments:
    """Tests for delete_all_documents method"""

    @patch('api.core.vector_store.create_engine')
    def test_delete_all_documents_success(self, mock_create_engine):
        """Test successful deletion of all documents"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        store.delete_all_documents()

        mock_conn.execute.assert_called()
        mock_conn.commit.assert_called()

    @patch('api.core.vector_store.create_engine')
    def test_delete_all_documents_raises_on_error(self, mock_create_engine):
        """Test delete_all_documents raises on database error"""
        from api.core.vector_store import VectorStore

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Delete error")
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_create_engine.return_value = mock_engine

        with patch.object(VectorStore, '_ensure_extension'):
            with patch.object(VectorStore, '_create_tables'):
                store = VectorStore()

        with pytest.raises(Exception) as exc_info:
            store.delete_all_documents()

        assert "Delete error" in str(exc_info.value)
