"""
Unit tests for EmbeddingService
Tests vector embedding generation with multiple providers
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
import numpy as np


class TestEmbeddingServiceInit:
    """Tests for EmbeddingService initialization"""

    def test_init_sentence_transformers_default(self):
        """Test initialization with sentence-transformers (default)"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384

        with patch('sentence_transformers.SentenceTransformer', return_value=mock_model) as mock_st:
            service = EmbeddingService()

            assert service.provider == "sentence-transformers"
            assert service.model_name == "all-MiniLM-L6-v2"
            assert service.embedding_dim == 384
            mock_st.assert_called_once_with("all-MiniLM-L6-v2")

    @patch('sentence_transformers.SentenceTransformer')
    def test_init_sentence_transformers_custom_model(self, mock_st):
        """Test initialization with custom sentence-transformers model"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_st.return_value = mock_model

        service = EmbeddingService(
            provider="sentence-transformers",
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )

        assert service.model_name == "paraphrase-multilingual-MiniLM-L12-v2"
        assert service.embedding_dim == 768

    def test_init_openai(self):
        """Test initialization with OpenAI provider"""
        from api.services.embedding_service import EmbeddingService

        with patch('builtins.__import__', return_value=MagicMock()):
            service = EmbeddingService(provider="openai", api_key="test-key")

            assert service.provider == "openai"
            assert service.model_name == "text-embedding-3-small"
            assert service.embedding_dim == 1536
            assert service.api_key == "test-key"

    @patch('sentence_transformers.SentenceTransformer')
    def test_init_deepseek_falls_back(self, mock_st):
        """Test deepseek provider falls back to sentence-transformers"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = EmbeddingService(provider="deepseek")

        # Should fallback to sentence-transformers
        assert service.provider == "sentence-transformers"
        assert service.model_name == "all-MiniLM-L6-v2"

    def test_init_unknown_provider(self):
        """Test initialization with unknown provider raises error"""
        from api.services.embedding_service import EmbeddingService

        with pytest.raises(ValueError, match="Unknown embedding provider"):
            EmbeddingService(provider="unknown-provider")

    def test_init_sentence_transformers_import_error(self):
        """Test sentence-transformers ImportError is handled"""
        from api.services.embedding_service import EmbeddingService

        with patch('builtins.__import__', side_effect=ImportError):
            with pytest.raises(ImportError, match="sentence-transformers not installed"):
                EmbeddingService(provider="sentence-transformers")


class TestFallbackToSentenceTransformers:
    """Tests for _fallback_to_sentence_transformers method"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_fallback_success(self, mock_st):
        """Test successful fallback to sentence-transformers"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = EmbeddingService.__new__(EmbeddingService)
        service._fallback_to_sentence_transformers()

        assert service.provider == "sentence-transformers"
        assert service.model_name == "all-MiniLM-L6-v2"

    def test_fallback_import_error(self):
        """Test fallback raises error when sentence-transformers unavailable"""
        from api.services.embedding_service import EmbeddingService

        service = EmbeddingService.__new__(EmbeddingService)
        with patch('builtins.__import__', side_effect=ImportError):
            with pytest.raises(ImportError, match="sentence-transformers required"):
                service._fallback_to_sentence_transformers()


