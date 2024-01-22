import numpy as np


class LinReg:
    # method used for slope estimation
    @staticmethod
    def estimate_slope(features, responses):
        if len(features) <= 1 or len(responses) <= 1 or len(features) != len(responses):
            raise ValueError("Input arrays must have >= 2 elements and be the same length.")

        feature_mean = np.mean(features)
        response_mean = np.mean(responses)

        denominator = np.sum((features - feature_mean) ** 2)
        if denominator == 0:
            raise ValueError("Denominator is zero, cannot compute slope.")
        numerator = np.sum((features - feature_mean) * (responses - response_mean))

        return numerator / denominator, feature_mean, response_mean

    # method used for intercept estimation
    @staticmethod
    def estimate_intercept(slope, feature_mean, response_mean):
        return response_mean - slope * feature_mean

    # method that returns a single, predicted value for the next year
    # 'features': a one-dimensional NumPy array that contains years for which we have the data
    # 'responses': a one-dimensional NumPy array that contains values for those years
    @staticmethod
    def predict_value(features, responses):
        slope, feature_mean, response_mean = LinReg.estimate_slope(features, responses)
        return (
            LinReg.estimate_intercept(slope, feature_mean, response_mean) +
            slope * (features[-1] + 1),
            features[-1] + 1
        )
