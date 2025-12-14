"""
Integration tests for Semantic Scholar API

Tests real API integration (requires internet connection).
Can be run with pytest -m integration to separate from unit tests.
"""

import pytest
import os
from unittest.mock import patch, Mock

from api.services.hybrid_rag import HybridRAGPipeline


@pytest.mark.integration
class TestSemanticScholarIntegration:
    """Integration tests for Semantic Scholar API."""

    @pytest.fixture
    def hybrid_rag(self):
        """Create HybridRAGPipeline instance."""
        return HybridRAGPipeline()

    @pytest.mark.skipif(
        not os.getenv("RUN_API_TESTS"),
        reason="Set RUN_API_TESTS=1 to run live API tests"
    )
    def test_semantic_scholar_live_api(self, hybrid_rag):
        """Test live Semantic Scholar API call."""
        results = hybrid_rag._search_scholar("sepsis treatment", max_results=2)

        assert isinstance(results, list)
        if len(results) > 0:
            # Check result structure
            paper = results[0]
            assert "content" in paper
            assert "source" in paper
            assert "Semantic Scholar" in paper["source"]
            assert "metadata" in paper
            assert "title" in paper["metadata"]
            assert "year" in paper["metadata"]

    @patch('requests.get')
    def test_semantic_scholar_api_structure(self, mock_get, hybrid_rag):
        """Test Semantic Scholar API response parsing."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "title": "Early Goal-Directed Therapy in Sepsis",
                    "abstract": "Sepsis is a life-threatening condition...",
                    "authors": [
                        {"name": "John Smith"},
                        {"name": "Jane Doe"}
                    ],
                    "year": 2020,
                    "citationCount": 150,
                    "url": "https://semanticscholar.org/paper/123",
                    "tldr": {"text": "Early treatment improves survival"},
                    "publicationTypes": ["Review"],
                    "fieldsOfStudy": ["Medicine"]
                }
            ]
        }
        mock_get.return_value = mock_response

        results = hybrid_rag._search_scholar("sepsis", max_results=1)

        assert len(results) == 1
        paper = results[0]

        # Verify structure
        assert "Early Goal-Directed Therapy" in paper["content"]
        assert "Smith" in paper["source"]
        assert paper["metadata"]["year"] == 2020
        assert paper["metadata"]["citation_count"] == 150
        assert paper["tier"] == "scholar"
        assert paper["score"] > 0.75  # High citation count should boost score

    @patch('requests.get')
    def test_semantic_scholar_medical_filtering(self, mock_get, hybrid_rag):
        """Test medical keyword filtering."""
        # Mock response with one medical and one non-medical paper
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "title": "Clinical Treatment of Septic Shock",
                    "abstract": "Medical intervention for critically ill patients...",
                    "authors": [{"name": "Dr. Smith"}],
                    "year": 2021,
                    "citationCount": 50,
                    "url": "https://test.com/1",
                    "publicationTypes": [],
                },
                {
                    "title": "Stock Market Analysis",
                    "abstract": "Financial markets and economic trends...",
                    "authors": [{"name": "John Doe"}],
                    "year": 2021,
                    "citationCount": 100,
                    "url": "https://test.com/2",
                    "publicationTypes": [],
                }
            ]
        }
        mock_get.return_value = mock_response

        results = hybrid_rag._search_scholar("shock", max_results=2)

        # Only medical paper should be included
        assert len(results) == 1
        assert "Clinical Treatment" in results[0]["content"]
        assert "Stock Market" not in str(results)

    @patch('requests.get')
    def test_semantic_scholar_api_error_handling(self, mock_get, hybrid_rag):
        """Test handling of API errors."""
        # Mock 500 error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        results = hybrid_rag._search_scholar("sepsis", max_results=1)

        # Should return empty list on error
        assert results == []

    @patch('requests.get')
    def test_semantic_scholar_timeout_handling(self, mock_get, hybrid_rag):
        """Test handling of API timeouts."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        results = hybrid_rag._search_scholar("sepsis", max_results=1)

        # Should handle timeout gracefully
        assert results == []

    @patch('requests.get')
    def test_semantic_scholar_tldr_preference(self, mock_get, hybrid_rag):
        """Test TL;DR is used when available."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "title": "Sepsis Treatment",
                    "abstract": "Long abstract text here...",
                    "tldr": {"text": "Short AI-generated summary"},
                    "authors": [{"name": "Smith"}],
                    "year": 2021,
                    "citationCount": 10,
                    "url": "https://test.com",
                    "publicationTypes": [],
                }
            ]
        }
        mock_get.return_value = mock_response

        results = hybrid_rag._search_scholar("sepsis", max_results=1)

        # TL;DR should be in content
        assert "Short AI-generated summary" in results[0]["content"]
        assert results[0]["metadata"]["has_tldr"] is True

    @patch('requests.get')
    def test_semantic_scholar_score_calculation(self, mock_get, hybrid_rag):
        """Test relevance score calculation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "title": "Recent Medical Review",
                    "abstract": "Clinical treatment guidelines...",
                    "authors": [{"name": "Smith"}],
                    "year": 2023,  # Recent year
                    "citationCount": 100,  # High citations
                    "url": "https://test.com",
                    "publicationTypes": ["Review"],  # Review paper
                }
            ]
        }
        mock_get.return_value = mock_response

        results = hybrid_rag._search_scholar("treatment", max_results=1)

        # Score should be boosted for: citations > 50, year >= 2020, Review type
        assert results[0]["score"] > 0.85  # Base 0.75 + bonuses

    @patch('requests.get')
    def test_semantic_scholar_max_results_limit(self, mock_get, hybrid_rag):
        """Test max_results parameter is respected."""
        mock_response = Mock()
        mock_response.status_code = 200
        # Return 10 papers
        mock_response.json.return_value = {
            "data": [
                {
                    "title": f"Paper {i}",
                    "abstract": "Medical clinical treatment patient...",
                    "authors": [{"name": "Author"}],
                    "year": 2021,
                    "citationCount": 10,
                    "url": f"https://test.com/{i}",
                    "publicationTypes": [],
                }
                for i in range(10)
            ]
        }
        mock_get.return_value = mock_response

        results = hybrid_rag._search_scholar("treatment", max_results=3)

        # Should limit to max_results
        assert len(results) <= 3

    @patch('requests.get')
    def test_semantic_scholar_api_key_usage(self, mock_get, hybrid_rag, monkeypatch):
        """Test API key is used when available."""
        monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "test_api_key")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        hybrid_rag._search_scholar("test", max_results=1)

        # Check API key was included in headers
        call_args = mock_get.call_args
        headers = call_args[1].get("headers", {})
        assert "x-api-key" in headers
        assert headers["x-api-key"] == "test_api_key"


