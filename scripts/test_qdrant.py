#!/usr/bin/env python3
"""
Test Qdrant Cloud Connection
Verifies Qdrant cluster connectivity and basic operations
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_qdrant_connection():
    """Test Qdrant connection"""
    print("=" * 60)
    print("Testing Qdrant Cloud Connection...")
    print("=" * 60)

    try:
        from qdrant_client import QdrantClient

        url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")

        if not url or not api_key:
            print("❌ QDRANT_URL or QDRANT_API_KEY not found in environment")
            print("\n💡 Setup instructions:")
            print("1. Go to: https://cloud.qdrant.io/")
            print("2. Create a free cluster (1GB)")
            print("3. Copy URL and API key to .env")
            print("   QDRANT_URL=https://xxxxx.cloud.qdrant.io")
            print("   QDRANT_API_KEY=your_key")
            return False

        print(f"✓ Qdrant URL: {url}")
        print(f"✓ API Key: {api_key[:8]}...{api_key[-4:]}")

        # Connect to Qdrant
        print("\nConnecting to Qdrant Cloud...")
        client = QdrantClient(url=url, api_key=api_key)
        print("✓ Connected to Qdrant")

        # Get cluster info
        collections = client.get_collections()
        print(f"\n✓ Cluster accessible")
        print(f"  Existing collections: {len(collections.collections)}")

        if collections.collections:
            print("\n  Collections:")
            for coll in collections.collections:
                print(f"    - {coll.name}")

        return True

    except ImportError:
        print("❌ qdrant-client not installed")
        print("   Install with: pip install qdrant-client")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("- Check QDRANT_URL format (must start with https://)")
        print("- Verify API key is correct")
        print("- Ensure cluster is running (check Qdrant Cloud dashboard)")
        return False


def test_create_collection():
    """Test creating a collection"""
    print("\n" + "=" * 60)
    print("Testing Collection Creation...")
    print("=" * 60)

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams

        url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")
        collection_name = "test_collection"

        client = QdrantClient(url=url, api_key=api_key)

        # Delete collection if exists
        try:
            client.delete_collection(collection_name)
            print(f"✓ Deleted existing collection: {collection_name}")
        except:
            pass

        # Create collection
        print(f"\nCreating collection: {collection_name}")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,  # sentence-transformers dimension
                distance=Distance.COSINE,
            ),
        )
        print("✓ Collection created")

        # Verify collection exists
        collection_info = client.get_collection(collection_name)
        print(f"\n✓ Collection info:")
        print(f"  Name: {collection_info.name}")
        print(f"  Vector size: {collection_info.config.params.vectors.size}")
        print(f"  Distance: {collection_info.config.params.vectors.distance}")
        print(f"  Points count: {collection_info.points_count}")

        # Cleanup
        client.delete_collection(collection_name)
        print(f"\n✓ Test collection deleted")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_vector_operations():
    """Test vector insert and search"""
    print("\n" + "=" * 60)
    print("Testing Vector Operations...")
    print("=" * 60)

    try:
        import numpy as np
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, PointStruct, VectorParams

        url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")
        collection_name = "test_vectors"

        client = QdrantClient(url=url, api_key=api_key)

        # Create collection
        try:
            client.delete_collection(collection_name)
        except:
            pass

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        print(f"✓ Created collection: {collection_name}")

        # Insert test vectors
        print("\nInserting test vectors...")
        test_docs = [
            {
                "id": 1,
                "vector": np.random.rand(384).tolist(),
                "payload": {
                    "content": "Sepsis is a life-threatening condition",
                    "category": "disease",
                },
            },
            {
                "id": 2,
                "vector": np.random.rand(384).tolist(),
                "payload": {
                    "content": "SOFA score measures organ dysfunction",
                    "category": "scoring",
                },
            },
            {
                "id": 3,
                "vector": np.random.rand(384).tolist(),
                "payload": {
                    "content": "Acute kidney injury KDIGO criteria",
                    "category": "guideline",
                },
            },
        ]

        points = [
            PointStruct(id=doc["id"], vector=doc["vector"], payload=doc["payload"])
            for doc in test_docs
        ]

        client.upsert(collection_name=collection_name, points=points)
        print(f"✓ Inserted {len(points)} vectors")

        # Search
        print("\nSearching for similar vectors...")
        query_vector = np.random.rand(384).tolist()

        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=3,
        )

        print(f"\n✓ Search results:")
        for i, result in enumerate(results, 1):
            print(f"\n  [{i}] Score: {result.score:.4f}")
            print(f"      Content: {result.payload['content']}")
            print(f"      Category: {result.payload['category']}")

        # Cleanup
        client.delete_collection(collection_name)
        print(f"\n✓ Test collection deleted")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all Qdrant tests"""
    print("\n" + "🧪 QDRANT TEST SUITE" + "\n")

    results = {}

    # Test 1: Connection
    results["connection"] = test_qdrant_connection()

    if results["connection"]:
        # Test 2: Create collection
        results["collection"] = test_create_collection()

        # Test 3: Vector operations
        results["vectors"] = test_vector_operations()
    else:
        print("\n⚠️ Skipping other tests due to connection failure")
        results["collection"] = False
        results["vectors"] = False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed!")
        print("\nQdrant Cloud is ready to use.")
        print("\nNext steps:")
        print("1. Run: python scripts/init_qdrant_store.py")
        print("2. Run: python scripts/seed_medical_knowledge.py")
        return 0
    else:
        print("\n⚠️ Some tests failed.")
        print("\nTroubleshooting:")
        print("- Verify QDRANT_URL and QDRANT_API_KEY in .env")
        print("- Check Qdrant Cloud dashboard: https://cloud.qdrant.io/")
        print("- Ensure cluster is running")
        return 1


if __name__ == "__main__":
    sys.exit(main())
