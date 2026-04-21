import pandas as pd

from app.models.summary_analytics import compute_treasury_summary


def test_summary_contains_keys() -> None:
    df = pd.DataFrame(
        {
            "date": pd.date_range("2025-01-01", periods=10),
            "inflow": [100] * 10,
            "outflow": [90] * 10,
            "balance": [1000 + i for i in range(10)],
            "net_cash_flow": [10] * 10,
            "liquidity_ratio": [1.2] * 10,
        }
    )
    summary = compute_treasury_summary(df)
    assert "average_inflow" in summary
    assert "low_liquidity_days" in summary
