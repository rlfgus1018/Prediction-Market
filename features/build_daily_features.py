from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


def feature_window(target_at: datetime, cutoff: time, tz_name: str = "Asia/Seoul") -> tuple[datetime, datetime]:
    """Return the observable news window for a daily market prediction.

    For a target date's close-based prediction, only data collected after the previous cutoff
    and at or before the target cutoff should be included.
    """
    tz = ZoneInfo(tz_name)
    target_local = target_at.astimezone(tz)
    end = datetime.combine(target_local.date(), cutoff, tzinfo=tz)
    start = end - timedelta(days=1)
    return start, end
