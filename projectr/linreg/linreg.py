import numpy as np


# method used for slope estimation
def estimate_slope(features, responses):
    if len(features) == 0 or len(responses) == 0 or len(features) != len(responses):
        raise ValueError("Input arrays must be non-empty and have the same length.")

    feature_mean = np.mean(features)
    response_mean = np.mean(responses)

    denominator = np.sum((features - feature_mean) ** 2)
    if denominator == 0:
        raise ValueError("Denominator is zero, cannot compute slope.")
    numerator = np.sum((features - feature_mean) * (responses - response_mean))

    return numerator / denominator, feature_mean, response_mean


# method used for intercept estimation
def estimate_intercept(slope, feature_mean, response_mean):
    return response_mean - slope * feature_mean


# method that returns a single, predicted value for the next year
# 'features': a one-dimensional NumPy array that contains years for which we have the data
# 'responses': a one-dimensional NumPy array that contains values for those years
def predict_value(features, responses):
    slope, feature_mean, response_mean = estimate_slope(features, responses)
    return (
        estimate_intercept(slope, feature_mean, response_mean) +
        slope * (features[-1] + 1),
        features[-1] + 1
    )

