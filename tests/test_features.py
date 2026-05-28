from datetime import UTC, datetime, time

from features.aggregate_news_features import NewsFeatureRow, aggregate_news_features
from features.build_daily_features import feature_window


def test_aggregate_news_features() -> None:
    result = aggregate_news_features(
        [
            NewsFeatureRow("positive", 1.0, importance_score=2.0),
            NewsFeatureRow("negative", -1.0, importance_score=1.0),
        ]
    )
    assert result["news_count_total"] == 2
    assert result["news_count_positive"] == 1
    assert result["news_count_negative"] == 1
    assert result["sentiment_weighted_by_importance"] == 1 / 3


def test_feature_window_uses_previous_cutoff() -> None:
    start, end = feature_window(datetime(2026, 5, 26, 9, 0, tzinfo=UTC), time(15, 30))
    assert start.date().isoformat() == "2026-05-25"
    assert end.date().isoformat() == "2026-05-26"
