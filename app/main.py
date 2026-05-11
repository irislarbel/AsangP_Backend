from fastapi import FastAPI
from app.api.v1.endpoints import api_router
from app.core.database import engine, Base
# 중요: Base.metadata가 모든 모델을 인지할 수 있도록 모델들을 임포트해야 합니다.
import app.models 

# 앱 시작 시 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AsangP Congestion Monitoring API",
    description="ESP32 WiFi/BT 신호를 활용한 혼잡도 모니터링 시스템 백엔드",
    version="0.1.0"
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
