"""Configuration loader for the treasury analytics platform."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseModel, Field


class DataConfig(BaseModel):
    raw_path: str = "data/raw/treasury_daily.csv"
    staging_path: str = "data/staging/treasury_staging.csv"
    curated_path: str = "data/curated/treasury_curated.csv"
    outputs_dir: str = "data/outputs"
    generate_if_missing: bool = True
    synthetic_days: int = 730


class ForecastConfig(BaseModel):
    target_column: str = "balance"
    horizon_days: int = 14
    arima_order: tuple[int, int, int] = (2, 1, 2)
    train_ratio: float = 0.8
    benchmark_models: list[str] = Field(default_factory=lambda: ["naive_last", "linear_trend"])
    backtest_windows: int = 4
    backtest_test_size: int = 14


class AppConfig(BaseModel):
    app_name: str = "Quantitative Treasury Analytics Platform"
    version: str = "1.0.0"
    log_level: str = "INFO"
    low_liquidity_threshold: float = 1.0
    data: DataConfig = Field(default_factory=DataConfig)
    forecast: ForecastConfig = Field(default_factory=ForecastConfig)


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def get_config(config_path: str = "config/config.yaml") -> AppConfig:
    loaded = _load_yaml(Path(config_path))
    return AppConfig.model_validate(loaded)
