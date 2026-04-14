"""
配置管理模块
基于 08-系统架构与技术选型.md 和 11-安全设计规格.md
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "研报问答助手"
    APP_VERSION: str = "v0.1"
    DEBUG: bool = True
    
    # MySQL配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "report_qa"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    # Milvus配置
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # 业务配置
    MAX_SESSIONS_PER_USER: int = 100
    MAX_QUERY_LENGTH: int = 500
    SESSION_CACHE_TTL: int = 86400  # 24小时
    QA_CACHE_TTL: int = 3600  # 1小时
    
    @property
    def mysql_url(self) -> str:
        """MySQL连接URL"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    @property
    def redis_url(self) -> str:
        """Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
