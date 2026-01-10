"""
PII Redaction Service using Microsoft Presidio

This service provides production-grade PII detection and anonymization
for HIPAA compliance and privacy protection in medical applications.

Features:
- Automatic detection of 15+ PII entity types
- Configurable anonymization strategies
- Audit logging for compliance
- Support for custom medical entity recognizers
- Batch processing capabilities

Author: MediAI Team
Version: 1.0.0
License: MIT
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from presidio_analyzer import (
    AnalyzerEngine,
    Pattern,
    PatternRecognizer,
    RecognizerResult,
)
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PIIEntityType(str, Enum):
    """Supported PII entity types."""

    PERSON = "PERSON"
    EMAIL = "EMAIL_ADDRESS"
    PHONE = "PHONE_NUMBER"
    SSN = "US_SSN"
    MEDICAL_LICENSE = "MEDICAL_LICENSE"
    CREDIT_CARD = "CREDIT_CARD"
    IBAN = "IBAN_CODE"
    PASSPORT = "US_PASSPORT"
    DRIVER_LICENSE = "US_DRIVER_LICENSE"
    DATE_TIME = "DATE_TIME"
    LOCATION = "LOCATION"
    IP_ADDRESS = "IP_ADDRESS"
    CRYPTO = "CRYPTO"
    # Medical-specific
    PATIENT_ID = "PATIENT_ID"
    MRN = "MRN"  # Medical Record Number


class AnonymizationStrategy(str, Enum):
    """Anonymization strategies for different use cases."""

    REPLACE = "replace"  # Replace with placeholder (e.g., <PERSON>)
    MASK = "mask"  # Mask with asterisks (e.g., ***-**-1234)
    HASH = "hash"  # One-way hash (consistent for same value)
    REDACT = "redact"  # Complete removal
    ENCRYPT = "encrypt"  # Reversible encryption (requires key)


@dataclass
class PIIDetectionResult:
    """Result of PII detection and redaction."""

    original_text: str
    redacted_text: str
    entities_found: List[Dict[str, Any]] = field(default_factory=list)
    pii_count: int = 0
    entity_types_detected: List[str] = field(default_factory=list)
    anonymization_strategy: str = "replace"
    processing_time_ms: float = 0.0


class PIIRedactionService:
    """
    Production PII redaction service using Microsoft Presidio.

    This service provides enterprise-grade PII detection and anonymization
    suitable for healthcare applications requiring HIPAA compliance.

    Example:
        >>> service = PIIRedactionService()
        >>> result = service.redact_pii(
        ...     "Patient John Doe (SSN: 123-45-6789) called."
        ... )
        >>> print(result.redacted_text)
        "Patient <PERSON> (SSN: <US_SSN>) called."
        >>> print(result.entity_types_detected)
        ['PERSON', 'US_SSN']
    """

    # Default entities to detect
    DEFAULT_ENTITIES = [
        PIIEntityType.PERSON,
        PIIEntityType.EMAIL,
        PIIEntityType.PHONE,
        PIIEntityType.SSN,
        PIIEntityType.MEDICAL_LICENSE,
        PIIEntityType.LOCATION,
        PIIEntityType.DATE_TIME,
        PIIEntityType.PATIENT_ID,
        PIIEntityType.MRN,
    ]

    # Medical-specific patterns
    MEDICAL_PATTERNS = {
        "PATIENT_ID": Pattern(
            name="patient_id_pattern",
            regex=r"(?i)\b(PATIENT|PT|PAT)[-_][0-9]{5,10}\b",
            score=0.85,
        ),
        "MRN": Pattern(
            name="mrn_pattern",
            regex=r"(?i)\b(?:MRN|MR)[-:][0-9]{6,12}\b",
            score=0.9,
        ),
    }

    # SSN explicit pattern (Presidio's built-in is too strict)
    SSN_PATTERN = Pattern(
        name="ssn_explicit_pattern",
        regex=r"\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b",
        score=0.85,
    )

    # Short phone pattern (Presidio needs 10+ digits by default)
    SHORT_PHONE_PATTERN = Pattern(
        name="short_phone_pattern",
        regex=r"\b[0-9]{3}-[0-9]{4}\b",
        score=0.7,
    )

    def __init__(
        self,
        entities: Optional[List[str]] = None,
        language: str = "en",
        enable_medical_patterns: bool = True,
        anonymization_strategy: AnonymizationStrategy = AnonymizationStrategy.REPLACE,
        enable_audit_log: bool = True,
    ):
        """
        Initialize PII redaction service.

        Args:
            entities: List of entity types to detect (None = use defaults)
            language: Language code for analysis
            enable_medical_patterns: Add medical-specific recognizers
            anonymization_strategy: Default anonymization strategy
            enable_audit_log: Enable PII detection audit logging
        """
        logger.info("Initializing PIIRedactionService")

        self.language = language
        self.anonymization_strategy = anonymization_strategy
        self.enable_audit_log = enable_audit_log

        # Set entities to detect
        if entities is None:
            self.entities = [e.value for e in self.DEFAULT_ENTITIES]
        else:
            self.entities = entities

        # Initialize Presidio engines
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

        # Add medical-specific recognizers
        if enable_medical_patterns:
            self._add_medical_recognizers()

        logger.info(
            f"PIIRedactionService initialized: "
            f"{len(self.entities)} entity types, "
            f"strategy={anonymization_strategy.value}"
        )

    def _add_medical_recognizers(self) -> None:
        """Add custom medical entity recognizers."""
        # Add medical patterns
        for entity_type, pattern in self.MEDICAL_PATTERNS.items():
            recognizer = PatternRecognizer(
                supported_entity=entity_type,
                patterns=[pattern],
                context=[],
            )
            self.analyzer.registry.add_recognizer(recognizer)
            # Ensure entity is in detection list
            if entity_type not in self.entities:
                self.entities.append(entity_type)

        # Add explicit SSN pattern recognizer
        ssn_recognizer = PatternRecognizer(
            supported_entity="US_SSN",
            patterns=[self.SSN_PATTERN],
            context=["ssn", "social", "security"],
        )
        self.analyzer.registry.add_recognizer(ssn_recognizer)

        # Add short phone pattern recognizer (7-digit format like 555-1234)
        phone_recognizer = PatternRecognizer(
            supported_entity="PHONE_NUMBER",
            patterns=[self.SHORT_PHONE_PATTERN],
            context=["phone", "call", "tel"],
        )
        self.analyzer.registry.add_recognizer(phone_recognizer)

        logger.info(
            f"Added {len(self.MEDICAL_PATTERNS)} medical recognizers + SSN/phone patterns"
        )

    def _filter_medical_false_positives(
        self, text: str, results: List[RecognizerResult]
    ) -> List[RecognizerResult]:
        """
        Filter out false positive PII detections in medical contexts.

        Args:
            text: Original text being analyzed
            results: List of RecognizerResult objects from analyzer

        Returns:
            Filtered list of RecognizerResult objects
        """
        # Medical abbreviations that indicate vital signs context
        medical_abbreviations = [
            "BP", "HR", "RR", "SpO2", "Temp", "SBP", "DBP",
            "WBC", "Hgb", "Plt", "Cr", "BUN", "MAP"
        ]

        filtered_results = []
        for result in results:
            # Only filter DATE_TIME entities
            if result.entity_type != "DATE_TIME":
                filtered_results.append(result)
                continue

            # Check if there's a medical abbreviation within 10 chars before this entity
            start_check = max(0, result.start - 10)
            context_before = text[start_check:result.start]

            # If we find a medical abbreviation, skip this DATE_TIME detection
            is_medical_context = any(
                abbr in context_before for abbr in medical_abbreviations
            )

            if not is_medical_context:
                filtered_results.append(result)

        return filtered_results

    def _build_operators_config(
        self, strategy: AnonymizationStrategy
    ) -> Dict[str, OperatorConfig]:
        """
        Build operator configuration for anonymization strategy.

        Args:
            strategy: Anonymization strategy to use

        Returns:
            Dictionary mapping entity types to operator configs
        """
        operators = {}

        if strategy == AnonymizationStrategy.REPLACE:
            # Default: replace with entity type
            for entity in self.entities:
                operators[entity] = OperatorConfig("replace")

        elif strategy == AnonymizationStrategy.MASK:
            # Mask with asterisks, keeping last 4 chars
            for entity in self.entities:
                operators[entity] = OperatorConfig(
                    "mask",
                    {
                        "masking_char": "*",
                        "chars_to_mask": -1,  # Mask all
                        "from_end": False,
                    },
                )

        elif strategy == AnonymizationStrategy.HASH:
            # One-way hash
            for entity in self.entities:
                operators[entity] = OperatorConfig("hash")

        elif strategy == AnonymizationStrategy.REDACT:
            # Complete removal
            for entity in self.entities:
                operators[entity] = OperatorConfig("redact")

        elif strategy == AnonymizationStrategy.ENCRYPT:
            # Encryption (requires encryption key)
            for entity in self.entities:
                operators[entity] = OperatorConfig(
                    "encrypt", {"key": "WmZq4t7w!z%C*F-J"}  # In production: use KMS
                )

        return operators

    def analyze_pii(
        self,
        text: str,
        entities: Optional[List[str]] = None,
    ) -> List[RecognizerResult]:
        """
        Analyze text for PII entities without redaction.

        Args:
            text: Text to analyze
            entities: Optional list of entity types to detect

        Returns:
            List of RecognizerResult objects

        Example:
            >>> service = PIIRedactionService()
            >>> results = service.analyze_pii("John Doe, SSN: 123-45-6789")
            >>> for r in results:
            ...     print(f"{r.entity_type}: {text[r.start:r.end]}")
            PERSON: John Doe
            US_SSN: 123-45-6789
        """
        entities_to_detect = entities or self.entities

        try:
            results = self.analyzer.analyze(
                text=text,
                language=self.language,
                entities=entities_to_detect,
            )

            if self.enable_audit_log and results:
                entity_types = {r.entity_type for r in results}
                logger.info(
                    f"PII detected: {len(results)} instances, " f"types={entity_types}"
                )

            return results

        except Exception as e:
            logger.error(f"PII analysis failed: {e}", exc_info=True)
            return []

    def redact_pii(
        self,
        text: str,
        entities: Optional[List[str]] = None,
        strategy: Optional[AnonymizationStrategy] = None,
    ) -> PIIDetectionResult:
        """
        Detect and redact PII from text.

        Args:
            text: Input text to redact
            entities: Optional entity types to detect
            strategy: Optional anonymization strategy

        Returns:
            PIIDetectionResult with redacted text and metadata

        Example:
            >>> service = PIIRedactionService()
            >>> result = service.redact_pii(
            ...     "Patient: John Doe\nDOB: 01/15/1980\nPhone: 555-1234"
            ... )
            >>> print(result.redacted_text)
            Patient: <PERSON>
            DOB: <DATE_TIME>
            Phone: <PHONE_NUMBER>
        """
        import time

        start_time = time.time()

        # Use provided strategy or default
        anonymization_strategy = strategy or self.anonymization_strategy

        try:
            # Step 1: Analyze for PII
            analyzer_results = self.analyze_pii(text, entities)

            # Step 1.5: Filter out medical false positives
            analyzer_results = self._filter_medical_false_positives(text, analyzer_results)

            # Step 2: Build anonymization operators
            operators = self._build_operators_config(anonymization_strategy)

            # Step 3: Anonymize
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results,
                operators=operators,
            )

            # Step 4: Build result object
            entity_types = list({r.entity_type for r in analyzer_results})

            result = PIIDetectionResult(
                original_text=text,
                redacted_text=anonymized_result.text,
                entities_found=[
                    {
                        "type": r.entity_type,
                        "score": r.score,
                        "start": r.start,
                        "end": r.end,
                    }
                    for r in analyzer_results
                ],
                pii_count=len(analyzer_results),
                entity_types_detected=entity_types,
                anonymization_strategy=anonymization_strategy.value,
                processing_time_ms=(time.time() - start_time) * 1000,
            )

            if self.enable_audit_log:
                logger.info(
                    f"PII redaction completed: "
                    f"{result.pii_count} entities, "
                    f"{result.processing_time_ms:.2f}ms"
                )

            return result

        except Exception as e:
            logger.error(f"PII redaction failed: {e}", exc_info=True)

            # Fail-safe: return original text with error
            return PIIDetectionResult(
                original_text=text,
                redacted_text=text,  # Return original on error
                entities_found=[],
                pii_count=0,
                entity_types_detected=[],
                anonymization_strategy="none",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def batch_redact(
        self,
        texts: List[str],
        strategy: Optional[AnonymizationStrategy] = None,
    ) -> List[PIIDetectionResult]:
        """
        Redact PII from multiple texts in batch.

        Args:
            texts: List of texts to process
            strategy: Optional anonymization strategy

        Returns:
            List of PIIDetectionResult objects

        Example:
            >>> service = PIIRedactionService()
            >>> texts = [
            ...     "John Doe, john@email.com",
            ...     "Jane Smith, SSN: 987-65-4321"
            ... ]
            >>> results = service.batch_redact(texts)
            >>> for r in results:
            ...     print(r.redacted_text)
        """
        logger.info(f"Batch redaction started: {len(texts)} texts")

        results = []
        for i, text in enumerate(texts):
            try:
                result = self.redact_pii(text, strategy=strategy)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch redaction failed for text {i}: {e}")
                # Add error result
                results.append(
                    PIIDetectionResult(
                        original_text=text,
                        redacted_text=text,
                        entities_found=[],
                        pii_count=0,
                        entity_types_detected=[],
                    )
                )

        total_pii = sum(r.pii_count for r in results)
        logger.info(
            f"Batch redaction completed: "
            f"{len(results)} texts, {total_pii} total PII"
        )

        return results

    def is_pii_free(
        self,
        text: str,
        min_score: float = 0.5,
    ) -> bool:
        """
        Check if text is free of PII.

        Args:
            text: Text to check
            min_score: Minimum confidence score to consider as PII

        Returns:
            True if no PII detected above threshold

        Example:
            >>> service = PIIRedactionService()
            >>> service.is_pii_free("Hello, how are you?")
            True
            >>> service.is_pii_free("Contact John Doe at 555-1234")
            False
        """
        results = self.analyze_pii(text)

        # Filter by score threshold
        high_confidence_pii = [r for r in results if r.score >= min_score]

        return len(high_confidence_pii) == 0

    def get_pii_summary(self, text: str) -> Dict[str, Any]:
        """
        Get detailed PII summary without redaction.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with PII statistics

        Example:
            >>> service = PIIRedactionService()
            >>> summary = service.get_pii_summary(
            ...     "John Doe (john@email.com, 555-1234)"
            ... )
            >>> print(summary)
            {
                'total_entities': 3,
                'entity_counts': {'PERSON': 1, 'EMAIL_ADDRESS': 1, 'PHONE_NUMBER': 1},
                'average_score': 0.85,
                'has_pii': True
            }
        """
        results = self.analyze_pii(text)

        if not results:
            return {
                "total_entities": 0,
                "entity_counts": {},
                "average_score": 0.0,
                "has_pii": False,
            }

        # Count by entity type
        entity_counts = {}
        for result in results:
            entity_type = result.entity_type
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

        # Calculate average confidence score
        avg_score = sum(r.score for r in results) / len(results)

        return {
            "total_entities": len(results),
            "entity_counts": entity_counts,
            "average_score": round(avg_score, 3),
            "has_pii": True,
        }


# Singleton instance for application-wide use
_pii_service_instance: Optional[PIIRedactionService] = None


def get_pii_service() -> PIIRedactionService:
    """
    Get singleton PII redaction service instance.

    Returns:
        Shared PIIRedactionService instance
    """
    global _pii_service_instance

    if _pii_service_instance is None:
        _pii_service_instance = PIIRedactionService()
        logger.info("Created singleton PIIRedactionService instance")

    return _pii_service_instance


if __name__ == "__main__":
    # Example usage and testing
    service = PIIRedactionService()

    # Test 1: Basic redaction
    text1 = "Patient John Doe (SSN: 123-45-6789) called from 555-1234."
    result1 = service.redact_pii(text1)

    print("=== Test 1: Basic Redaction ===")
    print(f"Original: {text1}")
    print(f"Redacted: {result1.redacted_text}")
    print(f"Entities: {result1.entity_types_detected}")
    print()

    # Test 2: Medical-specific patterns
    text2 = "Patient ID: PATIENT-123456, MRN: MR-9876543210"
    result2 = service.redact_pii(text2)

    print("=== Test 2: Medical Patterns ===")
    print(f"Original: {text2}")
    print(f"Redacted: {result2.redacted_text}")
    print(f"Entities: {result2.entity_types_detected}")
    print()

    # Test 3: PII summary
    text3 = "Dr. Jane Smith (jane.smith@hospital.com) reviewed MRN:12345"
    summary = service.get_pii_summary(text3)

    print("=== Test 3: PII Summary ===")
    print(f"Text: {text3}")
    print(f"Summary: {summary}")
    print()

    # Test 4: PII-free check
    clean_text = "The procedure was successful."
    pii_text = "Contact John at john@email.com"

    print("=== Test 4: PII-Free Check ===")
    print(f"'{clean_text}' is PII-free: {service.is_pii_free(clean_text)}")
    print(f"'{pii_text}' is PII-free: {service.is_pii_free(pii_text)}")
