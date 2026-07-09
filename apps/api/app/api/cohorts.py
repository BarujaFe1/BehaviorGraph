from fastapi import APIRouter

from app.services.analytics import build_retention_cohorts

router = APIRouter(tags=["cohorts"])


@router.get("/cohorts/retention")
def retention_cohorts() -> dict:
    return build_retention_cohorts()
