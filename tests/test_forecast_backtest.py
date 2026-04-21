from app.services.forecast_service import run_forecast


def test_forecast_contains_backtest_outputs() -> None:
    result = run_forecast()
    assert "backtest_metrics" in result
    assert "backtest_champion_model" in result
    assert result["backtest_champion_model"] in result["backtest_metrics"]
