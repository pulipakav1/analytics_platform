"""Benchmark forecasting models for model comparison."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from app.utils.metrics import compute_metrics


class NaiveLastValueForecaster:
    """Predict future values as the most recent observed value."""

    def evaluate(self, train_series: pd.Series, test_series: pd.Series) -> dict[str, float]:
        preds = np.full(len(test_series), train_series.iloc[-1], dtype=float)
        return compute_metrics(test_series.values, preds)


class LinearTrendForecaster:
    """Linear trend forecaster using time index as regressor."""

    def evaluate(self, train_series: pd.Series, test_series: pd.Series) -> dict[str, float]:
        x_train = np.arange(len(train_series)).reshape(-1, 1)
        y_train = train_series.values
        x_test = np.arange(len(train_series), len(train_series) + len(test_series)).reshape(-1, 1)
        model = LinearRegression()
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        return compute_metrics(test_series.values, preds)
