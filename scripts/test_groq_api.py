#!/usr/bin/env python3
"""
Test Groq API Connection
Verifies Groq API key and tests chat + vision capabilities
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_groq_chat():
    """Test Groq chat API"""
    print("=" * 60)
    print("Testing Groq Chat API...")
    print("=" * 60)

    try:
        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY not found in environment")
            print("   Add it to .env file: GROQ_API_KEY=your_key_here")
            return False

        print(f"✓ API Key found: {api_key[:8]}...{api_key[-4:]}")

        # Initialize client
        client = Groq(api_key=api_key)
        print("✓ Groq client initialized")

        # Test chat completion
        model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
        print(f"✓ Using model: {model}")

        print("\nSending test message...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful medical AI assistant.",
                },
                {
                    "role": "user",
                    "content": "What is sepsis in one sentence?",
                },
            ],
            max_tokens=100,
            temperature=0.3,
        )

        print("\n✅ Response received:")
        print("-" * 60)
        print(response.choices[0].message.content)
        print("-" * 60)

        print(f"\n✓ Model: {response.model}")
        print(f"✓ Finish reason: {response.choices[0].finish_reason}")
        print(f"✓ Usage: {response.usage}")

        return True

    except ImportError:
        print("❌ groq package not installed")
        print("   Install with: pip install groq")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_groq_vision():
    """Test Groq vision API"""
    print("\n" + "=" * 60)
    print("Testing Groq Vision API...")
    print("=" * 60)

    try:
        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY not found")
            return False

        client = Groq(api_key=api_key)
        vision_model = os.getenv("GROQ_VISION_MODEL", "llama-3.2-11b-vision-preview")
        print(f"✓ Using vision model: {vision_model}")

        # Test with a sample medical image URL (chest X-ray)
        print("\nTesting with sample medical image...")
        print("(Using a public chest X-ray image)")

        # Public sample chest X-ray
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Chest_radiograph_in_influenza_and_Haemophilus_influenzae%2C_posteroanterior%2C_annotated.jpg/440px-Chest_radiograph_in_influenza_and_Haemophilus_influenzae%2C_posteroanterior%2C_annotated.jpg"

        response = client.chat.completions.create(
            model=vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this medical image briefly.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                    ],
                }
            ],
            max_tokens=200,
        )

        print("\n✅ Vision response received:")
        print("-" * 60)
        print(response.choices[0].message.content)
        print("-" * 60)

        return True

    except Exception as e:
        print(f"⚠️ Vision API test failed: {e}")
        print("   This is optional - chat API is more important")
        return False


def test_llm_provider():
    """Test LLM provider service"""
    print("\n" + "=" * 60)
    print("Testing LLM Provider Service...")
    print("=" * 60)

    try:
        from api.services.llm_provider import LLMOrchestrator

        print("✓ LLM Provider module loaded")

        # Initialize orchestrator
        llm = LLMOrchestrator()
        print(f"✓ Orchestrator initialized")

        # Get status
        status = llm.get_status()
        print(f"\nStatus:")
        print(f"  Primary: {status['primary']}")
        print(f"  Fallback: {status['fallback']}")
        print(f"  Groq available: {status['groq_available']}")
        print(f"  HF available: {status['hf_available']}")
        print(f"  Rate limit remaining: {status['rate_limit_remaining']}")

        # Test generation
        print("\nTesting generation...")
        result = llm.generate(
            messages=[
                {
                    "role": "user",
                    "content": "What is acute kidney injury? Answer in one sentence.",
                }
            ],
            max_tokens=100,
        )

        print("\n✅ Generation result:")
        print(f"  Provider: {result['provider']}")
        print(f"  Model: {result['model']}")
        print(f"  Response: {result['content'][:100]}...")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all Groq tests"""
    print("\n" + "🧪 GROQ API TEST SUITE" + "\n")

    results = {}

    # Test 1: Chat API
    results["chat"] = test_groq_chat()

    # Test 2: Vision API (optional)
    results["vision"] = test_groq_vision()

    # Test 3: LLM Provider Service
    results["provider"] = test_llm_provider()

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
        print("\nNext steps:")
        print("1. Test Qdrant: python scripts/test_qdrant.py")
        print("2. Test PII Masker: python scripts/test_pii_masker.py")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check errors above.")
        print("\nTroubleshooting:")
        print("- Verify GROQ_API_KEY in .env file")
        print("- Get API key from: https://console.groq.com/")
        print("- Check network connection")
        return 1


if __name__ == "__main__":
    sys.exit(main())
