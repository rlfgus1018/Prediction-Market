from dataclasses import dataclass
from datetime import UTC, datetime

import pandas as pd

from models.train_baseline import train_logistic_regression
from models.train_lightgbm import train_lightgbm


@dataclass(frozen=True)
class MarketPrediction:
    symbol: str
    target_date: object
    prob_up: float
    expected_return: float
    confidence: float
    top_positive_features: list[dict[str, float | str]]
    top_negative_features: list[dict[str, float | str]]


@dataclass(frozen=True)
class MarketDirectionResult:
    model: object
    model_name: str
    model_version: str
    feature_columns: list[str]
    metrics: dict[str, float]
    predictions: list[MarketPrediction]


def train_market_direction_model(
    frame: pd.DataFrame,
    prefer_lightgbm: bool = True,
    min_train_rows: int = 20,
) -> MarketDirectionResult:
    if frame.empty:
        raise ValueError("daily_features has no labeled rows.")

    ordered = frame.sort_values(["target_date", "symbol"]).reset_index(drop=True)
    feature_columns = [
        column
        for column in ordered.columns
        if column not in {"target_date", "symbol", "label_up", "forward_return"}
        and pd.api.types.is_numeric_dtype(ordered[column])
    ]
    if not feature_columns:
        raise ValueError("No numeric feature columns were found in daily_features.feature_json.")

    train, valid = _time_split(ordered, min_train_rows=min_train_rows)
    model_name = "lightgbm"
    try:
        if not prefer_lightgbm:
            raise RuntimeError("LightGBM disabled.")
        training = train_lightgbm(train, valid, feature_columns)
    except RuntimeError:
        model_name = "logistic_regression"
        training = train_logistic_regression(train, valid, feature_columns)

    latest_rows = ordered.groupby("symbol", as_index=False).tail(1)
    probabilities = training.model.predict_proba(latest_rows[feature_columns])[:, 1]
    mean_abs_return = max(float(train["forward_return"].abs().mean() or 0), 0.001)
    predictions = [
        _build_prediction(row, prob_up, feature_columns, mean_abs_return)
        for (_, row), prob_up in zip(latest_rows.iterrows(), probabilities, strict=True)
    ]
    version_time = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return MarketDirectionResult(
        model=training.model,
        model_name=model_name,
        model_version=f"{model_name}-{version_time}",
        feature_columns=feature_columns,
        metrics=training.metrics,
        predictions=predictions,
    )


def _time_split(frame: pd.DataFrame, min_train_rows: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    if len(frame) < 8:
        raise ValueError("At least 8 labeled daily feature rows are required.")
    valid_size = max(2, min(len(frame) // 5, len(frame) - min_train_rows))
    if valid_size <= 0:
        valid_size = max(2, len(frame) // 4)
    split_at = len(frame) - valid_size
    if split_at <= 1:
        raise ValueError("Not enough rows for a time-ordered train/validation split.")
    return frame.iloc[:split_at], frame.iloc[split_at:]


def _build_prediction(
    row: pd.Series,
    prob_up: float,
    feature_columns: list[str],
    mean_abs_return: float,
) -> MarketPrediction:
    feature_values = row[feature_columns].fillna(0).astype(float)
    strongest = feature_values.reindex(feature_values.abs().sort_values(ascending=False).index).head(6)
    positive = [
        {"feature": name, "value": float(value)} for name, value in strongest.items() if value > 0
    ][:3]
    negative = [
        {"feature": name, "value": float(value)} for name, value in strongest.items() if value < 0
    ][:3]
    return MarketPrediction(
        symbol=str(row["symbol"]),
        target_date=row["target_date"],
        prob_up=float(prob_up),
        expected_return=float((prob_up - 0.5) * 2 * mean_abs_return),
        confidence=float(abs(prob_up - 0.5) * 2),
        top_positive_features=positive,
        top_negative_features=negative,
    )
