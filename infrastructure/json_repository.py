"""
インフラストラクチャ層: JSONデータソースからのスケジュール読み込みとドメインモデルマッピング
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from domain.models import Session, Speaker, Talk, Track
from domain.policies import TimePolicy


class JsonScheduleRepository:
    """ローカルJSONファイルからIBIS2026スケジュールデータを読み込むリポジトリ"""

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def load_all_sessions(self) -> List[Session]:
        """全日程のセッション一覧をドメインモデルとして読み込む"""
        if not self.file_path.exists():
            return []

        try:
            raw_text = self.file_path.read_text(encoding="utf-8")
            data = json.loads(raw_text)
        except Exception as e:
            print(f"Error loading {self.file_path}: {e}")
            return []

        sessions: List[Session] = []
        for item in data.get("sessions", []):
            session = self._map_to_session(item)
            sessions.append(session)

        return sessions

    def load_days(self) -> List[Dict[str, str]]:
        """カンファレンスの日程メタデータ一覧を読み込む"""
        if not self.file_path.exists():
            return []
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            return data.get("days", [])
        except Exception:
            return []

    def _map_to_session(self, item: Dict[str, Any]) -> Session:
        """JSON辞書からSessionドメインオブジェクトへマッピング"""
        start_time = item.get("start_time", "09:00")
        end_time = item.get("end_time", "10:00")

        start_min = TimePolicy.time_str_to_minutes(start_time)
        end_min = TimePolicy.time_str_to_minutes(end_time)

        # トラック値オブジェクトの構築
        raw_track = item.get("track", {})
        if isinstance(raw_track, dict):
            track = Track(
                code=raw_track.get("code", "Track A"),
                name=raw_track.get("name", "メインホール (2F)"),
                sort_order=raw_track.get("sort_order", 1),
            )
        else:
            # 文字列だった場合のフォールバック
            track_str = str(raw_track)
            code = "Track A"
            order = 1
            if "Track B" in track_str or "国際" in track_str:
                code = "Track B"
                order = 2
            elif "Track C" in track_str or "市民" in track_str or "ポスター" in track_str:
                code = "Track C"
                order = 3
            track = Track(code=code, name=track_str, sort_order=order)

        talks: List[Talk] = []
        for t in item.get("talks", []):
            spk_data = t.get("speaker", {})
            speaker = Speaker(
                name=spk_data.get("name", ""),
                affiliation=spk_data.get("affiliation", ""),
            )
            talk = Talk(
                title=t.get("title", ""),
                speaker=speaker,
                start_time=t.get("start_time", start_time),
                end_time=t.get("end_time", end_time),
                abstract=t.get("abstract"),
                citations=t.get("citations", []),
                tags=t.get("tags", []),
            )
            talks.append(talk)

        return Session(
            session_id=item.get("session_id", ""),
            day=item.get("day", ""),
            day_label=item.get("day_label", ""),
            title=item.get("title", ""),
            track=track,
            category=item.get("category", "general"),
            start_time=start_time,
            end_time=end_time,
            start_minutes=start_min,
            end_minutes=end_min,
            organizer=item.get("organizer"),
            talks=talks,
            abstract=item.get("abstract"),
            url=item.get("url"),
        )
