"""Pandera data contracts for treasury cashflow pipeline."""

from __future__ import annotations

import pandera as pa
from pandera import Check, Column, DataFrameSchema

RAW_SCHEMA = DataFrameSchema(
    columns={
        "date": Column(pa.DateTime, nullable=False, unique=True),
        "inflow": Column(pa.Float, checks=Check.greater_than_or_equal_to(0), nullable=False),
        "outflow": Column(pa.Float, checks=Check.greater_than_or_equal_to(0), nullable=False),
        "balance": Column(pa.Float, nullable=False),
        "liquidity_ratio": Column(pa.Float, checks=Check.greater_than(0), nullable=False),
    },
    coerce=True,
    strict=False,
    name="raw_treasury",
)

CURATED_SCHEMA = DataFrameSchema(
    columns={
        "date": Column(pa.DateTime, nullable=False),
        "net_flow": Column(pa.Float, nullable=False),
        "rolling_mean_7": Column(pa.Float, nullable=True),
        "rolling_mean_30": Column(pa.Float, nullable=True),
        "volatility_proxy": Column(pa.Float, nullable=True),
        "liquidity_stress_score": Column(
            pa.Float,
            checks=Check.in_range(0, 10),
            nullable=True,
        ),
    },
    coerce=True,
    strict=False,
    name="curated_treasury",
)
