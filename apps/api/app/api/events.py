from fastapi import APIRouter, Query

from app.models.schemas import TaxonomyResponse
from app.services.analytics import load_event_taxonomy, load_recent_events

router = APIRouter(tags=["events"])


@router.get("/events/taxonomy", response_model=TaxonomyResponse)
def event_taxonomy() -> TaxonomyResponse:
    return TaxonomyResponse.model_validate(load_event_taxonomy())


@router.get("/events/recent")
def recent_events(limit: int = Query(default=50, ge=1, le=500)) -> dict:
    return {"events": load_recent_events(limit=limit)}
