from fastapi import APIRouter

from app.services.analytics import build_friction_points, build_opportunity_memo

router = APIRouter(tags=["friction"])


@router.get("/friction")
def friction_points() -> dict:
    return build_friction_points()


@router.get("/opportunities")
def opportunities() -> dict:
    return build_opportunity_memo()
