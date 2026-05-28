import pandas as pd

from models.market_direction import train_market_direction_model


def test_train_market_direction_model_falls_back_to_logistic_regression() -> None:
    frame = pd.DataFrame(
        {
            "target_date": pd.date_range("2026-01-01", periods=12),
            "symbol": ["KOSPI"] * 12,
            "sentiment_mean": [
                -0.4,
                -0.2,
                0.1,
                0.3,
                -0.1,
                0.4,
                -0.3,
                0.2,
                0.5,
                -0.5,
                0.6,
                -0.6,
            ],
            "kospi_return_1d": [
                -0.01,
                -0.02,
                0.01,
                0.02,
                -0.01,
                0.03,
                -0.02,
                0.01,
                0.02,
                -0.03,
                0.04,
                -0.04,
            ],
            "label_up": [0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
            "forward_return": [
                -0.01,
                -0.02,
                0.01,
                0.02,
                -0.01,
                0.03,
                -0.02,
                0.01,
                0.02,
                -0.03,
                0.04,
                -0.04,
            ],
        }
    )

    result = train_market_direction_model(frame, prefer_lightgbm=False, min_train_rows=8)

    assert result.model_name == "logistic_regression"
    assert result.predictions
    assert 0 <= result.predictions[0].prob_up <= 1
