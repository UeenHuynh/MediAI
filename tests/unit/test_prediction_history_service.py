"""
Unit tests for Prediction History Service

Tests saving and retrieving prediction history with mocked database.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from decimal import Decimal

# Import the service under test
import sys
sys.path.insert(0, '/home/neeyuhuynh/Desktop/MediAI')

from api.services.prediction_history_service import PredictionHistoryService


class TestPredictionHistoryService:
    """Test suite for PredictionHistoryService."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = MagicMock()
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        db.query = MagicMock()
        return db

    @pytest.fixture
    def mock_prediction(self):
        """Create a mock prediction object."""
        prediction = MagicMock()
        prediction.id = 1
        prediction.prediction_type = "sepsis"
        prediction.risk_score = Decimal("0.75")
        prediction.risk_category = "high"
        prediction.patient_id = 1
        prediction.created_at = datetime(2026, 1, 7, 10, 0, 0)
        prediction.input_features = {"heart_rate": 100, "temperature": 38.5}
        prediction.shap_values = {"heart_rate": 0.15}
        return prediction

    @pytest.fixture
    def sample_prediction_data(self):
        """Sample prediction data for saving."""
        return {
            "prediction_type": "sepsis",
            "input_features": {"heart_rate": 100, "temperature": 38.5},
            "risk_score": 0.75,
            "risk_percentage": 75.0,
            "model_version": "v2.0.0",
            "model_file": "sepsis_model.pkl",
            "shap_values": {"heart_rate": 0.15},
            "top_features": [{"feature": "heart_rate", "importance": 0.15}],
            "patient_id": 1,
            "predicted_by": 1
        }

    @patch('api.services.prediction_history_service.Prediction')
    def test_save_prediction_success(self, MockPrediction, mock_db, sample_prediction_data):
        """Test successful prediction save."""
        # Setup
        mock_prediction_instance = MagicMock()
        MockPrediction.return_value = mock_prediction_instance

        # Execute
        result = PredictionHistoryService.save_prediction(
            mock_db,
            prediction_type=sample_prediction_data["prediction_type"],
            input_features=sample_prediction_data["input_features"],
            risk_score=sample_prediction_data["risk_score"],
            risk_percentage=sample_prediction_data["risk_percentage"],
            model_version=sample_prediction_data["model_version"],
            model_file=sample_prediction_data["model_file"],
            shap_values=sample_prediction_data["shap_values"],
            top_features=sample_prediction_data["top_features"],
            patient_id=sample_prediction_data["patient_id"],
            predicted_by=sample_prediction_data["predicted_by"]
        )

        # Verify
        MockPrediction.assert_called_once()
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @patch('api.services.prediction_history_service.Prediction')
    def test_save_sepsis_prediction(self, MockPrediction, mock_db):
        """Test saving a sepsis prediction."""
        mock_prediction_instance = MagicMock()
        MockPrediction.return_value = mock_prediction_instance

        # Execute
        PredictionHistoryService.save_prediction(
            mock_db,
            prediction_type="sepsis",
            input_features={"temperature": 39.0},
            risk_score=0.85,
            risk_percentage=85.0
        )

        # Verify sepsis type is passed
        call_kwargs = MockPrediction.call_args[1]
        assert call_kwargs['prediction_type'] == "sepsis"

    @patch('api.services.prediction_history_service.Prediction')
    def test_save_mortality_prediction(self, MockPrediction, mock_db):
        """Test saving a mortality prediction."""
        mock_prediction_instance = MagicMock()
        MockPrediction.return_value = mock_prediction_instance

        # Execute
        PredictionHistoryService.save_prediction(
            mock_db,
            prediction_type="mortality",
            input_features={"gcs_total": 8},
            risk_score=0.65,
            risk_percentage=65.0
        )

        # Verify mortality type is passed
        call_kwargs = MockPrediction.call_args[1]
        assert call_kwargs['prediction_type'] == "mortality"

    def test_get_prediction_found(self, mock_db, mock_prediction):
        """Test getting an existing prediction."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = mock_prediction
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        result = PredictionHistoryService.get_prediction(mock_db, prediction_id=1)

        # Verify
        assert result == mock_prediction
        assert result.id == 1

    def test_get_prediction_not_found(self, mock_db):
        """Test getting a non-existent prediction."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        result = PredictionHistoryService.get_prediction(mock_db, prediction_id=999)

        # Verify
        assert result is None

    def test_list_predictions_for_patient(self, mock_db, mock_prediction):
        """Test listing predictions for a specific patient."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.filter.return_value = mock_filter
        mock_filter.count.return_value = 3
        mock_order = MagicMock()
        mock_order.offset.return_value.limit.return_value.all.return_value = [mock_prediction] * 3
        mock_filter.order_by.return_value = mock_order
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        predictions, total = PredictionHistoryService.list_predictions_for_patient(
            mock_db, patient_id=1
        )

        # Verify
        assert total == 3
        assert len(predictions) == 3

    def test_list_predictions_for_patient_filtered_by_type(self, mock_db, mock_prediction):
        """Test filtering predictions by type."""
        # Setup
        mock_query = MagicMock()
        mock_filter1 = MagicMock()
        mock_filter2 = MagicMock()
        mock_filter2.count.return_value = 2
        mock_filter2.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_prediction] * 2
        mock_filter1.filter.return_value = mock_filter2
        mock_query.filter.return_value = mock_filter1
        mock_db.query.return_value = mock_query

        # Execute
        predictions, total = PredictionHistoryService.list_predictions_for_patient(
            mock_db, patient_id=1, prediction_type="sepsis"
        )

        # Verify filter was applied
        assert total == 2
        mock_filter1.filter.assert_called()

    def test_list_all_predictions(self, mock_db, mock_prediction):
        """Test listing all predictions."""
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 10
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_prediction] * 10
        mock_db.query.return_value = mock_query

        # Execute
        predictions, total = PredictionHistoryService.list_all_predictions(mock_db)

        # Verify
        assert total == 10
        assert len(predictions) == 10

    def test_list_all_predictions_with_risk_filter(self, mock_db, mock_prediction):
        """Test filtering all predictions by risk category."""
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_prediction] * 5
        mock_db.query.return_value = mock_query

        # Execute
        predictions, total = PredictionHistoryService.list_all_predictions(
            mock_db, risk_category="high"
        )

        # Verify
        assert total == 5

    def test_get_latest_prediction_for_patient(self, mock_db, mock_prediction):
        """Test getting the most recent prediction for a patient."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_order = MagicMock()
        mock_order.first.return_value = mock_prediction
        mock_filter.order_by.return_value = mock_order
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        result = PredictionHistoryService.get_latest_prediction_for_patient(
            mock_db, patient_id=1, prediction_type="sepsis"
        )

        # Verify
        assert result == mock_prediction

    @patch.object(PredictionHistoryService, 'get_prediction')
    def test_update_outcome_success(self, mock_get_prediction, mock_db, mock_prediction):
        """Test updating prediction outcome."""
        # Setup
        mock_get_prediction.return_value = mock_prediction

        # Execute
        result = PredictionHistoryService.update_outcome(
            mock_db,
            prediction_id=1,
            actual_outcome=True,
            outcome_notes="Patient developed sepsis"
        )

        # Verify
        assert result == mock_prediction
        assert mock_prediction.actual_outcome is True
        assert mock_prediction.outcome_notes == "Patient developed sepsis"
        mock_db.commit.assert_called_once()

    @patch.object(PredictionHistoryService, 'get_prediction')
    def test_update_outcome_not_found(self, mock_get_prediction, mock_db):
        """Test updating outcome for non-existent prediction."""
        # Setup
        mock_get_prediction.return_value = None

        # Execute
        result = PredictionHistoryService.update_outcome(
            mock_db,
            prediction_id=999,
            actual_outcome=True
        )

        # Verify
        assert result is None
        mock_db.commit.assert_not_called()


