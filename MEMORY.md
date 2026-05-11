# 프로젝트 메모리 (MEMORY.md)

## 1. 프로젝트 개요
- **프로젝트 명**: AsangP Backend
- **목적**: ESP32로부터 수집된 WiFi 및 Bluetooth 신호 데이터를 분석하여 특정 장소의 혼잡도를 측정하고 제공하는 API 서버.
- **주요 기능**:
    - ESP32 데이터 수집 API (WiFi/BT 기기 개수)
    - 혼잡도 조회 API (실시간 및 이력 데이터)
    - 장소별 장치 관리

## 2. 기술 스택
- **Language**: Python 3.12+
- **Framework**: FastAPI
- **Package Manager**: uv
- **Database**: SQLite (SQLAlchemy ORM)
- **Server**: Uvicorn
- **Architecture**: 3-Layer Architecture (Controller - Service - Repository)

## 3. 디렉토리 구조 (3-Layer Architecture)
```text
app/
├── api/            # Controller (Routers, Pydantic Schemas)
│   ├── v1/
│   └── schemas/     # Pydantic Schemas
├── services/       # Service (Business Logic)
├── repositories/   # Repository (Data Access)
├── models/         # Database Models (SQLAlchemy)
├── core/           # Configuration, Database Setup
└── main.py         # Entry point
```

## 4. 데이터베이스 스키마
- **Space**: (공간 정보)
    - `id`: Integer (PK)
    - `name`: String (공간 이름)
    - `description`: String (공간 설명)
- **ScannerDevice**: (ESP32 기기 정보)
    - `id`: String (PK, Device ID)
    - `space_id`: Integer (FK, Space)
    - `location_description`: String (설치 상세 위치)
    - `last_seen`: DateTime
- **CongestionData**: (수집된 데이터)
    - `id`: Integer (PK)
    - `device_id`: String (FK, ScannerDevice)
    - `wifi_count`: Integer
    - `bt_count`: Integer
    - `timestamp`: DateTime

## 5. 작업 단계 (Todo List)
- [x] 프로젝트 환경 설정 (`uv init`, 의존성 설치)
- [x] 기본 디렉토리 구조 생성
- [x] 데이터베이스 연결 설정 (SQLAlchemy + SQLite)
- [x] SQLAlchemy 모델 정의 (`models/`)
- [x] Pydantic 스키마 정의 (`api/schemas/`)
- [x] Repository 패턴 구현 (`repositories/`)
- [x] Service 로직 구현 (`services/`)
- [x] API 라우터 구현 (`api/v1/`)
- [x] Uvicorn 실행 및 테스트 (준비 완료)

---
*마지막 업데이트: 2026-05-11*
