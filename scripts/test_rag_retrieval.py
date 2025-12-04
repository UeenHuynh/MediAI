"""
Test RAG Retrieval System (without LLM)
Tests document indexing and semantic search
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.core.vector_store import VectorStore
from api.services.document_processor import MedicalDocumentProcessor
from api.services.embedding_service import MedicalEmbeddingService
from api.services.knowledge_loader import MedicalKnowledgeLoader

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Test RAG retrieval without LLM"""
    print("=" * 70)
    print("Testing RAG Retrieval System (No LLM Required)")
    print("=" * 70)

    # Initialize components
    print("\n[1/4] Initializing components...")
    vector_store = VectorStore()
    embedding_service = MedicalEmbeddingService(provider="sentence-transformers")
    document_processor = MedicalDocumentProcessor()
    loader = MedicalKnowledgeLoader()

    print("✓ Components initialized")
    print(f"  - Embedding dimension: {embedding_service.get_embedding_dimension()}")

    # Load documents
    print("\n[2/4] Loading medical knowledge base...")
    documents = loader.load_directory()
    print(f"✓ Loaded {len(documents)} documents")

    # Index documents
    print("\n[3/4] Indexing documents...")
    total_chunks = 0

    for doc in documents:
        try:
            # Categorize
            category = document_processor.categorize_content(
                doc["content"], doc["metadata"]
            )

            # Chunk
            chunks = document_processor.chunk_document(
                doc["content"], doc["metadata"]
            )

            if not chunks:
                print(f"  ⚠ No chunks for {doc['source']}")
                continue

            # Generate embeddings
            chunk_texts = [chunk[0] for chunk in chunks]
            embeddings = embedding_service.embed_batch(chunk_texts)

            # Store
            documents_data = []
            for (chunk_text, chunk_metadata), embedding in zip(chunks, embeddings):
                documents_data.append(
                    (chunk_text, embedding, chunk_metadata, doc["source"], category)
                )

            doc_ids = vector_store.add_documents_batch(documents_data)
            total_chunks += len(doc_ids)

            print(f"  ✓ {doc['source']}: {len(doc_ids)} chunks (category: {category})")

        except Exception as e:
            print(f"  ✗ Failed to index {doc['source']}: {e}")

    print(f"\n✓ Indexing complete: {total_chunks} chunks indexed")

    # Test queries
    print("\n[4/4] Testing retrieval...")
    print("=" * 70)

    test_queries = [
        "What are the criteria for diagnosing sepsis?",
        "How do I manage septic shock?",
        "What is the recommended dosing for norepinephrine?",
        "What factors increase mortality risk in ICU?",
    ]

    for query in test_queries:
        print(f"\n📋 Query: {query}")
        print("-" * 70)

        try:
            # Generate query embedding
            query_embedding = embedding_service.embed(query)

            # Search
            results = vector_store.hybrid_search(
                query_embedding=query_embedding,
                query_text=query,
                top_k=3,
                semantic_weight=0.7,
            )

            if results:
                for idx, doc in enumerate(results, 1):
                    print(f"\n  [{idx}] Score: {doc['hybrid_score']:.3f}")
                    print(f"      Source: {doc['source']}")
                    print(f"      Category: {doc['category']}")
                    print(f"      Preview: {doc['content'][:200]}...")
            else:
                print("  No results found")

        except Exception as e:
            print(f"  ✗ Search failed: {e}")

    # Statistics
    print("\n" + "=" * 70)
    print("RAG System Statistics")
    print("=" * 70)

    total_docs = vector_store.get_document_count()
    print(f"Total documents: {total_docs}")

    categories = ["drug", "disease", "guideline", "protocol", "general"]
    print("\nBy category:")
    for cat in categories:
        count = vector_store.get_document_count(category=cat)
        if count > 0:
            print(f"  - {cat}: {count}")

    print("\n" + "=" * 70)
    print("✓ RAG Retrieval Test Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Add LLM API key to test full RAG generation")
    print("2. Add more medical documents to knowledge base")
    print("3. Test via Streamlit chatbot interface")


if __name__ == "__main__":
    main()
