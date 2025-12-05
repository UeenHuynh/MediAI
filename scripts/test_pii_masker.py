#!/usr/bin/env python3
"""
Test PII Masking Service
Verifies PII detection and masking functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_pii_masking():
    """Test PII masking with various inputs"""
    print("=" * 60)
    print("Testing PII Masking Service...")
    print("=" * 60)

    try:
        from api.services.pii_masker import PIIMasker

        print("✓ PII Masker module loaded")

        # Initialize masker
        masker = PIIMasker(use_spacy=True)
        print(f"✓ Masker initialized (spaCy: {masker.use_spacy})")

        # Test cases
        test_cases = [
            {
                "name": "Email & Phone",
                "text": "Contact Dr. Smith at smith@hospital.com or call 555-123-4567",
            },
            {
                "name": "SSN & DOB",
                "text": "Patient SSN: 123-45-6789, DOB: 01/15/1980",
            },
            {
                "name": "Names (NER)",
                "text": "John Doe was admitted to Stanford Medical Center",
            },
            {
                "name": "Mixed PII",
                "text": """
                Patient: Jane Smith
                Email: jane.smith@email.com
                Phone: (555) 987-6543
                SSN: 987-65-4321
                Admitted to: Mayo Clinic
                """,
            },
        ]

        all_passed = True

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}: {test_case['name']}")
            print(f"{'='*60}")

            original_text = test_case["text"]
            print(f"\n📝 Original:")
            print(original_text)

            # Mask
            masked_text, metadata = masker.mask(
                original_text, session_id=f"test_{i}"
            )

            print(f"\n🔒 Masked:")
            print(masked_text)

            print(f"\n📊 Metadata:")
            print(f"  PII detected: {metadata['pii_detected']}")
            print(f"  PII types: {metadata['pii_types']}")
            print(f"  Matches: {metadata['num_matches']}")

            if metadata['matches']:
                print(f"\n  Detected PII:")
                for match in metadata['matches']:
                    print(f"    - {match.pii_type}: '{match.text}' → {match.token}")

            # Unmask
            unmasked_text = masker.unmask(masked_text, session_id=f"test_{i}")

            print(f"\n🔓 Unmasked:")
            print(unmasked_text)

            # Verify
            if unmasked_text.strip() == original_text.strip():
                print(f"\n✅ Test {i} PASSED: Unmask successful")
            else:
                print(f"\n❌ Test {i} FAILED: Unmask mismatch")
                all_passed = False

        # Test statistics
        print(f"\n{'='*60}")
        print("Statistics")
        print(f"{'='*60}")
        stats = masker.get_stats()
        print(f"Total mappings: {stats['total_mappings']}")
        print(f"Token counts: {stats['token_counts']}")
        print(f"spaCy enabled: {stats['spacy_enabled']}")
        print(f"Patterns count: {stats['patterns_count']}")

        return all_passed

    except ImportError as e:
        print(f"❌ Import error: {e}")
        if "spacy" in str(e):
            print("\n💡 Install spaCy:")
            print("   pip install spacy")
            print("   python -m spacy download en_core_web_sm")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_isolation():
    """Test session isolation for PII mappings"""
    print("\n" + "=" * 60)
    print("Testing Session Isolation...")
    print("=" * 60)

    try:
        from api.services.pii_masker import PIIMasker

        masker = PIIMasker(use_spacy=True)

        # Session 1
        text1 = "Patient: John Doe, email: john@example.com"
        masked1, _ = masker.mask(text1, session_id="session_1")
        print(f"\nSession 1 masked: {masked1}")

        # Session 2
        text2 = "Patient: Jane Smith, email: jane@example.com"
        masked2, _ = masker.mask(text2, session_id="session_2")
        print(f"Session 2 masked: {masked2}")

        # Unmask each session
        unmasked1 = masker.unmask(masked1, session_id="session_1")
        unmasked2 = masker.unmask(masked2, session_id="session_2")

        print(f"\nSession 1 unmasked: {unmasked1}")
        print(f"Session 2 unmasked: {unmasked2}")

        # Verify isolation
        success = (unmasked1 == text1) and (unmasked2 == text2)
        if success:
            print("\n✅ Session isolation PASSED")
        else:
            print("\n❌ Session isolation FAILED")

        return success

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all PII masker tests"""
    print("\n" + "🧪 PII MASKER TEST SUITE" + "\n")

    results = {}

    # Test 1: Basic masking
    results["masking"] = test_pii_masking()

    # Test 2: Session isolation
    results["session"] = test_session_isolation()

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
        print("\nPII Masker is working correctly.")
        print("\nNext steps:")
        print("1. Test Qdrant: python scripts/test_qdrant.py")
        print("2. Run full integration test")
        return 0
    else:
        print("\n⚠️ Some tests failed.")
        print("\nTroubleshooting:")
        print("- Ensure spaCy is installed: pip install spacy")
        print("- Download model: python -m spacy download en_core_web_sm")
        return 1


if __name__ == "__main__":
    sys.exit(main())
