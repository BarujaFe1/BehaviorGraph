from fastapi import APIRouter

from app.services.analytics import load_event_taxonomy, load_recent_events

router = APIRouter(tags=["events"])


@router.get("/events/taxonomy")
def event_taxonomy() -> dict:
    return load_event_taxonomy()


@router.get("/events/recent")
def recent_events(limit: int = 50) -> dict:
    return {"events": load_recent_events(limit=limit)}
