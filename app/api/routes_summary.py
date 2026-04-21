"""Summary routes."""

from fastapi import APIRouter

from app.schemas.response_models import SummaryResponse
from app.services.treasury_service import get_summary

router = APIRouter()


@router.get("/summary", response_model=SummaryResponse)
def summary() -> SummaryResponse:
    return SummaryResponse(summary=get_summary())
