"""Health route."""

from fastapi import APIRouter

from app.core.config import get_config
from app.schemas.response_models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    config = get_config()
    return HealthResponse(status="ok", app=config.app_name, version=config.version)
