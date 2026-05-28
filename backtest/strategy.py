def probability_threshold_signal(prob_up: float, upper: float = 0.55, lower: float = 0.45) -> int:
    if prob_up >= upper:
        return 1
    if prob_up <= lower:
        return -1
    return 0
