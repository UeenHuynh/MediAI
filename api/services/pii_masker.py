"""
PII Masking Service - Layer 2
Detects and masks Personally Identifiable Information using:
- Regex patterns (email, phone, SSN)
- spaCy NER (names, organizations)
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class PIIMatch:
    """Detected PII match"""

    text: str  # Original text
    token: str  # Replacement token (e.g., <EMAIL_1>)
    pii_type: str  # Type: email, phone, ssn, person, etc.
    start: int  # Start position
    end: int  # End position
    confidence: float  # Detection confidence (0-1)


class PIIMasker:
    """
    PII detection and masking service
    Protects sensitive information before sending to LLM
    """

    # Regex patterns for common PII
    PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "date_of_birth": r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        "zip_code": r"\b\d{5}(?:-\d{4})?\b",
        "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    }

    def __init__(self, use_spacy: bool = True, spacy_model: str = "en_core_web_sm"):
        """
        Initialize PII masker

        Args:
            use_spacy: Use spaCy NER for name detection
            spacy_model: spaCy model to use
        """
        self.use_spacy = use_spacy
        self.nlp = None

        # Token counters for different PII types
        self.token_counters: Dict[str, int] = {}

        # Mapping storage: {token: original_value}
        self.token_mapping: Dict[str, str] = {}

        # Initialize spaCy if enabled
        if use_spacy:
            try:
                import spacy

                self.nlp = spacy.load(spacy_model)
                logger.info(f"✅ spaCy model loaded: {spacy_model}")
            except Exception as e:
                logger.warning(f"❌ Failed to load spaCy: {e}")
                logger.warning("Install with: python -m spacy download en_core_web_sm")
                self.use_spacy = False

    def mask(self, text: str, session_id: Optional[str] = None) -> Tuple[str, Dict]:
        """
        Mask PII in text

        Args:
            text: Input text with potential PII
            session_id: Session ID for mapping storage (optional)

        Returns:
            (masked_text, pii_metadata)
            pii_metadata = {
                "pii_detected": bool,
                "pii_types": List[str],
                "num_matches": int,
                "matches": List[PIIMatch]
            }
        """
        if not text:
            return text, {
                "pii_detected": False,
                "pii_types": [],
                "num_matches": 0,
                "matches": [],
            }

        matches: List[PIIMatch] = []

        # 1. Regex-based detection
        matches.extend(self._detect_regex_pii(text))

        # 2. spaCy NER detection
        if self.use_spacy and self.nlp:
            matches.extend(self._detect_ner_pii(text))

        # Sort matches by position (reverse order for replacement)
        matches.sort(key=lambda m: m.start, reverse=True)

        # Replace PII with tokens
        masked_text = text
        for match in matches:
            masked_text = (
                masked_text[: match.start] + match.token + masked_text[match.end :]
            )

            # Store mapping
            mapping_key = match.token
            if session_id:
                mapping_key = f"{session_id}:{match.token}"
            self.token_mapping[mapping_key] = match.text

        # Build metadata
        pii_detected = len(matches) > 0
        pii_types = list(set(m.pii_type for m in matches))

        metadata = {
            "pii_detected": pii_detected,
            "pii_types": pii_types,
            "num_matches": len(matches),
            "matches": matches,
        }

        if pii_detected:
            logger.info(f"🔒 Masked {len(matches)} PII instances: {pii_types}")

        return masked_text, metadata

    def unmask(self, text: str, session_id: Optional[str] = None) -> str:
        """
        Restore original PII values

        Args:
            text: Masked text with tokens
            session_id: Session ID for mapping lookup

        Returns:
            Text with original PII restored
        """
        unmasked_text = text

        # Replace tokens with original values
        for token, original in self.token_mapping.items():
            # Handle session-specific tokens
            if session_id and token.startswith(f"{session_id}:"):
                token_to_replace = token.split(":", 1)[1]
            else:
                token_to_replace = token

            unmasked_text = unmasked_text.replace(token_to_replace, original)

        return unmasked_text

    def _detect_regex_pii(self, text: str) -> List[PIIMatch]:
        """Detect PII using regex patterns"""
        matches = []

        for pii_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text):
                token = self._generate_token(pii_type)
                matches.append(
                    PIIMatch(
                        text=match.group(),
                        token=token,
                        pii_type=pii_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=1.0,  # Regex has high confidence
                    )
                )

        return matches

    def _detect_ner_pii(self, text: str) -> List[PIIMatch]:
        """Detect PII using spaCy NER"""
        if not self.nlp:
            return []

        matches = []
        doc = self.nlp(text)

        # Entity types to mask
        pii_entity_types = {
            "PERSON": "person",
            "ORG": "organization",
            "GPE": "location",  # Geopolitical entities
            "LOC": "location",
        }

        for ent in doc.ents:
            if ent.label_ in pii_entity_types:
                pii_type = pii_entity_types[ent.label_]
                token = self._generate_token(pii_type)

                matches.append(
                    PIIMatch(
                        text=ent.text,
                        token=token,
                        pii_type=pii_type,
                        start=ent.start_char,
                        end=ent.end_char,
                        confidence=0.8,  # NER confidence (could use model score)
                    )
                )

        return matches

    def _generate_token(self, pii_type: str) -> str:
        """
        Generate unique token for PII type

        Args:
            pii_type: Type of PII (email, phone, person, etc.)

        Returns:
            Token like <EMAIL_1>, <PERSON_2>, etc.
        """
        # Increment counter for this type
        if pii_type not in self.token_counters:
            self.token_counters[pii_type] = 0

        self.token_counters[pii_type] += 1
        count = self.token_counters[pii_type]

        # Generate token
        token = f"<{pii_type.upper()}_{count}>"
        return token

    def reset_session(self, session_id: Optional[str] = None):
        """
        Reset PII mappings for a session

        Args:
            session_id: Session to reset (None = reset all)
        """
        if session_id:
            # Remove only session-specific mappings
            keys_to_remove = [
                k for k in self.token_mapping.keys() if k.startswith(f"{session_id}:")
            ]
            for key in keys_to_remove:
                del self.token_mapping[key]
            logger.info(f"Reset PII mappings for session: {session_id}")
        else:
            # Reset all
            self.token_mapping.clear()
            self.token_counters.clear()
            logger.info("Reset all PII mappings")

    def get_stats(self) -> Dict:
        """Get PII masking statistics"""
        return {
            "total_mappings": len(self.token_mapping),
            "token_counts": dict(self.token_counters),
            "spacy_enabled": self.use_spacy,
            "patterns_count": len(self.PATTERNS),
        }


# Example usage and testing
if __name__ == "__main__":
    # Test PII masker
    masker = PIIMasker(use_spacy=True)

    # Test text with PII
    test_text = """
    Patient: John Doe
    Email: john.doe@hospital.com
    Phone: 555-123-4567
    SSN: 123-45-6789
    DOB: 01/15/1980

    Dr. Smith from Stanford Medical Center reviewed the case.
    Contact at smith@stanford.edu or call 650-123-4567.
    """

    print("Original text:")
    print(test_text)
    print("\n" + "=" * 60 + "\n")

    # Mask PII
    masked_text, metadata = masker.mask(test_text, session_id="test_session")

    print("Masked text:")
    print(masked_text)
    print("\n" + "=" * 60 + "\n")

    print("Metadata:")
    print(f"PII detected: {metadata['pii_detected']}")
    print(f"PII types: {metadata['pii_types']}")
    print(f"Number of matches: {metadata['num_matches']}")
    print("\nMatches:")
    for match in metadata["matches"]:
        print(f"  - {match.pii_type}: '{match.text}' → {match.token}")

    print("\n" + "=" * 60 + "\n")

    # Unmask
    unmasked_text = masker.unmask(masked_text, session_id="test_session")
    print("Unmasked text:")
    print(unmasked_text)

    print("\n" + "=" * 60 + "\n")
    print("Stats:")
    print(masker.get_stats())
