from fastapi import APIRouter
from app.api.v1 import congestion, spaces

api_router = APIRouter()

# ESP32 데이터 전송용
api_router.include_router(congestion.router, prefix="/congestion", tags=["esp32"])
# 프론트엔드 조회용
api_router.include_router(spaces.router, prefix="/spaces", tags=["frontend"])
