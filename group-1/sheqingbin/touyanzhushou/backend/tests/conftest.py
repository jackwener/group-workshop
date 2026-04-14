"""
测试配置和 fixtures
"""
import pytest
import tempfile
import shutil
import os

from app import create_app
from app.storage import Storage, _storage_instance


@pytest.fixture
def app():
    """创建测试应用"""
    # 创建临时数据目录
    temp_dir = tempfile.mkdtemp()
    
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATA_DIR": temp_dir,
        "SECRET_KEY": "test-secret-key"
    })
    
    yield app
    
    # 清理临时目录
    shutil.rmtree(temp_dir)


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建测试 CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def storage(app):
    """创建测试存储实例"""
    storage = Storage(app.config["DATA_DIR"])
    return storage
