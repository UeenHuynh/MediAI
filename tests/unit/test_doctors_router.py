"""
Unit tests for Doctors router
Tests doctors API endpoints
"""

import pytest
from unittest.mock import MagicMock, patch


class TestDoctorsRouterConfig:
    """Tests for doctors router configuration"""

    def test_router_exists(self):
        """Test doctors router exists"""
        from api.routers.doctors import router
        
        assert router is not None

    def test_router_has_prefix(self):
        """Test doctors router has /doctors prefix"""
        from api.routers.doctors import router
        
        assert router.prefix == "/doctors"

    def test_router_has_tags(self):
        """Test doctors router has tags"""
        from api.routers.doctors import router
        
        assert "doctors" in router.tags


class TestDoctorsModels:
    """Tests for doctors Pydantic models"""

    def test_doctor_base_exists(self):
        """Test DoctorBase model exists"""
        from api.routers.doctors import DoctorBase
        
        assert DoctorBase is not None

    def test_doctor_response_exists(self):
        """Test DoctorResponse model exists"""
        from api.routers.doctors import DoctorResponse
        
        assert DoctorResponse is not None

    def test_doctor_list_response_exists(self):
        """Test DoctorListResponse model exists"""
        from api.routers.doctors import DoctorListResponse
        
        assert DoctorListResponse is not None


class TestDoctorBaseModel:
    """Tests for DoctorBase model fields"""

    def test_doctor_base_has_name(self):
        """Test DoctorBase has name field"""
        from api.routers.doctors import DoctorBase
        
        fields = list(DoctorBase.model_fields.keys())
        
        assert 'name' in fields

    def test_doctor_base_has_specialty(self):
        """Test DoctorBase has specialty field"""
        from api.routers.doctors import DoctorBase
        
        fields = list(DoctorBase.model_fields.keys())
        
        assert 'specialty' in fields

    def test_doctor_base_has_email(self):
        """Test DoctorBase has email field"""
        from api.routers.doctors import DoctorBase
        
        fields = list(DoctorBase.model_fields.keys())
        
        assert 'email' in fields


class TestDoctorResponseModel:
    """Tests for DoctorResponse model"""

    def test_doctor_response_has_id(self):
        """Test DoctorResponse has id field"""
        from api.routers.doctors import DoctorResponse
        
        fields = list(DoctorResponse.model_fields.keys())
        
        assert 'id' in fields

    def test_doctor_response_has_rating(self):
        """Test DoctorResponse has rating field"""
        from api.routers.doctors import DoctorResponse
        
        fields = list(DoctorResponse.model_fields.keys())
        
        assert 'rating' in fields

    def test_doctor_response_has_years_experience(self):
        """Test DoctorResponse has years_experience"""
        from api.routers.doctors import DoctorResponse
        
        fields = list(DoctorResponse.model_fields.keys())
        
        assert 'years_experience' in fields


class TestMockDoctors:
    """Tests for mock doctors data"""

    def test_mock_doctors_exists(self):
        """Test MOCK_DOCTORS data exists"""
        from api.routers.doctors import MOCK_DOCTORS
        
        assert MOCK_DOCTORS is not None
        assert isinstance(MOCK_DOCTORS, list)

    def test_mock_doctors_not_empty(self):
        """Test MOCK_DOCTORS has data"""
        from api.routers.doctors import MOCK_DOCTORS
        
        assert len(MOCK_DOCTORS) > 0

    def test_mock_doctors_have_specialties(self):
        """Test mock doctors have various specialties"""
        from api.routers.doctors import MOCK_DOCTORS
        
        specialties = {d.specialty for d in MOCK_DOCTORS}
        
        assert len(specialties) > 1

    def test_mock_doctors_have_ids(self):
        """Test mock doctors have unique IDs"""
        from api.routers.doctors import MOCK_DOCTORS
        
        ids = [d.id for d in MOCK_DOCTORS]
        
        assert len(ids) == len(set(ids))  # All unique


