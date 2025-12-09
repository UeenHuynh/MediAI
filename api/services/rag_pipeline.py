"""
RAG (Retrieval-Augmented Generation) Pipeline for Medical AI Chatbot
Combines document retrieval with LLM generation
"""

import logging
import os
from typing import Dict, List, Optional, Tuple

import numpy as np

from ..core.vector_store import VectorStore
from .document_processor import MedicalDocumentProcessor
from .embedding_service import MedicalEmbeddingService
from .hybrid_rag import HybridRAGPipeline

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    End-to-end RAG pipeline for medical question answering
    """

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[MedicalEmbeddingService] = None,
        document_processor: Optional[MedicalDocumentProcessor] = None,
        llm_api_key: Optional[str] = None,
        llm_provider: str = "deepseek",
        hybrid_rag: Optional[HybridRAGPipeline] = None,
    ):
        """
        Initialize RAG pipeline

        Args:
            vector_store: Vector database instance
            embedding_service: Embedding service instance
            document_processor: Document processor instance
            llm_api_key: API key for LLM (DeepSeek, OpenAI, etc.)
            llm_provider: LLM provider ('deepseek', 'openai', 'anthropic')
            hybrid_rag: Hybrid RAG pipeline instance for PubMed support
        """
        self.vector_store = vector_store or VectorStore()
        self.embedding_service = embedding_service or MedicalEmbeddingService(
            provider="sentence-transformers"
        )
        self.document_processor = (
            document_processor or MedicalDocumentProcessor()
        )
        self.hybrid_rag = hybrid_rag or HybridRAGPipeline()

        self.llm_provider = llm_provider

        # Map provider names to environment variable names
        provider_key_map = {
            "groq": "GROQ_API_KEY",
            "grok": "XAI_API_KEY",  # xAI Grok (different from Groq!)
            "xai": "XAI_API_KEY",  # Alternative name for xAI Grok
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GOOGLE_API_KEY",  # Gemini uses GOOGLE_API_KEY
        }

        env_key_name = provider_key_map.get(llm_provider.lower(), f"{llm_provider.upper()}_API_KEY")
        self.llm_api_key = llm_api_key or os.getenv(env_key_name)

        # Initialize LLM client
        self._init_llm_client()

    def _init_llm_client(self):
        """Initialize LLM client based on provider"""
        if self.llm_provider == "groq":
            # Groq API (fastest inference, free tier: 30 req/min)
            try:
                from groq import Groq

                self.llm_client = Groq(api_key=self.llm_api_key)
                self.llm_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
                logger.info(f"Initialized Groq LLM client with model {self.llm_model}")
            except ImportError:
                raise ImportError("groq package required. Install with: pip install groq")

        elif self.llm_provider in ["grok", "xai"]:
            # xAI Grok API (OpenAI-compatible, 2M context)
            try:
                import openai

                self.llm_client = openai.OpenAI(
                    api_key=self.llm_api_key,
                    base_url="https://api.x.ai/v1",
                )
                self.llm_model = os.getenv("GROK_MODEL", "grok-4-1-fast-reasoning")
                logger.info(f"Initialized xAI Grok LLM client with model {self.llm_model}")
            except ImportError:
                raise ImportError("openai package required for xAI Grok")

        elif self.llm_provider == "deepseek":
            # DeepSeek API (compatible with OpenAI API)
            try:
                import openai

                self.llm_client = openai.OpenAI(
                    api_key=self.llm_api_key,
                    base_url="https://api.deepseek.com",
                )
                self.llm_model = "deepseek-chat"
                logger.info("Initialized DeepSeek LLM client")
            except ImportError:
                raise ImportError("openai package required for DeepSeek")

        elif self.llm_provider == "openai":
            try:
                import openai

                self.llm_client = openai.OpenAI(api_key=self.llm_api_key)
                self.llm_model = "gpt-4o-mini"  # or gpt-4
                logger.info("Initialized OpenAI LLM client")
            except ImportError:
                raise ImportError("openai package required")

        elif self.llm_provider == "anthropic":
            try:
                import anthropic

                self.llm_client = anthropic.Anthropic(api_key=self.llm_api_key)
                self.llm_model = "claude-3-5-sonnet-20241022"
                logger.info("Initialized Anthropic LLM client")
            except ImportError:
                raise ImportError("anthropic package required")

        elif self.llm_provider == "gemini":
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.llm_api_key)
                self.llm_client = genai
                self.llm_model = "gemini-2.5-flash"  # Fast and free Gemini 2.5 Flash
                logger.info("Initialized Google Gemini LLM client")
            except ImportError:
                raise ImportError("google-generativeai package required for Gemini")

        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")

    def index_document(
        self, text: str, source: str, metadata: Optional[Dict] = None
    ) -> int:
        """
        Index a document into the vector store

        Args:
            text: Document text
            source: Source identifier (URL, file path, etc.)
            metadata: Additional metadata

        Returns:
            Number of chunks indexed
        """
        if not text or not text.strip():
            logger.warning("Empty document provided for indexing")
            return 0

        # Determine category
        category = self.document_processor.categorize_content(text, metadata)

        # Chunk document
        metadata = metadata or {}
        metadata["source"] = source
        chunks = self.document_processor.chunk_document(text, metadata)

        if not chunks:
            logger.warning(f"No chunks created for document: {source}")
            return 0

        # Generate embeddings for chunks
        chunk_texts = [chunk[0] for chunk in chunks]
        embeddings = self.embedding_service.embed_batch(chunk_texts)

        # Store in vector database
        documents_data = []
        for (chunk_text, chunk_metadata), embedding in zip(chunks, embeddings):
            documents_data.append(
                (chunk_text, embedding, chunk_metadata, source, category)
            )

        doc_ids = self.vector_store.add_documents_batch(documents_data)

        logger.info(
            f"Indexed {len(doc_ids)} chunks from document: {source} (category: {category})"
        )
        return len(doc_ids)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        use_hybrid: bool = True,
        use_query_expansion: bool = True,
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a query using HybridRAG

        Args:
            query: User query
            top_k: Number of documents to retrieve
            category: Filter by category (optional)
            use_hybrid: Use hybrid search (semantic + keyword)
            use_query_expansion: Expand query with medical synonyms

        Returns:
            List of relevant documents with metadata
        """
        # Use HybridRAG pipeline (includes PubMed + Scholar)
        if self.hybrid_rag:
            documents = self.hybrid_rag.retrieve(
                query=query,
                top_k=top_k,
                use_cag=True,
                use_qdrant=True,
                use_pubmed=True,  # Enable PubMed search
                use_scholar=True,  # Enable Google Scholar search
                score_threshold=0.5,
            )
            logger.info(f"Retrieved {len(documents)} documents via HybridRAG for query: {query[:50]}...")
            return documents

        # Fallback to legacy retrieval
        # Generate query embedding
        if use_query_expansion:
            query_embeddings = self.embedding_service.embed_with_expansion(query)
            # Use the first (original) embedding for now
            # TODO: Implement multi-query fusion
            query_embedding = query_embeddings[0]
        else:
            query_embedding = self.embedding_service.embed(query)

        # Retrieve documents
        if use_hybrid:
            documents = self.vector_store.hybrid_search(
                query_embedding=query_embedding,
                query_text=query,
                top_k=top_k,
                category=category,
                semantic_weight=0.7,
            )
        else:
            documents = self.vector_store.search_similar(
                query_embedding=query_embedding,
                top_k=top_k,
                category=category,
                min_similarity=0.5,
            )

        logger.info(f"Retrieved {len(documents)} documents for query: {query[:50]}...")
        return documents

    def generate_answer(
        self,
        query: str,
        context_docs: List[Dict],
        include_citations: bool = True,
        max_tokens: int = 800,
    ) -> Dict:
        """
        Generate answer using LLM with retrieved context

        Args:
            query: User query
            context_docs: Retrieved context documents
            include_citations: Include source citations
            max_tokens: Maximum tokens in response

        Returns:
            Dictionary with answer, citations, and metadata
        """
        # Build context from retrieved documents
        context_parts = []
        citations = []

        for idx, doc in enumerate(context_docs, 1):
            # Truncate content to max 1000 chars to avoid token limits
            content = doc['content']
            if len(content) > 1000:
                content = content[:1000] + "..."
            context_parts.append(f"[{idx}] {content}")

            # Build citation with full metadata
            citation = {
                "id": idx,
                "source": doc["source"],
                "category": doc["category"],
                "similarity": doc.get("hybrid_score", doc.get("similarity", 0)),
            }

            # Add PubMed-specific metadata if available
            if "metadata" in doc and doc["metadata"]:
                metadata = doc["metadata"]
                if "pmid" in metadata:
                    citation["pmid"] = metadata["pmid"]
                    citation["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{metadata['pmid']}/"
                if "title" in metadata:
                    citation["title"] = metadata["title"]

            citations.append(citation)

        context_text = "\n\n".join(context_parts)

        # Build prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(query, context_text, include_citations)

        # Generate response
        try:
            if self.llm_provider in ["groq", "grok", "xai", "deepseek", "openai"]:
                # Groq, xAI Grok, DeepSeek, and OpenAI use same OpenAI-compatible API
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=0.3,  # Lower temperature for medical accuracy
                )
                answer = response.choices[0].message.content

            elif self.llm_provider == "anthropic":
                response = self.llm_client.messages.create(
                    model=self.llm_model,
                    max_tokens=max_tokens,
                    temperature=0.3,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                answer = response.content[0].text

            elif self.llm_provider == "gemini":
                # Combine system and user prompts for Gemini
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                model = self.llm_client.GenerativeModel(
                    self.llm_model,  # Use configured model name
                    generation_config={
                        "temperature": 0.3,
                        "max_output_tokens": max_tokens,
                    }
                )
                response = model.generate_content(full_prompt)
                answer = response.text

            else:
                raise ValueError(f"Unknown provider: {self.llm_provider}")

            logger.info("Generated answer successfully")

            # Compute confidence score based on retrieval quality
            confidence = self._compute_confidence(context_docs)

            return {
                "answer": answer,
                "citations": citations if include_citations else [],
                "confidence": confidence,
                "num_sources": len(context_docs),
            }

        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return {
                "answer": "I apologize, but I'm unable to generate a response at this time. Please consult with a healthcare professional for medical guidance.",
                "citations": [],
                "confidence": 0.0,
                "error": str(e),
            }

    def _build_system_prompt(self) -> str:
        """Build system prompt for LLM"""
        return """You are a medical AI assistant with expertise in clinical medicine, designed to support healthcare professionals in ICU settings.

Your responsibilities:
1. Provide evidence-based medical information from the provided context
2. Explain clinical concepts clearly and accurately
3. Include relevant citations when available
4. Acknowledge uncertainty when information is insufficient
5. Always remind users that this is decision support, not a replacement for clinical judgment

Guidelines:
- ONLY use information from the provided context documents
- If the context doesn't contain relevant information, clearly state this
- Use medical terminology appropriately, but explain complex terms
- Be concise but comprehensive
- Always include appropriate medical disclaimers
- NEVER provide specific treatment recommendations without context
- Flag any emergency situations that require immediate attention

Remember: You are a support tool for healthcare professionals, not a replacement for medical expertise."""

    def _build_user_prompt(
        self, query: str, context: str, include_citations: bool
    ) -> str:
        """Build user prompt with context"""
        prompt = f"""Based on the following medical knowledge base context, please answer the question.

CONTEXT:
{context}

QUESTION:
{query}

INSTRUCTIONS:
- Answer based ONLY on the provided context
- Be accurate and evidence-based
"""

        if include_citations:
            prompt += "- Reference sources using [1], [2], etc.\n"

        prompt += """- If the context doesn't contain relevant information, say so clearly
- Include appropriate medical disclaimers
- Keep the response focused and professional

ANSWER:"""

        return prompt

    def _compute_confidence(self, context_docs: List[Dict]) -> float:
        """
        Compute confidence score based on retrieval quality

        Args:
            context_docs: Retrieved documents

        Returns:
            Confidence score (0-1)
        """
        if not context_docs:
            return 0.0

        # Average similarity/score
        scores = [
            doc.get("hybrid_score", doc.get("similarity", 0))
            for doc in context_docs
        ]
        avg_score = sum(scores) / len(scores)

        # Adjust based on number of sources
        num_sources = len(context_docs)
        source_factor = min(1.0, num_sources / 3)  # More sources = more confidence

        confidence = avg_score * 0.7 + source_factor * 0.3
        return float(confidence)

    def query(
        self,
        question: str,
        top_k: int = 5,
        category: Optional[str] = None,
        include_citations: bool = True,
    ) -> Dict:
        """
        End-to-end RAG query: retrieve + generate

        Args:
            question: User question
            top_k: Number of documents to retrieve
            category: Filter by category
            include_citations: Include source citations

        Returns:
            Dictionary with answer, citations, and metadata
        """
        # Retrieve relevant documents
        context_docs = self.retrieve(
            query=question,
            top_k=top_k,
            category=category,
            use_hybrid=True,
            use_query_expansion=True,
        )

        if not context_docs:
            return {
                "answer": "I don't have enough information in my knowledge base to answer this question accurately. Please consult with a healthcare professional or refer to established clinical guidelines.",
                "citations": [],
                "confidence": 0.0,
                "num_sources": 0,
            }

        # Generate answer
        result = self.generate_answer(
            query=question,
            context_docs=context_docs,
            include_citations=include_citations,
        )

        return result

    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        total_docs = self.vector_store.get_document_count()

        # Get counts by category
        categories = ["drug", "disease", "guideline", "protocol", "general"]
        category_counts = {}
        for cat in categories:
            category_counts[cat] = self.vector_store.get_document_count(category=cat)

        return {
            "total_documents": total_docs,
            "by_category": category_counts,
            "embedding_dimension": self.embedding_service.get_embedding_dimension(),
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
        }
