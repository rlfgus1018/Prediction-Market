from sklearn.calibration import calibration_curve


def calibration_points(y_true, probabilities, bins: int = 10) -> dict[str, list[float]]:
    prob_true, prob_pred = calibration_curve(y_true, probabilities, n_bins=bins)
    return {"prob_true": prob_true.tolist(), "prob_pred": prob_pred.tolist()}
