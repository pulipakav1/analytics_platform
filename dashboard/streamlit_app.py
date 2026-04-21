"""Streamlit dashboard for treasury analytics."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.forecast_service import run_forecast
from app.services.pipeline_service import load_curated, run_pipeline
from app.services.treasury_service import get_summary

st.set_page_config(page_title="Treasury Analytics Dashboard", layout="wide")
st.title("Quantitative Treasury Analytics Platform")

if st.button("Run Pipeline"):
    run_pipeline()
    st.success("Pipeline completed.")

df = load_curated().sort_values("date")
summary = get_summary()
min_date, max_date = df["date"].min().date(), df["date"].max().date()
start_date, end_date = st.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
filtered = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Inflow", f"${summary['average_inflow']:,.0f}")
col2.metric("Avg Outflow", f"${summary['average_outflow']:,.0f}")
col3.metric("Cashflow Volatility", f"${summary['cash_flow_volatility']:,.0f}")
col4.metric("Low Liquidity Days", summary["low_liquidity_days"])

st.plotly_chart(px.line(filtered, x="date", y=["inflow", "outflow"], title="Cash Flow Trends"), use_container_width=True)
st.plotly_chart(px.line(filtered, x="date", y="balance", title="Balance Trend"), use_container_width=True)
st.plotly_chart(px.line(filtered, x="date", y="rolling_std_30", title="Rolling Volatility (30d)"), use_container_width=True)

if st.button("Run ARIMA Forecast"):
    result = run_forecast()
    st.write("Metrics:", result["metrics"])

forecast_path = Path("data/outputs/forecast.csv")
if forecast_path.exists():
    forecast_df = pd.read_csv(forecast_path, parse_dates=["date"])
    st.plotly_chart(px.line(forecast_df, x="date", y="forecast", title="ARIMA Forecast"), use_container_width=True)

st.subheader("Summary")
st.json(summary)
