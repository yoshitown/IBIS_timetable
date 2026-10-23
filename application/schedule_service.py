"""
アプリケーション層: プレゼンテーション層からのユースケース要求を処理するサービス
設計原則: 貧血ドメインモデルの回避、ファーストクラスコレクションの構築、境界防御
"""

from typing import Dict, List, Optional

from domain.models import (
    DaySchedule,
    Session,
    SessionDetailResult,
    SessionNavigation,
    TimeBlock,
)
from domain.policies import FilterPolicy
from infrastructure.json_repository import JsonScheduleRepository


class ScheduleService:
    """スケジュール調整・抽出・進行中セッション判定を行うアプリケーションサービス"""

    def __init__(self, repository: JsonScheduleRepository):
        self.repository = repository
        self._cached_sessions: Optional[List[Session]] = None

    def _get_all_sessions(self) -> List[Session]:
        if self._cached_sessions is None:
            self._cached_sessions = self.repository.load_all_sessions()
        return self._cached_sessions

    def get_all_sessions(self) -> List[Session]:
        """全日程のセッション一覧を取得（キャッシュ利用）"""
        return self._get_all_sessions()

    def get_days(self) -> List[Dict[str, str]]:
        """カンファレンスの日程一覧を取得"""
        return self.repository.load_days()

    def filter_sessions(
        self,
        day: Optional[str] = None,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> List[Session]:
        """条件に基づくセッション一覧の抽出・絞り込み"""
        return FilterPolicy.apply(
            sessions=self._get_all_sessions(),
            day=day,
            category=category,
            keyword=keyword,
        )

    def get_day_schedule(
        self,
        date: str,
        keyword: Optional[str] = None,
    ) -> DaySchedule:
        """
        特定日のスケジュールをファーストクラスコレクション (DaySchedule) として構築。
        同一時間帯のセッションを TimeBlock に集約し、Track A → B → C の順に整列して返却。
        """
        all_sessions = self._get_all_sessions()
        day_sessions = FilterPolicy.apply(
            sessions=all_sessions,
            day=date,
            keyword=keyword,
        )

        # 時間帯 (start_minutes, end_minutes) ごとにグルーピング
        time_slot_map: Dict[tuple[int, int, str, str], List[Session]] = {}
        for s in day_sessions:
            key = (s.start_minutes, s.end_minutes, s.start_time, s.end_time)
            if key not in time_slot_map:
                time_slot_map[key] = []
            time_slot_map[key].append(s)

        # 時間帯順にソートして TimeBlock のリストを作成
        sorted_keys = sorted(time_slot_map.keys(), key=lambda k: k[0])
        time_blocks: List[TimeBlock] = []

        for key in sorted_keys:
            start_min, end_min, start_str, end_str = key
            slot_sessions = time_slot_map[key]
            # Track.sort_order 順（Track A → B → C）に整列
            sorted_slot_sessions = sorted(slot_sessions, key=lambda s: s.track.sort_order)

            time_blocks.append(
                TimeBlock(
                    start_time=start_str,
                    end_time=end_str,
                    start_minutes=start_min,
                    end_minutes=end_min,
                    sessions=sorted_slot_sessions,
                )
            )

        # 日付ラベルの取得
        days = self.get_days()
        label = next((d["label"] for d in days if d["date"] == date), date)

        return DaySchedule(
            date=date,
            label=label,
            time_blocks=time_blocks,
        )

    def get_session_detail(self, session_id: str) -> SessionDetailResult:
        """
        セッションIDから詳細と前後ナビゲーションを取得（境界防御と明示的な型）
        """
        sessions = self._get_all_sessions()
        target_session = None

        for idx, s in enumerate(sessions):
            if s.session_id == session_id:
                target_session = s
                break

        if target_session is None:
            return SessionDetailResult(
                is_found=False,
                error_message=f"セッションID '{session_id}' は存在しません。",
            )

        # 前後のセッション導出（同一日のセッション順）
        same_day_sessions = [s for s in sessions if s.day == target_session.day]
        same_day_idx = same_day_sessions.index(target_session)

        prev_session = same_day_sessions[same_day_idx - 1] if same_day_idx > 0 else None
        next_session = (
            same_day_sessions[same_day_idx + 1]
            if same_day_idx < len(same_day_sessions) - 1
            else None
        )

        navigation = SessionNavigation(
            previous_session=prev_session,
            next_session=next_session,
        )

        return SessionDetailResult(
            session=target_session,
            navigation=navigation,
            is_found=True,
        )

    def get_ongoing_session(self, date: str, current_minutes: int) -> Optional[Session]:
        """指定日の指定時刻（分）において現在進行中の代表セッションを取得"""
        schedule = self.get_day_schedule(date=date)
        ongoing_block = schedule.ongoing_block(current_minutes)
        if ongoing_block and ongoing_block.sessions:
            return ongoing_block.sessions[0]
        return None
