import pandas as pd

from backtest.walk_forward import walk_forward_splits


def test_walk_forward_splits_are_time_ordered() -> None:
    frame = pd.DataFrame({"target_date": pd.date_range("2026-01-01", periods=6), "x": range(6)})
    splits = list(walk_forward_splits(frame, train_size=3, valid_size=1))
    assert len(splits) == 3
    assert splits[0][0]["x"].tolist() == [0, 1, 2]
    assert splits[0][1]["x"].tolist() == [3]
