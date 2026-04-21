"""Treasury analytics service."""

from __future__ import annotations

import pandas as pd

from app.core.config import get_config
from app.models.summary_analytics import compute_treasury_summary
from app.services.pipeline_service import load_curated


def get_cashflow_data(limit: int = 120) -> list[dict]:
    df = load_curated().sort_values("date")
    cols = ["date", "inflow", "outflow", "balance", "net_cash_flow", "liquidity_ratio"]
    return df[cols].tail(limit).assign(date=lambda x: x["date"].dt.strftime("%Y-%m-%d")).to_dict(orient="records")


def get_summary() -> dict:
    config = get_config()
    df: pd.DataFrame = load_curated()
    return compute_treasury_summary(df, low_liquidity_threshold=config.low_liquidity_threshold)
