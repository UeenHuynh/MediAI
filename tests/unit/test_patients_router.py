"""
Unit tests for Patients router
Tests patient CRUD endpoints
"""

import pytest
from unittest.mock import MagicMock, patch


class TestPatientsRouterConfig:
    """Tests for patients router configuration"""

    def test_router_exists(self):
        """Test patients router exists"""
        from api.routers.patients import router
        
        assert router is not None

    def test_router_has_prefix(self):
        """Test patients router has /patients prefix"""
        from api.routers.patients import router
        
        assert router.prefix == "/patients"

    def test_router_has_tags(self):
        """Test patients router has tags"""
        from api.routers.patients import router
        
        assert "patients" in router.tags


class TestPatientsEndpoints:
    """Tests for patients endpoints"""

    def test_create_patient_endpoint_exists(self):
        """Test create patient endpoint"""
        from api.routers.patients import router
        
        routes = [(r.path, r.methods) for r in router.routes if hasattr(r, 'methods')]
        
        # Should have POST /
        assert any("/" in path and "POST" in methods for path, methods in routes)

    def test_get_patient_endpoint_exists(self):
        """Test get patient endpoint"""
        from api.routers.patients import router
        
        routes = [r.path for r in router.routes]
        
        # Should have GET /{patient_id}
        assert any("{patient_id}" in path for path in routes)

    def test_list_patients_endpoint_exists(self):
        """Test list patients endpoint"""
        from api.routers.patients import router

        routes = [(r.path, r.methods) for r in router.routes if hasattr(r, 'methods')]

        # Should have GET / or /patients/
        assert any(path in ["/", "/patients/"] and "GET" in methods for path, methods in routes)

    def test_update_patient_endpoint_exists(self):
        """Test update patient endpoint"""
        from api.routers.patients import router
        
        routes = [(r.path, r.methods) for r in router.routes if hasattr(r, 'methods')]
        
        # Should have PUT /{patient_id}
        assert any("{patient_id}" in path and "PUT" in methods for path, methods in routes)

    def test_delete_patient_endpoint_exists(self):
        """Test delete patient endpoint"""
        from api.routers.patients import router
        
        routes = [(r.path, r.methods) for r in router.routes if hasattr(r, 'methods')]
        
        # Should have DELETE /{patient_id}
        assert any("{patient_id}" in path and "DELETE" in methods for path, methods in routes)

    def test_get_by_code_endpoint_exists(self):
        """Test get by code endpoint"""
        from api.routers.patients import router
        
        routes = [r.path for r in router.routes]
        
        # Should have /code/{patient_code}
        assert any("code" in path for path in routes)


class TestCreatePatientFunction:
    """Tests for create_patient function"""

    def test_create_patient_function_exists(self):
        """Test create_patient function exists"""
        from api.routers.patients import create_patient
        
        assert create_patient is not None
        assert callable(create_patient)


class TestGetPatientFunction:
    """Tests for get_patient function"""

    def test_get_patient_function_exists(self):
        """Test get_patient function exists"""
        from api.routers.patients import get_patient
        
        assert get_patient is not None
        assert callable(get_patient)

    @patch('api.routers.patients.PatientService')
    def test_get_patient_not_found(self, mock_service):
        """Test get_patient returns 404 when not found"""
        from api.routers.patients import get_patient
        from fastapi import HTTPException
        
        mock_service.get_patient.return_value = None
        mock_db = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            get_patient(patient_id=999, db=mock_db)
        
        assert exc_info.value.status_code == 404


class TestListPatientsFunction:
    """Tests for list_patients function"""

    def test_list_patients_function_exists(self):
        """Test list_patients function exists"""
        from api.routers.patients import list_patients
        
        assert list_patients is not None
        assert callable(list_patients)

    @patch('api.routers.patients.PatientService')
    def test_list_patients_returns_response(self, mock_service):
        """Test list_patients returns paginated response"""
        from api.routers.patients import list_patients

        mock_service.list_patients.return_value = ([], 0)
        mock_db = MagicMock()

        result = list_patients(
            page=1,
            page_size=50,
            department=None,
            search=None,
            db=mock_db
        )

        assert hasattr(result, 'total')
        assert hasattr(result, 'patients')

    @patch('api.routers.patients.PatientService')
    def test_list_patients_pagination(self, mock_service):
        """Test list_patients handles pagination"""
        from api.routers.patients import list_patients

        mock_service.list_patients.return_value = ([], 100)
        mock_db = MagicMock()

        result = list_patients(
            page=2,
            page_size=10,
            department=None,
            search=None,
            db=mock_db
        )

        assert result.page == 2
        assert result.page_size == 10


class TestUpdatePatientFunction:
    """Tests for update_patient function"""

    def test_update_patient_function_exists(self):
        """Test update_patient function exists"""
        from api.routers.patients import update_patient
        
        assert update_patient is not None
        assert callable(update_patient)

    @patch('api.routers.patients.PatientService')
    def test_update_patient_not_found(self, mock_service):
        """Test update_patient returns 404 when not found"""
        from api.routers.patients import update_patient
        from api.schemas.patient import PatientUpdate
        from fastapi import HTTPException
        
        mock_service.update_patient.return_value = None
        mock_db = MagicMock()
        mock_data = MagicMock(spec=PatientUpdate)
        
        with pytest.raises(HTTPException) as exc_info:
            update_patient(patient_id=999, patient_data=mock_data, db=mock_db)
        
        assert exc_info.value.status_code == 404


class TestDeletePatientFunction:
    """Tests for delete_patient function"""

    def test_delete_patient_function_exists(self):
        """Test delete_patient function exists"""
        from api.routers.patients import delete_patient
        
        assert delete_patient is not None
        assert callable(delete_patient)

    @patch('api.routers.patients.PatientService')
    def test_delete_patient_not_found(self, mock_service):
        """Test delete_patient returns 404 when not found"""
        from api.routers.patients import delete_patient
        from fastapi import HTTPException
        
        mock_service.delete_patient.return_value = False
        mock_db = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            delete_patient(patient_id=999, db=mock_db)
        
        assert exc_info.value.status_code == 404


class TestGetPatientByCodeFunction:
    """Tests for get_patient_by_code function"""

    def test_get_patient_by_code_function_exists(self):
        """Test get_patient_by_code function exists"""
        from api.routers.patients import get_patient_by_code
        
        assert get_patient_by_code is not None
        assert callable(get_patient_by_code)

    @patch('api.routers.patients.PatientService')
    def test_get_patient_by_code_not_found(self, mock_service):
        """Test get_patient_by_code returns 404 when not found"""
        from api.routers.patients import get_patient_by_code
        from fastapi import HTTPException
        
        mock_service.get_patient_by_code.return_value = None
        mock_db = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            get_patient_by_code(patient_code="INVALID", db=mock_db)
        
        assert exc_info.value.status_code == 404
