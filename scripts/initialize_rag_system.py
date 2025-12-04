"""
Initialize RAG System
- Setup pgvector extension
- Create sample knowledge base
- Index documents
- Test system
"""

import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

from api.core.vector_store import VectorStore
from api.services.embedding_service import MedicalEmbeddingService
from api.services.knowledge_loader import MedicalKnowledgeLoader
from api.services.rag_pipeline import RAGPipeline

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Initialize RAG system"""
    logger.info("=" * 60)
    logger.info("Initializing Medical AI RAG System")
    logger.info("=" * 60)

    # Step 1: Create sample knowledge base
    logger.info("\n[1/5] Creating sample medical knowledge base...")
    loader = MedicalKnowledgeLoader()
    loader.create_sample_knowledge_base()

    # Step 2: Initialize vector store (creates pgvector extension and tables)
    logger.info("\n[2/5] Setting up vector store with pgvector...")
    try:
        vector_store = VectorStore()
        logger.info("✓ Vector store initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize vector store: {e}")
        logger.error(
            "Make sure PostgreSQL is running and DATABASE_URL is set correctly"
        )
        return

    # Step 3: Initialize embedding service
    logger.info("\n[3/5] Initializing embedding service...")
    try:
        embedding_service = MedicalEmbeddingService(provider="sentence-transformers")
        logger.info(
            f"✓ Embedding service initialized (dimension: {embedding_service.get_embedding_dimension()})"
        )
    except Exception as e:
        logger.error(f"✗ Failed to initialize embedding service: {e}")
        return

    # Step 4: Initialize RAG pipeline
    logger.info("\n[4/5] Initializing RAG pipeline...")
    llm_provider = os.getenv("LLM_PROVIDER", "deepseek")
    try:
        # Note: LLM API key should be set in environment variables
        rag = RAGPipeline(
            vector_store=vector_store,
            embedding_service=embedding_service,
            llm_provider=llm_provider,
        )
        logger.info(f"✓ RAG pipeline initialized with {llm_provider}")
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"⚠ RAG pipeline initialization failed: {error_msg}")
        logger.info("Creating retrieval-only pipeline...")
        # Create a minimal pipeline without LLM for retrieval-only
        rag = type('obj', (object,), {
            'vector_store': vector_store,
            'embedding_service': embedding_service,
            'document_processor': None,
            'llm_api_key': None,
            'index_document': lambda text, source, metadata=None: 0,
            'retrieve': lambda query, **kwargs: [],
            'get_stats': lambda: {'error': error_msg}
        })()
        logger.info("You can still test vector store and embeddings separately")

    # Step 5: Index documents
    logger.info("\n[5/5] Indexing medical knowledge base...")
    documents = loader.load_directory()

    if not documents:
        logger.warning("No documents found to index")
        return

    logger.info(f"Found {len(documents)} documents to index")

    total_chunks = 0
    for doc in documents:
        try:
            num_chunks = rag.index_document(
                text=doc["content"], source=doc["source"], metadata=doc["metadata"]
            )
            total_chunks += num_chunks
            logger.info(f"  ✓ Indexed: {doc['source']} ({num_chunks} chunks)")
        except Exception as e:
            logger.error(f"  ✗ Failed to index {doc['source']}: {e}")

    logger.info(f"\n✓ Indexing complete: {total_chunks} total chunks indexed")

    # Display statistics
    logger.info("\n" + "=" * 60)
    logger.info("RAG System Statistics")
    logger.info("=" * 60)
    try:
        stats = rag.get_stats()
        for key, value in stats.items():
            if isinstance(value, dict):
                logger.info(f"\n{key}:")
                for sub_key, sub_value in value.items():
                    logger.info(f"  {sub_key}: {sub_value}")
            else:
                logger.info(f"{key}: {value}")
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")

    # Test query
    logger.info("\n" + "=" * 60)
    logger.info("Testing RAG System")
    logger.info("=" * 60)

    test_query = "What are the criteria for diagnosing sepsis?"
    logger.info(f"\nTest Query: {test_query}")

    try:
        # Test retrieval only (doesn't require LLM)
        logger.info("\n[Retrieval Test]")
        docs = rag.retrieve(test_query, top_k=3)
        logger.info(f"Retrieved {len(docs)} relevant documents:")
        for idx, doc in enumerate(docs, 1):
            logger.info(
                f"\n  [{idx}] Source: {doc['source']} (score: {doc.get('hybrid_score', doc.get('similarity', 0)):.3f})"
            )
            logger.info(f"      Category: {doc['category']}")
            logger.info(f"      Preview: {doc['content'][:150]}...")

        # Test full RAG (requires LLM API key)
        if rag.llm_api_key:
            logger.info("\n[Full RAG Test]")
            result = rag.query(test_query, top_k=3)
            logger.info(f"\nAnswer:\n{result['answer']}")
            logger.info(f"\nConfidence: {result['confidence']:.2f}")
            logger.info(f"Sources: {result['num_sources']}")
        else:
            logger.warning(
                "\n⚠ LLM API key not set. Set DEEPSEEK_API_KEY (or OPENAI_API_KEY) to test full RAG."
            )

    except Exception as e:
        logger.error(f"Test failed: {e}")

    logger.info("\n" + "=" * 60)
    logger.info("Initialization Complete!")
    logger.info("=" * 60)
    logger.info(
        "\nNext steps:\n"
        "1. Set LLM API key in .env file (DEEPSEEK_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY)\n"
        "2. Add more medical documents to data/medical_knowledge/\n"
        "3. Update the Streamlit chatbot to use RAG (apps/pages/chatbot.py)\n"
        "4. Test with various medical queries\n"
    )


if __name__ == "__main__":
    main()
