"""
アプリケーション層: プレゼンテーション層からのユースケース要求を処理するサービス
設計原則: 貧血ドメインモデルの回避、ファーストクラスコレクションの構築、境界防御
"""

from typing import Dict, List, Optional

from domain.live import ActiveLive, LiveContext
from domain.models import (
    DaySchedule,
    RoomGuide,
    Session,
    SessionDetailResult,
    SessionNavigation,
    TimeBlock,
    VenueGuide,
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
        return self.get_live_session(date=date, live=ActiveLive(current_minutes))

    def get_live_session(self, date: str, live: LiveContext) -> Optional[Session]:
        """ライブ文脈に基づき、指定日の進行中セッションを取得 (非ライブ日は None)"""
        return live.ongoing_session(self.get_day_schedule(date=date))

    def get_venue_guide(self) -> VenueGuide:
        """会場全体・フロアマップ情報の取得"""
        rooms = [
            RoomGuide(
                track_code="Track A",
                room_name="メインホール (大ホール)",
                building="ホール棟",
                floor="2F",
                access_instruction="大宮駅西口の歩行者デッキ直結の北口エントランスから入館してすぐ正面です。総合受付もこのフロアに設置されます。",
                note="Day 2・3のポスターセッション時は2Fホワイエも併用されます。",
            ),
            RoomGuide(
                track_code="Track B",
                room_name="国際会議室",
                building="ホール棟",
                floor="4F",
                access_instruction="ホール棟2Fエントランスより館内奥のエレベーターを利用して4階へ上がってください。",
            ),
            RoomGuide(
                track_code="Track C",
                room_name="市民ギャラリー / 市民ホール",
                building="ビル棟 (ソニックシティビル)",
                floor="1F / B1F",
                access_instruction="歩行者デッキ右手のソニックシティビル入口より入館し、館内エスカレーターで1階または地下1階へ降りてください。",
            ),
            RoomGuide(
                track_code="Poster",
                room_name="第1展示場 (ポスター会場)",
                building="ビル棟 (ソニックシティビル)",
                floor="B1F",
                access_instruction="ビル棟入口よりエレベーターまたはエスカレーターで地下1階へお降りください。",
            ),
            RoomGuide(
                track_code="Party",
                room_name="パレスホテル大宮 (懇親会会場)",
                building="パレスホテル大宮",
                floor="宴会場フロア",
                access_instruction="ソニックシティビルに隣接。2F歩行者デッキ経由で直通アクセス可能です。",
            ),
        ]
        return VenueGuide(
            name="大宮ソニックシティ (Sonic City Hall)",
            address="埼玉県さいたま市大宮区桜木町1-7-5",
            station_access="JR・東武野田線・ニューシャトル「大宮駅」西口より歩行者デッキ直結 徒歩約3分",
            map_images={
                "overview": "data/maps/overview_diagram.png",
                "route": "data/maps/access_hall_intl.png",
                "floor": "data/maps/floor_hall_4f.jpg",
                "building": "data/maps/sonic_city_building_guide.png",
            },
            rooms=rooms,
        )

    def get_room_guide_for_track(self, track_code: str) -> Optional[RoomGuide]:
        """トラックコードに対応する部屋ガイドを取得"""
        venue = self.get_venue_guide()
        return venue.get_room_guide(track_code)
