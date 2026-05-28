from sqlalchemy.orm import Session

from database.repositories.predictions import PredictionsRepository
from models.datasets import load_daily_feature_frame
from models.market_direction import MarketDirectionResult, train_market_direction_model


def train_predict_and_store(
    db: Session,
    symbols: list[str] | None = None,
    prefer_lightgbm: bool = True,
) -> MarketDirectionResult:
    frame = load_daily_feature_frame(db, symbols=symbols)
    result = train_market_direction_model(frame, prefer_lightgbm=prefer_lightgbm)
    PredictionsRepository(db).upsert_model_result(result)
    return result
