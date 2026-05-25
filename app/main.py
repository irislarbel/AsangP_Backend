from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import api_router
from app.core.database import engine, Base
from app.core.config import settings
import app.models 

# 앱 시작 시 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="ESP32 WiFi/BT 신호를 활용한 혼잡도 모니터링 시스템 백엔드",
    version=settings.VERSION
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}. Visit /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    # 모듈 경로를 "app.main:app"으로 지정하여 실행
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
