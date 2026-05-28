from sqlalchemy.orm import Session

from collectors.base import NewsCollector
from collectors.naver_news import NaverNewsCollector
from collectors.rss import RssCollector
from database.repositories.news_raw import NewsRawRepository, UpsertStats


def collect_naver_news_to_db(
    keywords: list[str],
    db: Session,
    collector: NewsCollector | None = None,
) -> UpsertStats:
    news_collector = collector or NaverNewsCollector()
    items = news_collector.collect(keywords)
    return NewsRawRepository(db).upsert_many(items)


def collect_rss_news_to_db(
    keywords: list[str],
    db: Session,
    collector: NewsCollector | None = None,
) -> UpsertStats:
    news_collector = collector or RssCollector()
    items = news_collector.collect(keywords)
    return NewsRawRepository(db).upsert_many(items)
