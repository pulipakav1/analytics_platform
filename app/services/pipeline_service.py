"""Pipeline orchestration service."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core.config import get_config
from app.data.loader import load_raw_data
from app.data.preprocessing import to_staging_schema
from app.data.validator import clean_and_validate
from app.features.feature_engineering import build_features


def run_pipeline() -> dict:
    config = get_config()
    raw_df = load_raw_data(config)
    validated = clean_and_validate(raw_df)
    staging = to_staging_schema(validated)
    curated = build_features(staging)

    Path(config.data.staging_path).parent.mkdir(parents=True, exist_ok=True)
    Path(config.data.curated_path).parent.mkdir(parents=True, exist_ok=True)
    staging.to_csv(config.data.staging_path, index=False)
    curated.to_csv(config.data.curated_path, index=False)

    return {
        "status": "success",
        "raw_records": int(len(raw_df)),
        "staging_records": int(len(staging)),
        "curated_records": int(len(curated)),
        "staging_path": config.data.staging_path,
        "curated_path": config.data.curated_path,
    }


def load_curated() -> pd.DataFrame:
    config = get_config()
    curated_path = Path(config.data.curated_path)
    if not curated_path.exists():
        run_pipeline()
    df = pd.read_csv(curated_path, parse_dates=["date"])
    return df
