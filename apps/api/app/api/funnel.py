from fastapi import APIRouter

from app.models.schemas import FunnelResponse
from app.services.analytics import build_activation_funnel

router = APIRouter(tags=["funnel"])


@router.get("/funnel/activation", response_model=FunnelResponse)
def activation_funnel() -> FunnelResponse:
    return FunnelResponse.model_validate(build_activation_funnel())