class TestPredictionStatistics:
    """Test prediction statistics functionality."""

    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        return db

    def test_get_prediction_statistics(self, mock_db):
        """Test getting prediction statistics."""
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 100
        mock_db.query.return_value = mock_query

        # Execute
        stats = PredictionHistoryService.get_prediction_statistics(mock_db)

        # Verify
        assert isinstance(stats, dict)
        mock_db.query.assert_called()

    def test_get_prediction_statistics_by_type(self, mock_db):
        """Test getting statistics filtered by prediction type."""
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 50
        mock_db.query.return_value = mock_query

        # Execute
        stats = PredictionHistoryService.get_prediction_statistics(
            mock_db, prediction_type="sepsis"
        )

        # Verify
        assert isinstance(stats, dict)


class TestRiskCategoryClassification:
    """Test risk category classification."""

    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        return db

    @patch('api.services.prediction_history_service.Prediction')
    def test_high_risk_classification(self, MockPrediction, mock_db):
        """Test that high risk score gets high category."""
        mock_prediction = MagicMock()
        MockPrediction.return_value = mock_prediction

        # Execute with high risk percentage (>= 70 is critical, 30-70 is high)
        PredictionHistoryService.save_prediction(
            mock_db,
            prediction_type="sepsis",
            input_features={},
            risk_score=0.50,
            risk_percentage=50.0  # 30-70 = high
        )

        call_kwargs = MockPrediction.call_args[1]
        assert call_kwargs['risk_category'] == "high"

    @patch('api.services.prediction_history_service.Prediction')
    def test_low_risk_classification(self, MockPrediction, mock_db):
        """Test that low risk score gets low category."""
        mock_prediction = MagicMock()
        MockPrediction.return_value = mock_prediction

        # Execute with low risk percentage (< 10 = low)
        PredictionHistoryService.save_prediction(
            mock_db,
            prediction_type="sepsis",
            input_features={},
            risk_score=0.05,
            risk_percentage=5.0  # < 10 = low
        )

        call_kwargs = MockPrediction.call_args[1]
        assert call_kwargs['risk_category'] == "low"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
