from fastapi import APIRouter

from app.models.schemas import FrictionResponse, OpportunityMemo
from app.services.analytics import build_friction_points, build_opportunity_memo

router = APIRouter(tags=["friction"])


@router.get("/friction", response_model=FrictionResponse)
def friction_points() -> FrictionResponse:
    return FrictionResponse.model_validate(build_friction_points())


@router.get("/opportunities", response_model=OpportunityMemo)
def opportunities() -> OpportunityMemo:
    return OpportunityMemo.model_validate(build_opportunity_memo())
