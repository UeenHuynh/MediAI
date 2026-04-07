"""
Unit tests for PredictionExplainer service
Tests RAG-based explanation of sepsis and mortality predictions
"""

import pytest
from unittest.mock import MagicMock, patch


class TestPredictionExplainerInit:
    """Tests for PredictionExplainer initialization"""

    def test_init_with_rag_pipeline(self):
        """Test initialization with RAG pipeline"""
        from api.services.prediction_explainer import PredictionExplainer

        mock_rag = MagicMock()
        explainer = PredictionExplainer(rag_pipeline=mock_rag)

        assert explainer.rag == mock_rag


class TestExplainSepsisPrediction:
    """Tests for explain_sepsis_prediction method"""

    @pytest.fixture
    def explainer(self):
        """Create explainer with mocked RAG"""
        from api.services.prediction_explainer import PredictionExplainer

        mock_rag = MagicMock()
        mock_rag.query.return_value = {
            "answer": "Clinical guidance for sepsis management",
            "citations": ["Source 1", "Source 2"],
            "confidence": 0.85
        }
        return PredictionExplainer(rag_pipeline=mock_rag)

    def test_explain_sepsis_high_risk(self, explainer):
        """Test explaining high risk sepsis prediction"""
        prediction = {
            "risk_score": 0.85,
            "risk_level": "high",
            "important_features": [
                {"name": "lactate", "importance": 0.3, "value": 4.5},
                {"name": "sofa_score", "importance": 0.25, "value": 8}
            ]
        }
        patient_data = {"sofa_score": 8, "lactate": 4.5}

        result = explainer.explain_sepsis_prediction(prediction, patient_data)

        assert result["risk_score"] == 0.85
        assert result["risk_level"] == "high"
        assert "clinical_guidance" in result
        assert "evidence_sources" in result
        assert "key_risk_factors" in result
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

    def test_explain_sepsis_medium_risk(self, explainer):
        """Test explaining medium risk sepsis"""
        prediction = {
            "risk_score": 0.45,
            "risk_level": "medium",
            "important_features": []
        }
        patient_data = {}

        result = explainer.explain_sepsis_prediction(prediction, patient_data)

        assert result["risk_level"] == "medium"
        assert "⚠️" in " ".join(result["recommendations"])

    def test_explain_sepsis_low_risk(self, explainer):
        """Test explaining low risk sepsis"""
        prediction = {
            "risk_score": 0.15,
            "risk_level": "low",
            "important_features": []
        }
        patient_data = {}

        result = explainer.explain_sepsis_prediction(prediction, patient_data)

        assert result["risk_level"] == "low"
        assert "✓" in " ".join(result["recommendations"])

    def test_explain_sepsis_with_error(self):
        """Test sepsis explanation handles RAG errors"""
        from api.services.prediction_explainer import PredictionExplainer

        mock_rag = MagicMock()
        mock_rag.query.side_effect = Exception("RAG error")
        explainer = PredictionExplainer(rag_pipeline=mock_rag)

        prediction = {"risk_score": 0.5, "risk_level": "medium"}
        result = explainer.explain_sepsis_prediction(prediction, {})

        assert "error" in result
        assert result["confidence"] == 0.0
        assert "Unable to generate explanation" in result["clinical_guidance"]

    def test_explain_sepsis_calls_rag_with_category(self, explainer):
        """Test that RAG is called with guideline category"""
        prediction = {"risk_score": 0.7, "risk_level": "high"}
        explainer.explain_sepsis_prediction(prediction, {})

        explainer.rag.query.assert_called_once()
        call_kwargs = explainer.rag.query.call_args[1]
        assert call_kwargs["category"] == "guideline"


class TestExplainMortalityPrediction:
    """Tests for explain_mortality_prediction method"""

    @pytest.fixture
    def explainer(self):
        """Create explainer with mocked RAG"""
        from api.services.prediction_explainer import PredictionExplainer

        mock_rag = MagicMock()
        mock_rag.query.return_value = {
            "answer": "Prognostic guidance for mortality",
            "citations": ["Study 1", "Study 2"],
            "confidence": 0.9
        }
        return PredictionExplainer(rag_pipeline=mock_rag)

    def test_explain_mortality_high_risk(self, explainer):
        """Test explaining high mortality risk"""
        prediction = {
            "risk_score": 0.75,
            "risk_level": "high",
            "important_features": [
                {"name": "apache_score", "importance": 0.4},
                {"name": "organ_failures", "importance": 0.3}
            ]
        }
        patient_data = {"apache_score": 28, "organ_failures": 3}

        result = explainer.explain_mortality_prediction(prediction, patient_data)

        assert result["risk_score"] == 0.75
        assert result["risk_level"] == "high"
        assert "prognostic_guidance" in result
        assert "key_prognostic_factors" in result
        assert "🚨" in " ".join(result["recommendations"])

    def test_explain_mortality_medium_risk(self, explainer):
        """Test explaining medium mortality risk"""
        prediction = {"risk_score": 0.35, "risk_level": "medium"}
        result = explainer.explain_mortality_prediction(prediction, {})

        assert "⚠️" in " ".join(result["recommendations"])

    def test_explain_mortality_with_error(self):
        """Test mortality explanation handles errors"""
        from api.services.prediction_explainer import PredictionExplainer

        mock_rag = MagicMock()
        mock_rag.query.side_effect = Exception("Query failed")
        explainer = PredictionExplainer(rag_pipeline=mock_rag)

        prediction = {"risk_score": 0.5, "risk_level": "medium"}
        result = explainer.explain_mortality_prediction(prediction, {})

        assert "error" in result
        assert result["confidence"] == 0.0


