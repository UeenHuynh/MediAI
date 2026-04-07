"""Unit tests for ChatRAGService."""

from unittest.mock import MagicMock


class TestChatRAGService:
    """Focused tests for chat retrieval adapter."""

    def test_build_retrieval_package_formats_context_and_sources(self):
        from api.services.chat_rag_service import ChatRAGService

        mock_hybrid_rag = MagicMock()
        mock_hybrid_rag.retrieve.return_value = [
            {
                "content": "Sepsis guidelines recommend early antibiotics.",
                "source": "PubMed (PMID: 12345)",
                "category": "research",
                "tier": "pubmed",
                "score": 0.9,
                "metadata": {"pmid": "12345", "title": "Sepsis Guideline Paper"},
            }
        ]

        service = ChatRAGService(hybrid_rag=mock_hybrid_rag, top_k=1)

        result = service.build_retrieval_package("What is sepsis?")

        assert "[1] Sepsis Guideline Paper" in result["retrieved_context"]
        assert result["source_docs"][0]["pmid"] == "12345"
        assert result["source_docs"][0]["source_type"] == "live_api"
        assert result["retrieval_context"]["documents_count"] == 1

    def test_build_search_query_uses_previous_user_turn_for_short_follow_up(self):
        from api.services.chat_rag_service import ChatRAGService

        service = ChatRAGService(hybrid_rag=MagicMock())

        search_query = service._build_search_query(
            "And treatment?",
            [
                ("user", "Patient has septic shock"),
                ("assistant", "Can you share more details?"),
                ("user", "And treatment?"),
            ],
        )

        assert "Patient has septic shock" in search_query
        assert "And treatment?" in search_query

    def test_build_retrieval_package_keeps_live_api_source_when_available(self):
        from api.services.chat_rag_service import ChatRAGService

        mock_hybrid_rag = MagicMock()
        mock_hybrid_rag.retrieve.return_value = [
            {"content": "Cached sepsis summary", "source": "CAG Cache", "tier": "cag"},
            {"content": "Another local note", "source": "Local KB", "tier": "qdrant"},
            {
                "content": "PubMed abstract on sepsis updates",
                "source": "PubMed (PMID: 99999)",
                "tier": "pubmed",
                "metadata": {"pmid": "99999", "title": "Updated Sepsis Review"},
            },
            {
                "content": "Scholar summary",
                "source": "Semantic Scholar (Smith, 2025)",
                "tier": "scholar",
                "metadata": {"title": "Scholar Paper"},
            },
        ]

        service = ChatRAGService(hybrid_rag=mock_hybrid_rag, top_k=3)

        result = service.build_retrieval_package("What is the latest sepsis evidence?")

        tiers = {doc["tier"] for doc in result["source_docs"]}
        assert "pubmed" in tiers or "scholar" in tiers
        assert len(result["source_docs"]) == 3
