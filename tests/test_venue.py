"""
会場ガイド・部屋アクセスのドメインモデルおよびサービス層の単体テスト
"""

from pathlib import Path

import pytest

from application.schedule_service import ScheduleService
from domain.models import VenueGuide
from infrastructure.json_repository import JsonScheduleRepository


@pytest.fixture
def service() -> ScheduleService:
    repo_root = Path(__file__).parent.parent
    repo = JsonScheduleRepository(repo_root / "data" / "ibis2026_program.json")
    return ScheduleService(repo)


def test_venue_guide_structure(service: ScheduleService):
    """VenueGuide の属性完全性と部屋リストの検証"""
    venue = service.get_venue_guide()
    assert isinstance(venue, VenueGuide)
    assert "大宮ソニックシティ" in venue.name
    assert "桜木町" in venue.address
    assert "大宮駅" in venue.station_access
    assert len(venue.rooms) >= 4

    # 必須トラックが含まれていること
    track_codes = [r.track_code for r in venue.rooms]
    assert "Track A" in track_codes
    assert "Track B" in track_codes
    assert "Track C" in track_codes


def test_venue_map_images_exist(service: ScheduleService):
    """VenueGuide で指定されているマップ画像が実ファイルとして存在し破損していないこと"""
    repo_root = Path(__file__).parent.parent
    venue = service.get_venue_guide()

    required_keys = {"overview", "route", "floor", "building"}
    assert required_keys.issubset(venue.map_images.keys())

    for key, relative_path in venue.map_images.items():
        img_path = repo_root / relative_path
        assert img_path.exists(), f"画像ファイルが存在しません: {img_path}"
        assert img_path.stat().st_size > 1000, f"画像ファイルサイズが不正です: {img_path}"


def test_room_guide_matching_and_fallback(service: ScheduleService):
    """トラックコードからの部屋ガイド取得およびあいまい検索・フォールバック検証"""
    venue = service.get_venue_guide()

    # Track A
    room_a = venue.get_room_guide("Track A")
    assert room_a is not None
    assert room_a.floor == "2F"
    assert "メインホール" in room_a.room_name
    assert room_a.note is not None

    # 大文字小文字の吸収
    assert venue.get_room_guide("track a") == room_a

    # Track B
    room_b = venue.get_room_guide("Track B")
    assert room_b is not None
    assert room_b.floor == "4F"
    assert "国際会議室" in room_b.room_name

    # Track C
    room_c = venue.get_room_guide("Track C")
    assert room_c is not None
    assert "市民" in room_c.room_name

    # サービス層経由での取得
    assert service.get_room_guide_for_track("Track A") == room_a
    assert service.get_room_guide_for_track("Track B") == room_b

    # 存在しないトラック
    assert venue.get_room_guide("NonExistentTrack") is None
    assert service.get_room_guide_for_track("NonExistentTrack") is None
