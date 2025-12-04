"""
Prediction Explainer using RAG
Connects sepsis/mortality predictions with medical knowledge explanations
"""

import logging
from typing import Dict, List, Optional

from .rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)


class PredictionExplainer:
    """
    Explain model predictions using RAG system
    Provides clinical context and evidence-based guidance
    """

    def __init__(self, rag_pipeline: RAGPipeline):
        """
        Initialize prediction explainer

        Args:
            rag_pipeline: RAG pipeline instance
        """
        self.rag = rag_pipeline

    def explain_sepsis_prediction(
        self, prediction: Dict, patient_data: Dict
    ) -> Dict:
        """
        Explain sepsis prediction with clinical context

        Args:
            prediction: Model prediction result
                {
                    'risk_score': float,
                    'risk_level': str,
                    'important_features': list
                }
            patient_data: Patient clinical data

        Returns:
            Explanation dictionary with clinical guidance
        """
        risk_score = prediction.get("risk_score", 0)
        risk_level = prediction.get("risk_level", "unknown")
        features = prediction.get("important_features", [])

        # Build context-aware query
        query = self._build_sepsis_query(risk_score, risk_level, features, patient_data)

        # Retrieve relevant clinical guidance
        try:
            result = self.rag.query(
                question=query, top_k=5, category="guideline", include_citations=True
            )

            # Enhance explanation
            explanation = {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "clinical_guidance": result["answer"],
                "evidence_sources": result["citations"],
                "confidence": result["confidence"],
                "key_risk_factors": self._extract_risk_factors(features),
                "recommendations": self._generate_sepsis_recommendations(
                    risk_level, result
                ),
            }

            logger.info(f"Generated sepsis explanation (confidence: {result['confidence']:.2f})")
            return explanation

        except Exception as e:
            logger.error(f"Failed to generate sepsis explanation: {e}")
            return {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "clinical_guidance": "Unable to generate explanation. Please refer to clinical guidelines.",
                "evidence_sources": [],
                "confidence": 0.0,
                "error": str(e),
            }

    def explain_mortality_prediction(
        self, prediction: Dict, patient_data: Dict
    ) -> Dict:
        """
        Explain mortality risk prediction with clinical context

        Args:
            prediction: Model prediction result
            patient_data: Patient clinical data

        Returns:
            Explanation dictionary
        """
        risk_score = prediction.get("risk_score", 0)
        risk_level = prediction.get("risk_level", "unknown")
        features = prediction.get("important_features", [])

        # Build query
        query = self._build_mortality_query(risk_score, risk_level, features, patient_data)

        try:
            result = self.rag.query(
                question=query, top_k=5, include_citations=True
            )

            explanation = {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "prognostic_guidance": result["answer"],
                "evidence_sources": result["citations"],
                "confidence": result["confidence"],
                "key_prognostic_factors": self._extract_risk_factors(features),
                "recommendations": self._generate_mortality_recommendations(
                    risk_level, result
                ),
            }

            logger.info(f"Generated mortality explanation (confidence: {result['confidence']:.2f})")
            return explanation

        except Exception as e:
            logger.error(f"Failed to generate mortality explanation: {e}")
            return {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "prognostic_guidance": "Unable to generate explanation. Please consult with intensivist.",
                "evidence_sources": [],
                "confidence": 0.0,
                "error": str(e),
            }

    def _build_sepsis_query(
        self, risk_score: float, risk_level: str, features: List, patient_data: Dict
    ) -> str:
        """Build context-aware query for sepsis explanation"""

        query_parts = [
            f"A patient has a sepsis risk score of {risk_score:.1%} ({risk_level} risk)."
        ]

        # Add key features
        if features:
            feature_names = [f.get("name", str(f)) for f in features[:3]]
            query_parts.append(
                f"Key risk factors include: {', '.join(feature_names)}."
            )

        # Add clinical context
        if patient_data:
            if "sofa_score" in patient_data:
                query_parts.append(f"SOFA score is {patient_data['sofa_score']}.")
            if "lactate" in patient_data:
                query_parts.append(f"Lactate is {patient_data['lactate']} mmol/L.")

        query_parts.append(
            "What are the current evidence-based guidelines for sepsis management at this risk level? "
            "Include immediate actions, monitoring, and treatment priorities."
        )

        return " ".join(query_parts)

    def _build_mortality_query(
        self, risk_score: float, risk_level: str, features: List, patient_data: Dict
    ) -> str:
        """Build context-aware query for mortality explanation"""

        query_parts = [
            f"An ICU patient has a mortality risk of {risk_score:.1%} ({risk_level} risk)."
        ]

        # Add key prognostic factors
        if features:
            feature_names = [f.get("name", str(f)) for f in features[:3]]
            query_parts.append(
                f"Key prognostic factors: {', '.join(feature_names)}."
            )

        # Add severity scores
        if patient_data:
            if "apache_score" in patient_data:
                query_parts.append(f"APACHE II score: {patient_data['apache_score']}.")
            if "organ_failures" in patient_data:
                query_parts.append(
                    f"Number of organ failures: {patient_data['organ_failures']}."
                )

        query_parts.append(
            "What factors contribute to ICU mortality at this risk level? "
            "What are appropriate clinical interventions and when should goals of care be discussed?"
        )

        return " ".join(query_parts)

    def _extract_risk_factors(self, features: List) -> List[Dict]:
        """Extract and format key risk factors"""
        risk_factors = []

        for feature in features[:5]:  # Top 5 features
            if isinstance(feature, dict):
                risk_factors.append(
                    {
                        "name": feature.get("name", "Unknown"),
                        "importance": feature.get("importance", 0),
                        "value": feature.get("value"),
                    }
                )
            else:
                risk_factors.append({"name": str(feature), "importance": 0, "value": None})

        return risk_factors

    def _generate_sepsis_recommendations(
        self, risk_level: str, rag_result: Dict
    ) -> List[str]:
        """Generate specific recommendations based on risk level"""
        recommendations = []

        if risk_level == "critical" or risk_level == "high":
            recommendations.extend(
                [
                    "🚨 Immediate ICU assessment required",
                    "Initiate Surviving Sepsis Hour-1 Bundle",
                    "Measure lactate level immediately",
                    "Obtain blood cultures before antibiotics",
                    "Administer broad-spectrum antibiotics within 1 hour",
                    "Begin fluid resuscitation (30 mL/kg crystalloid)",
                    "Apply vasopressors if hypotensive (target MAP ≥ 65 mmHg)",
                    "Identify and control infection source",
                    "Serial lactate monitoring (q2-4h)",
                ]
            )
        elif risk_level == "medium":
            recommendations.extend(
                [
                    "⚠️ Close monitoring in ICU",
                    "Assess for sepsis criteria (qSOFA, SOFA)",
                    "Trend vital signs and labs",
                    "Consider source control measures",
                    "Prepare for potential escalation",
                ]
            )
        else:
            recommendations.extend(
                [
                    "✓ Continue routine monitoring",
                    "Monitor for early signs of deterioration",
                    "Maintain infection prevention practices",
                ]
            )

        # Add evidence-based recommendations from RAG
        if rag_result.get("confidence", 0) > 0.7:
            recommendations.append(
                "💡 See clinical guidance above for detailed evidence-based recommendations"
            )

        return recommendations

    def _generate_mortality_recommendations(
        self, risk_level: str, rag_result: Dict
    ) -> List[str]:
        """Generate recommendations for mortality risk management"""
        recommendations = []

        if risk_level == "critical" or risk_level == "high":
            recommendations.extend(
                [
                    "🚨 High mortality risk - consider:",
                    "Intensivist consultation for care optimization",
                    "Goals of care discussion with family",
                    "Palliative care consultation if appropriate",
                    "Review code status and advance directives",
                    "Assess for reversible causes",
                    "Maximize organ support therapies",
                    "Daily multidisciplinary rounds",
                ]
            )
        elif risk_level == "medium":
            recommendations.extend(
                [
                    "⚠️ Moderate risk - optimize:",
                    "Address reversible factors",
                    "Optimize organ support",
                    "Monitor response to therapy",
                    "Update family on prognosis",
                ]
            )
        else:
            recommendations.extend(
                [
                    "✓ Lower risk - continue:",
                    "Standard ICU care",
                    "Monitor for deterioration",
                    "Plan for step-down when stable",
                ]
            )

        return recommendations

    def explain_feature_importance(
        self, feature_name: str, feature_value: Optional[float] = None
    ) -> Dict:
        """
        Explain a specific feature's clinical significance

        Args:
            feature_name: Name of the feature (e.g., 'lactate', 'sofa_score')
            feature_value: Current value (optional)

        Returns:
            Clinical explanation
        """
        # Build query
        if feature_value is not None:
            query = f"Explain the clinical significance of {feature_name} = {feature_value} in ICU patients. What does this indicate?"
        else:
            query = f"Explain the clinical significance of {feature_name} in ICU risk assessment. What does this measure indicate?"

        try:
            result = self.rag.query(question=query, top_k=3, include_citations=True)

            return {
                "feature": feature_name,
                "value": feature_value,
                "explanation": result["answer"],
                "sources": result["citations"],
                "confidence": result["confidence"],
            }

        except Exception as e:
            logger.error(f"Failed to explain feature {feature_name}: {e}")
            return {
                "feature": feature_name,
                "value": feature_value,
                "explanation": f"Unable to generate explanation for {feature_name}. Please consult clinical reference.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e),
            }

    def compare_with_guidelines(
        self, prediction: Dict, patient_data: Dict, guideline_type: str = "sepsis"
    ) -> Dict:
        """
        Compare prediction with established clinical guidelines

        Args:
            prediction: Model prediction
            patient_data: Patient data
            guideline_type: 'sepsis' or 'mortality'

        Returns:
            Comparison with guidelines
        """
        if guideline_type == "sepsis":
            query = "What are the established criteria for sepsis diagnosis (qSOFA, SOFA, Sepsis-3)?"
        else:
            query = "What are standard ICU mortality risk stratification tools (APACHE II, SAPS II, SOFA)?"

        try:
            result = self.rag.query(question=query, top_k=3, category="guideline")

            return {
                "guideline_type": guideline_type,
                "established_criteria": result["answer"],
                "model_prediction": prediction,
                "alignment": self._assess_alignment(prediction, result),
                "sources": result["citations"],
            }

        except Exception as e:
            logger.error(f"Failed to compare with guidelines: {e}")
            return {
                "guideline_type": guideline_type,
                "established_criteria": "Unable to retrieve guidelines.",
                "model_prediction": prediction,
                "error": str(e),
            }

    def _assess_alignment(self, prediction: Dict, guideline: Dict) -> str:
        """Assess how prediction aligns with established guidelines"""
        # Simplified alignment assessment
        confidence = guideline.get("confidence", 0)

        if confidence > 0.7:
            return "Model prediction aligns with established clinical guidelines and evidence-based practice."
        elif confidence > 0.5:
            return "Model prediction is consistent with general clinical principles."
        else:
            return "Limited evidence available for comparison. Use clinical judgment."
