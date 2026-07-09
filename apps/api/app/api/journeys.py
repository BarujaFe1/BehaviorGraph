from fastapi import APIRouter

from app.services.analytics import build_journey_graph

router = APIRouter(tags=["journeys"])


@router.get("/journeys/graph")
def journey_graph(limit_edges: int = 40) -> dict:
    return build_journey_graph(limit_edges=limit_edges)
