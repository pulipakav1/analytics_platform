"""Simple model registry and benchmarking for treasury forecasts."""

from __future__ import annotations

from typing import Protocol

import pandas as pd

from app.models.arima_forecast import ArimaForecaster
from app.models.benchmark_models import LinearTrendForecaster, NaiveLastValueForecaster


class Evaluator(Protocol):
    def evaluate(self, train_series: pd.Series, test_series: pd.Series) -> dict[str, float]:
        ...


class ModelRegistry:
    """In-memory registry with model factory and benchmark utilities."""

    def __init__(self) -> None:
        self._registry: dict[str, object] = {}

    def register(self, name: str, model: object) -> None:
        self._registry[name] = model

    def get(self, name: str) -> object:
        if name not in self._registry:
            raise KeyError(f"Model '{name}' is not registered.")
        return self._registry[name]

    def list_models(self) -> list[str]:
        return sorted(self._registry.keys())


def build_default_registry(arima_order: tuple[int, int, int]) -> ModelRegistry:
    registry = ModelRegistry()
    registry.register("arima", ArimaForecaster(order=arima_order))
    registry.register("naive_last", NaiveLastValueForecaster())
    registry.register("linear_trend", LinearTrendForecaster())
    return registry
