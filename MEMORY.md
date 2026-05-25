# 프로젝트 메모리 (MEMORY.md)

## 1. 프로젝트 개요
- **프로젝트 명**: AsangP Backend
- **목적**: ESP32로부터 수집된 WiFi 및 Bluetooth 신호 데이터를 분석하여 특정 장소의 혼잡도를 측정하고 제공하는 API 서버.
- **주요 기능**:
    - API Key 인증 기반의 센서 데이터 수집
    - 공간별 임계값(Threshold) 기반 혼잡도 자동 판정 (여유/보통/혼잡)
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
    - `count <= low_threshold`: **여유**
    - `low_threshold < count <= medium_threshold`: **보통**
    - `count > medium_threshold`: **혼잡**
- **특이사항**: 공간(Space)별로 서로 다른 임계값을 설정하여 장소 특성 반영 가능.

## 4. 데이터베이스 스키마
- **Space**: (공간 정보)
    - `low_threshold`: Float (여유 기준)
    - `medium_threshold`: Float (보통 기준)
- **CongestionData**: (가공된 데이터 저장)
    - `count`: Float (계산된 점수)
    - `result`: String (판정 결과: "여유", "보통", "혼잡")

## 5. 작업 단계 (Todo List)
- [x] 프로젝트 환경 설정 및 기본 구조 생성
- [x] 데이터베이스 연결 및 SQLAlchemy 모델 정의
- [x] API Key 인증 시스템 구축 (`X-API-KEY` 헤더)
- [x] 데이터 가공 및 자동 판정 로직 구현
- [x] Docker 배포 환경 설정 (`Dockerfile`, `docker-compose.yml`)
- [x] 초기 데이터 시딩 스크립트(`seed.py`) 최신화
- [x] 웹 관리자 페이지(`sqladmin`) 및 원본 로그 시스템 구축
- [ ] HTTPS (SSL/TLS) 적용 및 리버스 프록시 설정
- [ ] ESP32 클라이언트 연동 코드 작성

## 6. 보안 강화 및 HTTPS 로드맵
- **단계 1: 설정 및 API Key 도입** (완료)
- **단계 2: HTTPS (SSL/TLS) 적용** (진행 예정 - 리버스 프록시 활용)
- **단계 3: ESP32 클라이언트 연동** (진행 예정)

---
*마지막 업데이트: 2026-05-25*
