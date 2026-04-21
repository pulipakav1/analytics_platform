import pandas as pd

from app.models.model_registry import build_default_registry


def test_registry_and_benchmark_metrics() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    series = pd.Series([1000 + i * 3 + (i % 5) for i in range(120)], index=idx, dtype=float)
    train, test = series.iloc[:96], series.iloc[96:]

    registry = build_default_registry((1, 1, 1))
    model_names = registry.list_models()
    assert "arima" in model_names
    assert "naive_last" in model_names
    assert "linear_trend" in model_names

    for name in model_names:
        metrics = registry.get(name).evaluate(train, test)  # type: ignore[union-attr]
        assert "rmse" in metrics and "mae" in metrics and "mape" in metrics
