import secrets
import hashlib
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqladmin import Admin, ModelView

from sqladmin.authentication import AuthenticationBackend
from starlette.responses import RedirectResponse

from app.api.v1.endpoints import api_router
from app.core.database import engine, Base
from app.core.config import settings
from app.models.models import Space, ScannerDevice, CongestionData, RawScannerData
import app.models 

# 앱 시작 시 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# --- Admin 인증 로직 ---
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form.get("username"), form.get("password")

        # secrets.compare_digest를 사용하여 타이밍 공격 방지
        is_valid_username = secrets.compare_digest(str(username), settings.ADMIN_USERNAME)
        
        # 입력받은 비밀번호를 해시화 (SHA-256)하여 환경 변수에 저장된 해시값과 비교
        password_hash = hashlib.sha256(str(password).encode()).hexdigest()
        is_valid_password = secrets.compare_digest(password_hash, settings.ADMIN_PASSWORD)

        if is_valid_username and is_valid_password:
            # 관리자 식별 정보를 세션에 저장 (보안 강화)
            request.session.update({"admin_user": settings.ADMIN_USERNAME})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        admin_user = request.session.get("admin_user")
        # 저장된 관리자 아이디가 설정된 관리자 아이디와 정확히 일치하는지 확인
        return admin_user == settings.ADMIN_USERNAME

authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
# ----------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="ESP32 WiFi/BT 신호를 활용한 혼잡도 모니터링 시스템 백엔드",
    version=settings.VERSION
)

# Session Middleware (Required for sqladmin authentication)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# --- Admin 설정 ---
admin = Admin(app, engine, title="AsangP 관리자 페이지", authentication_backend=authentication_backend)

class SpaceAdmin(ModelView, model=Space):
    name = "SpaceList"
    column_list = (Space.id, Space.name, Space.low_threshold, Space.medium_threshold)
    form_columns = (Space.name, Space.description, Space.low_threshold, Space.medium_threshold)
    icon = "fa-solid fa-map-location-dot"

class DeviceAdmin(ModelView, model=ScannerDevice):
    name = "DeviceList"
    column_list = (ScannerDevice.id, ScannerDevice.space_id, ScannerDevice.last_seen)
    icon = "fa-solid fa-microchip"

class CongestionAdmin(ModelView, model=CongestionData):
    name = "CongestionData"
    column_list = (CongestionData.id, CongestionData.device_id, CongestionData.count, CongestionData.result, CongestionData.timestamp)
    icon = "fa-solid fa-chart-line"

class RawLogAdmin(ModelView, model=RawScannerData):
    name = "ScannerRawLog"
    column_list = (
        RawScannerData.id, 
        RawScannerData.device_id, 
        RawScannerData.wifi_count, 
        RawScannerData.bt_count, 
        RawScannerData.count, 
        RawScannerData.result, 
        RawScannerData.timestamp
    )
    icon = "fa-solid fa-list-ul"

admin.add_view(SpaceAdmin)
admin.add_view(DeviceAdmin)
admin.add_view(CongestionAdmin)
admin.add_view(RawLogAdmin)
# ------------------

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
    return {"하이염"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
