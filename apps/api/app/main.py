from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    cohorts,
    demo,
    events,
    friction,
    funnel,
    health,
    journeys,
    releases,
    segments,
)

app = FastAPI(
    title="BehaviorGraph API",
    description=(
        "Behavioral analytics MVP: event taxonomy, activation funnel, "
        "retention cohorts, journey paths, segments and friction signals."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(demo.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(funnel.router, prefix="/api")
app.include_router(cohorts.router, prefix="/api")
app.include_router(journeys.router, prefix="/api")
app.include_router(segments.router, prefix="/api")
app.include_router(friction.router, prefix="/api")
app.include_router(releases.router, prefix="/api")
