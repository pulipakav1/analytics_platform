"""Cashflow routes."""

from fastapi import APIRouter, Query

from app.schemas.response_models import CashflowResponse
from app.services.treasury_service import get_cashflow_data

router = APIRouter()


@router.get("/cashflow", response_model=CashflowResponse)
def cashflow(limit: int = Query(default=120, ge=10, le=1000)) -> CashflowResponse:
    return CashflowResponse(data=get_cashflow_data(limit=limit))
