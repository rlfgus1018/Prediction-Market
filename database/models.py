from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Integer, Numeric, Text, UniqueConstraint
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from database.session import Base

BigIntPk = BigInteger().with_variant(Integer, "sqlite")


class NewsRaw(Base):
    __tablename__ = "news_raw"

    id: Mapped[int] = mapped_column(BigIntPk, primary_key=True)
    source: Mapped[str] = mapped_column(Text)
    publisher: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text, unique=True)
    url_hash: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    raw_payload: Mapped[dict] = mapped_column(JSON)


class NewsClean(Base):
    __tablename__ = "news_clean"

    news_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    clean_title: Mapped[str] = mapped_column(Text)
    clean_body: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str] = mapped_column(Text, default="ko")
    duplicate_group_id: Mapped[str | None] = mapped_column(Text)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)


class NewsFeatures(Base):
    __tablename__ = "news_features"

    news_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sentiment_label: Mapped[str | None] = mapped_column(Text)
    sentiment_score: Mapped[Decimal | None] = mapped_column(Numeric)
    event_type: Mapped[str | None] = mapped_column(Text)
    importance_score: Mapped[Decimal | None] = mapped_column(Numeric)
    novelty_score: Mapped[Decimal | None] = mapped_column(Numeric)
    market_relevance_score: Mapped[Decimal | None] = mapped_column(Numeric)
    entities: Mapped[dict | None] = mapped_column(JSON)
    sectors: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class IndexBars(Base):
    __tablename__ = "index_bars"

    symbol: Mapped[str] = mapped_column(Text, primary_key=True)
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    open: Mapped[Decimal | None] = mapped_column(Numeric)
    high: Mapped[Decimal | None] = mapped_column(Numeric)
    low: Mapped[Decimal | None] = mapped_column(Numeric)
    close: Mapped[Decimal] = mapped_column(Numeric)
    volume: Mapped[Decimal | None] = mapped_column(Numeric)


class ListedStock(Base):
    __tablename__ = "listed_stocks"
    __table_args__ = (UniqueConstraint("base_date", "short_code"),)

    id: Mapped[int] = mapped_column(BigIntPk, primary_key=True)
    base_date: Mapped[str] = mapped_column(Text)
    short_code: Mapped[str] = mapped_column(Text)
    isin_code: Mapped[str | None] = mapped_column(Text)
    market_category: Mapped[str | None] = mapped_column(Text)
    item_name: Mapped[str] = mapped_column(Text)
    corp_registration_number: Mapped[str | None] = mapped_column(Text)
    corp_name: Mapped[str | None] = mapped_column(Text)
    raw_payload: Mapped[dict] = mapped_column(JSON)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DailyFeatures(Base):
    __tablename__ = "daily_features"

    target_date: Mapped[date] = mapped_column(Date, primary_key=True)
    symbol: Mapped[str] = mapped_column(Text, primary_key=True)
    feature_json: Mapped[dict] = mapped_column(JSON)
    label_up: Mapped[int | None]
    forward_return: Mapped[Decimal | None] = mapped_column(Numeric)


class Predictions(Base):
    __tablename__ = "predictions"
    __table_args__ = (UniqueConstraint("prediction_date", "target_symbol", "horizon", "model_version"),)

    id: Mapped[int] = mapped_column(BigIntPk, primary_key=True)
    prediction_date: Mapped[date] = mapped_column(Date)
    target_symbol: Mapped[str] = mapped_column(Text)
    horizon: Mapped[str] = mapped_column(Text)
    model_version: Mapped[str] = mapped_column(Text)
    prob_up: Mapped[Decimal] = mapped_column(Numeric)
    expected_return: Mapped[Decimal | None] = mapped_column(Numeric)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric)
    explanation: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
