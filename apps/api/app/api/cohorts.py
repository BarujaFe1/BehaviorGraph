from fastapi import APIRouter

from app.models.schemas import CohortsResponse
from app.services.analytics import build_retention_cohorts

router = APIRouter(tags=["cohorts"])


@router.get("/cohorts/retention", response_model=CohortsResponse)
def retention_cohorts() -> CohortsResponse:
    return CohortsResponse.model_validate(build_retention_cohorts())
