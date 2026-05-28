from dataclasses import dataclass
from datetime import UTC, date, datetime
import math

from sqlalchemy import select
from sqlalchemy.orm import Session

from collectors.ingest_news import collect_rss_news_to_db
from collectors.ingest_stocks import collect_krx_listed_stocks_to_db
from database.models import ListedStock, NewsRaw
from database.repositories.predictions import PredictionsRepository
from processing.cleaner import strip_html
from processing.sentiment_analyzer import KeywordSentimentAnalyzer


@dataclass(frozen=True)
class StockSignalResult:
    target_symbol: str
    item_name: str
    news_count: int
    prob_up: float
    confidence: float
    top_news: list[dict[str, str]]


def analyze_company_by_name(db: Session, item_name: str) -> StockSignalResult:
    collect_krx_listed_stocks_to_db(db, item_name=item_name, rows=20)
    return collect_news_and_predict_stock_signal(db, item_name)


def collect_news_and_predict_stock_signal(db: Session, item_name: str) -> StockSignalResult:
    stock = _find_latest_stock(db, item_name)
    keywords = _keywords_for_stock(stock, item_name)
    collect_rss_news_to_db(keywords, db)

    news_rows = _matching_news(db, keywords)
    analyzer = KeywordSentimentAnalyzer()
    scores = []
    top_news = []
    for row in news_rows:
        text = f"{strip_html(row.title)} {strip_html(row.summary)}"
        result = analyzer.analyze(text)
        scores.append(result.score)
        if len(top_news) < 10:
            top_news.append(
                {
                    "title": strip_html(row.title),
                    "summary": strip_html(row.summary),
                    "url": row.url,
                    "published_at": row.published_at.isoformat() if row.published_at else "",
                }
            )

    mean_score = sum(scores) / len(scores) if scores else 0.0
    prob_up = 0.5 + math.tanh(mean_score / 3) * 0.25
    confidence = min(0.9, abs(prob_up - 0.5) * 2 + min(len(news_rows) / 50, 0.4))
    target_symbol = f"{stock.short_code} {stock.item_name}" if stock else item_name

    PredictionsRepository(db).upsert_prediction(
        prediction_date=date.today(),
        target_symbol=target_symbol,
        horizon="news-signal",
        model_version=f"stock_news_signal-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
        prob_up=prob_up,
        expected_return=(prob_up - 0.5) / 20,
        confidence=confidence,
        explanation={
            "model_name": "stock_news_signal",
            "item_name": stock.item_name if stock else item_name,
            "short_code": stock.short_code if stock else None,
            "keywords": keywords,
            "news_count": len(news_rows),
            "mean_sentiment_score": mean_score,
            "top_news": top_news,
        },
    )

    return StockSignalResult(
        target_symbol=target_symbol,
        item_name=stock.item_name if stock else item_name,
        news_count=len(news_rows),
        prob_up=prob_up,
        confidence=confidence,
        top_news=top_news,
    )


def _find_latest_stock(db: Session, item_name: str) -> ListedStock | None:
    statement = (
        select(ListedStock)
        .where(ListedStock.item_name.contains(item_name))
        .order_by(ListedStock.base_date.desc())
        .limit(1)
    )
    return db.scalars(statement).first()


def _keywords_for_stock(stock: ListedStock | None, fallback_name: str) -> list[str]:
    keywords = [fallback_name]
    if stock:
        keywords.extend([stock.item_name, stock.corp_name or "", stock.short_code])
    return sorted({keyword.strip() for keyword in keywords if keyword and keyword.strip()})


def _matching_news(db: Session, keywords: list[str]) -> list[NewsRaw]:
    if not keywords:
        return []
    rows = db.scalars(select(NewsRaw).order_by(NewsRaw.collected_at.desc())).all()
    lowered = [keyword.lower() for keyword in keywords]
    matches = []
    for row in rows:
        text = f"{row.title or ''} {row.summary or ''}".lower()
        if any(keyword.lower() in text for keyword in lowered):
            matches.append(row)
    return matches
