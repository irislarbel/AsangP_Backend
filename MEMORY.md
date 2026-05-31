# 프로젝트 메모리 (MEMORY.md)

## 1. 프로젝트 개요
- **프로젝트 명**: AsangP Backend
- **목적**: ESP32로부터 수집된 WiFi 및 Bluetooth 신호 데이터를 분석하여 특정 장소의 혼잡도를 측정하고 제공하는 API 서버.
- **주요 기능**:
    - API Key 인증 기반의 센서 데이터 수집 (타이밍 공격 방어 적용)
    - 공간별 최대 수용 인원(max_capacity) 대비 백분율 기반 혼잡도 산출 (0~100%)
    - WiFi/BT 신호 가중치 적용 산출 공식 (WiFi + BT * 0.5)
    - 실시간 혼잡도 조회 및 이력 관리

## 2. 기술 스택
- **Language**: Python 3.12+
- **Framework**: FastAPI
- **Package Manager**: uv
- **Database**: SQLite (SQLAlchemy ORM)
- **Container**: Docker, Docker Compose
- **Architecture**: 3-Layer Architecture

## 3. 핵심 로직: 혼잡도 산출 및 판정
- **산출 공식**: `count = wifi_count + (bt_count * 0.5)`
- **판정 기준**:
    - `congestion_level = min(100, round((count / max_capacity) * 100))`
    - 정수 백분율로 반환하며 100%를 초과하지 않음.
- **주간 피크 추세 API (KST 고정)**:
    - 논리적 일자(Logical Day): 06:00 ~ 익일 06:00 (심야 시간대 피크 분절 방지)
    - 결측치 처리: 센서 로그가 전혀 없는 구간은 차트 구분을 위해 `null`로 응답

## 4. 보안 및 배포 설정 (Security & Deployment)
- **CORS**: `BACKEND_CORS_ORIGINS` 환경 변수로 관리 (배포 시 프론트 도메인 추가 필수)
- **API 보안**: 
    - `X-API-KEY` 헤더 검증 시 `secrets.compare_digest` 사용 (타이밍 공격 방지)
    - 관리자 페이지 비밀번호 SHA-256 해싱 저장 및 비교
- **배포 설정**:
    - `reload=False` (프로덕션 모드)
    - `SessionMiddleware`: `same_site="lax"` 적용 (HTTPS 전환 시 `https_only=True` 상향 필요)

## 5. 작업 단계 (Todo List)
- [x] 프로젝트 환경 설정 및 기본 구조 생성
- [x] 데이터베이스 연결 및 SQLAlchemy 모델 정의
- [x] API Key 인증 시스템 구축 및 보안 강화 (타이밍 공격 방어 적용)
- [x] 데이터 가공 및 자동 판정 로직 구현
- [x] Docker 배포 환경 설정 (`Dockerfile`, `docker-compose.yml`)
- [x] 웹 관리자 페이지(`sqladmin`) 구축 및 보안 강화
- [x] 리포지토리 레이어 트랜잭션 관리 및 Upsert 로직 최적화
- [x] 배포용 환경 설정 전환 및 CORS 환경 변수 이관 완료
- [x] 서버 Nginx 설치 및 리버스 프록시 설정 (Cloudflare Origin CA 적용)
- [x] 도메인 연결 및 HTTPS (SSL/TLS) 인증서 적용 완료
- [x] API 및 서비스 전체 경로 접두사 적용 (`/asangp` 추가)
- [x] 프론트엔드 최적화용 7일간 혼잡도 피크 및 주간 추세 조회 API (`GET /api/v1/spaces/{space_id}/peaks`) 구현
- [ ] ESP32 클라이언트 연동 코드 작성

---
*마지막 업데이트: 2026-05-31 (주간 혼잡도 피크 API 추가 및 KST 논리적 일자 적용)*
