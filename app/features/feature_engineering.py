"""Treasury feature engineering."""

from __future__ import annotations

import pandas as pd


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["net_cash_flow"] = out["inflow"] - out["outflow"]
    out["rolling_mean_7"] = out["net_cash_flow"].rolling(7, min_periods=1).mean()
    out["rolling_std_7"] = out["net_cash_flow"].rolling(7, min_periods=1).std().fillna(0)
    out["rolling_mean_30"] = out["net_cash_flow"].rolling(30, min_periods=1).mean()
    out["rolling_std_30"] = out["net_cash_flow"].rolling(30, min_periods=1).std().fillna(0)
    out["lag_1"] = out["net_cash_flow"].shift(1).fillna(0)
    out["lag_7"] = out["net_cash_flow"].shift(7).fillna(0)
    out["pct_change_balance"] = out["balance"].pct_change().fillna(0)
    out["cumulative_net_flow"] = out["net_cash_flow"].cumsum()
    out["volatility_proxy"] = out["rolling_std_30"]
    out["liquidity_stress_proxy"] = 1 / out["liquidity_ratio"].clip(lower=0.01)
    out["day_of_week"] = out["date"].dt.dayofweek
    out["month"] = out["date"].dt.month
    out["is_month_end"] = out["date"].dt.is_month_end.astype(int)
    out["is_quarter_end"] = out["date"].dt.is_quarter_end.astype(int)
    return out
