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
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    SECRET_KEY: str
    
    # CORS: .env에서 JSON 리스트 형식으로 작성해야 함
    BACKEND_CORS_ORIGINS: List[str] = []

    # 데이터베이스
    DATABASE_URL: str

settings = Settings()
