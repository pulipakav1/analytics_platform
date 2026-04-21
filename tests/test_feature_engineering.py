import pandas as pd

from app.features.feature_engineering import build_features


def test_feature_columns_present() -> None:
    df = pd.DataFrame(
        {
            "date": pd.date_range("2025-01-01", periods=40),
            "inflow": [100.0] * 40,
            "outflow": [90.0] * 40,
            "balance": [1000 + i for i in range(40)],
            "transaction_count": [100] * 40,
            "liquidity_ratio": [1.2] * 40,
            "cash_position": [980 + i for i in range(40)],
        }
    )
    out = build_features(df)
    assert "rolling_mean_7" in out.columns
    assert "lag_7" in out.columns
