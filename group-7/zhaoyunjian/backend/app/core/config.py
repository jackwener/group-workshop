import os

class Config:
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # 数据目录
    DATA_DIR = os.getenv('DATA_DIR', './data')
    
    # 上传文件配置
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './data/uploads')
    
    # CoPaw配置
    COPAW_API_KEY = os.getenv('COPAW_API_KEY', '')
    COPAW_API_URL = os.getenv('COPAW_API_URL', '')
    
    # 百炼DashScope配置
    BAILIAN_API_KEY = os.getenv('BAILIAN_API_KEY', '')
    BAILIAN_MODEL = os.getenv('BAILIAN_MODEL', 'qwen-max')
    
    # 超时配置
    COPAW_TIMEOUT = 20  # 20秒
    BAILIAN_TIMEOUT = 120  # 120秒
    
    @classmethod
    def get_caps(cls):
        """获取系统能力配置状态"""
        return {
            'copaw_configured': bool(cls.COPAW_API_KEY and cls.COPAW_API_URL),
            'bailian_configured': bool(cls.BAILIAN_API_KEY),
            'demo_mode': not (bool(cls.COPAW_API_KEY) or bool(cls.BAILIAN_API_KEY))
        }
