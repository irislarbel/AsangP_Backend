from datetime import datetime, timedelta, timezone, date
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.space_repository import SpaceRepository
from app.repositories.congestion_repository import CongestionRepository
from app.api.schemas.space import SpaceCreate, SpaceUpdate, SpaceHistoryResponse, HistoryPoint

class SpaceService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = SpaceRepository(db)
        self.congestion_repository = CongestionRepository(db)

    def get_all_spaces(self):
        return self.repository.get_all()

    def get_space(self, space_id: int):
        space = self.repository.get_by_id(space_id)
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{space_id}번자리도업다..."
            )
        return space

    def get_history(self, space_id: int, target_date: Optional[date] = None) -> SpaceHistoryResponse:
        """선택한 날짜(기본값: 오늘)와 그 일주일 전의 혼잡도 이력을 10분 단위로 가공하여 반환합니다. (06:00 시작 기준)"""
        # 1. 공간 존재 여부 확인
        self.get_space(space_id)

        now = datetime.now(timezone(timedelta(hours=9))).replace(tzinfo=None)
        today_date = now.date()

        # 2. 날짜 범위 유효성 검사
        if target_date:
            # 미래 날짜 차단
            if target_date > today_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="저는아마네스즈하가아닙니다"
                )
            # 너무 오래된 과거 데이터 차단 (예: 2024년 이전)
            if target_date < date(2026, 5, 10):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="너무많이궁금해하시네요~,, 2026-05-10 이전의데이터는없답니다"
                )
        
        # 기준 시점 결정
        if target_date:
            # 특정 날짜가 지정된 경우 해당 날짜의 06:00부터 시작
            start_dt = datetime.combine(target_date, datetime.min.time()).replace(hour=6)
        else:
            # 지정되지 않은 경우 '오늘'의 06:00 (현재가 06시 이전이면 어제 06시부터)
            if now.hour < 6:
                start_dt = (now - timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
            else:
                start_dt = now.replace(hour=6, minute=0, second=0, microsecond=0)
        
        comparison_start = start_dt - timedelta(days=7)
        comparison_end = comparison_start + timedelta(days=1) - timedelta(seconds=1)
        
        # 오늘이 포함된 주기인 경우 현재 시간까지만 조회하기 위해 end_dt 설정
        target_end_dt = start_dt + timedelta(days=1)
        if start_dt <= now < target_end_dt:
            actual_target_end = now
        else:
            actual_target_end = target_end_dt - timedelta(seconds=1)

        # 데이터 조회
        target_raw = self.congestion_repository.get_raw_history_by_space(space_id, start_dt, actual_target_end)
        comparison_raw = self.congestion_repository.get_raw_history_by_space(space_id, comparison_start, comparison_end)

        def resample_data(raw_data, base_start: datetime, is_today_period: bool):
            """데이터를 10분 단위로 그룹화하여 평균을 냅니다."""
            buckets = {}
            for log in raw_data:
                minute_bucket = (log.timestamp.minute // 10) * 10
                key = (log.timestamp.date(), log.timestamp.hour, minute_bucket)
                if key not in buckets: buckets[key] = []
                buckets[key].append(log.count)

            result = []
            current_slot = base_start
            for _ in range(144):
                if is_today_period and current_slot > now:
                    break

                key = (current_slot.date(), current_slot.hour, current_slot.minute)
                time_str = f"{current_slot.hour:02d}:{current_slot.minute:02d}"
                
                avg_count = sum(buckets[key]) / len(buckets[key]) if key in buckets else 0
                result.append(HistoryPoint(time=time_str, count=round(avg_count, 2)))
                current_slot += timedelta(minutes=10)
            
            return result

        # 현재 주기에 해당하는지 여부 확인
        is_target_today = (start_dt <= now < target_end_dt)

        return SpaceHistoryResponse(
            target=resample_data(target_raw, start_dt, is_target_today),
            comparison=resample_data(comparison_raw, comparison_start, False)
        )

    def create_space(self, space_in: SpaceCreate):
        space = self.repository.create(space_in)
        self.db.commit()
        self.db.refresh(space)
        return space

    def update_space(self, space_id: int, space_in: SpaceUpdate):
        space = self.repository.update(space_id, space_in)
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{space_id}자리는틀렷다"
            )
        self.db.commit()
        self.db.refresh(space)
        return space

    def delete_space(self, space_id: int):
        success = self.repository.delete(space_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{space_id}번자리는업다"
            )
        self.db.commit()
        return {"message": "Successfully deleted"}