class TestEmbed:
    """Tests for embed method"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_sentence_transformers(self, mock_st):
        """Test embedding with sentence-transformers"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_embedding = np.random.rand(384)
        mock_model.encode.return_value = mock_embedding
        mock_st.return_value = mock_model

        service = EmbeddingService()
        result = service.embed("Test medical text")

        assert isinstance(result, np.ndarray)
        assert len(result) == 384
        mock_model.encode.assert_called_once_with("Test medical text", convert_to_numpy=True)

    def test_embed_openai(self):
        """Test embedding with OpenAI"""
        from api.services.embedding_service import EmbeddingService
        import sys

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]

        mock_openai = MagicMock()
        mock_openai.embeddings.create.return_value = mock_response

        with patch.dict(sys.modules, {'openai': mock_openai}):
            service = EmbeddingService(provider="openai", api_key="test-key")
            result = service.embed("Test text")

            assert isinstance(result, np.ndarray)
            assert len(result) == 1536
            mock_openai.embeddings.create.assert_called_with(
                input=["Test text"],
                model="text-embedding-3-small"
            )

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_empty_text_raises_error(self, mock_st):
        """Test embedding empty text raises ValueError"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = EmbeddingService()

        with pytest.raises(ValueError, match="Text cannot be empty"):
            service.embed("")

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_whitespace_only_raises_error(self, mock_st):
        """Test embedding whitespace-only text raises ValueError"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = EmbeddingService()

        with pytest.raises(ValueError, match="Text cannot be empty"):
            service.embed("   \n\t  ")

    def test_embed_openai_error(self):
        """Test OpenAI embedding error is propagated"""
        from api.services.embedding_service import EmbeddingService
        import sys

        mock_openai = MagicMock()
        mock_openai.embeddings.create.side_effect = Exception("API Error")

        with patch.dict(sys.modules, {'openai': mock_openai}):
            service = EmbeddingService(provider="openai", api_key="test-key")

            with pytest.raises(Exception, match="API Error"):
                service.embed("Test text")

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_unknown_provider(self, mock_st):
        """Test embed with unknown provider raises error"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = EmbeddingService()
        service.provider = "unknown"

        with pytest.raises(ValueError, match="Unknown provider"):
            service.embed("Test text")


class TestEmbedBatch:
    """Tests for embed_batch method"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_batch_sentence_transformers(self, mock_st):
        """Test batch embedding with sentence-transformers"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_embeddings = np.random.rand(3, 384)
        mock_model.encode.return_value = mock_embeddings
        mock_st.return_value = mock_model

        service = EmbeddingService()
        texts = ["Text 1", "Text 2", "Text 3"]
        results = service.embed_batch(texts)

        assert len(results) == 3
        assert all(isinstance(emb, np.ndarray) for emb in results)
        mock_model.encode.assert_called_once()

    def test_embed_batch_openai(self):
        """Test batch embedding with OpenAI"""
        from api.services.embedding_service import EmbeddingService
        import sys

        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1] * 1536),
            MagicMock(embedding=[0.2] * 1536)
        ]

        mock_openai = MagicMock()
        mock_openai.embeddings.create.return_value = mock_response

        with patch.dict(sys.modules, {'openai': mock_openai}):
            service = EmbeddingService(provider="openai", api_key="test-key")
            results = service.embed_batch(["Text 1", "Text 2"])

            assert len(results) == 2
            assert all(isinstance(emb, np.ndarray) for emb in results)

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_batch_empty_list(self, mock_st):
        """Test batch embedding with empty list"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = EmbeddingService()
        results = service.embed_batch([])

        assert results == []

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_batch_filters_empty_texts(self, mock_st):
        """Test batch embedding filters out empty texts"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_embeddings = np.random.rand(2, 384)
        mock_model.encode.return_value = mock_embeddings
        mock_st.return_value = mock_model

        service = EmbeddingService()
        texts = ["Valid text", "", "Another valid", "  \n  "]
        results = service.embed_batch(texts)

        # Should filter to only 2 valid texts
        assert len(results) == 2
        # Check that only valid texts were passed to encode
        call_args = mock_model.encode.call_args[0][0]
        assert len(call_args) == 2
        assert "Valid text" in call_args

    def test_embed_batch_openai_large_batch(self):
        """Test OpenAI batch embedding with chunking"""
        from api.services.embedding_service import EmbeddingService
        import sys

        # Mock responses for multiple batches
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536) for _ in range(32)]

        mock_openai = MagicMock()
        mock_openai.embeddings.create.return_value = mock_response

        with patch.dict(sys.modules, {'openai': mock_openai}):
            service = EmbeddingService(provider="openai", api_key="test-key")
            texts = [f"Text {i}" for i in range(64)]
            results = service.embed_batch(texts, batch_size=32)

            # Should process in 2 batches
            assert len(results) == 64
            assert mock_openai.embeddings.create.call_count == 2

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_batch_shows_progress_bar(self, mock_st):
        """Test progress bar shown for large batches"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_embeddings = np.random.rand(150, 384)
        mock_model.encode.return_value = mock_embeddings
        mock_st.return_value = mock_model

        service = EmbeddingService()
        texts = [f"Text {i}" for i in range(150)]
        service.embed_batch(texts)

        # Verify show_progress_bar parameter was set to True
        call_kwargs = mock_model.encode.call_args[1]
        assert call_kwargs['show_progress_bar'] is True


class TestGetEmbeddingDimension:
    """Tests for get_embedding_dimension method"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_get_embedding_dimension_sentence_transformers(self, mock_st):
        """Test get embedding dimension for sentence-transformers"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = EmbeddingService()
        dim = service.get_embedding_dimension()

        assert dim == 384

    def test_get_embedding_dimension_openai(self):
        """Test get embedding dimension for OpenAI"""
        from api.services.embedding_service import EmbeddingService
        import sys

        mock_openai = MagicMock()
        with patch.dict(sys.modules, {'openai': mock_openai}):
            service = EmbeddingService(provider="openai", api_key="test-key")
            dim = service.get_embedding_dimension()

            assert dim == 1536


