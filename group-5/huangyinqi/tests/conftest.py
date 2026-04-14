"""Pytest fixtures for all test levels."""

import os
import sys
import shutil
import tempfile
import pytest

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from storage import Storage
from app import create_app


@pytest.fixture
def tmp_data_dir():
    """Create a temporary data directory for tests."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


@pytest.fixture
def storage(tmp_data_dir):
    """Storage instance with temporary directory."""
    return Storage(data_dir=tmp_data_dir)


@pytest.fixture
def app(tmp_data_dir):
    """Flask app configured for testing."""
    app = create_app(data_dir=tmp_data_dir)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()
