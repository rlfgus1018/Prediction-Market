import numpy as np


def directional_hit_ratio(actual: list[int], predicted: list[int]) -> float:
    if not actual:
        return 0.0
    return float(np.mean(np.array(actual) == np.array(predicted)))


def max_drawdown(returns: list[float]) -> float:
    if not returns:
        return 0.0
    equity = np.cumprod(1 + np.array(returns))
    running_max = np.maximum.accumulate(equity)
    drawdown = equity / running_max - 1
    return float(drawdown.min())