class TestBuildSepsisQuery:
    """Tests for _build_sepsis_query method"""

    @pytest.fixture
    def explainer(self):
        """Create explainer"""
        from api.services.prediction_explainer import PredictionExplainer
        return PredictionExplainer(rag_pipeline=MagicMock())

    def test_build_sepsis_query_basic(self, explainer):
        """Test building basic sepsis query"""
        query = explainer._build_sepsis_query(
            risk_score=0.75,
            risk_level="high",
            features=[],
            patient_data={}
        )

        assert "sepsis risk score of 75.0%" in query
        assert "high risk" in query
        assert "evidence-based guidelines" in query

    def test_build_sepsis_query_with_features(self, explainer):
        """Test sepsis query includes feature names"""
        features = [
            {"name": "lactate", "importance": 0.3},
            {"name": "sofa_score", "importance": 0.2},
            {"name": "temperature", "importance": 0.1}
        ]

        query = explainer._build_sepsis_query(0.8, "critical", features, {})

        assert "lactate" in query
        assert "sofa_score" in query
        assert "temperature" in query

    def test_build_sepsis_query_with_patient_data(self, explainer):
        """Test sepsis query includes patient clinical data"""
        patient_data = {"sofa_score": 8, "lactate": 4.2}

        query = explainer._build_sepsis_query(0.7, "high", [], patient_data)

        assert "SOFA score is 8" in query
        assert "Lactate is 4.2 mmol/L" in query


class TestBuildMortalityQuery:
    """Tests for _build_mortality_query method"""

    @pytest.fixture
    def explainer(self):
        """Create explainer"""
        from api.services.prediction_explainer import PredictionExplainer
        return PredictionExplainer(rag_pipeline=MagicMock())

    def test_build_mortality_query_basic(self, explainer):
        """Test building basic mortality query"""
        query = explainer._build_mortality_query(
            risk_score=0.65,
            risk_level="high",
            features=[],
            patient_data={}
        )

        assert "mortality risk of 65.0%" in query
        assert "high risk" in query
        assert "ICU mortality" in query

    def test_build_mortality_query_with_features(self, explainer):
        """Test mortality query includes prognostic factors"""
        features = [
            {"name": "apache_score"},
            {"name": "organ_failures"},
            {"name": "mechanical_ventilation"}
        ]

        query = explainer._build_mortality_query(0.7, "high", features, {})

        assert "apache_score" in query
        assert "organ_failures" in query

    def test_build_mortality_query_with_patient_data(self, explainer):
        """Test mortality query includes severity scores"""
        patient_data = {"apache_score": 25, "organ_failures": 2}

        query = explainer._build_mortality_query(0.6, "high", [], patient_data)

        assert "APACHE II score: 25" in query
        assert "Number of organ failures: 2" in query


class TestExtractRiskFactors:
    """Tests for _extract_risk_factors method"""

    @pytest.fixture
    def explainer(self):
        """Create explainer"""
        from api.services.prediction_explainer import PredictionExplainer
        return PredictionExplainer(rag_pipeline=MagicMock())

    def test_extract_risk_factors_from_dicts(self, explainer):
        """Test extracting risk factors from dict features"""
        features = [
            {"name": "lactate", "importance": 0.3, "value": 4.5},
            {"name": "sofa_score", "importance": 0.2, "value": 8}
        ]

        risk_factors = explainer._extract_risk_factors(features)

        assert len(risk_factors) == 2
        assert risk_factors[0]["name"] == "lactate"
        assert risk_factors[0]["importance"] == 0.3
        assert risk_factors[0]["value"] == 4.5

    def test_extract_risk_factors_from_strings(self, explainer):
        """Test extracting risk factors from string features"""
        features = ["feature1", "feature2", "feature3"]

        risk_factors = explainer._extract_risk_factors(features)

        assert len(risk_factors) == 3
        assert risk_factors[0]["name"] == "feature1"
        assert risk_factors[0]["importance"] == 0
        assert risk_factors[0]["value"] is None

    def test_extract_risk_factors_limits_to_five(self, explainer):
        """Test that only top 5 risk factors are extracted"""
        features = [{"name": f"feature_{i}"} for i in range(10)]

        risk_factors = explainer._extract_risk_factors(features)

        assert len(risk_factors) == 5


