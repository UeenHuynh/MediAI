"""
Unit tests for Prediction History router
Tests prediction history API endpoints
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException


class TestPredictionHistoryRouterConfig:
    """Tests for prediction history router configuration"""

    def test_router_exists(self):
        """Test prediction history router exists"""
        from api.routers.prediction_history import router
        assert router is not None

    def test_router_has_endpoints(self):
        """Test router has endpoints registered"""
        from api.routers.prediction_history import router
        assert len(router.routes) > 0

    def test_router_prefix(self):
        """Test router has correct prefix"""
        from api.routers.prediction_history import router
        assert router.prefix == "/predictions"


class TestGetPredictionEndpoint:
    """Tests for GET /{prediction_id} endpoint"""

    def test_get_prediction_success(self):
        """Test successful retrieval of prediction by ID"""
        from api.routers.prediction_history import get_prediction

        mock_db = MagicMock()
        mock_prediction = {
            "id": 1,
            "patient_id": 123,
            "prediction_type": "sepsis",
            "risk_score": 0.75
        }

        with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
            mock_service.get_prediction.return_value = mock_prediction

            result = get_prediction(prediction_id=1, db=mock_db)

            assert result == mock_prediction
            mock_service.get_prediction.assert_called_once_with(mock_db, 1)

    def test_get_prediction_not_found(self):
        """Test 404 when prediction not found"""
        from api.routers.prediction_history import get_prediction

        mock_db = MagicMock()

        with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
            mock_service.get_prediction.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                get_prediction(prediction_id=999, db=mock_db)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()


class TestGetPatientPredictionsEndpoint:
    """Tests for GET /patient/{patient_id}/history endpoint"""

    def test_get_patient_predictions_success(self):
        """Test successful retrieval of patient predictions"""
        from api.routers.prediction_history import get_patient_predictions

        mock_db = MagicMock()
        mock_patient = {"id": 123, "name": "Test Patient"}

        with patch('api.routers.prediction_history.PatientService') as mock_patient_service:
            with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
                with patch('api.routers.prediction_history.PredictionListResponse') as mock_response:
                    mock_patient_service.get_patient.return_value = mock_patient
                    mock_service.list_predictions_for_patient.return_value = ([], 2)

                    mock_response_instance = MagicMock()
                    mock_response_instance.total = 2
                    mock_response.return_value = mock_response_instance

                    result = get_patient_predictions(
                        patient_id=123,
                        prediction_type=None,
                        page=1,
                        page_size=50,
                        db=mock_db
                    )

                    assert result.total == 2
                    mock_response.assert_called_once_with(
                        total=2, predictions=[], page=1, page_size=50
                    )

    def test_get_patient_predictions_with_type_filter(self):
        """Test filtering patient predictions by type"""
        from api.routers.prediction_history import get_patient_predictions

        mock_db = MagicMock()
        mock_patient = {"id": 123}

        with patch('api.routers.prediction_history.PatientService') as mock_patient_service:
            with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
                with patch('api.routers.prediction_history.PredictionListResponse'):
                    mock_patient_service.get_patient.return_value = mock_patient
                    mock_service.list_predictions_for_patient.return_value = ([], 1)

                    get_patient_predictions(
                        patient_id=123,
                        prediction_type="sepsis",
                        page=1,
                        page_size=50,
                        db=mock_db
                    )

                    mock_service.list_predictions_for_patient.assert_called_once_with(
                        mock_db,
                        patient_id=123,
                        prediction_type="sepsis",
                        skip=0,
                        limit=50
                    )

    def test_get_patient_predictions_patient_not_found(self):
        """Test 404 when patient not found"""
        from api.routers.prediction_history import get_patient_predictions

        mock_db = MagicMock()

        with patch('api.routers.prediction_history.PatientService') as mock_patient_service:
            mock_patient_service.get_patient.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                get_patient_predictions(
                    patient_id=999,
                    prediction_type=None,
                    page=1,
                    page_size=50,
                    db=mock_db
                )

            assert exc_info.value.status_code == 404
            assert "Patient" in exc_info.value.detail

    def test_get_patient_predictions_pagination(self):
        """Test pagination parameters work correctly"""
        from api.routers.prediction_history import get_patient_predictions

        mock_db = MagicMock()
        mock_patient = {"id": 123}

        with patch('api.routers.prediction_history.PatientService') as mock_patient_service:
            with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
                with patch('api.routers.prediction_history.PredictionListResponse'):
                    mock_patient_service.get_patient.return_value = mock_patient
                    mock_service.list_predictions_for_patient.return_value = ([], 100)

                    get_patient_predictions(
                        patient_id=123,
                        prediction_type=None,
                        page=2,
                        page_size=10,
                        db=mock_db
                    )

                    # skip should be (2-1)*10 = 10
                    mock_service.list_predictions_for_patient.assert_called_once_with(
                        mock_db,
                        patient_id=123,
                        prediction_type=None,
                        skip=10,
                        limit=10
                    )


class TestListAllPredictionsEndpoint:
    """Tests for GET / endpoint"""

    def test_list_all_predictions_success(self):
        """Test successful listing of all predictions"""
        from api.routers.prediction_history import list_all_predictions

        mock_db = MagicMock()

        with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
            with patch('api.routers.prediction_history.PredictionListResponse'):
                mock_service.list_all_predictions.return_value = ([], 2)

                list_all_predictions(
                    prediction_type=None,
                    risk_category=None,
                    page=1,
                    page_size=50,
                    db=mock_db
                )

                mock_service.list_all_predictions.assert_called_once_with(
                    mock_db,
                    prediction_type=None,
                    risk_category=None,
                    skip=0,
                    limit=50
                )

    def test_list_all_predictions_with_filters(self):
        """Test listing with prediction type and risk category filters"""
        from api.routers.prediction_history import list_all_predictions

        mock_db = MagicMock()

        with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
            with patch('api.routers.prediction_history.PredictionListResponse'):
                mock_service.list_all_predictions.return_value = ([], 1)

                list_all_predictions(
                    prediction_type="sepsis",
                    risk_category="high",
                    page=1,
                    page_size=50,
                    db=mock_db
                )

                mock_service.list_all_predictions.assert_called_once_with(
                    mock_db,
                    prediction_type="sepsis",
                    risk_category="high",
                    skip=0,
                    limit=50
                )


class TestGetLatestPredictionEndpoint:
    """Tests for GET /patient/{patient_id}/latest/{prediction_type} endpoint"""

    def test_get_latest_prediction_success(self):
        """Test successful retrieval of latest prediction"""
        from api.routers.prediction_history import get_latest_prediction

        mock_db = MagicMock()
        mock_patient = {"id": 123}
        mock_prediction = {
            "id": 5,
            "patient_id": 123,
            "prediction_type": "sepsis",
            "risk_score": 0.65
        }

        with patch('api.routers.prediction_history.PatientService') as mock_patient_service:
            with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
                mock_patient_service.get_patient.return_value = mock_patient
                mock_service.get_latest_prediction_for_patient.return_value = mock_prediction

                result = get_latest_prediction(
                    patient_id=123,
                    prediction_type="sepsis",
                    db=mock_db
                )

                assert result == mock_prediction
                mock_service.get_latest_prediction_for_patient.assert_called_once_with(
                    mock_db, 123, "sepsis"
                )

    def test_get_latest_prediction_patient_not_found(self):
        """Test 404 when patient not found"""
        from api.routers.prediction_history import get_latest_prediction

        mock_db = MagicMock()

        with patch('api.routers.prediction_history.PatientService') as mock_patient_service:
            mock_patient_service.get_patient.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                get_latest_prediction(
                    patient_id=999,
                    prediction_type="sepsis",
                    db=mock_db
                )

            assert exc_info.value.status_code == 404
            assert "Patient" in exc_info.value.detail

    def test_get_latest_prediction_invalid_type(self):
        """Test 400 when prediction type is invalid"""
        from api.routers.prediction_history import get_latest_prediction

        mock_db = MagicMock()
        mock_patient = {"id": 123}

        with patch('api.routers.prediction_history.PatientService') as mock_patient_service:
            mock_patient_service.get_patient.return_value = mock_patient

            with pytest.raises(HTTPException) as exc_info:
                get_latest_prediction(
                    patient_id=123,
                    prediction_type="invalid_type",
                    db=mock_db
                )

            assert exc_info.value.status_code == 400
            assert "sepsis" in exc_info.value.detail.lower()
            assert "mortality" in exc_info.value.detail.lower()

    def test_get_latest_prediction_no_predictions_found(self):
        """Test 404 when no predictions exist for patient"""
        from api.routers.prediction_history import get_latest_prediction

        mock_db = MagicMock()
        mock_patient = {"id": 123}

        with patch('api.routers.prediction_history.PatientService') as mock_patient_service:
            with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
                mock_patient_service.get_patient.return_value = mock_patient
                mock_service.get_latest_prediction_for_patient.return_value = None

                with pytest.raises(HTTPException) as exc_info:
                    get_latest_prediction(
                        patient_id=123,
                        prediction_type="sepsis",
                        db=mock_db
                    )

                assert exc_info.value.status_code == 404
                assert "No" in exc_info.value.detail


class TestUpdatePredictionOutcomeEndpoint:
    """Tests for POST /{prediction_id}/outcome endpoint"""

    def test_update_outcome_success(self):
        """Test successful outcome update"""
        from api.routers.prediction_history import update_prediction_outcome, OutcomeUpdate

        mock_db = MagicMock()
        outcome_data = OutcomeUpdate(
            actual_outcome=True,
            outcome_notes="Patient developed sepsis"
        )
        mock_updated_prediction = {
            "id": 1,
            "actual_outcome": True,
            "outcome_notes": "Patient developed sepsis"
        }

        with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
            mock_service.update_outcome.return_value = mock_updated_prediction

            result = update_prediction_outcome(
                prediction_id=1,
                outcome_data=outcome_data,
                db=mock_db
            )

            assert result == mock_updated_prediction
            mock_service.update_outcome.assert_called_once_with(
                mock_db, 1, True, "Patient developed sepsis"
            )

    def test_update_outcome_prediction_not_found(self):
        """Test 404 when prediction not found"""
        from api.routers.prediction_history import update_prediction_outcome, OutcomeUpdate

        mock_db = MagicMock()
        outcome_data = OutcomeUpdate(
            actual_outcome=False,
            outcome_notes="No sepsis developed"
        )

        with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
            mock_service.update_outcome.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                update_prediction_outcome(
                    prediction_id=999,
                    outcome_data=outcome_data,
                    db=mock_db
                )

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()

    def test_update_outcome_without_notes(self):
        """Test outcome update without optional notes"""
        from api.routers.prediction_history import update_prediction_outcome, OutcomeUpdate

        mock_db = MagicMock()
        outcome_data = OutcomeUpdate(actual_outcome=False)
        mock_updated_prediction = {"id": 1, "actual_outcome": False}

        with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
            mock_service.update_outcome.return_value = mock_updated_prediction

            result = update_prediction_outcome(
                prediction_id=1,
                outcome_data=outcome_data,
                db=mock_db
            )

            assert result == mock_updated_prediction
            mock_service.update_outcome.assert_called_once_with(
                mock_db, 1, False, None
            )


class TestGetPredictionStatisticsEndpoint:
    """Tests for GET /statistics endpoint"""

    def test_get_statistics_success(self):
        """Test successful retrieval of statistics"""
        from api.routers.prediction_history import get_prediction_statistics

        mock_db = MagicMock()
        mock_stats = {
            "total_predictions": 100,
            "by_type": {"sepsis": 60, "mortality": 40},
            "by_risk": {"low": 30, "medium": 40, "high": 20, "critical": 10},
            "avg_risk_score": 0.55
        }

        with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
            mock_service.get_prediction_statistics.return_value = mock_stats

            result = get_prediction_statistics(
                prediction_type=None,
                db=mock_db
            )

            assert result == mock_stats
            mock_service.get_prediction_statistics.assert_called_once_with(mock_db, None)

    def test_get_statistics_with_type_filter(self):
        """Test statistics filtered by prediction type"""
        from api.routers.prediction_history import get_prediction_statistics

        mock_db = MagicMock()
        mock_stats = {
            "total_predictions": 60,
            "by_type": {"sepsis": 60},
            "avg_risk_score": 0.62
        }

        with patch('api.routers.prediction_history.PredictionHistoryService') as mock_service:
            mock_service.get_prediction_statistics.return_value = mock_stats

            result = get_prediction_statistics(
                prediction_type="sepsis",
                db=mock_db
            )

            assert result == mock_stats
            mock_service.get_prediction_statistics.assert_called_once_with(mock_db, "sepsis")


class TestOutcomeUpdateSchema:
    """Tests for OutcomeUpdate schema"""

    def test_outcome_update_with_notes(self):
        """Test OutcomeUpdate schema with notes"""
        from api.routers.prediction_history import OutcomeUpdate

        outcome = OutcomeUpdate(
            actual_outcome=True,
            outcome_notes="Patient condition worsened"
        )

        assert outcome.actual_outcome is True
        assert outcome.outcome_notes == "Patient condition worsened"

    def test_outcome_update_without_notes(self):
        """Test OutcomeUpdate schema without notes"""
        from api.routers.prediction_history import OutcomeUpdate

        outcome = OutcomeUpdate(actual_outcome=False)

        assert outcome.actual_outcome is False
        assert outcome.outcome_notes is None
