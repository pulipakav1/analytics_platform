"""ARIMA forecasting module with MLflow experiment tracking."""

from __future__ import annotations

from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from app.utils.metrics import compute_metrics


class ArimaForecaster:
    """ARIMA forecaster with train/test evaluation, MLflow tracking, and future prediction."""

    EXPERIMENT_NAME = "treasury-arima-forecasting"

    def __init__(self, order: tuple[int, int, int] = (2, 1, 2)) -> None:
        self.order = order
        self.model_fit = None
        mlflow.set_experiment(self.EXPERIMENT_NAME)

    def fit(self, series: pd.Series) -> None:
        model = ARIMA(series, order=self.order)
        self.model_fit = model.fit()

    def predict_in_sample(self, steps: int) -> pd.Series:
        if self.model_fit is None:
            raise ValueError("Model must be fit before prediction.")
        return self.model_fit.forecast(steps=steps)

    def evaluate(self, train_series: pd.Series, test_series: pd.Series) -> dict[str, float]:
        run_name = f"arima_p{self.order[0]}_d{self.order[1]}_q{self.order[2]}"
        with mlflow.start_run(run_name=run_name):
            mlflow.log_params({
                "p": self.order[0],
                "d": self.order[1],
                "q": self.order[2],
                "train_size": len(train_series),
                "test_size": len(test_series),
                "train_start": str(train_series.index.min()),
                "test_end": str(test_series.index.max()),
            })
            mlflow.set_tags({"model_type": "ARIMA", "domain": "treasury-cashflow"})

            self.fit(train_series)
            preds = self.predict_in_sample(len(test_series))
            metrics = compute_metrics(test_series.values, preds.values)
            mlflow.log_metrics(metrics)
        return metrics

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
        try:
            if mlflow.active_run():
                mlflow.log_artifact(str(path_obj))
        except Exception:
            pass
