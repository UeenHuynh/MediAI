"""
Chat RAG Service

Builds retrieval context for the chat endpoint using the existing Hybrid RAG
pipeline without coupling retrieval logic to the API router or database layer.
"""

import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    from api.services.hybrid_rag import HybridRAGPipeline, get_hybrid_rag
except ImportError:
    from services.hybrid_rag import HybridRAGPipeline, get_hybrid_rag

logger = logging.getLogger(__name__)


class ChatRAGService:
    """Adapter between chat requests and the hybrid retrieval pipeline."""
    LIVE_API_TIERS = {"pubmed", "scholar"}

    def __init__(
        self,
        hybrid_rag: Optional[HybridRAGPipeline] = None,
        top_k: int = 3,
        max_chars_per_doc: int = 1000,
    ):
        self.hybrid_rag = hybrid_rag or get_hybrid_rag()
        self.top_k = top_k
        self.max_chars_per_doc = max_chars_per_doc

    def build_retrieval_package(
        self,
        question: str,
        conversation_history: Optional[Sequence[Tuple[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve documents and format them for LLM consumption.

        Returns:
            Dict containing:
                - retrieved_context: Prompt-ready context string
                - source_docs: Citation metadata list
                - retrieval_context: Persistable retrieval metadata
        """
        search_query = self._build_search_query(question, conversation_history)

        try:
            documents = self.hybrid_rag.retrieve(
                query=search_query,
                top_k=max(self.top_k * 3, 6),
                use_cag=True,
                use_qdrant=True,
                use_pubmed=True,
                use_scholar=True,
                score_threshold=0.5,
            )
        except Exception as exc:
            logger.error("Chat RAG retrieval failed: %s", exc, exc_info=True)
            documents = []

        documents = self._select_documents(documents, question)
        retrieved_context, source_docs = self._format_documents(documents)

        return {
            "retrieved_context": retrieved_context,
            "source_docs": source_docs,
            "retrieval_context": {
                "search_query": search_query,
                "documents_count": len(source_docs),
                "documents": source_docs,
            },
        }

    def _build_search_query(
        self,
        question: str,
        conversation_history: Optional[Sequence[Tuple[str, str]]] = None,
    ) -> str:
        """Prefer the current question, with lightweight follow-up expansion."""
        cleaned_question = question.strip()
        if not conversation_history:
            return cleaned_question

        prior_user_messages = [
            content.strip()
            for role, content in conversation_history[:-1]
            if role == "user" and content and content.strip()
        ]

        if len(cleaned_question) >= 40 or not prior_user_messages:
            return cleaned_question

        return (
            f"{prior_user_messages[-1]}\n"
            f"Follow-up clinical question: {cleaned_question}"
        )

    def _select_documents(
        self, documents: List[Dict[str, Any]], question: str
    ) -> List[Dict[str, Any]]:
        """
        Select prompt documents while ensuring live API coverage when available.

        Strategy:
        - Keep the highest-ranked result.
        - Add at least one live API result (PubMed/Semantic Scholar) if available.
        - For freshness-oriented questions, prefer one additional live result when possible.
        - Fill remaining slots in original rank order.
        """
        if not documents or self.top_k <= 0:
            return []

        selected: List[Dict[str, Any]] = []
        remaining = list(documents)

        def pop_first(predicate):
            for idx, doc in enumerate(remaining):
                if predicate(doc):
                    return remaining.pop(idx)
            return None

        # Always keep the top-ranked item first.
        selected.append(remaining.pop(0))

        needs_live_doc = not any(
            doc.get("tier") in self.LIVE_API_TIERS for doc in selected
        )
        if needs_live_doc:
            live_doc = pop_first(lambda doc: doc.get("tier") in self.LIVE_API_TIERS)
            if live_doc is not None and len(selected) < self.top_k:
                selected.append(live_doc)

        if self._query_prefers_live_sources(question):
            second_live_doc = pop_first(
                lambda doc: doc.get("tier") in self.LIVE_API_TIERS
            )
            if second_live_doc is not None and len(selected) < self.top_k:
                selected.append(second_live_doc)

        while remaining and len(selected) < self.top_k:
            selected.append(remaining.pop(0))

        return selected

    def _query_prefers_live_sources(self, question: str) -> bool:
        """Detect queries where fresh API-backed sources should be emphasized."""
        freshness_terms = {
            "latest",
            "recent",
            "new",
            "newest",
            "updated",
            "current",
            "guideline update",
            "new evidence",
            "today",
            "2024",
            "2025",
            "2026",
        }
        normalized = question.lower()
        return any(term in normalized for term in freshness_terms)

    def _format_documents(
        self, documents: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Convert retrieved documents into prompt context and citation metadata."""
        context_parts: List[str] = []
        source_docs: List[Dict[str, Any]] = []

        for idx, doc in enumerate(documents, 1):
            content = (doc.get("content") or "").strip()
            if not content:
                continue

            metadata = doc.get("metadata") or {}
            source = doc.get("source") or metadata.get("source") or f"Source {idx}"
            title = metadata.get("title") or source
            pmid = metadata.get("pmid")
            url = metadata.get("url")
            if pmid and not url:
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            truncated_content = content[: self.max_chars_per_doc].rstrip()
            if len(content) > self.max_chars_per_doc:
                truncated_content += "..."

            context_parts.append(
                f"[{idx}] {title}\nSource: {source}\n{truncated_content}"
            )

            source_docs.append(
                {
                    "number": idx,
                    "source": source,
                    "title": title,
                    "url": url,
                    "pmid": str(pmid) if pmid is not None else None,
                    "tier": doc.get("tier"),
                    "source_type": self._classify_source_type(doc),
                    "category": doc.get("category"),
                    "score": doc.get("score"),
                    "content_preview": truncated_content,
                }
            )

        return "\n\n".join(context_parts), source_docs

    def _classify_source_type(self, doc: Dict[str, Any]) -> str:
        """Classify source origin for UI display."""
        return (
            "live_api"
            if doc.get("tier") in self.LIVE_API_TIERS
            else "local"
        )
