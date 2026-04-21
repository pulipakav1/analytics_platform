"""Synthetic treasury data generator."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def generate_synthetic_treasury_data(days: int = 730, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="D")
    base_inflow = 1_200_000 + 80_000 * np.sin(np.arange(days) * 2 * np.pi / 30)
    base_outflow = 1_050_000 + 65_000 * np.cos(np.arange(days) * 2 * np.pi / 7)
    inflow = np.maximum(base_inflow + rng.normal(0, 60_000, days), 1000)
    outflow = np.maximum(base_outflow + rng.normal(0, 50_000, days), 1000)
    net = inflow - outflow
    balance = 20_000_000 + np.cumsum(net)
    tx_count = np.maximum((inflow + outflow) / 5000 + rng.normal(0, 30, days), 50).astype(int)
    liquidity_ratio = np.clip(balance / (outflow * 7), 0.4, 4.0)
    cash_position = balance - 0.2 * outflow

    return pd.DataFrame(
        {
            "date": dates,
            "inflow": inflow.round(2),
            "outflow": outflow.round(2),
            "balance": balance.round(2),
            "transaction_count": tx_count,
            "cash_position": cash_position.round(2),
            "liquidity_ratio": liquidity_ratio.round(4),
        }
    )


def generate_and_save(path: str, days: int = 730) -> pd.DataFrame:
    df = generate_synthetic_treasury_data(days=days)
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path_obj, index=False)
    return df
