from app.services.pipeline_service import load_curated, run_pipeline


def test_pipeline_runs() -> None:
    result = run_pipeline()
    assert result["status"] == "success"
    assert result["curated_records"] > 100


def test_curated_loads() -> None:
    df = load_curated()
    assert "net_cash_flow" in df.columns
