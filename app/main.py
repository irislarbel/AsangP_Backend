from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import api_router
from app.core.database import engine, Base
import app.models 

# 앱 시작 시 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AsangP Congestion Monitoring API",
    description="ESP32 WiFi/BT 신호를 활용한 혼잡도 모니터링 시스템 백엔드",
    version="0.1.0"
)

# CORS 설정
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to AsangP Congestion Monitoring API. Visit /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    # 모듈 경로를 "app.main:app"으로 지정하여 실행
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
