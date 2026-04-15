import os
import json
import shutil
import tempfile

import pytest

from app import create_app
from config import TestConfig


@pytest.fixture
def app(tmp_path):
    class _TestConfig(TestConfig):
        DATA_DIR = str(tmp_path)

    # Initialize empty JSON files
    for fname in ["sessions.json", "qa_records.json", "upload_files.json", "reports.json"]:
        with open(os.path.join(str(tmp_path), fname), "w", encoding="utf-8") as f:
            json.dump([], f)

    app = create_app(_TestConfig)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def storage(app):
    from storage import Storage
    return Storage(app.config["DATA_DIR"])


@pytest.fixture
def seed_session(client):
    """Create a session and return its data."""
    resp = client.post("/api/v1/agent/sessions",
                       json={},
                       content_type="application/json")
    return resp.get_json()