class TestGenerateSepsisRecommendations:
    """Tests for _generate_sepsis_recommendations method"""

    @pytest.fixture
    def explainer(self):
        """Create explainer"""
        from api.services.prediction_explainer import PredictionExplainer
        return PredictionExplainer(rag_pipeline=MagicMock())

    def test_generate_sepsis_recommendations_critical(self, explainer):
        """Test critical risk recommendations"""
        recommendations = explainer._generate_sepsis_recommendations(
            "critical", {"confidence": 0.8}
        )

        assert len(recommendations) > 5
        assert any("ICU assessment" in r for r in recommendations)
        assert any("Hour-1 Bundle" in r for r in recommendations)

    def test_generate_sepsis_recommendations_high(self, explainer):
        """Test high risk recommendations"""
        recommendations = explainer._generate_sepsis_recommendations(
            "high", {"confidence": 0.8}
        )

        assert any("antibiotics" in r for r in recommendations)
        assert any("lactate" in r for r in recommendations)

    def test_generate_sepsis_recommendations_medium(self, explainer):
        """Test medium risk recommendations"""
        recommendations = explainer._generate_sepsis_recommendations(
            "medium", {"confidence": 0.7}
        )

        assert any("monitoring" in r for r in recommendations)
        assert any("qSOFA" in r or "SOFA" in r for r in recommendations)

    def test_generate_sepsis_recommendations_low(self, explainer):
        """Test low risk recommendations"""
        recommendations = explainer._generate_sepsis_recommendations(
            "low", {"confidence": 0.5}
        )

        assert any("routine" in r for r in recommendations)

    def test_add_rag_recommendations_high_confidence(self, explainer):
        """Test RAG recommendations added for high confidence"""
        recommendations = explainer._generate_sepsis_recommendations(
            "high", {"confidence": 0.8}
        )

        assert any("clinical guidance" in r for r in recommendations)


class TestGenerateMortalityRecommendations:
    """Tests for _generate_mortality_recommendations method"""

    @pytest.fixture
    def explainer(self):
        """Create explainer"""
        from api.services.prediction_explainer import PredictionExplainer
        return PredictionExplainer(rag_pipeline=MagicMock())

    def test_generate_mortality_recommendations_critical(self, explainer):
        """Test critical mortality risk recommendations"""
        recommendations = explainer._generate_mortality_recommendations(
            "critical", {}
        )

        # Check for critical risk indicators
        assert len(recommendations) > 5
        assert any("goals of care" in r.lower() for r in recommendations)
        assert any("palliative" in r.lower() for r in recommendations)

    def test_generate_mortality_recommendations_medium(self, explainer):
        """Test medium mortality risk recommendations"""
        recommendations = explainer._generate_mortality_recommendations(
            "medium", {}
        )

        assert any("optimize" in r.lower() for r in recommendations)

    def test_generate_mortality_recommendations_low(self, explainer):
        """Test low mortality risk recommendations"""
        recommendations = explainer._generate_mortality_recommendations(
            "low", {}
        )

        assert any("Standard ICU care" in r for r in recommendations)


class TestExplainFeatureImportance:
    """Tests for explain_feature_importance method"""

    @pytest.fixture
    def explainer(self):
        """Create explainer with mocked RAG"""
        from api.services.prediction_explainer import PredictionExplainer

        mock_rag = MagicMock()
        mock_rag.query.return_value = {
            "answer": "Lactate measures tissue hypoperfusion",
            "citations": ["Reference 1"],
            "confidence": 0.85
        }
        return PredictionExplainer(rag_pipeline=mock_rag)

    def test_explain_feature_with_value(self, explainer):
        """Test explaining feature with specific value"""
        result = explainer.explain_feature_importance("lactate", 4.5)

        assert result["feature"] == "lactate"
        assert result["value"] == 4.5
        assert "explanation" in result
        assert "sources" in result
        assert result["confidence"] == 0.85

    def test_explain_feature_without_value(self, explainer):
        """Test explaining feature without value"""
        result = explainer.explain_feature_importance("sofa_score")

        assert result["feature"] == "sofa_score"
        assert result["value"] is None
        assert "explanation" in result

    def test_explain_feature_with_error(self):
        """Test feature explanation handles errors"""
        from api.services.prediction_explainer import PredictionExplainer

        mock_rag = MagicMock()
        mock_rag.query.side_effect = Exception("Query error")
        explainer = PredictionExplainer(rag_pipeline=mock_rag)

        result = explainer.explain_feature_importance("lactate")

        assert "error" in result
        assert result["confidence"] == 0.0
        assert "Unable to generate explanation" in result["explanation"]


