from fastapi import APIRouter, Query

from app.models.schemas import JourneyGraph
from app.services.analytics import build_journey_graph

router = APIRouter(tags=["journeys"])


@router.get("/journeys/graph", response_model=JourneyGraph)
def journey_graph(limit_edges: int = Query(default=40, ge=1, le=200)) -> JourneyGraph:
    return JourneyGraph.model_validate(build_journey_graph(limit_edges=limit_edges))
