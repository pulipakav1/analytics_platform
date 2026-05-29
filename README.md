# Treasury Analytics Platform

Production-grade treasury cashflow analytics system: RAW → STAGING → CURATED pipeline, ARIMA(2,1,2) forecasting with MLflow experiment tracking, Apache Airflow orchestration, Pandera data contracts, and a FastAPI + Streamlit serving layer.

## Architecture

```
CSV Source / Synthetic Generator (730-day daily series)
        │
        ▼
┌─────────────────────────────────────────────┐
│              Apache Airflow DAG             │
│   ingest_and_validate → transform_features  │
│         → train_and_forecast                │
│   Schedule: 06:00 UTC daily │ SLA: 2h       │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │     Data Pipeline       │
        │  RAW → STAGING → CURATED│
        │  Pandera schema contracts│
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Feature Engineering   │
        │  Rolling stats · lags   │
        │  Liquidity signals      │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │  ARIMA(2,1,2) Forecaster│
        │  MLflow experiment log  │
        │  14-day horizon         │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │  FastAPI + Streamlit    │
        │  5 endpoints · KPI dash │
        └─────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | Apache Airflow 2.9 — daily DAG, 2-retry SLA enforcement |
| Data Contracts | Pandera — typed schemas for RAW and CURATED layers |
| Experiment Tracking | MLflow — param/metric logging, model artifact registry |
| Data Pipeline | Pandas, NumPy — RAW → STAGING → CURATED |
| Forecasting | statsmodels ARIMA, scikit-learn benchmarks, rolling backtests |
| API | FastAPI, Uvicorn, Pydantic response schemas |
| Dashboard | Streamlit, Plotly |
| Config | PyYAML + Pydantic |
| Testing | pytest — 7 test suites |
| CI/CD | GitHub Actions — lint, test coverage, DAG import check |
| Runtime | Docker, Docker Compose |

## Quick Start

```bash
git clone https://github.com/pulipakav1/analytics_platform.git
cd treasury-analytics-platform

cp .env.example .env
docker-compose up --build
# API docs  →  http://localhost:8000/docs
# Dashboard →  http://localhost:8501
# MLflow UI →  mlflow ui (port 5000)
```

**Local Python:**

```bash
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt

make pipeline     # RAW → STAGING → CURATED
make api          # FastAPI at :8000
make dashboard    # Streamlit at :8501
make test         # pytest
```

## Data Pipeline

| Stage | What happens |
|---|---|
| **RAW** | CSV ingestion or 730-day synthetic fallback; Pandera schema contract enforced |
| **STAGING** | Type casting, duplicate removal, date ordering, cash position calculation |
| **CURATED** | 22-feature engineering: rolling stats (7/30-day), lags, drawdown, liquidity stress, temporal flags |

## Airflow DAG — `treasury_analytics_pipeline`

```
ingest_and_validate  →  transform_features  →  train_and_forecast
   • schema check         • run_pipeline()        • ARIMA fit
   • XCom: raw_count      • curated validation    • MLflow run logged
   • 2 retries            • XCom: curated_count   • 14-day forecast saved
```

Runs at `0 6 * * *` (06:00 UTC). 2-hour SLA. 2 auto-retries per task.

## Forecasting & MLflow

Each ARIMA evaluation run logs to the `treasury-arima-forecasting` experiment:

- **Parameters:** p, d, q orders; train/test sizes; date range
- **Metrics:** RMSE, MAE, MAPE per holdout run
- **Artifacts:** serialized model (joblib)
- **Tags:** `model_type=ARIMA`, `domain=treasury-cashflow`

Compare runs: `mlflow ui` → `http://localhost:5000`

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/cashflow?limit=120` | Net cashflow time series |
| `GET` | `/summary` | Liquidity KPIs — stress, volatility, peak usage |
| `GET` | `/forecast` | ARIMA forecast + benchmark leaderboard + 14-day predictions |
| `POST` | `/run-pipeline` | Trigger full pipeline run |

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs on every push:

1. **Lint** — ruff checks `app/`, `tests/`, `dags/`
2. **Pandera validation** — imports schema contracts to catch drift early
3. **pytest** — full suite with coverage report uploaded as artifact
4. **DAG import check** — validates Airflow DAG parses without error

## Project Structure

```
treasury-analytics-platform/
├── app/
│   ├── api/                        ← 5 FastAPI route modules
│   ├── core/                       ← config (Pydantic + YAML), structured logger
│   ├── data/
│   │   ├── loader.py               ← CSV ingestion + synthetic fallback
│   │   ├── validator.py            ← schema, type, duplicate, ordering checks
│   │   ├── preprocessing.py        ← STAGING transforms
│   │   ├── schema.py               ← Pandera RAW + CURATED contracts
│   │   └── synthetic_data.py       ← 730-day realistic data generator
│   ├── features/feature_engineering.py  ← 22-feature engineering
│   ├── models/
│   │   ├── arima_forecast.py       ← ARIMA + MLflow tracking
│   │   └── summary_analytics.py   ← cashflow, stress, volatility KPIs
│   └── services/                   ← pipeline + treasury orchestration
├── dags/
│   └── treasury_pipeline_dag.py   ← Airflow DAG (daily, SLA-enforced)
├── dashboard/streamlit_app.py      ← Streamlit UI
├── tests/                          ← 7 pytest suites
├── .github/workflows/ci.yml        ← GitHub Actions CI
├── config/config.yaml
├── Dockerfile
├── docker-compose.yml
└── Makefile
```
