from collections.abc import Iterator

import pandas as pd


def walk_forward_splits(
    frame: pd.DataFrame,
    train_size: int,
    valid_size: int,
) -> Iterator[tuple[pd.DataFrame, pd.DataFrame]]:
    ordered = frame.sort_values("target_date")
    start = 0
    while start + train_size + valid_size <= len(ordered):
        train = ordered.iloc[start : start + train_size]
        valid = ordered.iloc[start + train_size : start + train_size + valid_size]
        yield train, valid
        start += valid_size
