from dataclasses import dataclass

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, f1_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class TrainingResult:
    model: Pipeline
    metrics: dict[str, float]


def train_logistic_regression(
    train: pd.DataFrame,
    valid: pd.DataFrame,
    feature_columns: list[str],
    label_column: str = "label_up",
) -> TrainingResult:
    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=1000)),
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
    return TrainingResult(model=model, metrics=metrics)
