"""Treasury summary analytics."""

from __future__ import annotations

import pandas as pd


def compute_treasury_summary(df: pd.DataFrame, low_liquidity_threshold: float = 1.0) -> dict:
    low_liq = df[df["liquidity_ratio"] < low_liquidity_threshold]
    peak_usage = df.nsmallest(5, "net_cash_flow")[["date", "net_cash_flow"]]
    return {
        "records": int(len(df)),
        "date_range": {
            "start": str(df["date"].min().date()),
            "end": str(df["date"].max().date()),
        },
        "average_inflow": float(df["inflow"].mean()),
        "average_outflow": float(df["outflow"].mean()),
        "average_balance": float(df["balance"].mean()),
        "cash_flow_volatility": float(df["net_cash_flow"].std()),
        "rolling_balance_trend_30d": float(df["balance"].rolling(30, min_periods=1).mean().iloc[-1]),
        "low_liquidity_days": int(len(low_liq)),
        "low_liquidity_dates": [str(d.date()) for d in low_liq["date"].head(10)],
        "peak_usage_periods": [
            {"date": str(row["date"].date()), "net_cash_flow": float(row["net_cash_flow"])}
            for _, row in peak_usage.iterrows()
        ],
    }
