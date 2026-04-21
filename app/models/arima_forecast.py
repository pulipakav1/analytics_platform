"""ARIMA forecasting module."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from app.utils.metrics import compute_metrics


class ArimaForecaster:
    """ARIMA forecaster with train/test evaluation and future prediction."""

    def __init__(self, order: tuple[int, int, int] = (2, 1, 2)) -> None:
        self.order = order
        self.model_fit = None

    def fit(self, series: pd.Series) -> None:
        model = ARIMA(series, order=self.order)
        self.model_fit = model.fit()

    def predict_in_sample(self, steps: int) -> pd.Series:
        if self.model_fit is None:
            raise ValueError("Model must be fit before prediction.")
        return self.model_fit.forecast(steps=steps)

    def evaluate(self, train_series: pd.Series, test_series: pd.Series) -> dict[str, float]:
        self.fit(train_series)
        preds = self.predict_in_sample(len(test_series))
        return compute_metrics(test_series.values, preds.values)

    def forecast_future(self, full_series: pd.Series, horizon: int) -> pd.DataFrame:
        self.fit(full_series)
        future = self.predict_in_sample(horizon)
        future_dates = pd.date_range(
            start=full_series.index[-1] + pd.Timedelta(days=1),
            periods=horizon,
            freq="D",
        )
        return pd.DataFrame({"date": future_dates, "forecast": future.values})

    def save(self, path: str) -> None:
        if self.model_fit is None:
            raise ValueError("No fitted model to persist.")
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"order": self.order, "model_fit": self.model_fit}, path_obj)
