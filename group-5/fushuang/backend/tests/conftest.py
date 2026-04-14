"""
pytest 配置文件
"""
import pytest
import tempfile
import shutil
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage import Storage


@pytest.fixture
def temp_data_dir():
    """创建临时数据目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def storage(temp_data_dir):
    """创建 Storage 实例"""
    return Storage(data_dir=temp_data_dir)


@pytest.fixture
def sample_session(storage):
    """创建示例会话"""
    return storage.create_session(title="测试会话")
