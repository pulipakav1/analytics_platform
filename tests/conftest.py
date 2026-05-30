"""Shared fixtures for the treasury analytics test suite."""

import pandas as pd
import pytest

from app.data.preprocessing import to_staging_schema
from app.data.synthetic_data import generate_synthetic_treasury_data
from app.data.validator import clean_and_validate
from app.features.feature_engineering import build_features


@pytest.fixture(scope="session")
def raw_df() -> pd.DataFrame:
    return generate_synthetic_treasury_data(days=200)


@pytest.fixture(scope="session")
def validated_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    return clean_and_validate(raw_df)


@pytest.fixture(scope="session")
def staging_df(validated_df: pd.DataFrame) -> pd.DataFrame:
    return to_staging_schema(validated_df)


@pytest.fixture(scope="session")
def curated_df(staging_df: pd.DataFrame) -> pd.DataFrame:
    return build_features(staging_df)


@pytest.fixture(scope="session")
def net_cash_flow_series(curated_df: pd.DataFrame) -> pd.Series:
    return curated_df.set_index("date")["net_cash_flow"].dropna()
