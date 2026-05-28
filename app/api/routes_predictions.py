from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.models import Predictions
from database.repositories.predictions import PredictionsRepository
from database.session import get_db
from models.run_prediction import train_predict_and_store

router = APIRouter()


class PredictionRunRequest(BaseModel):
    symbols: list[str] | None = None
    prefer_lightgbm: bool = True


@router.get("/latest")
def latest_predictions(db: Session = Depends(get_db)) -> dict[str, object]:
    items = PredictionsRepository(db).latest()
    return {
        "items": [_serialize_prediction(item) for item in items],
        "message": "No predictions found. Run POST /predictions/run after daily_features is populated."
        if not items
        else "ok",
    }


@router.post("/run")
def run_predictions(
    payload: PredictionRunRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = train_predict_and_store(
        db,
        symbols=payload.symbols,
        prefer_lightgbm=payload.prefer_lightgbm,
    )
    return {
        "model_name": result.model_name,
        "model_version": result.model_version,
        "metrics": result.metrics,
        "predictions": [
            {
                "symbol": prediction.symbol,
                "target_date": str(prediction.target_date),
                "prob_up": prediction.prob_up,
                "expected_return": prediction.expected_return,
                "confidence": prediction.confidence,
                "top_positive_features": prediction.top_positive_features,
                "top_negative_features": prediction.top_negative_features,
            }
            for prediction in result.predictions
        ],
    }


def _serialize_prediction(prediction: Predictions) -> dict[str, Any]:
    return {
        "prediction_date": str(prediction.prediction_date),
        "target_symbol": prediction.target_symbol,
        "horizon": prediction.horizon,
        "model_version": prediction.model_version,
        "prob_up": _float(prediction.prob_up),
        "expected_return": _float(prediction.expected_return),
        "confidence": _float(prediction.confidence),
        "explanation": prediction.explanation or {},
        "created_at": prediction.created_at.isoformat(),
    }


def _float(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None
