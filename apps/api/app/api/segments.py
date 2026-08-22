from fastapi import APIRouter

from app.models.schemas import SegmentsResponse
from app.services.analytics import build_segments

router = APIRouter(tags=["segments"])


@router.get("/segments", response_model=SegmentsResponse)
def segments() -> SegmentsResponse:
    return SegmentsResponse.model_validate(build_segments())