class TestListDoctorsEndpoint:
    """Tests for list_doctors endpoint"""

    def test_list_doctors_function_exists(self):
        """Test list_doctors function exists"""
        from api.routers.doctors import list_doctors
        
        assert list_doctors is not None
        assert callable(list_doctors)

    @pytest.mark.asyncio
    @patch('api.routers.doctors.require_authenticated')
    async def test_list_doctors_returns_response(self, mock_auth):
        """Test list_doctors returns DoctorListResponse"""
        from api.routers.doctors import list_doctors

        mock_user = MagicMock()
        mock_auth.return_value = mock_user

        result = await list_doctors(
            page=1,
            page_size=10,
            specialty=None,
            available=None,
            search=None,
            user=mock_user
        )

        assert hasattr(result, 'doctors')
        assert hasattr(result, 'total')
        assert hasattr(result, 'page')

    @pytest.mark.asyncio
    @patch('api.routers.doctors.require_authenticated')
    async def test_list_doctors_pagination(self, mock_auth):
        """Test list_doctors pagination works"""
        from api.routers.doctors import list_doctors

        mock_user = MagicMock()

        result = await list_doctors(
            page=1,
            page_size=2,
            specialty=None,
            available=None,
            search=None,
            user=mock_user
        )

        assert result.page == 1
        assert len(result.doctors) <= 2

    @pytest.mark.asyncio
    @patch('api.routers.doctors.require_authenticated')
    async def test_list_doctors_filter_available(self, mock_auth):
        """Test filtering by availability"""
        from api.routers.doctors import list_doctors

        mock_user = MagicMock()

        result = await list_doctors(
            page=1,
            page_size=10,
            specialty=None,
            available=True,
            search=None,
            user=mock_user
        )

        for doctor in result.doctors:
            assert doctor.available is True


class TestGetDoctorEndpoint:
    """Tests for get_doctor endpoint"""

    def test_get_doctor_function_exists(self):
        """Test get_doctor function exists"""
        from api.routers.doctors import get_doctor
        
        assert get_doctor is not None
        assert callable(get_doctor)

    @pytest.mark.asyncio
    @patch('api.routers.doctors.require_authenticated')
    async def test_get_doctor_found(self, mock_auth):
        """Test get_doctor returns doctor when found"""
        from api.routers.doctors import get_doctor
        
        mock_user = MagicMock()
        
        result = await get_doctor(doctor_id=1, user=mock_user)
        
        assert result.id == 1

    @pytest.mark.asyncio
    @patch('api.routers.doctors.require_authenticated')
    async def test_get_doctor_not_found(self, mock_auth):
        """Test get_doctor raises 404 when not found"""
        from api.routers.doctors import get_doctor
        from fastapi import HTTPException
        
        mock_user = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            await get_doctor(doctor_id=9999, user=mock_user)
        
        assert exc_info.value.status_code == 404


class TestGetDoctorScheduleEndpoint:
    """Tests for get_doctor_schedule endpoint"""

    def test_get_doctor_schedule_function_exists(self):
        """Test get_doctor_schedule function exists"""
        from api.routers.doctors import get_doctor_schedule
        
        assert get_doctor_schedule is not None
        assert callable(get_doctor_schedule)

    @pytest.mark.asyncio
    @patch('api.routers.doctors.require_authenticated')
    async def test_get_doctor_schedule_returns_dict(self, mock_auth):
        """Test get_doctor_schedule returns schedule dict"""
        from api.routers.doctors import get_doctor_schedule
        
        mock_user = MagicMock()
        
        result = await get_doctor_schedule(doctor_id=1, user=mock_user)
        
        assert isinstance(result, dict)
        assert 'schedule' in result

    @pytest.mark.asyncio
    @patch('api.routers.doctors.require_authenticated')
    async def test_schedule_has_days(self, mock_auth):
        """Test schedule includes days of week"""
        from api.routers.doctors import get_doctor_schedule
        
        mock_user = MagicMock()
        
        result = await get_doctor_schedule(doctor_id=1, user=mock_user)
        
        assert len(result['schedule']) == 7  # 7 days

    @pytest.mark.asyncio
    @patch('api.routers.doctors.require_authenticated')
    async def test_schedule_not_found(self, mock_auth):
        """Test schedule raises 404 for invalid doctor"""
        from api.routers.doctors import get_doctor_schedule
        from fastapi import HTTPException
        
        mock_user = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            await get_doctor_schedule(doctor_id=9999, user=mock_user)
        
        assert exc_info.value.status_code == 404
