from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from app.models.release import (
    InstrumentationReportModel,
    JourneyDiffModel,
    ReleaseComparisonModel,
    ReleasesOverviewModel,
)
from app.services.instrumentation import validate_release
from app.services.journey_diff import diff_journeys
from app.services.release_compare import build_overview, compare_release
from app.services.release_fixture import RELEASE_PROFILES

router = APIRouter(tags=["releases"])


def _ensure_known_release(release: str) -> None:
    if release not in RELEASE_PROFILES:
        raise HTTPException(
            status_code=404,
            detail=(
                f"unknown release '{release}'. Known releases: "
                + ", ".join(sorted(RELEASE_PROFILES))
            ),
        )


@router.get("/releases/overview", response_model=ReleasesOverviewModel)
def releases_overview() -> ReleasesOverviewModel:
    return ReleasesOverviewModel.model_validate(build_overview())


@router.get("/releases/diff", response_model=JourneyDiffModel)
def journey_diff(
    baseline: str = "v2.2.0-healthy",
    target: str = "v2.3.0-buggy",
    min_support: int = 10,
) -> JourneyDiffModel:
    _ensure_known_release(baseline)
    _ensure_known_release(target)
    return JourneyDiffModel.model_validate(
        diff_journeys(baseline, target, min_support=min_support)
    )


@router.get("/releases/{release}/instrumentation", response_model=InstrumentationReportModel)
def release_instrumentation(release: str) -> InstrumentationReportModel:
    _ensure_known_release(release)
    report = validate_release(release)
    payload = asdict(report)
    payload["violations"] = [asdict(v) for v in report.violations]
    payload["unknown_events"] = list(report.unknown_events)
    return InstrumentationReportModel.model_validate(payload)


@router.get("/releases/{release}/comparison", response_model=ReleaseComparisonModel)
def release_comparison(release: str) -> ReleaseComparisonModel:
    _ensure_known_release(release)
    comparison = compare_release(release)
    payload = asdict(comparison)
    return ReleaseComparisonModel.model_validate(payload)
