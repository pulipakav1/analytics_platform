"""Validation logic for treasury datasets."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

REQUIRED_COLUMNS = [
    "date",
    "inflow",
    "outflow",
    "balance",
    "transaction_count",
    "liquidity_ratio",
]

NUMERIC_COLUMNS = [
    "inflow",
    "outflow",
    "balance",
    "transaction_count",
    "liquidity_ratio",
]


def validate_columns(df: pd.DataFrame, required: Iterable[str] = REQUIRED_COLUMNS) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def clean_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df)
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out = out.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")
    for col in NUMERIC_COLUMNS:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.dropna(subset=NUMERIC_COLUMNS)
    if not out["date"].is_monotonic_increasing:
        raise ValueError("Date column is not monotonic increasing after sorting.")
    out.reset_index(drop=True, inplace=True)
    return out
