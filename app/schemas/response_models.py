"""API response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str


class CashflowResponse(BaseModel):
    data: list[dict[str, Any]]


class ForecastResponse(BaseModel):
    target_column: str
    horizon_days: int
    arima_order: tuple[int, int, int]
    metrics: dict[str, float]
    benchmark_metrics: dict[str, dict[str, float]]
    champion_model: str
    backtest_metrics: dict[str, dict[str, float]]
    backtest_champion_model: str
    forecast_records: list[dict[str, Any]]
    forecast_path: str


class SummaryResponse(BaseModel):
    summary: dict[str, Any]


class PipelineResponse(BaseModel):
    status: str
    raw_records: int
    staging_records: int
    curated_records: int
    staging_path: str
    curated_path: str
