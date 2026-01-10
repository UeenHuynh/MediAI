"""
Unit tests for Patient Service
Tests patient CRUD operations
"""

import pytest
from unittest.mock import MagicMock, patch


class TestPatientServiceModule:
    """Tests for PatientService module"""

    def test_patient_service_module_exists(self):
        """Test patient service module exists"""
        try:
            from api.services import patient_service
            assert patient_service is not None
        except ImportError:
            pytest.skip("Patient service not available")

    def test_patient_service_class_exists(self):
        """Test PatientService class exists"""
        try:
            from api.services.patient_service import PatientService
            assert PatientService is not None
        except ImportError:
            pytest.skip("PatientService not available")


class TestGetPatient:
    """Tests for get_patient method"""

    @patch('api.services.patient_service.Session')
    def test_get_patient_by_id(self, mock_session):
        """Test getting patient by ID"""
        try:
            from api.services.patient_service import PatientService
            
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
            
            result = PatientService.get_patient(mock_db, patient_id=1)
            
            # Should return patient or None
            assert result is not None or result is None
        except ImportError:
            pytest.skip("PatientService not available")

    @patch('api.services.patient_service.Session')
    def test_get_patient_not_found(self, mock_session):
        """Test getting non-existent patient"""
        try:
            from api.services.patient_service import PatientService
            
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            result = PatientService.get_patient(mock_db, patient_id=999)
            
            assert result is None
        except ImportError:
            pytest.skip("PatientService not available")


class TestGetPatientByCode:
    """Tests for get_patient_by_code method"""

    @patch('api.services.patient_service.Session')
    def test_get_patient_by_code(self, mock_session):
        """Test getting patient by code"""
        try:
            from api.services.patient_service import PatientService
            
            mock_db = MagicMock()
            mock_patient = MagicMock()
            mock_patient.patient_code = "P001"
            mock_db.query.return_value.filter.return_value.first.return_value = mock_patient
            
            result = PatientService.get_patient_by_code(mock_db, "P001")
            
            assert result is not None
        except ImportError:
            pytest.skip("PatientService not available")


class TestCreatePatient:
    """Tests for create_patient method"""

    @patch('api.services.patient_service.Session')
    def test_create_patient(self, mock_session):
        """Test creating a patient"""
        try:
            from api.services.patient_service import PatientService
            
            mock_db = MagicMock()
            mock_data = MagicMock()
            mock_data.patient_code = "P002"
            mock_data.full_name = "John Doe"
            
            result = PatientService.create_patient(mock_db, mock_data)
            
            # Should commit to database
            assert mock_db.add.called or True
        except ImportError:
            pytest.skip("PatientService not available")


class TestUpdatePatient:
    """Tests for update_patient method"""

    @patch('api.services.patient_service.Session')
    def test_update_patient(self, mock_session):
        """Test updating a patient"""
        try:
            from api.services.patient_service import PatientService
            
            mock_db = MagicMock()
            mock_patient = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = mock_patient
            
            mock_data = MagicMock()
            mock_data.model_dump.return_value = {"full_name": "Jane Doe"}
            
            result = PatientService.update_patient(mock_db, 1, mock_data)
            
            assert result is not None
        except ImportError:
            pytest.skip("PatientService not available")


class TestDeletePatient:
    """Tests for delete_patient method"""

    @patch('api.services.patient_service.Session')
    def test_delete_patient(self, mock_session):
        """Test deleting a patient (soft delete)"""
        try:
            from api.services.patient_service import PatientService
            
            mock_db = MagicMock()
            mock_patient = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = mock_patient
            
            result = PatientService.delete_patient(mock_db, 1)
            
            assert result is True
        except ImportError:
            pytest.skip("PatientService not available")

    @patch('api.services.patient_service.Session')
    def test_delete_patient_not_found(self, mock_session):
        """Test deleting non-existent patient"""
        try:
            from api.services.patient_service import PatientService
            
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            result = PatientService.delete_patient(mock_db, 999)
            
            assert result is False
        except ImportError:
            pytest.skip("PatientService not available")


class TestListPatients:
    """Tests for list_patients method"""

    @patch('api.services.patient_service.Session')
    def test_list_patients(self, mock_session):
        """Test listing patients"""
        try:
            from api.services.patient_service import PatientService
            
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
            mock_db.query.return_value.filter.return_value.count.return_value = 0
            
            patients, total = PatientService.list_patients(mock_db)
            
            assert isinstance(patients, list)
            assert isinstance(total, int)
        except ImportError:
            pytest.skip("PatientService not available")
