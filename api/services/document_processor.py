"""
Document Processing and Chunking for Medical Content
Handles text splitting with medical context preservation
"""

import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class MedicalDocumentProcessor:
    """Process and chunk medical documents preserving clinical context"""

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
        min_chunk_size: int = 100,
    ):
        """
        Initialize document processor

        Args:
            chunk_size: Target size of each chunk (in characters)
            chunk_overlap: Overlap between chunks to preserve context
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

        # Medical section markers (headers that should not be split)
        self.section_markers = [
            r"^#+\s+",  # Markdown headers
            r"^\d+\.\s+",  # Numbered sections
            r"^[A-Z][A-Z\s]+:$",  # ALL CAPS headers with colon
            r"^(INDICATION|CONTRAINDICATION|DOSAGE|ADVERSE|WARNING|MECHANISM|TREATMENT|DIAGNOSIS|PROTOCOL|GUIDELINE):",
            r"^(Background|Methods|Results|Conclusion|Introduction|Discussion):",
        ]

        # Medical entity patterns (should not be split)
        self.preserve_patterns = [
            r"\d+\s*(?:mg|mcg|g|mL|L|units?)",  # Dosages
            r"\d+[-–]\d+\s*(?:mg|mcg|g|mL|L)",  # Dose ranges
            r"(?:q|Q)(?:\d+)?h",  # Frequency (q6h, q4h)
            r"ICD-\d+[\w.-]*",  # ICD codes
            r"CPT-\d+",  # CPT codes
            r"SNOMED[-\s]?\d+",  # SNOMED codes
        ]

    def chunk_document(
        self, text: str, metadata: Dict = None
    ) -> List[Tuple[str, Dict]]:
        """
        Chunk document into semantically meaningful pieces

        Args:
            text: Document text
            metadata: Document metadata (will be copied to each chunk)

        Returns:
            List of (chunk_text, chunk_metadata) tuples
        """
        if not text or len(text.strip()) < self.min_chunk_size:
            return []

        # Clean text
        text = self._clean_text(text)

        # Try to split by sections first
        sections = self._split_by_sections(text)

        # If sections are too large, split further
        chunks = []
        for section in sections:
            if len(section) <= self.chunk_size:
                chunks.append(section)
            else:
                # Split large sections by paragraphs
                section_chunks = self._split_by_paragraphs(section)
                chunks.extend(section_chunks)

        # Create chunks with metadata
        chunk_list = []
        for idx, chunk_text in enumerate(chunks):
            if len(chunk_text.strip()) >= self.min_chunk_size:
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata.update(
                    {
                        "chunk_index": idx,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk_text),
                    }
                )
                chunk_list.append((chunk_text.strip(), chunk_metadata))

        logger.info(f"Created {len(chunk_list)} chunks from document")
        return chunk_list

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove multiple newlines (but keep paragraph breaks)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Normalize unicode characters
        text = text.replace("\u00a0", " ")  # Non-breaking space
        text = text.replace("\u2019", "'")  # Right single quote
        text = text.replace("\u201c", '"')  # Left double quote
        text = text.replace("\u201d", '"')  # Right double quote

        return text.strip()

    def _split_by_sections(self, text: str) -> List[str]:
        """Split text by major sections (headers)"""
        sections = []
        current_section = []

        lines = text.split("\n")
        for line in lines:
            # Check if line is a section marker
            is_marker = False
            for pattern in self.section_markers:
                if re.match(pattern, line.strip()):
                    is_marker = True
                    break

            if is_marker and current_section:
                # Start new section
                sections.append("\n".join(current_section))
                current_section = [line]
            else:
                current_section.append(line)

        # Add final section
        if current_section:
            sections.append("\n".join(current_section))

        return sections

    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraphs with overlap"""
        # Split by double newlines (paragraph breaks)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        if not paragraphs:
            # Fallback: split by sentences
            return self._split_by_sentences(text)

        chunks = []
        current_chunk = []
        current_size = 0

        for i, para in enumerate(paragraphs):
            para_size = len(para)

            if current_size + para_size <= self.chunk_size:
                # Add to current chunk
                current_chunk.append(para)
                current_size += para_size
            else:
                # Start new chunk
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                # Start new chunk with overlap
                overlap_paras = []
                overlap_size = 0
                for prev_para in reversed(current_chunk):
                    if overlap_size + len(prev_para) <= self.chunk_overlap:
                        overlap_paras.insert(0, prev_para)
                        overlap_size += len(prev_para)
                    else:
                        break

                current_chunk = overlap_paras + [para]
                current_size = sum(len(p) for p in current_chunk)

        # Add final chunk
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def _split_by_sentences(self, text: str) -> List[str]:
        """Split text by sentences with overlap (fallback method)"""
        # Simple sentence splitting (can be improved with spaCy/NLTK)
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence)

            if current_size + sentence_size <= self.chunk_size:
                current_chunk.append(sentence)
                current_size += sentence_size
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))

                # Overlap: include last few sentences
                overlap_sentences = []
                overlap_size = 0
                for prev_sent in reversed(current_chunk):
                    if overlap_size + len(prev_sent) <= self.chunk_overlap:
                        overlap_sentences.insert(0, prev_sent)
                        overlap_size += len(prev_sent)
                    else:
                        break

                current_chunk = overlap_sentences + [sentence]
                current_size = sum(len(s) for s in current_chunk)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def extract_medical_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract medical entities from text (simplified version)

        Returns:
            Dictionary of entity types and their values
        """
        entities = {
            "dosages": [],
            "frequencies": [],
            "icd_codes": [],
            "snomed_codes": [],
        }

        # Extract dosages
        dosage_pattern = r"\d+\.?\d*\s*(?:mg|mcg|g|mL|L|units?|U)"
        entities["dosages"] = re.findall(dosage_pattern, text, re.IGNORECASE)

        # Extract frequencies
        freq_pattern = r"(?:q|Q)(?:\d+)?h"
        entities["frequencies"] = re.findall(freq_pattern, text)

        # Extract ICD codes
        icd_pattern = r"ICD-(?:9|10|11)[\w.-]+"
        entities["icd_codes"] = re.findall(icd_pattern, text, re.IGNORECASE)

        # Extract SNOMED codes
        snomed_pattern = r"SNOMED[-\s]?\d+"
        entities["snomed_codes"] = re.findall(snomed_pattern, text, re.IGNORECASE)

        return entities

    def categorize_content(self, text: str, metadata: Dict = None) -> str:
        """
        Automatically categorize medical content

        Returns:
            Category string: 'drug', 'disease', 'guideline', 'protocol', 'general'
        """
        text_lower = text.lower()

        # Check for drug-related content
        drug_keywords = [
            "dosage",
            "medication",
            "drug",
            "pharmaceutical",
            "administration",
            "contraindication",
            "adverse effect",
            "pharmacology",
        ]
        if any(kw in text_lower for kw in drug_keywords):
            return "drug"

        # Check for disease/condition content
        disease_keywords = [
            "diagnosis",
            "symptom",
            "pathophysiology",
            "etiology",
            "prognosis",
            "epidemiology",
            "complication",
        ]
        if any(kw in text_lower for kw in disease_keywords):
            return "disease"

        # Check for guideline content
        guideline_keywords = [
            "guideline",
            "recommendation",
            "evidence level",
            "clinical practice",
            "consensus",
            "standard of care",
        ]
        if any(kw in text_lower for kw in guideline_keywords):
            return "guideline"

        # Check for protocol content
        protocol_keywords = [
            "protocol",
            "algorithm",
            "procedure",
            "step-by-step",
            "workflow",
            "treatment plan",
        ]
        if any(kw in text_lower for kw in protocol_keywords):
            return "protocol"

        # Check metadata if available
        if metadata:
            if "category" in metadata:
                return metadata["category"]
            if "type" in metadata:
                return metadata["type"]

        return "general"
