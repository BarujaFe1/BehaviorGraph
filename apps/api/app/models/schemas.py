"""Pydantic response models for BehaviorGraph API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class DemoSummary(BaseModel):
    product: str
    dataset: str
    users: int = Field(ge=0)
    events: int = Field(ge=0)
    sessions: int = Field(ge=0)
    activated_users: int = Field(ge=0)
    activation_rate: float = Field(ge=0, le=1)
    notice: str


class TaxonomyEvent(BaseModel):
    event_name: str
    category: str
    description: str
    owner: str


class TaxonomyResponse(BaseModel):
    events: list[TaxonomyEvent]


class FunnelStep(BaseModel):
    step: str
    users: int = Field(ge=0)
    conversion_from_previous: float = Field(ge=0, le=1)
    conversion_from_start: float = Field(ge=0, le=1)


class FunnelResponse(BaseModel):
    funnel: str
    method: str = "nested_unique_users"
    steps: list[FunnelStep]


class CohortWeek(BaseModel):
    week_offset: int = Field(ge=0)
    week: str
    retained_users: int = Field(ge=0)
    retention_rate: float = Field(ge=0, le=1)


class Cohort(BaseModel):
    cohort_week: str
    cohort_size: int = Field(ge=0)
    weeks: list[CohortWeek]


class CohortsResponse(BaseModel):
    cohorts: list[Cohort]
    method: str = "first_seen_week"


class JourneyNode(BaseModel):
    id: str
    label: str


class JourneyEdge(BaseModel):
    source: str
    target: str
    weight: int = Field(ge=0)


class JourneyGraph(BaseModel):
    nodes: list[JourneyNode]
    edges: list[JourneyEdge]
    engine: str = "networkx"


class Segment(BaseModel):
    id: str
    name: str
    users: int = Field(ge=0)
    definition: str


class SegmentsResponse(BaseModel):
    segments: list[Segment]


class FunnelDrop(BaseModel):
    from_step: str
    to_step: str
    drop_users: int
    drop_rate: float = Field(ge=0, le=1)
    severity: Literal["low", "medium", "high"]


class ErrorSignal(BaseModel):
    event_name: str
    affected_users: int = Field(ge=0)


class FrictionResponse(BaseModel):
    funnel_drops: list[FunnelDrop]
    error_signals: list[ErrorSignal]


class Opportunity(BaseModel):
    title: str
    why: str
    suggested_action: str
    impact_hypothesis: str


class OpportunityMemo(BaseModel):
    headline: str
    summary: DemoSummary
    opportunities: list[Opportunity]
    limitations: list[str]


class HealthResponse(BaseModel):
    status: str
    service: str
