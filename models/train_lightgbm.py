from dataclasses import dataclass

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, brier_score_loss, f1_score, roc_auc_score
from sklearn.pipeline import Pipeline


@dataclass(frozen=True)
class LightGbmTrainingResult:
    model: Pipeline
    metrics: dict[str, float]


def train_lightgbm(
    train: pd.DataFrame,
    valid: pd.DataFrame,
    feature_columns: list[str],
    label_column: str = "label_up",
) -> LightGbmTrainingResult:
    """Train a LightGBM classifier for market direction prediction."""
    try:
        from lightgbm import LGBMClassifier
    except ImportError as exc:
        raise RuntimeError("Install the ml extra to train LightGBM: pip install -e '.[ml]'") from exc

    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "classifier",
                LGBMClassifier(
                    objective="binary",
                    n_estimators=300,
                    learning_rate=0.03,
                    num_leaves=15,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    verbosity=-1,
                ),
            ),
        ]
    )
    model.fit(train[feature_columns], train[label_column])
    probabilities = model.predict_proba(valid[feature_columns])[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    metrics = {
        "accuracy": accuracy_score(valid[label_column], predictions),
        "auc": roc_auc_score(valid[label_column], probabilities),
        "f1": f1_score(valid[label_column], predictions),
        "brier": brier_score_loss(valid[label_column], probabilities),
    }
    return LightGbmTrainingResult(model=model, metrics=metrics)
