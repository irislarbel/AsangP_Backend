import secrets
from typing import Generator
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.config import settings

# 헤더에서 X-API-KEY를 찾도록 설정
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def validate_api_key(api_key: str = Security(api_key_header)):
    """
    센서 전송 데이터의 보안을 위해 API Key를 검증합니다.
    secrets.compare_digest를 사용하여 타이밍 공격을 방어합니다.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key가 누락되었습니다."
        )
    
    # 타이밍 공격 방지를 위한 안전한 비교
    is_valid = secrets.compare_digest(api_key, settings.SENSOR_API_KEY)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="유효하지 않은 API Key입니다."
        )
    return api_key
