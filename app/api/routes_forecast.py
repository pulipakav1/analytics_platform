"""Forecast routes."""

from fastapi import APIRouter

from app.schemas.response_models import ForecastResponse
from app.services.forecast_service import run_forecast

router = APIRouter()


@router.get("/forecast", response_model=ForecastResponse)
def forecast() -> ForecastResponse:
    result = run_forecast()
    return ForecastResponse(**result)
