# Quantitative Treasury Analytics Platform

Production-grade treasury analytics platform for liquidity monitoring, cashflow analytics, and time-series forecasting.

## Why This Project

Treasury teams need reliable visibility into liquidity, cash position, and near-term balances. This project demonstrates an end-to-end implementation of that problem:

- data ingestion and quality controls
- layered analytics pipeline (`RAW -> STAGING -> CURATED`)
- time-series forecasting using ARIMA
- benchmark model registry and rolling backtests
- API delivery and dashboard consumption
- Dockerized deployment and automated tests

## Core Features

### 1) Data Engineering Pipeline
- Ingests treasury daily records from configurable CSV paths.
- Auto-generates realistic synthetic 2-year daily treasury data if source file is missing.
- Validates schema, types, missing values, duplicates, and date ordering.
- Writes layered outputs:
  - `data/raw/treasury_daily.csv`
  - `data/staging/treasury_staging.csv`
  - `data/curated/treasury_curated.csv`

### 2) Treasury Analytics
- Net cash flow and rolling trend metrics.
- Liquidity stress proxy and low-liquidity period detection.
- Volatility and peak usage analysis for treasury reporting.

### 3) Forecasting (ARIMA + Model Registry)
- ARIMA forecasting for treasury balance (`statsmodels`).
- Metrics: RMSE, MAE, MAPE.
- Benchmark models:
  - `naive_last`
  - `linear_trend`
- Champion model selection on:
  - single time-based holdout split
  - rolling-window backtesting

### 4) Serving & Visualization
- FastAPI endpoints for health, cashflow, summary, forecast, and pipeline run.
- Streamlit dashboard with KPIs, trend charts, forecast view, volatility tracking, and filters.

## Architecture

```text
Data Source / Synthetic Generator
        |
        v
RAW Layer (ingestion)
        |
        v
STAGING Layer (validation + cleaning + schema normalization)
        |
        v
CURATED Layer (feature engineering + model-ready signals)
        |
        +--> FastAPI endpoints (operational serving)
        |
        +--> ARIMA + benchmark registry + backtesting
        |
        +--> Streamlit dashboard (analytics UI)
```

## Tech Stack

- **Language**: Python
- **Data/Quant**: Pandas, NumPy, statsmodels, scikit-learn
- **API**: FastAPI, Uvicorn, Pydantic
- **Dashboard**: Streamlit, Plotly
- **Config**: PyYAML
- **Testing**: pytest
- **Packaging/Runtime**: Docker, docker-compose

## Project Structure

```text
treasury-analytics-platform/
├── app/
│   ├── api/                  # FastAPI routes
│   ├── core/                 # config + logging
│   ├── data/                 # loading, validation, preprocessing, synthetic generation
│   ├── features/             # feature engineering
│   ├── models/               # ARIMA, benchmarks, model registry, analytics
│   ├── schemas/              # typed response contracts
│   ├── services/             # orchestration and business logic
│   └── utils/                # metrics helpers
├── dashboard/                # Streamlit app
├── config/                   # yaml configuration
├── data/                     # raw/staging/curated/outputs artifacts
├── sql/                      # dbt-style transformation references
├── tests/                    # unit tests
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## Quick Start (Local)

```bash
python -m venv .venv
```

Activate environment:
- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
python -m pytest -q
```

Run pipeline:

```bash
python -c "from app.services.pipeline_service import run_pipeline; print(run_pipeline())"
```

Run API:

```bash
uvicorn app.main:app --reload --port 8000
```

Run dashboard (separate terminal):

```bash
streamlit run dashboard/streamlit_app.py
```

## API Endpoints

- `GET /health`
- `GET /cashflow?limit=120`
- `GET /summary`
- `GET /forecast`
- `POST /run-pipeline`

Docs: `http://localhost:8000/docs`

## Docker

Build and run all services:

```bash
docker-compose up --build
```

Services:
- API: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8501`

## Forecasting Methodology

1. Build daily curated series for target (default: `balance`).
2. Time-based train/test split for realistic forward validation.
3. Evaluate ARIMA on holdout (`RMSE`, `MAE`, `MAPE`).
4. Benchmark ARIMA vs `naive_last` and `linear_trend`.
5. Compute champion for holdout split (`champion_model`).
6. Run rolling-window backtests and compute aggregate champion (`backtest_champion_model`).
7. Generate future 14-day ARIMA forecast and persist artifacts.

## Example Forecast Response Signals

The `/forecast` endpoint returns:
- ARIMA metrics (`metrics`)
- benchmark leaderboard (`benchmark_metrics`)
- single-split winner (`champion_model`)
- rolling backtest aggregates (`backtest_metrics`)
- robust winner (`backtest_champion_model`)
- future predictions (`forecast_records`)

## Testing Coverage

Current test suite covers:
- data pipeline creation and curated loading
- feature engineering outputs
- ARIMA forecasting behavior
- model registry and benchmark evaluation
- rolling-backtest response fields
- treasury summary analytics

## Roadmap

- PostgreSQL persistence + SQLAlchemy data models
- scheduled orchestration (Airflow or APScheduler)
- CI/CD pipeline and cloud deployment templates
- alerting channel integration for liquidity risk thresholds
