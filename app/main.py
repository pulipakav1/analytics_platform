"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.api.routes_cashflow import router as cashflow_router
from app.api.routes_forecast import router as forecast_router
from app.api.routes_health import router as health_router
from app.api.routes_pipeline import router as pipeline_router
from app.api.routes_summary import router as summary_router
from app.core.config import get_config
from app.core.logger import setup_logger

config = get_config()
logger = setup_logger(config.log_level)

app = FastAPI(title=config.app_name, version=config.version)
app.include_router(health_router)
app.include_router(cashflow_router)
app.include_router(forecast_router)
app.include_router(summary_router)
app.include_router(pipeline_router)


@app.get("/")
def root() -> dict[str, str]:
    logger.info("Root endpoint called")
    return {"message": "Quantitative Treasury Analytics Platform"}
