#!/usr/bin/env python3
"""
Initialize Qdrant Vector Store with Medical Knowledge

This script:
1. Loads medical knowledge from CAG cache
2. Generates embeddings using sentence-transformers
3. Uploads documents to Qdrant Cloud
4. Verifies the collection

Usage:
    python scripts/initialize_qdrant.py

Environment Variables Required:
    QDRANT_URL: Qdrant Cloud URL (e.g., https://xyz.cloud.qdrant.io)
    QDRANT_API_KEY: Qdrant API key
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.core.cag_cache import CAGCache
from api.core.qdrant_store import QdrantVectorStore
from api.services.embedding_service import EmbeddingService

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Initialize Qdrant with medical knowledge."""

    print("=" * 60)
    print("Qdrant Vector Store Initialization")
    print("=" * 60)

    # Check environment variables
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        print("\n❌ ERROR: Qdrant credentials not configured")
        print("\nPlease set environment variables:")
        print("  export QDRANT_URL='https://your-cluster.cloud.qdrant.io'")
        print("  export QDRANT_API_KEY='your-api-key'")
        print("\nOr create a .env file with:")
        print("  QDRANT_URL=https://your-cluster.cloud.qdrant.io")
        print("  QDRANT_API_KEY=your-api-key")
        sys.exit(1)

    print(f"\n✓ Qdrant URL: {qdrant_url}")
    print(f"✓ API Key: {'*' * 20}{qdrant_api_key[-8:]}")

    # Initialize components
    print("\n📦 Initializing components...")

    try:
        cag_cache = CAGCache()
        print(f"  ✓ CAG Cache loaded ({len(cag_cache.MEDICAL_KNOWLEDGE)} documents)")
    except Exception as e:
        print(f"  ❌ Failed to load CAG cache: {e}")
        sys.exit(1)

    try:
        embedding_service = EmbeddingService(provider="sentence-transformers")
        print(f"  ✓ Embedding service loaded (model: {embedding_service.model_name})")
    except Exception as e:
        print(f"  ❌ Failed to load embedding service: {e}")
        sys.exit(1)

    try:
        qdrant_store = QdrantVectorStore(
            url=qdrant_url, api_key=qdrant_api_key, collection_name="medical_knowledge"
        )
        print(f"  ✓ Qdrant client connected")
    except Exception as e:
        print(f"  ❌ Failed to connect to Qdrant: {e}")
        sys.exit(1)

    # Prepare documents
    print("\n📝 Preparing documents...")

    documents = []
    for key, data in cag_cache.MEDICAL_KNOWLEDGE.items():
        documents.append(
            {
                "content": data["content"],
                "source": "CAG Cache",
                "category": data.get("category", "general"),
                "metadata": {
                    "key": key,
                    "keywords": data.get("keywords", []),
                    "priority": data.get("priority", 5),
                },
            }
        )

    print(f"  ✓ Prepared {len(documents)} documents")

    # Generate embeddings
    print("\n🔢 Generating embeddings...")

    try:
        texts = [doc["content"] for doc in documents]
        embeddings = embedding_service.embed_batch(texts, batch_size=16)

        if not embeddings:
            print("  ❌ Failed to generate embeddings")
            sys.exit(1)

        print(f"  ✓ Generated {len(embeddings)} embeddings")

        # Add embeddings to documents
        for doc, embedding in zip(documents, embeddings):
            # Convert numpy array to list if needed
            if hasattr(embedding, "tolist"):
                doc["embedding"] = embedding.tolist()
            else:
                doc["embedding"] = embedding

    except Exception as e:
        print(f"  ❌ Failed to generate embeddings: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Upload to Qdrant
    print("\n☁️  Uploading to Qdrant...")

    try:
        count = qdrant_store.add_documents(documents, batch_size=50)
        print(f"  ✓ Uploaded {count} documents")
    except Exception as e:
        print(f"  ❌ Failed to upload documents: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Verify collection
    print("\n✓ Verifying collection...")

    try:
        info = qdrant_store.get_collection_info()
        if info:
            print(f"  ✓ Collection: {info['name']}")
            print(f"  ✓ Points count: {info['points_count']}")
            print(f"  ✓ Vectors count: {info['vectors_count']}")
            print(f"  ✓ Status: {info['status']}")
        else:
            print("  ⚠️  Could not retrieve collection info")
    except Exception as e:
        print(f"  ⚠️  Verification failed: {e}")

    # Test search
    print("\n🔍 Testing search...")

    try:
        test_query = "What is sepsis?"
        test_embedding = embedding_service.embed(test_query)

        if hasattr(test_embedding, "tolist"):
            test_embedding = test_embedding.tolist()

        results = qdrant_store.search(
            query_embedding=test_embedding, top_k=3, score_threshold=0.3
        )

        print(f"  ✓ Query: '{test_query}'")
        print(f"  ✓ Found {len(results)} results:")

        for i, result in enumerate(results, 1):
            print(f"\n  [{i}] Score: {result['score']:.3f}")
            print(f"      Category: {result['category']}")
            print(f"      Content: {result['content'][:100]}...")

    except Exception as e:
        print(f"  ❌ Search test failed: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ Qdrant initialization complete!")
    print("=" * 60)
    print("\nYou can now use the hybrid RAG pipeline in your application.")
    print()


if __name__ == "__main__":
    main()
