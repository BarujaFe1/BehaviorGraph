from fastapi import APIRouter

from app.services.analytics import load_demo_summary

router = APIRouter(tags=["demo"])


@router.get("/demo")
def demo_summary() -> dict:
    return load_demo_summary()
