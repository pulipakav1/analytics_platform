"""Pipeline routes."""

from fastapi import APIRouter

from app.schemas.response_models import PipelineResponse
from app.services.pipeline_service import run_pipeline

router = APIRouter()


@router.post("/run-pipeline", response_model=PipelineResponse)
def trigger_pipeline() -> PipelineResponse:
    return PipelineResponse(**run_pipeline())
