def predict_probability(model, features):
    probabilities = model.predict_proba(features)
    return probabilities[:, 1]
