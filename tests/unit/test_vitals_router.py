"""
Unit tests for Vitals router
Tests vital signs CRUD endpoints
"""

import pytest
from unittest.mock import MagicMock, patch


class TestVitalsRouterConfig:
    """Tests for vitals router configuration"""

    def test_router_exists(self):
        """Test vitals router exists"""
        from api.routers.vitals import router
        
        assert router is not None

    def test_router_has_prefix(self):
        """Test vitals router has /vitals prefix"""
        from api.routers.vitals import router
        
        assert router.prefix == "/vitals"

    def test_router_has_tags(self):
        """Test vitals router has tags"""
        from api.routers.vitals import router
        
        assert "vitals" in router.tags


class TestVitalsEndpoints:
    """Tests for vitals endpoints"""

    def test_create_vital_endpoint_exists(self):
        """Test create vital endpoint"""
        from api.routers.vitals import router

        routes = [(r.path, r.methods) for r in router.routes if hasattr(r, 'methods')]

        # Should have POST / or /vitals/
        assert any(path in ["/", "/vitals/"] and "POST" in methods for path, methods in routes)

    def test_get_vital_endpoint_exists(self):
        """Test get vital endpoint"""
        from api.routers.vitals import router
        
        routes = [r.path for r in router.routes]
        
        # Should have GET /{vital_id}
        assert any("{vital_id}" in path for path in routes)

    def test_list_patient_vitals_endpoint_exists(self):
        """Test list patient vitals endpoint"""
        from api.routers.vitals import router
        
        routes = [r.path for r in router.routes]
        
        # Should have /patient/{patient_id}
        assert any("patient" in path for path in routes)

    def test_get_latest_vitals_endpoint_exists(self):
        """Test get latest vitals endpoint"""
        from api.routers.vitals import router
        
        routes = [r.path for r in router.routes]
        
        # Should have /patient/{patient_id}/latest
        assert any("latest" in path for path in routes)

    def test_delete_vital_endpoint_exists(self):
        """Test delete vital endpoint"""
        from api.routers.vitals import router
        
        routes = [(r.path, r.methods) for r in router.routes if hasattr(r, 'methods')]
        
        # Should have DELETE /{vital_id}
        assert any("{vital_id}" in path and "DELETE" in methods for path, methods in routes)


class TestCreateVitalFunction:
    """Tests for create_vital function"""

    def test_create_vital_function_exists(self):
        """Test create_vital function exists"""
        from api.routers.vitals import create_vital
        
        assert create_vital is not None
        assert callable(create_vital)

    @patch('api.routers.vitals.VitalService')
    @patch('api.routers.vitals.PatientService')
    def test_create_vital_patient_not_found(self, mock_patient_svc, mock_vital_svc):
        """Test create_vital returns 404 when patient not found"""
        from api.routers.vitals import create_vital
        from fastapi import HTTPException
        
        mock_patient_svc.get_patient.return_value = None
        mock_db = MagicMock()
        mock_data = MagicMock()
        mock_data.patient_id = 999
        
        with pytest.raises(HTTPException) as exc_info:
            create_vital(vital_data=mock_data, db=mock_db)
        
        assert exc_info.value.status_code == 404


class TestGetVitalFunction:
    """Tests for get_vital function"""

    def test_get_vital_function_exists(self):
        """Test get_vital function exists"""
        from api.routers.vitals import get_vital
        
        assert get_vital is not None
        assert callable(get_vital)

    @patch('api.routers.vitals.VitalService')
    def test_get_vital_not_found(self, mock_service):
        """Test get_vital returns 404 when not found"""
        from api.routers.vitals import get_vital
        from fastapi import HTTPException
        
        mock_service.get_vital.return_value = None
        mock_db = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            get_vital(vital_id=999, db=mock_db)
        
        assert exc_info.value.status_code == 404


class TestListPatientVitalsFunction:
    """Tests for list_patient_vitals function"""

    def test_list_patient_vitals_function_exists(self):
        """Test list_patient_vitals function exists"""
        from api.routers.vitals import list_patient_vitals
        
        assert list_patient_vitals is not None
        assert callable(list_patient_vitals)

    @patch('api.routers.vitals.VitalService')
    @patch('api.routers.vitals.PatientService')
    def test_list_vitals_patient_not_found(self, mock_patient_svc, mock_vital_svc):
        """Test list_patient_vitals returns 404 when patient not found"""
        from api.routers.vitals import list_patient_vitals
        from fastapi import HTTPException
        
        mock_patient_svc.get_patient.return_value = None
        mock_db = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            list_patient_vitals(patient_id=999, db=mock_db)
        
        assert exc_info.value.status_code == 404

    @patch('api.routers.vitals.VitalService')
    @patch('api.routers.vitals.PatientService')
    def test_list_vitals_returns_response(self, mock_patient_svc, mock_vital_svc):
        """Test list_patient_vitals returns paginated response"""
        from api.routers.vitals import list_patient_vitals

        mock_patient_svc.get_patient.return_value = MagicMock()
        mock_vital_svc.list_vitals_for_patient.return_value = ([], 0)
        mock_db = MagicMock()

        result = list_patient_vitals(
            patient_id=1,
            page=1,
            page_size=100,
            db=mock_db
        )

        assert hasattr(result, 'total')
        assert hasattr(result, 'vitals')


class TestGetLatestVitals:
    """Tests for get_latest_vitals function"""

    def test_get_latest_vitals_function_exists(self):
        """Test get_latest_vitals function exists"""
        from api.routers.vitals import get_latest_vitals
        
        assert get_latest_vitals is not None
        assert callable(get_latest_vitals)

    @patch('api.routers.vitals.VitalService')
    def test_get_latest_vitals_not_found(self, mock_service):
        """Test get_latest_vitals returns 404 when no vitals"""
        from api.routers.vitals import get_latest_vitals
        from fastapi import HTTPException
        
        mock_service.get_latest_vitals.return_value = []
        mock_db = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            get_latest_vitals(patient_id=1, db=mock_db)
        
        assert exc_info.value.status_code == 404


class TestDeleteVitalFunction:
    """Tests for delete_vital function"""

    def test_delete_vital_function_exists(self):
        """Test delete_vital function exists"""
        from api.routers.vitals import delete_vital
        
        assert delete_vital is not None
        assert callable(delete_vital)

    @patch('api.routers.vitals.VitalService')
    def test_delete_vital_not_found(self, mock_service):
        """Test delete_vital returns 404 when not found"""
        from api.routers.vitals import delete_vital
        from fastapi import HTTPException
        
        mock_service.delete_vital.return_value = False
        mock_db = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            delete_vital(vital_id=999, db=mock_db)
        
        assert exc_info.value.status_code == 404

    @patch('api.routers.vitals.VitalService')
    def test_delete_vital_success(self, mock_service):
        """Test delete_vital returns None on success"""
        from api.routers.vitals import delete_vital
        
        mock_service.delete_vital.return_value = True
        mock_db = MagicMock()
        
        result = delete_vital(vital_id=1, db=mock_db)
        
        assert result is None
