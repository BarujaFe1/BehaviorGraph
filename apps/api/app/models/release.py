"""Pydantic response models for release intelligence endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ViolationModel(BaseModel):
    event_name: str
    code: str
    release: str
    user_count: int = Field(ge=0)
    evidence_count: int = Field(ge=0)
    severity: str


class InstrumentationReportModel(BaseModel):
    release: str
    total_events: int = Field(ge=0)
    trusted_events: int = Field(ge=0)
    violations: list[ViolationModel]
    unknown_events: list[str]
    status: str


class ReleaseFunnelStep(BaseModel):
    step: str
    users: int = Field(ge=0)
    conversion_from_start: float = Field(ge=0, le=1)
    unique_user_basis: bool


class VerdictModel(BaseModel):
    classification: str
    raw_looks_better: bool
    survives_trusted_filter: bool
    gain_step: str | None
    raw_gain_pct: float
    trusted_gain_pct: float


class ReleaseComparisonModel(BaseModel):
    release: str
    total_events: int = Field(ge=0)
    trusted_events: int = Field(ge=0)
    raw_funnel: list[ReleaseFunnelStep]
    trusted_funnel: list[ReleaseFunnelStep]
    activation_raw_rate: float = Field(ge=0, le=1)
    activation_trusted_rate: float = Field(ge=0, le=1)
    verdict: VerdictModel


class OverviewReleaseModel(BaseModel):
    release: str
    total_events: int = Field(ge=0)
    trusted_events: int = Field(ge=0)
    activation_raw_rate: float = Field(ge=0, le=1)
    activation_trusted_rate: float = Field(ge=0, le=1)
    activation_trusted_ci: tuple[float, float]
    instrumentation_status: str
    verdict: VerdictModel
    raw_funnel: list[ReleaseFunnelStep]
    trusted_funnel: list[ReleaseFunnelStep]


class ReleasesOverviewModel(BaseModel):
    method: str
    baseline: str
    observational_notice: str
    releases: list[OverviewReleaseModel]


class JourneyEdgeDiff(BaseModel):
    source: str
    target: str
    target_weight: int | None = Field(default=None, ge=0)
    baseline_weight: int | None = Field(default=None, ge=0)


class JourneyDiffModel(BaseModel):
    baseline: str
    target: str
    min_support: int = Field(ge=1)
    baseline_edges: list[list[str]]
    added: list[JourneyEdgeDiff]
    removed: list[JourneyEdgeDiff]
    notice: str
