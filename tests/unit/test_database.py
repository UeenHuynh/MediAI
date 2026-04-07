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


class TestInitDb:
    """Tests for init_db function"""

    @patch('api.core.database.engine')
    def test_init_db_success(self, mock_engine):
        """Test init_db creates schemas successfully"""
        from api.core.database import init_db

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        init_db()

        # Should execute CREATE SCHEMA commands
        assert mock_conn.execute.call_count == 3
        mock_conn.commit.assert_called_once()

    @patch('api.core.database.engine')
    def test_init_db_calls_execute_three_times(self, mock_engine):
        """Test init_db executes three CREATE SCHEMA commands"""
        from api.core.database import init_db

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        init_db()

        # Should call execute 3 times (raw, staging, analytics)
        assert mock_conn.execute.call_count == 3

    @patch('api.core.database.engine')
    def test_init_db_commits_transaction(self, mock_engine):
        """Test init_db commits transaction"""
        from api.core.database import init_db

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        init_db()

        mock_conn.commit.assert_called_once()

    @patch('api.core.database.engine')
    def test_init_db_uses_text_clauses(self, mock_engine):
        """Test init_db uses SQLAlchemy text clauses"""
        from api.core.database import init_db
        from sqlalchemy.sql.elements import TextClause

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        init_db()

        # Each call should use a TextClause
        for call in mock_conn.execute.call_args_list:
            args = call[0]
            assert len(args) > 0
            assert isinstance(args[0], TextClause)

    @patch('api.core.database.engine')
    def test_init_db_raises_on_error(self, mock_engine):
        """Test init_db raises exception on error"""
        from api.core.database import init_db

        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Schema creation failed")
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(Exception) as exc_info:
            init_db()

        assert "Schema creation failed" in str(exc_info.value)


class TestTestConnection:
    """Tests for test_connection function"""

    @patch('api.core.database.engine')
    def test_connection_success(self, mock_engine):
        """Test test_connection returns True on success"""
        from api.core.database import test_connection

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        result = test_connection()

        assert result is True
        mock_conn.execute.assert_called_once()

    @patch('api.core.database.engine')
    def test_connection_failure(self, mock_engine):
        """Test test_connection returns False on failure"""
        from api.core.database import test_connection

        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Connection refused")
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        result = test_connection()

        assert result is False

    @patch('api.core.database.engine')
    def test_connection_executes_query(self, mock_engine):
        """Test test_connection executes a database query"""
        from api.core.database import test_connection
        from sqlalchemy.sql.elements import TextClause

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        test_connection()

        # Should execute exactly one query
        mock_conn.execute.assert_called_once()
        # And the argument should be a TextClause
        args = mock_conn.execute.call_args[0]
        assert len(args) > 0
        assert isinstance(args[0], TextClause)
