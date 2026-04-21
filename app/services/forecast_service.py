"""Forecast service for ARIMA workflows."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core.config import get_config
from app.models.arima_forecast import ArimaForecaster
from app.models.model_registry import build_default_registry
from app.services.pipeline_service import load_curated


def _evaluate_models(
    train: pd.Series,
    test: pd.Series,
    arima_order: tuple[int, int, int],
    benchmark_models: list[str],
) -> dict[str, dict[str, float]]:
    registry = build_default_registry(arima_order)
    selected_models = ["arima"] + [name for name in benchmark_models if name in registry.list_models()]
    scores: dict[str, dict[str, float]] = {}
    for model_name in selected_models:
        model = registry.get(model_name)
        scores[model_name] = model.evaluate(train, test)  # type: ignore[union-attr]
    return scores


def _rolling_backtest(
    series: pd.Series,
    train_ratio: float,
    test_size: int,
    windows: int,
    arima_order: tuple[int, int, int],
    benchmark_models: list[str],
) -> dict[str, dict[str, float]]:
    split_idx = int(len(series) * train_ratio)
    window_scores: dict[str, list[dict[str, float]]] = {}
    for w in range(windows):
        test_end = len(series) - (windows - 1 - w) * test_size
        test_start = max(split_idx, test_end - test_size)
        if test_start <= 30 or test_end <= test_start:
            continue
        train = series.iloc[:test_start]
        test = series.iloc[test_start:test_end]
        scores = _evaluate_models(train, test, arima_order, benchmark_models)
        for model_name, metrics in scores.items():
            window_scores.setdefault(model_name, []).append(metrics)

    aggregates: dict[str, dict[str, float]] = {}
    for model_name, score_list in window_scores.items():
        if not score_list:
            continue
        aggregates[model_name] = {
            "rmse_mean": float(sum(s["rmse"] for s in score_list) / len(score_list)),
            "mae_mean": float(sum(s["mae"] for s in score_list) / len(score_list)),
            "mape_mean": float(sum(s["mape"] for s in score_list) / len(score_list)),
            "windows": float(len(score_list)),
        }
    return aggregates


def run_forecast() -> dict:
    config = get_config()
    df = load_curated().sort_values("date")
    target = config.forecast.target_column
    ts = df.set_index("date")[target].asfreq("D").ffill()

    split_idx = int(len(ts) * config.forecast.train_ratio)
    train, test = ts.iloc[:split_idx], ts.iloc[split_idx:]

    model_scores = _evaluate_models(
        train=train,
        test=test,
        arima_order=config.forecast.arima_order,
        benchmark_models=config.forecast.benchmark_models,
    )

    champion_model = min(model_scores.items(), key=lambda item: item[1]["rmse"])[0]
    backtest_scores = _rolling_backtest(
        series=ts,
        train_ratio=config.forecast.train_ratio,
        test_size=config.forecast.backtest_test_size,
        windows=config.forecast.backtest_windows,
        arima_order=config.forecast.arima_order,
        benchmark_models=config.forecast.benchmark_models,
    )
    backtest_champion = (
        min(backtest_scores.items(), key=lambda item: item[1]["rmse_mean"])[0] if backtest_scores else champion_model
    )

    forecaster = ArimaForecaster(order=config.forecast.arima_order)
    metrics = model_scores["arima"]
    future_df = forecaster.forecast_future(ts, config.forecast.horizon_days)

    outputs_dir = Path(config.data.outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    forecast_path = outputs_dir / "forecast.csv"
    model_path = outputs_dir / "arima_model.joblib"
    future_df.to_csv(forecast_path, index=False)
    forecaster.save(str(model_path))

    return {
        "target_column": target,
        "horizon_days": config.forecast.horizon_days,
        "arima_order": config.forecast.arima_order,
        "metrics": metrics,
        "benchmark_metrics": model_scores,
        "champion_model": champion_model,
        "backtest_metrics": backtest_scores,
        "backtest_champion_model": backtest_champion,
        "forecast_records": future_df.to_dict(orient="records"),
        "forecast_path": str(forecast_path),
    }
