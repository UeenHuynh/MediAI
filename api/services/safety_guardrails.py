"""
Safety Guardrails for Medical AI Chatbot
Detects emergencies, inappropriate queries, and ensures safe responses
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SafetyGuardrails:
    """
    Safety system for medical chatbot
    - Emergency detection
    - Inappropriate query filtering
    - Response safety checks
    - Disclaimer management
    """

    def __init__(self):
        # Emergency keywords and patterns
        self.emergency_keywords = [
            "chest pain",
            "can't breathe",
            "cannot breathe",
            "difficulty breathing",
            "shortness of breath",
            "severe headache",
            "sudden weakness",
            "paralysis",
            "seizure",
            "unconscious",
            "unresponsive",
            "suicide",
            "suicidal",
            "self harm",
            "overdose",
            "severe bleeding",
            "heavy bleeding",
            "stroke symptoms",
            "heart attack",
            "anaphylaxis",
            "allergic reaction severe",
            "severe pain",
            "losing consciousness",
        ]

        # Vital sign thresholds for emergency
        self.emergency_vitals = {
            "heart_rate": (40, 150),  # (min, max) bpm
            "blood_pressure_systolic": (70, 200),  # mmHg
            "respiratory_rate": (8, 35),  # breaths/min
            "oxygen_saturation": (85, 100),  # SpO2 %
            "temperature": (35.0, 40.0),  # Celsius
        }

        # Inappropriate query patterns
        self.inappropriate_patterns = [
            r"how to (kill|harm|hurt)",
            r"illegal drug",
            r"prescription without doctor",
            r"fake (prescription|medical)",
            r"abortion (at home|without doctor)",
        ]

        # Standard disclaimers
        self.disclaimer_emergency = "\n\n⚠️ **EMERGENCY ALERT**: If you are experiencing a medical emergency, call 911 (US) or your local emergency number immediately. Do not rely on this AI system for emergency medical care."

        self.disclaimer_standard = "\n\n**Medical Disclaimer**: This information is for educational purposes and clinical decision support only. It should not replace professional medical judgment. All clinical decisions must be made by qualified healthcare professionals based on individual patient assessment."

        self.disclaimer_not_clinical_use = "\n\n**Important**: This is a demonstration system and is NOT approved for clinical use. Please consult with qualified healthcare professionals for all medical decisions."

    def check_emergency(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Check if query indicates a medical emergency

        Args:
            query: User query

        Returns:
            Tuple of (is_emergency, emergency_type)
        """
        query_lower = query.lower()

        # Check for emergency keywords
        for keyword in self.emergency_keywords:
            if keyword in query_lower:
                logger.warning(f"Emergency keyword detected: {keyword}")
                return True, keyword

        # Check for critical vital signs
        emergency_vital = self._check_vital_signs(query)
        if emergency_vital:
            logger.warning(f"Emergency vital signs detected: {emergency_vital}")
            return True, emergency_vital

        return False, None

    def _check_vital_signs(self, query: str) -> Optional[str]:
        """Check for critical vital signs in query"""

        # Heart rate
        hr_match = re.search(r"heart rate.*?(\d+)", query, re.IGNORECASE)
        if hr_match:
            hr = int(hr_match.group(1))
            min_hr, max_hr = self.emergency_vitals["heart_rate"]
            if hr < min_hr or hr > max_hr:
                return f"heart_rate_{hr}"

        # Blood pressure
        bp_match = re.search(r"blood pressure.*?(\d+)/(\d+)", query, re.IGNORECASE)
        if bp_match:
            systolic = int(bp_match.group(1))
            min_bp, max_bp = self.emergency_vitals["blood_pressure_systolic"]
            if systolic < min_bp or systolic > max_bp:
                return f"blood_pressure_{systolic}"

        # Respiratory rate
        rr_match = re.search(r"respiratory rate.*?(\d+)", query, re.IGNORECASE)
        if rr_match:
            rr = int(rr_match.group(1))
            min_rr, max_rr = self.emergency_vitals["respiratory_rate"]
            if rr < min_rr or rr > max_rr:
                return f"respiratory_rate_{rr}"

        # Oxygen saturation
        spo2_match = re.search(
            r"(?:spo2|oxygen sat|o2 sat).*?(\d+)", query, re.IGNORECASE
        )
        if spo2_match:
            spo2 = int(spo2_match.group(1))
            min_spo2, _ = self.emergency_vitals["oxygen_saturation"]
            if spo2 < min_spo2:
                return f"oxygen_saturation_{spo2}"

        return None

    def check_inappropriate(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Check if query is inappropriate or potentially harmful

        Args:
            query: User query

        Returns:
            Tuple of (is_inappropriate, reason)
        """
        query_lower = query.lower()

        for pattern in self.inappropriate_patterns:
            if re.search(pattern, query_lower):
                logger.warning(f"Inappropriate query detected: {pattern}")
                return True, pattern

        return False, None

    def validate_response(self, response: str) -> Tuple[bool, List[str]]:
        """
        Validate AI response for safety issues

        Args:
            response: Generated response

        Returns:
            Tuple of (is_safe, issues_found)
        """
        issues = []
        response_lower = response.lower()

        # Check for definitive medical advice without caveats
        definitive_phrases = [
            "you should definitely",
            "you must take",
            "the diagnosis is",
            "you have",
            "you need to take",
            "stop taking",
            "start taking",
        ]

        for phrase in definitive_phrases:
            if phrase in response_lower:
                # Check if response has appropriate qualifiers
                qualifiers = [
                    "consult",
                    "healthcare provider",
                    "doctor",
                    "physician",
                    "may need",
                    "consider",
                    "discuss with",
                ]
                has_qualifier = any(q in response_lower for q in qualifiers)
                if not has_qualifier:
                    issues.append(f"Definitive advice without qualifier: {phrase}")

        # Check for missing emergency warnings
        if any(kw in response_lower for kw in ["emergency", "urgent", "immediate"]):
            if "911" not in response and "emergency number" not in response_lower:
                issues.append("Emergency situation without 911 reference")

        # Check for proper disclaimers
        if "disclaimer" not in response_lower and "educational" not in response_lower:
            issues.append("Missing medical disclaimer")

        is_safe = len(issues) == 0
        if not is_safe:
            logger.warning(f"Response safety issues: {issues}")

        return is_safe, issues

    def add_disclaimer(
        self, response: str, is_emergency: bool = False, is_demo: bool = True
    ) -> str:
        """
        Add appropriate disclaimer to response

        Args:
            response: Original response
            is_emergency: Whether query was flagged as emergency
            is_demo: Whether this is a demo system

        Returns:
            Response with disclaimer
        """
        if is_emergency:
            response += self.disclaimer_emergency

        if is_demo:
            response += self.disclaimer_not_clinical_use
        else:
            response += self.disclaimer_standard

        return response

    def create_emergency_response(self, emergency_type: str) -> str:
        """
        Create appropriate response for emergency situation

        Args:
            emergency_type: Type of emergency detected

        Returns:
            Emergency response message
        """
        response = f"""🚨 **MEDICAL EMERGENCY DETECTED**

Based on your query, this appears to be a **medical emergency** requiring immediate attention.

**IMMEDIATE ACTIONS:**

1. **CALL 911** (US) or your local emergency number NOW
2. **Do NOT** wait for medical advice from this system
3. If in a hospital/ICU, activate the rapid response team
4. Ensure qualified medical personnel are aware of the situation

**For Healthcare Professionals:**
- Initiate ACLS/ATLS protocols as appropriate
- Assemble emergency response team
- Prepare for potential ICU admission
- Document time of emergency recognition

**Emergency Type Detected**: {emergency_type}

⚠️ **CRITICAL**: This AI system cannot provide emergency medical care. Immediate evaluation by qualified medical personnel is essential.
"""

        return response

    def create_inappropriate_response(self) -> str:
        """Create response for inappropriate query"""
        response = """I cannot provide assistance with this request.

This system is designed to support healthcare professionals with evidence-based medical information for clinical decision-making.

**I cannot help with:**
- Illegal activities
- Obtaining medications without proper prescriptions
- Self-harm or harm to others
- Circumventing medical supervision
- Unethical practices

**If you need help:**
- For medical care: Contact your healthcare provider
- For mental health crisis: National Suicide Prevention Lifeline: 988
- For substance abuse: SAMHSA National Helpline: 1-800-662-4357

Please use this system responsibly for its intended purpose: supporting evidence-based clinical decision-making by qualified healthcare professionals.
"""

        return response

    def process_query(self, query: str) -> Dict:
        """
        Complete safety check for incoming query

        Args:
            query: User query

        Returns:
            Dictionary with safety assessment
        """
        # Check for emergency
        is_emergency, emergency_type = self.check_emergency(query)

        # Check for inappropriate content
        is_inappropriate, inappropriate_reason = self.check_inappropriate(query)

        # Determine if query should be blocked
        should_block = is_inappropriate

        # Determine if special response needed
        special_response = None
        if should_block:
            special_response = self.create_inappropriate_response()
        elif is_emergency:
            special_response = self.create_emergency_response(emergency_type)

        return {
            "is_safe": not should_block,
            "is_emergency": is_emergency,
            "emergency_type": emergency_type,
            "is_inappropriate": is_inappropriate,
            "inappropriate_reason": inappropriate_reason,
            "should_block": should_block,
            "special_response": special_response,
        }

    def process_response(
        self, response: str, query_safety: Dict, is_demo: bool = True
    ) -> str:
        """
        Process and enhance response with safety measures

        Args:
            response: Generated response
            query_safety: Safety assessment from process_query
            is_demo: Whether this is a demo system

        Returns:
            Enhanced response with safety measures
        """
        # If query should be blocked, return special response
        if query_safety["should_block"]:
            return query_safety["special_response"]

        # If emergency, prepend emergency response
        if query_safety["is_emergency"]:
            return query_safety["special_response"]

        # Validate response
        is_safe, issues = self.validate_response(response)

        if not is_safe:
            logger.warning(f"Response safety issues detected: {issues}")
            # Add extra warning
            response = (
                "⚠️ **Safety Note**: Please consult with qualified healthcare professionals before taking any action based on this information.\n\n"
                + response
            )

        # Add appropriate disclaimer
        response = self.add_disclaimer(
            response, is_emergency=query_safety["is_emergency"], is_demo=is_demo
        )

        return response
