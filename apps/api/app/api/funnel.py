from fastapi import APIRouter

from app.services.analytics import build_activation_funnel

router = APIRouter(tags=["funnel"])


@router.get("/funnel/activation")
def activation_funnel() -> dict:
    return build_activation_funnel()
