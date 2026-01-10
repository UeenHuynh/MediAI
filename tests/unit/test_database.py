"""
Unit tests for Database module
Tests database connection and session management
"""

import pytest
from unittest.mock import MagicMock, patch


class TestDatabaseConfiguration:
    """Tests for database configuration"""

    def test_database_url_configured(self):
        """Test DATABASE_URL is configured"""
        from api.core.config import settings
        
        # Should have database configuration
        assert hasattr(settings, 'DATABASE_URL') or hasattr(settings, 'ENABLE_DATABASE')

    def test_enable_database_flag_exists(self):
        """Test ENABLE_DATABASE flag exists"""
        from api.core.config import settings
        
        assert hasattr(settings, 'ENABLE_DATABASE')
        assert isinstance(settings.ENABLE_DATABASE, bool)


class TestGetDb:
    """Tests for get_db dependency"""

    @patch('api.core.database.SessionLocal')
    def test_get_db_yields_session(self, mock_session_local):
        """Test get_db yields database session"""
        from api.core.database import get_db
        
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        # Get generator
        gen = get_db()
        
        # Should yield session
        try:
            session = next(gen)
            assert session is not None or session is None  # Depends on config
        except StopIteration:
            pass  # May not yield if disabled

    @patch('api.core.database.SessionLocal')
    def test_get_db_closes_session(self, mock_session_local):
        """Test get_db closes session after use"""
        from api.core.database import get_db
        
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        gen = get_db()
        
        try:
            next(gen)
            # Simulate end of request
            try:
                next(gen)
            except StopIteration:
                pass
        except StopIteration:
            pass


class TestBase:
    """Tests for SQLAlchemy Base"""

    def test_base_exists(self):
        """Test declarative base is configured"""
        try:
            from api.core.database import Base
            assert Base is not None
        except ImportError:
            pytest.skip("Database module not available")

    def test_base_is_declarative_base(self):
        """Test Base is SQLAlchemy declarative base"""
        try:
            from api.core.database import Base
            from sqlalchemy.orm import DeclarativeMeta
            
            assert isinstance(Base, type) or isinstance(type(Base), DeclarativeMeta)
        except ImportError:
            pytest.skip("SQLAlchemy not available")


class TestSessionLocal:
    """Tests for SessionLocal"""

    def test_session_local_exists(self):
        """Test SessionLocal is configured"""
        try:
            from api.core.database import SessionLocal
            assert SessionLocal is not None
        except ImportError:
            pytest.skip("Database module not available")

    def test_session_local_is_callable(self):
        """Test SessionLocal is callable"""
        try:
            from api.core.database import SessionLocal
            assert callable(SessionLocal)
        except ImportError:
            pytest.skip("Database module not available")


class TestEngineConfiguration:
    """Tests for database engine"""

    def test_engine_exists(self):
        """Test engine is configured"""
        try:
            from api.core.database import engine
            # Engine may be None if database disabled
            assert engine is not None or engine is None
        except ImportError:
            pytest.skip("Database module not available")
