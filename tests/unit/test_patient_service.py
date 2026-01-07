"""
Unit tests for Patient Service

Tests CRUD operations for patient management with mocked database.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime

# Import the service under test
import sys
sys.path.insert(0, '/home/neeyuhuynh/Desktop/MediAI')

from api.services.patient_service import PatientService


class TestPatientService:
    """Test suite for PatientService."""

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
    def sample_patient_data(self):
        """Sample patient creation data."""
        mock_data = MagicMock()
        mock_data.patient_code = "PT-001"
        mock_data.full_name = "John Doe"
        mock_data.date_of_birth = date(1980, 1, 15)
        mock_data.gender = "M"
        mock_data.admission_date = datetime.now()
        mock_data.department = "ICU"
        mock_data.chief_complaint = "Fever and cough"
        mock_data.ssn = "123-45-6789"
        mock_data.address = "123 Main St"
        mock_data.phone = "555-1234"
        mock_data.medical_history = {"conditions": ["diabetes"]}
        mock_data.current_medications = ["insulin"]
        mock_data.allergies = ["penicillin"]
        return mock_data

    @pytest.fixture
    def mock_patient(self):
        """Create a mock patient object."""
        patient = MagicMock()
        patient.id = 1
        patient.patient_code = "PT-001"
        patient.full_name = "John Doe"
        patient.is_active = True
        patient.department = "ICU"
        return patient

    @patch('api.services.patient_service.encrypt_field')
    @patch('api.services.patient_service.Patient')
    def test_create_patient_success(self, MockPatient, mock_encrypt, mock_db, sample_patient_data):
        """Test successful patient creation."""
        # Setup
        mock_encrypt.return_value = "encrypted_value"
        mock_patient_instance = MagicMock()
        MockPatient.return_value = mock_patient_instance

        # Execute
        result = PatientService.create_patient(mock_db, sample_patient_data, created_by=1)

        # Verify
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert mock_encrypt.call_count == 3  # ssn, address, phone

    def test_get_patient_found(self, mock_db, mock_patient):
        """Test getting an existing patient."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = mock_patient
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        result = PatientService.get_patient(mock_db, patient_id=1)

        # Verify
        assert result == mock_patient
        mock_db.query.assert_called_once()

    def test_get_patient_not_found(self, mock_db):
        """Test getting a non-existent patient."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        result = PatientService.get_patient(mock_db, patient_id=999)

        # Verify
        assert result is None

    def test_get_patient_by_code_found(self, mock_db, mock_patient):
        """Test getting patient by code."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = mock_patient
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        result = PatientService.get_patient_by_code(mock_db, patient_code="PT-001")

        # Verify
        assert result == mock_patient
        assert result.patient_code == "PT-001"

    def test_list_patients_pagination(self, mock_db, mock_patient):
        """Test listing patients with pagination."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.count.return_value = 1
        mock_order = MagicMock()
        mock_offset = MagicMock()
        mock_offset.limit.return_value.all.return_value = [mock_patient]
        mock_order.offset.return_value = mock_offset
        mock_filter.order_by.return_value = mock_order
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        patients, total = PatientService.list_patients(mock_db, skip=0, limit=10)

        # Verify
        assert total == 1
        assert len(patients) == 1
        assert patients[0] == mock_patient

    def test_list_patients_with_department_filter(self, mock_db, mock_patient):
        """Test listing patients filtered by department."""
        # Setup
        mock_query = MagicMock()
        mock_filter1 = MagicMock()
        mock_filter2 = MagicMock()
        mock_filter2.count.return_value = 1
        mock_filter2.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_patient]
        mock_filter1.filter.return_value = mock_filter2
        mock_query.filter.return_value = mock_filter1
        mock_db.query.return_value = mock_query

        # Execute
        patients, total = PatientService.list_patients(mock_db, department="ICU")

        # Verify
        assert total == 1
        mock_filter1.filter.assert_called()

    @patch.object(PatientService, 'get_patient')
    def test_update_patient_success(self, mock_get_patient, mock_db, mock_patient):
        """Test updating patient information."""
        # Setup
        mock_get_patient.return_value = mock_patient
        update_data = MagicMock()
        update_data.model_dump.return_value = {"full_name": "Jane Doe"}

        # Execute
        result = PatientService.update_patient(mock_db, patient_id=1, patient_data=update_data)

        # Verify
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert result == mock_patient

    @patch.object(PatientService, 'get_patient')
    def test_update_patient_not_found(self, mock_get_patient, mock_db):
        """Test updating non-existent patient."""
        # Setup
        mock_get_patient.return_value = None
        update_data = MagicMock()

        # Execute
        result = PatientService.update_patient(mock_db, patient_id=999, patient_data=update_data)

        # Verify
        assert result is None
        mock_db.commit.assert_not_called()

    @patch.object(PatientService, 'get_patient')
    def test_delete_patient_soft_delete(self, mock_get_patient, mock_db, mock_patient):
        """Test soft deleting a patient (sets is_active=False)."""
        # Setup
        mock_get_patient.return_value = mock_patient

        # Execute
        result = PatientService.delete_patient(mock_db, patient_id=1)

        # Verify
        assert result is True
        assert mock_patient.is_active is False
        mock_db.commit.assert_called_once()

    @patch.object(PatientService, 'get_patient')
    def test_delete_patient_not_found(self, mock_get_patient, mock_db):
        """Test deleting non-existent patient."""
        # Setup
        mock_get_patient.return_value = None

        # Execute
        result = PatientService.delete_patient(mock_db, patient_id=999)

        # Verify
        assert result is False
        mock_db.commit.assert_not_called()

    def test_get_active_patients_count(self, mock_db):
        """Test counting active patients."""
        # Setup
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.scalar.return_value = 42
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Execute
        result = PatientService.get_active_patients_count(mock_db)

        # Verify
        assert result == 42


class TestPatientServiceEncryption:
    """Test PII encryption in PatientService."""

    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        return db

    @patch('api.services.patient_service.encrypt_field')
    @patch('api.services.patient_service.Patient')
    def test_ssn_encrypted_on_create(self, MockPatient, mock_encrypt, mock_db):
        """Test that SSN is encrypted when creating patient."""
        # Setup
        mock_encrypt.return_value = "encrypted_ssn"
        mock_data = MagicMock()
        mock_data.ssn = "123-45-6789"
        mock_data.address = None
        mock_data.phone = None
        mock_data.medical_history = None
        mock_data.current_medications = None
        mock_data.allergies = None

        # Execute
        PatientService.create_patient(mock_db, mock_data)

        # Verify SSN was encrypted
        mock_encrypt.assert_called_with("123-45-6789")

    @patch('api.services.patient_service.encrypt_field')
    @patch('api.services.patient_service.Patient')
    def test_pii_fields_encrypted(self, MockPatient, mock_encrypt, mock_db):
        """Test all PII fields are encrypted."""
        # Setup
        mock_encrypt.return_value = "encrypted_value"
        mock_data = MagicMock()
        mock_data.ssn = "123-45-6789"
        mock_data.address = "123 Main St"
        mock_data.phone = "555-1234"
        mock_data.medical_history = None
        mock_data.current_medications = None
        mock_data.allergies = None

        # Execute
        PatientService.create_patient(mock_db, mock_data)

        # Verify all 3 PII fields were encrypted
        assert mock_encrypt.call_count == 3

    @patch('api.services.patient_service.encrypt_field')
    @patch('api.services.patient_service.Patient')
    def test_optional_pii_not_encrypted_if_none(self, MockPatient, mock_encrypt, mock_db):
        """Test that None PII fields are not encrypted."""
        # Setup
        mock_data = MagicMock()
        mock_data.ssn = None
        mock_data.address = None
        mock_data.phone = None
        mock_data.medical_history = None
        mock_data.current_medications = None
        mock_data.allergies = None

        # Execute
        PatientService.create_patient(mock_db, mock_data)

        # Verify encrypt was not called for None values
        mock_encrypt.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