class TestCompareWithGuidelines:
    """Tests for compare_with_guidelines method"""

    @pytest.fixture
    def explainer(self):
        """Create explainer with mocked RAG"""
        from api.services.prediction_explainer import PredictionExplainer

        mock_rag = MagicMock()
        mock_rag.query.return_value = {
            "answer": "Sepsis-3 criteria include...",
            "citations": ["Sepsis-3 Guidelines"],
            "confidence": 0.9
        }
        return PredictionExplainer(rag_pipeline=mock_rag)

    def test_compare_with_sepsis_guidelines(self, explainer):
        """Test comparing with sepsis guidelines"""
        prediction = {"risk_score": 0.8, "risk_level": "high"}
        patient_data = {}

        result = explainer.compare_with_guidelines(
            prediction, patient_data, guideline_type="sepsis"
        )

        assert result["guideline_type"] == "sepsis"
        assert "established_criteria" in result
        assert "model_prediction" in result
        assert "alignment" in result

    def test_compare_with_mortality_guidelines(self, explainer):
        """Test comparing with mortality guidelines"""
        prediction = {"risk_score": 0.6}
        result = explainer.compare_with_guidelines(
            prediction, {}, guideline_type="mortality"
        )

        assert result["guideline_type"] == "mortality"
        assert "APACHE" in result["established_criteria"] or "established_criteria" in result

    def test_compare_with_guidelines_error(self):
        """Test guidelines comparison handles errors"""
        from api.services.prediction_explainer import PredictionExplainer

        mock_rag = MagicMock()
        mock_rag.query.side_effect = Exception("Query failed")
        explainer = PredictionExplainer(rag_pipeline=mock_rag)

        result = explainer.compare_with_guidelines({}, {})

        assert "error" in result
        assert "Unable to retrieve guidelines" in result["established_criteria"]


class TestAssessAlignment:
    """Tests for _assess_alignment method"""

    @pytest.fixture
    def explainer(self):
        """Create explainer"""
        from api.services.prediction_explainer import PredictionExplainer
        return PredictionExplainer(rag_pipeline=MagicMock())

    def test_assess_alignment_high_confidence(self, explainer):
        """Test alignment assessment with high confidence"""
        guideline = {"confidence": 0.8}
        alignment = explainer._assess_alignment({}, guideline)

        assert "aligns with established clinical guidelines" in alignment

    def test_assess_alignment_medium_confidence(self, explainer):
        """Test alignment assessment with medium confidence"""
        guideline = {"confidence": 0.6}
        alignment = explainer._assess_alignment({}, guideline)

        assert "consistent with general clinical principles" in alignment

    def test_assess_alignment_low_confidence(self, explainer):
        """Test alignment assessment with low confidence"""
        guideline = {"confidence": 0.3}
        alignment = explainer._assess_alignment({}, guideline)

        assert "Limited evidence" in alignment
        assert "clinical judgment" in alignment


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    @pytest.fixture
    def explainer(self):
        """Create explainer with mocked RAG"""
        from api.services.prediction_explainer import PredictionExplainer

        mock_rag = MagicMock()
        mock_rag.query.return_value = {
            "answer": "Response",
            "citations": [],
            "confidence": 0.5
        }
        return PredictionExplainer(rag_pipeline=mock_rag)

    def test_empty_prediction(self, explainer):
        """Test handling empty prediction dict"""
        result = explainer.explain_sepsis_prediction({}, {})

        assert result["risk_score"] == 0
        assert result["risk_level"] == "unknown"

    def test_missing_features(self, explainer):
        """Test handling missing important_features key"""
        prediction = {"risk_score": 0.5, "risk_level": "medium"}
        result = explainer.explain_sepsis_prediction(prediction, {})

        assert "key_risk_factors" in result
        assert len(result["key_risk_factors"]) == 0

    def test_none_patient_data(self, explainer):
        """Test handling None patient_data"""
        prediction = {"risk_score": 0.5, "risk_level": "medium"}
        result = explainer.explain_sepsis_prediction(prediction, None)

        assert "clinical_guidance" in result

    def test_feature_without_name(self, explainer):
        """Test handling features without 'name' key"""
        features = [{"importance": 0.5}, {"value": 10}]
        risk_factors = explainer._extract_risk_factors(features)

        assert risk_factors[0]["name"] == "Unknown"
