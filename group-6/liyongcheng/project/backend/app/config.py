"""应用配置模块"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""
    
    # 基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    
    # 数据目录
    DATA_DIR = Path(os.getenv('DATA_DIR', './data'))
    UPLOAD_DIR = DATA_DIR / 'files'
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # LLM 配置
    COPAW_API_URL = os.getenv('IRA_COPAW_API_URL', '')
    COPAW_API_KEY = os.getenv('IRA_COPAW_API_KEY', '')
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
    
    # 超时配置
    COPAW_TIMEOUT = 30  # 秒
    BAILIAN_TIMEOUT = 120  # 秒
    STOCK_API_TIMEOUT = 10  # 秒
    
    @classmethod
    def init_app(cls):
        """初始化应用，创建必要目录"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


config = Config()
