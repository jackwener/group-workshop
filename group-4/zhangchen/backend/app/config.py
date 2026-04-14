from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "基金模拟投资大赛系统"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./fun_invest.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    
    # 初始资金配置
    DEFAULT_INITIAL_BALANCE: float = 100000.00
    
    # 比赛配置
    DEFAULT_CONTEST_DAYS: int = 30
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
