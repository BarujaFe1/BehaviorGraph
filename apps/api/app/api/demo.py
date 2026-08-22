from fastapi import APIRouter

from app.models.schemas import DemoSummary
from app.services.analytics import load_demo_summary

router = APIRouter(tags=["demo"])


@router.get("/demo", response_model=DemoSummary)
def demo_summary() -> DemoSummary:
    return DemoSummary.model_validate(load_demo_summary())
