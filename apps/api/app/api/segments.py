from fastapi import APIRouter

from app.services.analytics import build_segments

router = APIRouter(tags=["segments"])


@router.get("/segments")
def segments() -> dict:
    return build_segments()
