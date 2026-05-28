import json
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import DailyFeatures, ListedStock, NewsRaw


def news_raw_frame(db: Session) -> pd.DataFrame:
    rows = db.scalars(select(NewsRaw).order_by(NewsRaw.collected_at.desc(), NewsRaw.id.desc())).all()
    records = [
        {
            "id": row.id,
            "source": row.source,
            "publisher": row.publisher,
            "title": row.title,
            "summary": row.summary,
            "url": row.url,
            "url_hash": row.url_hash,
            "published_at": _to_iso(row.published_at),
            "collected_at": _to_iso(row.collected_at),
            "raw_payload": json.dumps(row.raw_payload or {}, ensure_ascii=False),
        }
        for row in rows
    ]
    return pd.DataFrame(records)


def daily_features_frame(db: Session) -> pd.DataFrame:
    rows = db.scalars(
        select(DailyFeatures).order_by(DailyFeatures.target_date.desc(), DailyFeatures.symbol)
    ).all()
    records = [
        {
            "target_date": row.target_date.isoformat(),
            "symbol": row.symbol,
            "feature_json": json.dumps(row.feature_json or {}, ensure_ascii=False),
            "label_up": row.label_up,
            "forward_return": float(row.forward_return or 0),
        }
        for row in rows
    ]
    return pd.DataFrame(records)


def listed_stocks_frame(db: Session) -> pd.DataFrame:
    rows = db.scalars(
        select(ListedStock).order_by(ListedStock.base_date.desc(), ListedStock.short_code)
    ).all()
    records = [
        {
            "base_date": row.base_date,
            "short_code": row.short_code,
            "isin_code": row.isin_code,
            "market_category": row.market_category,
            "item_name": row.item_name,
            "corp_registration_number": row.corp_registration_number,
            "corp_name": row.corp_name,
            "collected_at": _to_iso(row.collected_at),
            "raw_payload": json.dumps(row.raw_payload or {}, ensure_ascii=False),
        }
        for row in rows
    ]
    return pd.DataFrame(records)


def dataframe_to_csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8-sig")


def dataframe_to_json_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8")


def _to_iso(value: Any) -> str | None:
    return value.isoformat() if value else None
