from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data/app.db"
    
    # LLM Configuration
    LLM_PROVIDER: str = "mock"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    OPENAI_MODEL: str = "gpt-4"
    
    # App
    APP_ENV: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
