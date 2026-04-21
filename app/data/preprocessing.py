"""Preprocessing transformations for staging layer."""

from __future__ import annotations

import pandas as pd


def to_staging_schema(df: pd.DataFrame) -> pd.DataFrame:
    staging = df.copy()
    if "cash_position" not in staging.columns:
        staging["cash_position"] = staging["balance"] - 0.2 * staging["outflow"]
    staging["inflow"] = staging["inflow"].round(2)
    staging["outflow"] = staging["outflow"].round(2)
    staging["balance"] = staging["balance"].round(2)
    staging["cash_position"] = staging["cash_position"].round(2)
    staging["liquidity_ratio"] = staging["liquidity_ratio"].round(4)
    return staging
