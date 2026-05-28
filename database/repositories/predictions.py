from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from database.models import Predictions
from models.market_direction import MarketDirectionResult


class PredictionsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert_model_result(self, result: MarketDirectionResult) -> int:
        rows = []
        now = datetime.now(UTC)
        for prediction in result.predictions:
            rows.append(
                {
                    "prediction_date": prediction.target_date,
                    "target_symbol": prediction.symbol,
                    "horizon": "T+1",
                    "model_version": result.model_version,
                    "prob_up": Decimal(str(round(prediction.prob_up, 6))),
                    "expected_return": Decimal(str(round(prediction.expected_return, 6))),
                    "confidence": Decimal(str(round(prediction.confidence, 6))),
                    "explanation": {
                        "model_name": result.model_name,
                        "metrics": result.metrics,
                        "feature_columns": result.feature_columns,
                        "top_positive_features": prediction.top_positive_features,
                        "top_negative_features": prediction.top_negative_features,
                    },
                    "created_at": now,
                }
            )
        if not rows:
            return 0

        bind = getattr(self.db, "bind", None)
        insert_fn = sqlite_insert if bind and bind.dialect.name == "sqlite" else pg_insert
        statement = insert_fn(Predictions).values(rows)
        statement = statement.on_conflict_do_update(
            index_elements=[
                Predictions.prediction_date,
                Predictions.target_symbol,
                Predictions.horizon,
                Predictions.model_version,
            ],
            set_={
                "prob_up": statement.excluded.prob_up,
                "expected_return": statement.excluded.expected_return,
                "confidence": statement.excluded.confidence,
                "explanation": statement.excluded.explanation,
                "created_at": statement.excluded.created_at,
            },
        )
        result_proxy = self.db.execute(statement)
        self.db.commit()
        return result_proxy.rowcount or len(rows)

    def latest(self, limit: int = 20) -> list[Predictions]:
        statement = (
            select(Predictions)
            .order_by(Predictions.created_at.desc(), Predictions.prediction_date.desc())
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def upsert_prediction(
        self,
        prediction_date,
        target_symbol: str,
        horizon: str,
        model_version: str,
        prob_up: float,
        expected_return: float | None = None,
        confidence: float | None = None,
        explanation: dict[str, Any] | None = None,
    ) -> int:
        now = datetime.now(UTC)
        row = {
            "prediction_date": prediction_date,
            "target_symbol": target_symbol,
            "horizon": horizon,
            "model_version": model_version,
            "prob_up": Decimal(str(round(prob_up, 6))),
            "expected_return": Decimal(str(round(expected_return or 0, 6))),
            "confidence": Decimal(str(round(confidence or 0, 6))),
            "explanation": explanation or {},
            "created_at": now,
        }
        bind = getattr(self.db, "bind", None)
        insert_fn = sqlite_insert if bind and bind.dialect.name == "sqlite" else pg_insert
        statement = insert_fn(Predictions).values([row])
        statement = statement.on_conflict_do_update(
            index_elements=[
                Predictions.prediction_date,
                Predictions.target_symbol,
                Predictions.horizon,
                Predictions.model_version,
            ],
            set_={
                "prob_up": statement.excluded.prob_up,
                "expected_return": statement.excluded.expected_return,
                "confidence": statement.excluded.confidence,
                "explanation": statement.excluded.explanation,
                "created_at": statement.excluded.created_at,
            },
        )
        result_proxy = self.db.execute(statement)
        self.db.commit()
        return result_proxy.rowcount or 1
