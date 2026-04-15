import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    DATA_DIR = os.path.join(BASE_DIR, "data")
    CORS_ORIGINS = ["http://localhost:5173"]
    COPAW_TIMEOUT = 3
    BAILIAN_TIMEOUT = 5
    MAX_QUERY_LENGTH = 500
    MAX_TITLE_LENGTH = 100
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES = ["pdf", "docx", "xlsx"]


class TestConfig(Config):
    TESTING = True
    DATA_DIR = os.path.join(BASE_DIR, "test_data")
