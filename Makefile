PYTHON  = python
PIP     = $(PYTHON) -m pip

.DEFAULT_GOAL := help

.PHONY: help install install-dev lint format test pipeline api dashboard mlflow clean

help:
	@echo "Treasury Analytics Platform"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "  install      Install runtime dependencies"
	@echo "  install-dev  Install all dependencies including dev/test tools"
	@echo "  lint         Run ruff linter"
	@echo "  format       Run ruff formatter"
	@echo "  test         Run test suite with coverage"
	@echo "  pipeline     Run RAW → STAGING → CURATED pipeline"
	@echo "  api          Start FastAPI server on :8000"
	@echo "  dashboard    Start Streamlit dashboard on :8501"
	@echo "  mlflow       Launch MLflow UI on :5000"
	@echo "  clean        Remove generated artifacts"

install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements-dev.txt
	pre-commit install

lint:
	ruff check app/ tests/ dags/

format:
	ruff format app/ tests/ dags/

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

pipeline:
	$(PYTHON) -c "from app.services.pipeline_service import run_pipeline; import json; print(json.dumps(run_pipeline(), indent=2))"

api:
	uvicorn app.main:app --reload --port 8000

dashboard:
	streamlit run dashboard/streamlit_app.py

mlflow:
	mlflow ui --port 5000

clean:
	rm -rf data/staging/*.csv data/curated/*.csv data/outputs/* mlruns/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
