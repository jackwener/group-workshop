import pytest
import os
import tempfile
from wsgi import create_app

@pytest.fixture
def app(tmp_path):
    """Create application for testing."""
    app = create_app(data_dir=str(tmp_path))
    app.config['TESTING'] = True
    # 初始化空 JSON 文件
    for fname in ['sessions.json', 'qa_records.json', 'reports.json']:
        fpath = os.path.join(str(tmp_path), fname)
        if not os.path.exists(fpath):
            with open(fpath, 'w') as f:
                f.write('[]')
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
