"""
Hybrid RAG Pipeline for Medical Knowledge Retrieval

Combines three retrieval strategies:
1. CAG (Cache-Augmented Generation) - Static medical knowledge (~50ms)
2. Qdrant Vector Search - Dynamic medical documents (~200ms)
3. PubMed API - Latest research (fallback, ~1-2s)
"""

import logging
import os
from typing import Any, Dict, List, Optional

from api.core.cag_cache import CAGCache
from api.core.qdrant_store import QdrantVectorStore
from api.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class HybridRAGPipeline:
    """
    Hybrid retrieval pipeline combining CAG, Qdrant, and PubMed.

    Strategy:
    - Tier 1 (CAG): Instant keyword-based cache lookup
    - Tier 2 (Qdrant): Fast vector similarity search
    - Tier 3 (PubMed): Fallback for latest research

    Results are ranked and deduplicated.
    """

    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        embedding_provider: str = "sentence-transformers",
    ):
        """
        Initialize hybrid RAG pipeline.

        Args:
            qdrant_url: Qdrant Cloud URL
            qdrant_api_key: Qdrant API key
            embedding_provider: Embedding service provider
        """
        # Initialize components
        self.cag_cache = CAGCache()
        self.qdrant_store = QdrantVectorStore(url=qdrant_url, api_key=qdrant_api_key)
        self.embedding_service = EmbeddingService(provider=embedding_provider)

        logger.info("Hybrid RAG pipeline initialized")

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        use_cag: bool = True,
        use_qdrant: bool = True,
        use_pubmed: bool = False,
        score_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant medical knowledge using hybrid search.

        Args:
            query: User query
            top_k: Maximum number of results to return
            use_cag: Enable CAG cache lookup
            use_qdrant: Enable Qdrant vector search
            use_pubmed: Enable PubMed API search (slower)
            score_threshold: Minimum similarity score

        Returns:
            List of retrieved documents with metadata
        """
        results = []

        # Tier 1: CAG Cache (instant)
        if use_cag:
            cag_results = self._search_cag(query)
            results.extend(cag_results)
            logger.info(f"CAG cache returned {len(cag_results)} results")

        # Tier 2: Qdrant Vector Search (fast)
        if use_qdrant:
            qdrant_results = self._search_qdrant(
                query, top_k=top_k, score_threshold=score_threshold
            )
            results.extend(qdrant_results)
            logger.info(f"Qdrant search returned {len(qdrant_results)} results")

        # Tier 3: PubMed API (always search for latest research)
        if use_pubmed:
            pubmed_results = self._search_pubmed(query, max_results=5)
            results.extend(pubmed_results)
            logger.info(f"PubMed search returned {len(pubmed_results)} results")

        # Deduplicate and rank
        results = self._deduplicate_results(results)
        results = self._rank_results(results, query)

        # Return top-k
        final_results = results[:top_k]
        logger.info(f"Returning {len(final_results)} total results")

        return final_results

    def _search_cag(self, query: str) -> List[Dict[str, Any]]:
        """
        Search CAG cache using keyword matching.

        Args:
            query: User query

        Returns:
            List of matched documents from cache
        """
        try:
            cache_results = self.cag_cache.search(query, top_k=3)

            return [
                {
                    "content": result["content"],
                    "source": "CAG Cache",
                    "category": result.get("category", "general"),
                    "score": 1.0,  # Perfect match from cache
                    "tier": "cag",
                    "keywords": result.get("keywords", []),
                }
                for result in cache_results
            ]

        except Exception as e:
            logger.error(f"CAG search failed: {e}")
            return []

    def _search_qdrant(
        self, query: str, top_k: int = 5, score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search Qdrant using vector similarity.

        Args:
            query: User query
            top_k: Number of results
            score_threshold: Minimum similarity score

        Returns:
            List of similar documents from Qdrant
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.embed(query)

            if query_embedding is None:
                logger.warning("Failed to generate query embedding")
                return []

            # Convert numpy array to list if needed
            if hasattr(query_embedding, "tolist"):
                query_embedding = query_embedding.tolist()

            # Search Qdrant
            qdrant_results = self.qdrant_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                score_threshold=score_threshold,
            )

            # Add tier metadata
            for result in qdrant_results:
                result["tier"] = "qdrant"

            return qdrant_results

        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            return []

    def _search_pubmed(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search PubMed for latest medical research.

        Args:
            query: User query
            max_results: Maximum number of results

        Returns:
            List of PubMed articles
        """
        try:
            from Bio import Entrez

            # Set email and API key for PubMed API
            Entrez.email = os.getenv("NCBI_EMAIL", "noreply@mediai.com")
            Entrez.api_key = os.getenv("NCBI_API_KEY")  # Use API key for higher rate limits

            # Search PubMed
            handle = Entrez.esearch(
                db="pubmed", term=query, retmax=max_results, sort="relevance"
            )
            search_results = Entrez.read(handle)
            handle.close()

            # Get article IDs
            id_list = search_results["IdList"]

            if not id_list:
                return []

            # Fetch article details
            handle = Entrez.efetch(
                db="pubmed", id=id_list, rettype="abstract", retmode="xml"
            )
            articles = Entrez.read(handle)
            handle.close()

            # Format results
            pubmed_results = []
            for article in articles["PubmedArticle"]:
                try:
                    medline = article["MedlineCitation"]
                    article_data = medline["Article"]

                    title = article_data.get("ArticleTitle", "")
                    abstract = article_data.get("Abstract", {}).get("AbstractText", [""])
                    abstract_text = " ".join(abstract) if isinstance(abstract, list) else str(abstract)

                    pmid = medline["PMID"]

                    pubmed_results.append(
                        {
                            "content": f"{title}\n\n{abstract_text}",
                            "source": f"PubMed (PMID: {pmid})",
                            "category": "research",
                            "score": 0.8,  # Default score for PubMed
                            "tier": "pubmed",
                            "metadata": {
                                "pmid": str(pmid),
                                "title": title,
                            },
                        }
                    )

                except Exception as e:
                    logger.error(f"Error parsing PubMed article: {e}")
                    continue

            return pubmed_results

        except ImportError:
            logger.warning("Biopython not installed. PubMed search disabled.")
            return []

        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return []

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate results based on content similarity.

        Args:
            results: List of results

        Returns:
            Deduplicated results
        """
        if len(results) <= 1:
            return results

        unique_results = []
        seen_content = set()

        for result in results:
            # Use first 100 chars as dedup key
            content_key = result["content"][:100].strip().lower()

            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_results.append(result)

        logger.info(
            f"Deduplicated {len(results)} → {len(unique_results)} results"
        )

        return unique_results

    def _rank_results(
        self, results: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """
        Rank results by relevance.

        Ranking strategy:
        - CAG cache: Priority boost (1.0)
        - Qdrant: Score from vector similarity
        - PubMed: Fixed score (0.8)

        Args:
            results: List of results
            query: Original query

        Returns:
            Sorted results by score
        """
        # Sort by score (descending) and tier priority
        tier_priority = {"cag": 3, "qdrant": 2, "pubmed": 1}

        sorted_results = sorted(
            results,
            key=lambda x: (tier_priority.get(x.get("tier", ""), 0), x.get("score", 0)),
            reverse=True,
        )

        return sorted_results

    def health_check(self) -> Dict[str, Any]:
        """
        Check health of all RAG components.

        Returns:
            Health status of each component
        """
        return {
            "cag_cache": {
                "status": "healthy" if self.cag_cache else "unavailable",
                "documents_count": len(self.cag_cache.MEDICAL_KNOWLEDGE) if self.cag_cache else 0,
            },
            "qdrant": {
                "status": "healthy" if self.qdrant_store.health_check() else "unavailable",
                "collection_info": self.qdrant_store.get_collection_info(),
            },
            "embedding_service": {
                "status": "healthy" if self.embedding_service else "unavailable",
                "provider": getattr(self.embedding_service, "provider", "unknown"),
                "model": getattr(self.embedding_service, "model_name", "unknown"),
            },
        }


# Singleton instance
_hybrid_rag = None


def get_hybrid_rag() -> HybridRAGPipeline:
    """
    Get or create hybrid RAG pipeline singleton.

    Returns:
        HybridRAGPipeline instance
    """
    global _hybrid_rag
    if _hybrid_rag is None:
        _hybrid_rag = HybridRAGPipeline()
    return _hybrid_rag
