from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    PROJECT_NAME: str
    VERSION: str
    API_V1_STR: str = "/api/v1"
    
    # 보안 설정
    SENSOR_API_KEY: str
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # 데이터베이스
    DATABASE_URL: str

settings = Settings()
