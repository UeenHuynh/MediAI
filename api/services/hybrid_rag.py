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
        use_scholar: bool = False,
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

        # Tier 4: Semantic Scholar (optional, API-based)
        if use_scholar:
            scholar_results = self._search_scholar(query, max_results=3)
            results.extend(scholar_results)
            logger.info(f"Semantic Scholar returned {len(scholar_results)} results")

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
        logger.info(f"=== PubMed search called with query: '{query}', max_results: {max_results}")
        try:
            from Bio import Entrez
            logger.info("✓ Biopython imported successfully")

            # Set email and API key for PubMed API
            Entrez.email = os.getenv("NCBI_EMAIL", "noreply@mediai.com")
            Entrez.api_key = os.getenv("NCBI_API_KEY")  # Use API key for higher rate limits
            logger.info(f"✓ Entrez configured - Email: {Entrez.email}, API key: {'SET' if Entrez.api_key else 'NOT SET'}")

            # Search PubMed
            handle = Entrez.esearch(
                db="pubmed", term=query, retmax=max_results, sort="relevance"
            )
            search_results = Entrez.read(handle)
            handle.close()

            # Get article IDs
            id_list = search_results["IdList"]
            logger.info(f"✓ PubMed search returned {len(id_list)} article IDs: {id_list[:3]}...")

            if not id_list:
                logger.warning("No PubMed articles found for query")
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

            logger.info(f"✓ Successfully formatted {len(pubmed_results)} PubMed articles")
            return pubmed_results

        except ImportError:
            logger.warning("❌ Biopython not installed. PubMed search disabled.")
            return []

        except Exception as e:
            logger.error(f"❌ PubMed search failed: {e}")
            return []

    def _search_scholar(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search Semantic Scholar for medical research papers.

        Uses Semantic Scholar API with medical field filtering for high-quality results.
        Rate limit: 100 requests per 5 minutes (free tier), 10,000 with API key.

        Args:
            query: User query
            max_results: Maximum number of results

        Returns:
            List of Semantic Scholar papers with enriched metadata
        """
        logger.info(f"=== Semantic Scholar search: query='{query}', max={max_results}")

        try:
            import requests

            # Semantic Scholar API endpoint
            url = "https://api.semanticscholar.org/graph/v1/paper/search"

            # Enhance query with medical context
            enhanced_query = f"{query} medicine clinical treatment patient"

            # API parameters with medical field filter
            params = {
                "query": enhanced_query,
                "fields": "title,abstract,authors,year,citationCount,url,tldr,publicationTypes,fieldsOfStudy",
                "limit": max_results * 2,  # Get extra to filter for quality
                "fieldsOfStudy": "Medicine",  # Filter to medical papers only
                "minCitationCount": 5,  # Quality threshold
            }

            # Optional API key for higher rate limits
            headers = {}
            api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
            if api_key:
                headers["x-api-key"] = api_key
                logger.info("✓ Using Semantic Scholar API key")

            # Make API request with timeout
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10,
            )

            if response.status_code != 200:
                logger.error(f"Semantic Scholar API error: {response.status_code}")
                return []

            data = response.json()
            papers = data.get("data", [])

            logger.info(f"✓ Semantic Scholar returned {len(papers)} papers")

            # Define medical keywords for additional filtering
            medical_keywords = {
                'medical', 'clinical', 'patient', 'treatment', 'therapy',
                'diagnosis', 'disease', 'syndrome', 'hospital', 'care',
                'sepsis', 'shock', 'infection', 'antibiotic', 'intensive care'
            }

            scholar_results = []

            for paper in papers:
                if len(scholar_results) >= max_results:
                    break

                try:
                    # Extract paper details
                    title = paper.get("title", "Untitled")
                    abstract = paper.get("abstract", "")

                    # Use TL;DR if available (AI-generated summary)
                    tldr = paper.get("tldr", {})
                    summary = tldr.get("text", "") if tldr else ""

                    # Additional relevance check
                    text_to_check = f"{title} {abstract} {summary}".lower()
                    has_medical_keyword = any(
                        keyword in text_to_check
                        for keyword in medical_keywords
                    )

                    if not has_medical_keyword:
                        logger.debug(f"Skipping non-medical: {title[:50]}")
                        continue

                    # Extract authors
                    authors = paper.get("authors", [])
                    if authors:
                        author_names = [a.get("name", "") for a in authors[:3]]
                        author_str = ", ".join([
                            name.split()[-1] if ' ' in name else name
                            for name in author_names if name
                        ])
                        if len(authors) > 3:
                            author_str += " et al."
                    else:
                        author_str = "Unknown"

                    # Other metadata
                    year = paper.get("year") or "N/A"
                    citation_count = paper.get("citationCount", 0)
                    url = paper.get("url", "")
                    pub_types = paper.get("publicationTypes", [])

                    # Calculate relevance score based on citations and recency
                    base_score = 0.75
                    if citation_count > 50:
                        base_score += 0.1
                    if year and isinstance(year, int) and year >= 2020:
                        base_score += 0.05
                    if "Review" in pub_types or "Meta-Analysis" in pub_types:
                        base_score += 0.05

                    score = min(base_score, 0.95)  # Cap at 0.95

                    # Build content with TL;DR if available
                    content_parts = [title]
                    if summary:
                        content_parts.append(f"\nSummary: {summary}")
                    elif abstract:
                        # Truncate abstract to 500 chars
                        truncated_abstract = abstract[:500]
                        if len(abstract) > 500:
                            truncated_abstract += "..."
                        content_parts.append(f"\n{truncated_abstract}")

                    content = "\n".join(content_parts)

                    logger.info(
                        f"✓ Added paper: {title[:50]}... "
                        f"({year}, {citation_count} citations)"
                    )

                    scholar_results.append({
                        "content": content,
                        "source": f"Semantic Scholar ({author_str}, {year})",
                        "category": "research",
                        "score": score,
                        "tier": "scholar",
                        "metadata": {
                            "title": title,
                            "authors": author_str,
                            "year": year,
                            "url": url,
                            "citation_count": citation_count,
                            "publication_types": pub_types,
                            "has_tldr": bool(summary),
                        }
                    })

                except Exception as e:
                    logger.error(f"Error parsing Semantic Scholar paper: {e}")
                    continue

            logger.info(f"✓ Formatted {len(scholar_results)} Semantic Scholar papers")
            return scholar_results

        except ImportError:
            logger.error("❌ 'requests' library not installed")
            return []

        except requests.exceptions.Timeout:
            logger.error("❌ Semantic Scholar API timeout")
            return []

        except Exception as e:
            logger.error(f"❌ Semantic Scholar search failed: {e}", exc_info=True)
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
        tier_priority = {"cag": 4, "qdrant": 3, "pubmed": 2, "scholar": 1}

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
