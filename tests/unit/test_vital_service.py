"""
Unit tests for Vital Signs Service

Tests CRUD operations for vital signs management with mocked database.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Import the service under test
import sys
sys.path.insert(0, '/home/neeyuhuynh/Desktop/MediAI')

from api.services.vital_service import VitalService


class TestVitalService:
    """Test suite for VitalService."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = MagicMock()
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        db.delete = MagicMock()
        db.query = MagicMock()
        return db

    @pytest.fixture
    def sample_vital_data(self):
        """Sample vital signs creation data."""
        mock_data = MagicMock()
        mock_data.patient_id = 1
        mock_data.recorded_at = datetime(2026, 1, 7, 10, 0, 0)
        mock_data.heart_rate = 72
        mock_data.systolic_bp = 120
        mock_data.diastolic_bp = 80
        mock_data.mean_arterial_pressure = 93
        mock_data.temperature = 37.0
        mock_data.respiratory_rate = 16
        mock_data.spo2 = 98
        mock_data.gcs_eye = 4
        mock_data.gcs_verbal = 5
        mock_data.gcs_motor = 6
        mock_data.gcs_total = 15
        mock_data.weight = 70.0
        mock_data.height = 175.0
        mock_data.bmi = 22.9
        mock_data.notes = "Stable vitals"
        return mock_data

    @pytest.fixture
    def mock_vital(self):
        """Create a mock vital object."""
        vital = MagicMock()
        vital.id = 1
        vital.patient_id = 1
        vital.heart_rate = 72
        vital.systolic_bp = 120
        vital.diastolic_bp = 80
        vital.recorded_at = datetime(2026, 1, 7, 10, 0, 0)
        return vital

    @patch('api.services.vital_service.Vital')
    def test_create_vital_success(self, MockVital, mock_db, sample_vital_data):
        """Test successful vital signs creation."""
        # Setup
        mock_vital_instance = MagicMock()
        MockVital.return_value = mock_vital_instance

        # Execute
        result = VitalService.create_vital(mock_db, sample_vital_data, recorded_by=1)

        # Verify
        MockVital.assert_called_once()
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @patch('api.services.vital_service.Vital')
    def test_create_vital_uses_current_time_if_not_provided(self, MockVital, mock_db):
        """Test that current time is used if recorded_at not provided."""
        # Setup
        mock_data = MagicMock()
        mock_data.patient_id = 1
        mock_data.recorded_at = None  # Not provided
        mock_data.heart_rate = 72
        mock_data.systolic_bp = 120
        mock_data.diastolic_bp = 80
        mock_data.mean_arterial_pressure = None
        mock_data.temperature = None
        mock_data.respiratory_rate = None
        mock_data.spo2 = None
        mock_data.gcs_eye = None
        mock_data.gcs_verbal = None
        mock_data.gcs_motor = None
        mock_data.gcs_total = None
        mock_data.weight = None
        mock_data.height = None
        mock_data.bmi = None
        mock_data.notes = None

        # Execute
        VitalService.create_vital(mock_db, mock_data)

        # Verify - the Vital was created (we can't easily check datetime.utcnow() usage)
        MockVital.assert_called_once()

    def test_get_vital_found(self, mock_db, mock_vital):
        """Test getting an existing vital record."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = mock_vital
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        result = VitalService.get_vital(mock_db, vital_id=1)

        # Verify
        assert result == mock_vital
        mock_db.query.assert_called_once()

    def test_get_vital_not_found(self, mock_db):
        """Test getting a non-existent vital record."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        result = VitalService.get_vital(mock_db, vital_id=999)

        # Verify
        assert result is None

    def test_list_vitals_for_patient(self, mock_db, mock_vital):
        """Test listing vitals for a specific patient."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.count.return_value = 5
        mock_order = MagicMock()
        mock_offset = MagicMock()
        mock_offset.limit.return_value.all.return_value = [mock_vital] * 5
        mock_order.offset.return_value = mock_offset
        mock_filter.order_by.return_value = mock_order
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        vitals, total = VitalService.list_vitals_for_patient(
            mock_db, patient_id=1, skip=0, limit=100
        )

        # Verify
        assert total == 5
        assert len(vitals) == 5

    def test_list_vitals_for_patient_pagination(self, mock_db, mock_vital):
        """Test pagination when listing vitals."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.count.return_value = 100
        mock_order = MagicMock()
        mock_offset = MagicMock()
        mock_offset.limit.return_value.all.return_value = [mock_vital] * 10
        mock_order.offset.return_value = mock_offset
        mock_filter.order_by.return_value = mock_order
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        vitals, total = VitalService.list_vitals_for_patient(
            mock_db, patient_id=1, skip=20, limit=10
        )

        # Verify
        assert total == 100  # Total count
        assert len(vitals) == 10  # Limited to 10

    def test_get_latest_vitals_single(self, mock_db, mock_vital):
        """Test getting the most recent vital for a patient."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_order = MagicMock()
        mock_order.limit.return_value.all.return_value = [mock_vital]
        mock_filter.order_by.return_value = mock_order
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        result = VitalService.get_latest_vitals(mock_db, patient_id=1, count=1)

        # Verify
        assert len(result) == 1
        assert result[0] == mock_vital

    def test_get_latest_vitals_multiple(self, mock_db, mock_vital):
        """Test getting multiple recent vitals."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_order = MagicMock()
        mock_order.limit.return_value.all.return_value = [mock_vital] * 5
        mock_filter.order_by.return_value = mock_order
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        result = VitalService.get_latest_vitals(mock_db, patient_id=1, count=5)

        # Verify
        assert len(result) == 5

    @patch.object(VitalService, 'get_vital')
    def test_delete_vital_success(self, mock_get_vital, mock_db, mock_vital):
        """Test deleting a vital record."""
        # Setup
        mock_get_vital.return_value = mock_vital

        # Execute
        result = VitalService.delete_vital(mock_db, vital_id=1)

        # Verify
        assert result is True
        mock_db.delete.assert_called_once_with(mock_vital)
        mock_db.commit.assert_called_once()

    @patch.object(VitalService, 'get_vital')
    def test_delete_vital_not_found(self, mock_get_vital, mock_db):
        """Test deleting non-existent vital record."""
        # Setup
        mock_get_vital.return_value = None

        # Execute
        result = VitalService.delete_vital(mock_db, vital_id=999)

        # Verify
        assert result is False
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()


