from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import DailyFeatures


def load_daily_feature_frame(db: Session, symbols: list[str] | None = None) -> pd.DataFrame:
    statement = select(DailyFeatures)
    if symbols:
        statement = statement.where(DailyFeatures.symbol.in_(symbols))
    rows = db.scalars(statement.order_by(DailyFeatures.target_date, DailyFeatures.symbol)).all()

    records: list[dict[str, Any]] = []
    for row in rows:
        if row.label_up is None:
            continue
        record = {
            "target_date": row.target_date,
            "symbol": row.symbol,
            "label_up": row.label_up,
            "forward_return": float(row.forward_return or 0),
        }
        record.update(_flatten_feature_json(row.feature_json))
        records.append(record)
    return pd.DataFrame(records)


def _flatten_feature_json(features: dict[str, Any], prefix: str = "") -> dict[str, float]:
    flat: dict[str, float] = {}
    for key, value in features.items():
        name = f"{prefix}_{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(_flatten_feature_json(value, name))
        elif isinstance(value, bool):
            flat[name] = float(value)
        elif isinstance(value, int | float):
            flat[name] = float(value)
    return flat
