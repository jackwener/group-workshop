"""
pytest fixtures — 对齐 Spec 13 测试策略
"""
import os
import shutil
import tempfile
import pytest
from app import create_app


@pytest.fixture
def tmp_data_dir():
    """创建临时数据目录，测试结束后清理"""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def app(tmp_data_dir):
    """Flask 测试 app"""
    app = create_app(test_config={
        "TESTING": True,
        "DATA_DIR": tmp_data_dir,
    })
    # 确保无 LLM 配置 → 默认 Demo 模式
    os.environ.pop("IRA_COPAW_CHAT_URL", None)
    os.environ.pop("DASHSCOPE_API_KEY", None)
    return app


@pytest.fixture
def client(app):
    """Flask test_client"""
    return app.test_client()
