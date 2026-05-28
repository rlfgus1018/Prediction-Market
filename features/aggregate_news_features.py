from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class NewsFeatureRow:
    sentiment_label: str
    sentiment_score: float
    event_type: str | None = None
    importance_score: float = 1.0
    novelty_score: float = 1.0


def aggregate_news_features(rows: list[NewsFeatureRow]) -> dict[str, float | int]:
    if not rows:
        return {
            "news_count_total": 0,
            "news_count_positive": 0,
            "news_count_negative": 0,
            "sentiment_mean": 0.0,
            "sentiment_weighted_by_importance": 0.0,
        }

    labels = Counter(row.sentiment_label for row in rows)
    weighted_sum = sum(
        row.sentiment_score * row.importance_score * row.novelty_score for row in rows
    )
    weight_total = sum(row.importance_score * row.novelty_score for row in rows)
    return {
        "news_count_total": len(rows),
        "news_count_positive": labels["positive"],
        "news_count_negative": labels["negative"],
        "sentiment_mean": sum(row.sentiment_score for row in rows) / len(rows),
        "sentiment_weighted_by_importance": weighted_sum / weight_total if weight_total else 0.0,
    }
