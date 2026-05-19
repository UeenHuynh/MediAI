"""Free-tier friendly retrieval pipeline for chatbot v2."""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests

try:
    from api.core.cag_cache import CAGCache
except ImportError:
    from core.cag_cache import CAGCache

logger = logging.getLogger(__name__)


class ChatbotV2Retrieval:
    """
    Retrieval adapter that prefers the legacy RAG service but can run without it.

    The fallback path keeps free-tier deployments usable even when optional
    packages like `qdrant-client` or `biopython` are unavailable.
    """

    LIVE_API_TIERS = {"pubmed", "scholar"}
    TIER_PRIORITY = {
        "cag": 4.0,
        "qdrant": 3.0,
        "pubmed": 2.0,
        "scholar": 1.0,
    }

    def __init__(self, top_k: int = 3, max_chars_per_doc: int = 1000):
        self.top_k = top_k
        self.max_chars_per_doc = max_chars_per_doc
        self.cag_cache = CAGCache()
        self.legacy_service = self._init_legacy_service()
        self.embedding_service = None
        self.qdrant_store = None
        self._init_vector_stack()

    def _init_legacy_service(self):
        """Try to use the existing chat RAG service when its dependencies exist."""
        try:
            try:
                from api.services.chat_rag_service import ChatRAGService
            except ImportError:
                from services.chat_rag_service import ChatRAGService

            service = ChatRAGService(
                top_k=self.top_k,
                max_chars_per_doc=self.max_chars_per_doc,
            )
            logger.info("Chatbot V2 retrieval using legacy ChatRAGService")
            return service
        except Exception as exc:
            logger.warning(
                "Chatbot V2 retrieval falling back to lightweight mode: %s",
                exc,
            )
            return None

    def _init_vector_stack(self) -> None:
        """Optionally enable Qdrant vector search when dependencies exist."""
        try:
            try:
                from api.core.qdrant_store import QdrantVectorStore
                from api.services.embedding_service import EmbeddingService
            except ImportError:
                from core.qdrant_store import QdrantVectorStore
                from services.embedding_service import EmbeddingService

            self.embedding_service = EmbeddingService(
                provider="sentence-transformers"
            )
            self.qdrant_store = QdrantVectorStore()

            if getattr(self.qdrant_store, "client", None) is None:
                self.qdrant_store = None
        except Exception as exc:
            logger.warning("Qdrant vector stack unavailable in chatbot v2: %s", exc)
            self.embedding_service = None
            self.qdrant_store = None

    def build_retrieval_package(
        self,
        question: str,
        conversation_history: Optional[Sequence[Tuple[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Build prompt context and citation metadata for the chat router."""
        result: Optional[Dict[str, Any]] = None
        # Always use direct retrieval path (CAG + Scholar) for better citations
        if result is None:
            search_query = self._build_search_query(question, conversation_history)
            documents: List[Dict[str, Any]] = []
            documents.extend(self._search_cag(search_query))
            documents.extend(self._search_qdrant(search_query))

            if self._query_prefers_live_sources(question) or len(documents) < self.top_k:
                documents.extend(self._search_pubmed(search_query, max_results=2))
            documents.extend(self._search_scholar(search_query, max_results=2))

            documents = self._deduplicate_results(documents)
            documents = self._rank_results(documents, search_query)
            documents = self._select_documents(documents, question)
            retrieved_context, source_docs = self._format_documents(documents)

            result = {
                "retrieved_context": retrieved_context,
                "source_docs": source_docs,
                "retrieval_context": {
                    "search_query": search_query,
                    "documents_count": len(source_docs),
                    "documents": source_docs,
                },
            }

        self._log_retrieval_trace(question, result.get("source_docs", []))
        return result

    def _log_retrieval_trace(
        self, question: str, source_docs: List[Dict[str, Any]]
    ) -> None:
        """Emit a single structured log line showing which retrieval tiers fired."""
        tiers: set = {d.get("tier") for d in source_docs if d.get("tier")}
        logger.info(
            "RETRIEVAL_TRACE used_cag=%s used_qdrant=%s used_pubmed=%s "
            "used_scholar=%s docs=%d wants_live=%s legacy_path=%s",
            "cag" in tiers,
            "qdrant" in tiers,
            "pubmed" in tiers,
            "scholar" in tiers,
            len(source_docs),
            self._query_prefers_live_sources(question),
            self.legacy_service is not None,
        )

    def _build_search_query(
        self,
        question: str,
        conversation_history: Optional[Sequence[Tuple[str, str]]] = None,
    ) -> str:
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

    def _query_prefers_live_sources(self, question: str) -> bool:
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

    def _search_cag(self, query: str) -> List[Dict[str, Any]]:
        """Always-available local knowledge search."""
        try:
            return self.cag_cache.search(query, top_k=max(self.top_k, 3))
        except Exception as exc:
            logger.warning("Chatbot V2 CAG search failed: %s", exc)
            return []

    def _search_qdrant(self, query: str) -> List[Dict[str, Any]]:
        """Optional vector search when Qdrant and embeddings are available."""
        if self.embedding_service is None or self.qdrant_store is None:
            return []

        try:
            query_embedding = self.embedding_service.embed(query)
            if query_embedding is None:
                return []

            if hasattr(query_embedding, "tolist"):
                query_embedding = query_embedding.tolist()

            results = self.qdrant_store.search(
                query_embedding=query_embedding,
                top_k=max(self.top_k, 3),
                score_threshold=0.5,
            )
            for result in results:
                result["tier"] = "qdrant"
            return results
        except Exception as exc:
            logger.warning("Chatbot V2 Qdrant search failed: %s", exc)
            return []

    def _search_pubmed(self, query: str, max_results: int = 2) -> List[Dict[str, Any]]:
        """Optional PubMed retrieval when Biopython is installed."""
        try:
            from Bio import Entrez
        except ImportError:
            return []

        try:
            Entrez.email = os.getenv("NCBI_EMAIL", "noreply@mediai.com")
            Entrez.api_key = os.getenv("NCBI_API_KEY")

            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort="relevance",
            )
            search_results = Entrez.read(handle)
            handle.close()

            id_list = search_results.get("IdList", [])
            if not id_list:
                return []

            handle = Entrez.efetch(
                db="pubmed",
                id=id_list,
                rettype="abstract",
                retmode="xml",
            )
            articles = Entrez.read(handle)
            handle.close()

            results = []
            for article in articles.get("PubmedArticle", []):
                try:
                    medline = article["MedlineCitation"]
                    article_data = medline["Article"]
                    title = article_data.get("ArticleTitle", "")
                    abstract = article_data.get("Abstract", {}).get(
                        "AbstractText", [""]
                    )
                    abstract_text = (
                        " ".join(abstract)
                        if isinstance(abstract, list)
                        else str(abstract)
                    )
                    pmid = str(medline["PMID"])

                    results.append(
                        {
                            "content": f"{title}\n\n{abstract_text}".strip(),
                            "source": f"PubMed (PMID: {pmid})",
                            "category": "research",
                            "score": 0.8,
                            "tier": "pubmed",
                            "metadata": {
                                "pmid": pmid,
                                "title": title,
                                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                            },
                        }
                    )
                except Exception as exc:
                    logger.warning("Chatbot V2 PubMed parse failed: %s", exc)

            return results
        except Exception as exc:
            logger.warning("Chatbot V2 PubMed search failed: %s", exc)
            return []

    def _search_scholar(self, query: str, max_results: int = 2) -> List[Dict[str, Any]]:
        """Lightweight Semantic Scholar retrieval using `requests` only."""
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": f"{query} medicine clinical treatment patient",
            "fields": "title,abstract,authors,year,citationCount,url,tldr,fieldsOfStudy",
            "limit": max_results * 2,
            "fieldsOfStudy": "Medicine",
        }

        headers: Dict[str, str] = {}
        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        if api_key:
            headers["x-api-key"] = api_key

        try:
            response = requests.get(url, params=params, headers=headers, timeout=8)
            if response.status_code != 200:
                return []

            data = response.json()
            papers = data.get("data", [])
            results = []

            for paper in papers:
                title = paper.get("title") or ""
                abstract = paper.get("abstract") or ""
                if not (title or abstract):
                    continue

                year = paper.get("year")
                citation_count = paper.get("citationCount") or 0
                authors = paper.get("authors") or []
                author_name = authors[0]["name"] if authors else "Unknown"
                tldr = (paper.get("tldr") or {}).get("text") or ""
                content_parts = [part for part in [title, abstract, tldr] if part]
                content = "\n\n".join(content_parts)

                base_score = 0.55
                if citation_count >= 100:
                    base_score += 0.15
                elif citation_count >= 25:
                    base_score += 0.05
                if year and int(year) >= 2020:
                    base_score += 0.05

                results.append(
                    {
                        "content": content,
                        "source": f"Semantic Scholar ({author_name}, {year or 'n.d.'})",
                        "category": "research",
                        "score": base_score,
                        "tier": "scholar",
                        "metadata": {
                            "title": title,
                            "url": paper.get("url"),
                            "authors": [author.get("name") for author in authors],
                            "year": year,
                            "citation_count": citation_count,
                        },
                    }
                )

            results.sort(key=lambda item: item.get("score", 0), reverse=True)
            return results[:max_results]
        except Exception as exc:
            logger.warning("Chatbot V2 scholar search failed: %s", exc)
            return []

    def _deduplicate_results(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        deduped = []

        for doc in documents:
            metadata = doc.get("metadata") or {}
            key = (
                doc.get("tier"),
                metadata.get("pmid"),
                metadata.get("url"),
                metadata.get("title") or doc.get("source"),
                (doc.get("content") or "")[:120],
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(doc)

        return deduped

    def _rank_results(self, documents: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        query_terms = set(re.findall(r"[a-z0-9]+", query.lower()))

        def rank(doc: Dict[str, Any]) -> float:
            metadata = doc.get("metadata") or {}
            haystack = " ".join(
                [
                    doc.get("source", ""),
                    metadata.get("title", ""),
                    doc.get("content", ""),
                ]
            ).lower()
            overlap = sum(1 for term in query_terms if term in haystack)
            return (
                self.TIER_PRIORITY.get(doc.get("tier"), 0.0)
                + float(doc.get("score") or 0.0)
                + overlap * 0.05
            )

        return sorted(documents, key=rank, reverse=True)

    def _select_documents(
        self, documents: List[Dict[str, Any]], question: str
    ) -> List[Dict[str, Any]]:
        if not documents or self.top_k <= 0:
            return []

        selected: List[Dict[str, Any]] = []
        remaining = list(documents)

        def pop_first(predicate):
            for idx, doc in enumerate(remaining):
                if predicate(doc):
                    return remaining.pop(idx)
            return None

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

    def _format_documents(
        self, documents: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
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
        return "live_api" if doc.get("tier") in self.LIVE_API_TIERS else "local"
