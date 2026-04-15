"""Pytest configuration and fixtures."""
import os
import tempfile
import shutil
import pytest

from app import create_app
from app.dao.session_dao import SessionDAO
from app.dao.analysis_dao import AnalysisDAO
from app.dao.report_dao import ReportDAO


@pytest.fixture
def app():
    """Create application for testing."""
    # Create temporary directory for test data
    temp_dir = tempfile.mkdtemp()
    
    test_config = {
        'TESTING': True,
        'DATA_DIR': temp_dir
    }
    
    app = create_app(test_config)
    
    yield app
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def session_dao(app):
    """Create SessionDAO for testing."""
    with app.app_context():
        return SessionDAO(app.config['DATA_DIR'])


@pytest.fixture
def analysis_dao(app):
    """Create AnalysisDAO for testing."""
    with app.app_context():
        return AnalysisDAO(app.config['DATA_DIR'])


@pytest.fixture
def report_dao(app):
    """Create ReportDAO for testing."""
    with app.app_context():
        return ReportDAO(app.config['DATA_DIR'])


@pytest.fixture
def sample_session(session_dao):
    """Create a sample session for testing."""
    return session_dao.create_session(title="测试会话", session_type="general")
