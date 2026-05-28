import pandas as pd


def add_return_features(index_bars: pd.DataFrame) -> pd.DataFrame:
    frame = index_bars.sort_values(["symbol", "date"]).copy()
    frame["return_1d"] = frame.groupby("symbol")["close"].pct_change()
    frame["return_5d"] = frame.groupby("symbol")["close"].pct_change(5)
    frame["volatility_5d"] = frame.groupby("symbol")["return_1d"].rolling(5).std().reset_index(0, drop=True)
    return frame
