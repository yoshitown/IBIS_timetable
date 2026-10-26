"""
ドメインポリシー層: 時刻計算、フィルタリング規則、カテゴリカラーマッピング等のビジネスルール
"""

from domain.models import Session


class TimePolicy:
    """時刻に関するビジネスルール"""

    @staticmethod
    def time_str_to_minutes(time_str: str) -> int:
        """'10:30' -> 630 分に変換"""
        parts = time_str.strip().split(":")
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        return hours * 60 + minutes

    @staticmethod
    def minutes_to_time_str(minutes: int) -> str:
        """630 -> '10:30' に変換"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"


class DayPolicy:
    """日程タブに関するビジネスルール"""

    FALLBACK_DAY = "2026-10-27"  # 会期外アクセス時の既定日: Day 2

    @staticmethod
    def default_day(days: list[dict[str, str]], today: str) -> str:
        """会期中ならその日、会期外は Day 2 を既定とする"""
        return today if any(d["date"] == today for d in days) else DayPolicy.FALLBACK_DAY

    @staticmethod
    def badge_label(days: list[dict[str, str]], date: str) -> str:
        """ヘッダー用の 'Day N' ラベル (不明な日付は 'Live')"""
        label = next((d["label"] for d in days if d["date"] == date), "")
        return label.split(":")[0] or "Live"

    @staticmethod
    def tab_label(label: str) -> str:
        """'Day 2: Oct 27 (Tue)' -> 'Day 2 Oct 27'"""
        day, _, rest = label.partition(":")
        return f"{day} {rest.split('(')[0].strip()}"


class CategoryVisualPolicy:
    """Stitchデザインシステムに準拠したセッションカテゴリのビジュアル仕様"""

    PALETTE: dict[str, dict[str, str]] = {
        "os": {
            "label": "Organized Sessions (OS)",
            "badge_bg": "bg-primary-container",
            "badge_text": "text-on-primary",
            "border_color": "#4F46E5",
            "card_bg": "#4F46E5",
            "accent_hex": "#4F46E5",
        },
        "invited": {
            "label": "Invited Talks",
            "badge_bg": "bg-secondary-container",
            "badge_text": "text-on-secondary-container",
            "border_color": "#D97706",
            "card_bg": "#FE932C",
            "accent_hex": "#D97706",
        },
        "tutorial": {
            "label": "Tutorials",
            "badge_bg": "bg-surface-tint",
            "badge_text": "text-on-primary",
            "border_color": "#4D44E3",
            "card_bg": "#4D44E3",
            "accent_hex": "#4D44E3",
        },
        "poster": {
            "label": "Posters",
            "badge_bg": "bg-tertiary",
            "badge_text": "text-on-tertiary",
            "border_color": "#0D9488",
            "card_bg": "#00524B",
            "accent_hex": "#0D9488",
        },
        "panel": {
            "label": "Panels",
            "badge_bg": "bg-inverse-surface",
            "badge_text": "text-inverse-on-surface",
            "border_color": "#0F172A",
            "card_bg": "#283044",
            "accent_hex": "#0F172A",
        },
        "general": {
            "label": "General / Remarks",
            "badge_bg": "bg-surface-container",
            "badge_text": "text-on-surface",
            "border_color": "#777587",
            "card_bg": "#EAEDFF",
            "accent_hex": "#777587",
        },
    }

    @classmethod
    def get_style(cls, category: str) -> dict[str, str]:
        return cls.PALETTE.get(category.lower(), cls.PALETTE["general"])


class FilterPolicy:
    """セッションの抽出・絞り込みポリシー"""

    @staticmethod
    def apply(
        sessions: list[Session],
        day: str | None = None,
        category: str | None = None,
        keyword: str | None = None,
    ) -> list[Session]:
        """日付、カテゴリ、検索語の複合条件を適用"""
        result = sessions

        if day and day != "all":
            result = [s for s in result if s.day == day or day in s.day_label]

        if category and category.lower() != "all":
            cat_norm = category.lower()
            result = [s for s in result if s.category.lower() == cat_norm]

        if keyword:
            kw_clean = keyword.strip()
            if kw_clean:
                result = [s for s in result if s.matches_keyword(kw_clean)]

        return result
