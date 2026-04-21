PYTHON=python

.PHONY: install test pipeline api dashboard

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	pytest -q

pipeline:
	$(PYTHON) -c "from app.services.pipeline_service import run_pipeline; print(run_pipeline())"

api:
	uvicorn app.main:app --reload --port 8000

dashboard:
	streamlit run dashboard/streamlit_app.py
