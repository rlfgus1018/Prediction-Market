from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from collectors.base import RawNewsItem
from database.models import DailyFeatures
from database.repositories.news_raw import NewsRawRepository


def seed_demo_daily_features(db: Session, days: int = 40) -> int:
    start = date.today() - timedelta(days=days)
    count = 0
    for index in range(days):
        day = start + timedelta(days=index)
        for symbol, offset in [("KOSPI", 0.0), ("KOSDAQ", 0.07)]:
            sentiment = ((index % 7) - 3) / 10 + offset
            market_return = ((index % 5) - 2) / 100
            row = DailyFeatures(
                target_date=day,
                symbol=symbol,
                feature_json={
                    "sentiment_mean": sentiment,
                    "sentiment_weighted_by_importance": sentiment * 1.2,
                    "news_count_positive": 8 + index % 4,
                    "news_count_negative": 5 + (index + 2) % 4,
                    "kospi_return_1d": market_return,
                    "kospi_volatility_5d": 0.012 + (index % 5) / 1000,
                    "semiconductor_sentiment": sentiment + 0.05,
                    "fx_news_score": -sentiment / 2,
                },
                label_up=1 if sentiment + market_return > 0 else 0,
                forward_return=Decimal(str(round((sentiment + market_return) / 20, 6))),
            )
            db.merge(row)
            count += 1
    db.commit()
    return count


def seed_demo_news_raw(db: Session, days: int = 10) -> int:
    items = []
    start = date.today() - timedelta(days=days)
    keywords = ["KOSPI", "KOSDAQ", "semiconductor", "fx", "policy"]
    for index in range(days):
        day = start + timedelta(days=index)
        for keyword_index, keyword in enumerate(keywords):
            tone = "positive" if (index + keyword_index) % 2 == 0 else "negative"
            items.append(
                RawNewsItem(
                    source="demo_news",
                    publisher="demo",
                    title=f"{keyword} {tone} market signal {day.isoformat()}",
                    summary=f"Demo scraped news item for {keyword} with {tone} tone.",
                    url=f"https://example.com/news/{day.isoformat()}/{keyword.lower()}",
                    published_at=None,
                    collected_at=None,
                    raw_payload={"keyword": keyword, "tone": tone, "demo": True},
                )
            )
    stats = NewsRawRepository(db).upsert_many(items)
    return stats.affected


def seed_demo_dataset(db: Session) -> dict[str, int]:
    return {
        "daily_features": seed_demo_daily_features(db),
        "news_raw": seed_demo_news_raw(db),
    }
