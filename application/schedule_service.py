"""
アプリケーション層: プレゼンテーション層からのユースケース要求を処理するサービス
"""

from typing import Any, Dict, List, Optional
from domain.models import Session
from domain.policies import CategoryVisualPolicy, FilterPolicy, TimePolicy
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

    def get_days(self) -> List[Dict[str, str]]:
        """カンファレンスの日程一覧を取得"""
        return self.repository.load_days()

    def get_filtered_schedule(
        self,
        day: Optional[str] = None,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> List[Session]:
        """指定された検索・フィルタ条件に合致するセッション一覧を取得"""
        sessions = self._get_all_sessions()
        return FilterPolicy.apply(
            sessions=sessions,
            day=day,
            category=category,
            keyword=keyword,
        )

    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        """セッションIDから特定のセッション詳細を取得"""
        sessions = self._get_all_sessions()
        for s in sessions:
            if s.session_id == session_id:
                return s
        return None

    def get_ongoing_session(self, day: str, minutes: int) -> Optional[Session]:
        """指定日の指定時刻（分）において現在進行中のセッションを取得"""
        day_sessions = self.get_filtered_schedule(day=day)
        for s in day_sessions:
            if s.is_ongoing(minutes):
                return s
        return None

    def get_category_filters(self) -> List[Dict[str, str]]:
        """利用可能なカテゴリ一覧と表示メタデータを取得"""
        categories = ["all", "os", "invited", "tutorial", "poster", "panel"]
        result = []
        for cat in categories:
            if cat == "all":
                result.append({"key": "all", "label": "All Sessions"})
            else:
                style = CategoryVisualPolicy.get_style(cat)
                result.append({"key": cat, "label": style["label"]})
        return result
