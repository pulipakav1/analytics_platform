"""Data loading functions."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core.config import AppConfig
from app.data.synthetic_data import generate_and_save


def load_raw_data(config: AppConfig) -> pd.DataFrame:
    raw_path = Path(config.data.raw_path)
    if not raw_path.exists():
        if not config.data.generate_if_missing:
            raise FileNotFoundError(f"Raw dataset not found: {raw_path}")
        return generate_and_save(str(raw_path), days=config.data.synthetic_days)
    return pd.read_csv(raw_path)
