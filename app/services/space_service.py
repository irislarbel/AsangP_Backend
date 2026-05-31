from datetime import datetime, timedelta, timezone, date
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.space_repository import SpaceRepository
from app.repositories.congestion_repository import CongestionRepository
from app.api.schemas.space import SpaceCreate, SpaceUpdate, SpaceHistoryResponse, HistoryPoint, SpacePeaksResponse, PeakDayData

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
            # 너무 오래된 과거 데이터 차단
            if target_date < date(2026, 5, 10):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="너무많이궁금해하시네요~,, 2026-05-10 이전의데이터는없답니다"
                )
        
        # 기준 시점 결정
        if target_date:
            if target_date == today_date and now.hour < 6:
                # 오늘 날짜를 요청했지만 아직 06시 이전인 경우 전날 06시 주기로 처리
                start_dt = (datetime.combine(target_date, datetime.min.time()) - timedelta(days=1)).replace(hour=6)
            else:
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
                # congestion_level이 None인 경우 계산에서 제외
                if log.congestion_level is None:
                    continue
                
                minute_bucket = (log.timestamp.minute // 10) * 10
                key = (log.timestamp.date(), log.timestamp.hour, minute_bucket)
                if key not in buckets: buckets[key] = []
                buckets[key].append(log.congestion_level)

            result = []
            current_slot = base_start
            for _ in range(144):
                if is_today_period and current_slot > now:
                    break

                key = (current_slot.date(), current_slot.hour, current_slot.minute)
                time_str = f"{current_slot.hour:02d}:{current_slot.minute:02d}"
                
                avg_level = sum(buckets[key]) / len(buckets[key]) if key in buckets else 0
                result.append(HistoryPoint(time=time_str, congestion_level=round(avg_level)))
                current_slot += timedelta(minutes=10)
            
            return result

        # 현재 주기에 해당하는지 여부 확인
        is_target_today = (start_dt <= now < target_end_dt)

        return SpaceHistoryResponse(
            target=resample_data(target_raw, start_dt, is_target_today),
            comparison=resample_data(comparison_raw, comparison_start, False)
        )

    def get_peaks(self, space_id: int, target_date: date, threshold: int = 70) -> SpacePeaksResponse:
        """선택한 날짜를 포함하여 과거 7일간의 혼잡도 피크 데이터(06시 기준 논리적 일자)를 반환합니다."""
        # 1. 공간 존재 여부 확인
        self.get_space(space_id)

        now = datetime.now(timezone(timedelta(hours=9))).replace(tzinfo=None)
        
        # 2. 날짜 산출 (target_date 6일 전 06:00 ~ target_date 익일 06:00)
        start_dt = datetime.combine(target_date, datetime.min.time()).replace(hour=6) - timedelta(days=6)
        end_dt = datetime.combine(target_date, datetime.min.time()).replace(hour=6) + timedelta(days=1)
        
        # 미래 데이터 조회 방지 (현재 시간까지만 실제 조회)
        if end_dt > now:
            actual_end_dt = now
        else:
            actual_end_dt = end_dt - timedelta(seconds=1)

        # 3. 데이터 조회
        raw_data = self.congestion_repository.get_raw_history_by_space(space_id, start_dt, actual_end_dt)

        # 4. 데이터를 1시간 단위로 논리적 일자 버킷에 담기
        # day_buckets: { logical_date: { hour_index: [levels] } }
        # hour_index: 0=06:00, 1=07:00, ..., 18=00:00(자정), 23=05:00
        day_buckets = {}
        for i in range(7):
            logical_date = (start_dt + timedelta(days=i)).date()
            day_buckets[logical_date] = {h: [] for h in range(24)}

        for log in raw_data:
            if log.congestion_level is None:
                continue
            
            # logical day 계산: 00:00 ~ 05:59는 논리적으로 전날에 속함
            log_time = log.timestamp
            if log_time.hour < 6:
                logical_date = (log_time - timedelta(days=1)).date()
                hour_index = log_time.hour + 18 # 0->18, 5->23
            else:
                logical_date = log_time.date()
                hour_index = log_time.hour - 6  # 6->0, 23->17
            
            if logical_date in day_buckets:
                day_buckets[logical_date][hour_index].append(log.congestion_level)

        # 5. 응답 데이터 가공
        result_data = []
        for i in range(7):
            logical_date = (start_dt + timedelta(days=i)).date()
            buckets = day_buckets.get(logical_date, {h: [] for h in range(24)})
            
            daily_trend = []
            for h in range(24):
                levels = buckets[h]
                if not levels:
                    daily_trend.append(None) # 결측치는 null
                else:
                    avg_level = sum(levels) / len(levels)
                    daily_trend.append(round(avg_level))
            
            max_congestion = None
            valid_trends = [t for t in daily_trend if t is not None]
            if valid_trends:
                max_congestion = max(valid_trends)

            # 연속된 피크 구간 찾기
            peak_ranges = []
            start_hour_index = -1
            
            for h in range(25): # 24까지 돌아서 마지막 구간이 끝나는 것도 처리
                val = daily_trend[h] if h < 24 else None
                is_peak = val is not None and val >= threshold
                
                if is_peak:
                    if start_hour_index == -1:
                        start_hour_index = h
                else:
                    if start_hour_index != -1:
                        end_hour_index = h
                        start_actual_hour = (start_hour_index + 6) % 24
                        end_actual_hour = (end_hour_index + 6) % 24
                        peak_ranges.append(f"{start_actual_hour:02d}:00~{end_actual_hour:02d}:00")
                        start_hour_index = -1

            result_data.append(PeakDayData(
                date=logical_date.isoformat(),
                peak_ranges=peak_ranges,
                max_congestion=max_congestion,
                daily_trend=daily_trend
            ))

        return SpacePeaksResponse(
            space_id=space_id,
            target_date=target_date.isoformat(),
            threshold=threshold,
            data=result_data
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