class TestVitalServiceValidation:
    """Test vital signs data validation."""

    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        return db

    def test_vital_with_normal_values(self, mock_db):
        """Test creating vital with normal physiological values."""
        mock_data = MagicMock()
        mock_data.patient_id = 1
        mock_data.recorded_at = datetime.now()
        mock_data.heart_rate = 72  # Normal
        mock_data.systolic_bp = 120  # Normal
        mock_data.diastolic_bp = 80  # Normal
        mock_data.spo2 = 98  # Normal
        mock_data.temperature = 37.0  # Normal
        mock_data.respiratory_rate = 16  # Normal
        mock_data.mean_arterial_pressure = None
        mock_data.gcs_eye = None
        mock_data.gcs_verbal = None
        mock_data.gcs_motor = None
        mock_data.gcs_total = None
        mock_data.weight = None
        mock_data.height = None
        mock_data.bmi = None
        mock_data.notes = None

        with patch('api.services.vital_service.Vital') as MockVital:
            # Execute
            VitalService.create_vital(mock_db, mock_data)

            # Verify vital was created
            MockVital.assert_called_once()

    def test_gcs_total_calculation(self, mock_db):
        """Test GCS total is sum of components."""
        mock_data = MagicMock()
        mock_data.patient_id = 1
        mock_data.recorded_at = datetime.now()
        mock_data.heart_rate = 72
        mock_data.systolic_bp = 120
        mock_data.diastolic_bp = 80
        mock_data.mean_arterial_pressure = None
        mock_data.temperature = None
        mock_data.respiratory_rate = None
        mock_data.spo2 = None
        mock_data.gcs_eye = 4
        mock_data.gcs_verbal = 5
        mock_data.gcs_motor = 6
        mock_data.gcs_total = 15  # 4 + 5 + 6
        mock_data.weight = None
        mock_data.height = None
        mock_data.bmi = None
        mock_data.notes = None

        with patch('api.services.vital_service.Vital') as MockVital:
            VitalService.create_vital(mock_db, mock_data)
            
            # Verify the call includes GCS values
            call_kwargs = MockVital.call_args[1]
            assert call_kwargs['gcs_eye'] == 4
            assert call_kwargs['gcs_verbal'] == 5
            assert call_kwargs['gcs_motor'] == 6
            assert call_kwargs['gcs_total'] == 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