class TestComputeSimilarity:
    """Tests for compute_similarity method"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_compute_similarity_identical_vectors(self, mock_st):
        """Test similarity of identical vectors is 1.0"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = EmbeddingService()
        vec = np.array([1.0, 2.0, 3.0])
        similarity = service.compute_similarity(vec, vec)

        assert abs(similarity - 1.0) < 0.001

    @patch('sentence_transformers.SentenceTransformer')
    def test_compute_similarity_orthogonal_vectors(self, mock_st):
        """Test similarity of orthogonal vectors is 0.0"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = EmbeddingService()
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])
        similarity = service.compute_similarity(vec1, vec2)

        assert abs(similarity - 0.0) < 0.001

    @patch('sentence_transformers.SentenceTransformer')
    def test_compute_similarity_zero_vector(self, mock_st):
        """Test similarity with zero vector returns 0.0"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = EmbeddingService()
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([0.0, 0.0, 0.0])
        similarity = service.compute_similarity(vec1, vec2)

        assert similarity == 0.0


class TestMedicalEmbeddingServiceInit:
    """Tests for MedicalEmbeddingService initialization"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_init_medical_service(self, mock_st):
        """Test MedicalEmbeddingService initialization"""
        from api.services.embedding_service import MedicalEmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = MedicalEmbeddingService()

        assert isinstance(service.medical_synonyms, dict)
        assert "heart attack" in service.medical_synonyms
        assert "stroke" in service.medical_synonyms


class TestExpandMedicalQuery:
    """Tests for expand_medical_query method"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_expand_medical_query_with_synonyms(self, mock_st):
        """Test query expansion with medical synonyms"""
        from api.services.embedding_service import MedicalEmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = MedicalEmbeddingService()
        queries = service.expand_medical_query("What causes heart attack?")

        # Should include original + variations with medical terms
        assert len(queries) > 1
        assert any("heart attack" in q.lower() for q in queries)
        assert any("myocardial infarction" in q.lower() for q in queries)

    @patch('sentence_transformers.SentenceTransformer')
    def test_expand_medical_query_no_synonyms(self, mock_st):
        """Test query expansion with no matching synonyms"""
        from api.services.embedding_service import MedicalEmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = MedicalEmbeddingService()
        queries = service.expand_medical_query("Random medical question")

        # Should only return original query
        assert len(queries) == 1
        assert queries[0] == "Random medical question"

    @patch('sentence_transformers.SentenceTransformer')
    def test_expand_medical_query_deduplication(self, mock_st):
        """Test query expansion removes duplicates"""
        from api.services.embedding_service import MedicalEmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = MedicalEmbeddingService()
        queries = service.expand_medical_query("diabetes diabetes")

        # Should deduplicate
        assert len(queries) == len(set(queries))


class TestEmbedWithExpansion:
    """Tests for embed_with_expansion method"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_with_expansion_enabled(self, mock_st):
        """Test embedding with medical term expansion"""
        from api.services.embedding_service import MedicalEmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_embeddings = np.random.rand(3, 384)
        mock_model.encode.return_value = mock_embeddings
        mock_st.return_value = mock_model

        service = MedicalEmbeddingService()
        embeddings = service.embed_with_expansion("heart attack symptoms", include_expansion=True)

        # Should return multiple embeddings (original + expansions)
        assert len(embeddings) > 1
        assert all(isinstance(emb, np.ndarray) for emb in embeddings)

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_with_expansion_disabled(self, mock_st):
        """Test embedding without expansion"""
        from api.services.embedding_service import MedicalEmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_embedding = np.random.rand(384)
        mock_model.encode.return_value = mock_embedding
        mock_st.return_value = mock_model

        service = MedicalEmbeddingService()
        embeddings = service.embed_with_expansion("heart attack symptoms", include_expansion=False)

        # Should return single embedding
        assert len(embeddings) == 1
        assert isinstance(embeddings[0], np.ndarray)


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_very_long_text(self, mock_st):
        """Test embedding very long text"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_embedding = np.random.rand(384)
        mock_model.encode.return_value = mock_embedding
        mock_st.return_value = mock_model

        service = EmbeddingService()
        long_text = "Medical text. " * 10000  # Very long text
        result = service.embed(long_text)

        assert isinstance(result, np.ndarray)
        assert len(result) == 384

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_unicode_text(self, mock_st):
        """Test embedding text with Unicode characters"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_embedding = np.random.rand(384)
        mock_model.encode.return_value = mock_embedding
        mock_st.return_value = mock_model

        service = EmbeddingService()
        unicode_text = "Patient temperature: 37°C, μg/mL dosage"
        result = service.embed(unicode_text)

        assert isinstance(result, np.ndarray)

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_batch_all_empty_returns_empty(self, mock_st):
        """Test batch embedding with all empty texts returns empty list"""
        from api.services.embedding_service import EmbeddingService

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model

        service = EmbeddingService()
        results = service.embed_batch(["", "  ", "\n\t", ""])

        assert results == []
