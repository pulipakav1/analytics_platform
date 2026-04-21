import pandas as pd

from app.models.arima_forecast import ArimaForecaster


def test_arima_forecast_shape() -> None:
    idx = pd.date_range("2024-01-01", periods=180, freq="D")
    series = pd.Series([i + (i % 7) for i in range(180)], index=idx, dtype=float)
    forecaster = ArimaForecaster(order=(1, 1, 1))
    forecast_df = forecaster.forecast_future(series, horizon=10)
    assert len(forecast_df) == 10
    assert "forecast" in forecast_df.columns
