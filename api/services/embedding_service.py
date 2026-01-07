"""
Embedding Service for RAG System
Supports both OpenAI and local embedding models
"""

import logging
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings
    Supports: OpenAI, sentence-transformers (local), DeepSeek
    """

    def __init__(
        self,
        provider: str = "sentence-transformers",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize embedding service

        Args:
            provider: 'openai', 'sentence-transformers', or 'deepseek'
            model_name: Specific model name (optional)
            api_key: API key for cloud providers (optional)
        """
        self.provider = provider
        self.api_key = api_key

        if provider == "sentence-transformers":
            # Local embedding model (good for on-premise deployment)
            try:
                from sentence_transformers import SentenceTransformer

                self.model_name = model_name or "all-MiniLM-L6-v2"
                self.model = SentenceTransformer(self.model_name)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                logger.info(
                    f"Loaded sentence-transformers model: {self.model_name} (dim={self.embedding_dim})"
                )
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. Install with: pip install sentence-transformers"
                )

        elif provider == "openai":
            # OpenAI embeddings (high quality, cloud-based)
            try:
                import openai

                self.model_name = model_name or "text-embedding-3-small"
                self.embedding_dim = 1536
                openai.api_key = api_key
                logger.info(f"Using OpenAI embeddings: {self.model_name}")
            except ImportError:
                raise ImportError(
                    "openai not installed. Install with: pip install openai"
                )

        elif provider == "deepseek":
            # DeepSeek API (if they provide embeddings)
            # Note: DeepSeek primarily provides LLM inference, not embeddings
            # This is a placeholder for future integration
            logger.warning(
                "DeepSeek embeddings not yet supported, falling back to sentence-transformers"
            )
            self._fallback_to_sentence_transformers(model_name)

        else:
            raise ValueError(f"Unknown embedding provider: {provider}")

    def _fallback_to_sentence_transformers(self, model_name: Optional[str] = None):
        """Fallback to local sentence-transformers"""
        try:
            from sentence_transformers import SentenceTransformer

            self.provider = "sentence-transformers"
            self.model_name = model_name or "all-MiniLM-L6-v2"
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Fallback to sentence-transformers: {self.model_name}")
        except ImportError:
            raise ImportError("sentence-transformers required for fallback")

    def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text

        Args:
            text: Input text

        Returns:
            Embedding vector as numpy array
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if self.provider == "sentence-transformers":
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding

        elif self.provider == "openai":
            import openai

            try:
                response = openai.embeddings.create(input=[text], model=self.model_name)
                embedding = np.array(response.data[0].embedding)
                return embedding
            except Exception as e:
                logger.error(f"OpenAI embedding failed: {e}")
                raise

        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of input texts
            batch_size: Batch size for processing

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Remove empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if len(valid_texts) != len(texts):
            logger.warning(
                f"Removed {len(texts) - len(valid_texts)} empty texts from batch"
            )

        if not valid_texts:
            return []

        if self.provider == "sentence-transformers":
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=len(valid_texts) > 100,
            )
            return [emb for emb in embeddings]

        elif self.provider == "openai":
            import openai

            embeddings = []
            try:
                # OpenAI has a limit on batch size, process in chunks
                for i in range(0, len(valid_texts), batch_size):
                    batch = valid_texts[i : i + batch_size]
                    response = openai.embeddings.create(
                        input=batch, model=self.model_name
                    )
                    batch_embeddings = [
                        np.array(item.embedding) for item in response.data
                    ]
                    embeddings.extend(batch_embeddings)
                    logger.info(
                        f"Processed {len(embeddings)}/{len(valid_texts)} embeddings"
                    )
                return embeddings
            except Exception as e:
                logger.error(f"OpenAI batch embedding failed: {e}")
                raise

        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service"""
        return self.embedding_dim

    def compute_similarity(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity (0 to 1)
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)


# Medical-specific embedding utilities
class MedicalEmbeddingService(EmbeddingService):
    """
    Extended embedding service with medical domain enhancements
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Medical synonyms for query expansion
        self.medical_synonyms = {
            "heart attack": ["myocardial infarction", "MI", "AMI"],
            "stroke": ["cerebrovascular accident", "CVA"],
            "high blood pressure": ["hypertension", "HTN"],
            "diabetes": ["diabetes mellitus", "DM", "hyperglycemia"],
            "infection": ["sepsis", "septicemia", "bacteremia"],
            "kidney failure": ["renal failure", "acute kidney injury", "AKI"],
            "liver failure": ["hepatic failure", "liver disease"],
            "breathing problem": ["respiratory distress", "dyspnea"],
            "chest pain": ["angina", "thoracic pain"],
            "fever": ["pyrexia", "hyperthermia"],
        }

    def expand_medical_query(self, query: str) -> List[str]:
        """
        Expand query with medical synonyms

        Args:
            query: Original query

        Returns:
            List of query variations including synonyms
        """
        queries = [query]
        query_lower = query.lower()

        # Add synonym variations
        for lay_term, medical_terms in self.medical_synonyms.items():
            if lay_term in query_lower:
                for medical_term in medical_terms:
                    expanded_query = query_lower.replace(lay_term, medical_term)
                    queries.append(expanded_query)

        # Deduplicate
        queries = list(set(queries))
        logger.info(f"Expanded query to {len(queries)} variations")
        return queries

    def embed_with_expansion(
        self, query: str, include_expansion: bool = True
    ) -> List[np.ndarray]:
        """
        Generate embeddings with medical term expansion

        Args:
            query: Original query
            include_expansion: Whether to include expanded queries

        Returns:
            List of embeddings (original + expansions)
        """
        if include_expansion:
            queries = self.expand_medical_query(query)
            embeddings = self.embed_batch(queries)
            return embeddings
        else:
            embedding = self.embed(query)
            return [embedding]
