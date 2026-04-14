import pytest
import os
import tempfile
import shutil
from app import create_app
from app.services.storage import Storage, reset_storage

@pytest.fixture
def app():
    """创建测试应用"""
    # 创建临时数据目录
    temp_dir = tempfile.mkdtemp()
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'DATA_DIR': temp_dir,
    })
    
    yield app
    
    # 清理临时目录
    shutil.rmtree(temp_dir)
    reset_storage()

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def storage(app):
    """创建测试存储实例"""
    with app.app_context():
        return Storage(app.config['DATA_DIR'])