@pytest.mark.integration
class TestHybridRAGWithSemanticScholar:
    """Test HybridRAG integration with Semantic Scholar."""

    @pytest.fixture
    def hybrid_rag(self):
        return HybridRAGPipeline()

    @patch('api.services.hybrid_rag.HybridRAGPipeline._search_scholar')
    @patch('api.services.hybrid_rag.HybridRAGPipeline._search_pubmed')
    @patch('api.services.hybrid_rag.HybridRAGPipeline._search_qdrant')
    @patch('api.services.hybrid_rag.HybridRAGPipeline._search_cag_cache')
    def test_hybrid_retrieve_includes_scholar(
        self, mock_cag, mock_qdrant, mock_pubmed, mock_scholar, hybrid_rag
    ):
        """Test Semantic Scholar is included in hybrid retrieval."""
        # Mock all tier results
        mock_cag.return_value = [{"content": "CAG result", "tier": "cag", "score": 0.9}]
        mock_qdrant.return_value = [{"content": "Qdrant result", "tier": "qdrant", "score": 0.8}]
        mock_pubmed.return_value = [{"content": "PubMed result", "tier": "pubmed", "score": 0.7}]
        mock_scholar.return_value = [{"content": "Scholar result", "tier": "scholar", "score": 0.75}]

        results = hybrid_rag.retrieve(
            query="sepsis treatment",
            top_k=5,
            use_scholar=True
        )

        # Verify Scholar was called
        mock_scholar.assert_called_once()

        # Verify results include Scholar tier
        scholar_results = [r for r in results if r.get("tier") == "scholar"]
        assert len(scholar_results) > 0

    @patch('api.services.hybrid_rag.HybridRAGPipeline._search_scholar')
    def test_hybrid_retrieve_scholar_optional(self, mock_scholar, hybrid_rag):
        """Test Semantic Scholar is optional in hybrid retrieval."""
        mock_scholar.return_value = []

        # Call without Scholar
        results = hybrid_rag.retrieve(
            query="test",
            use_scholar=False
        )

        # Scholar should not be called
        mock_scholar.assert_not_called()


# Pytest configuration
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "-m", "integration",
        "--cov=api.services.hybrid_rag"
    ])
