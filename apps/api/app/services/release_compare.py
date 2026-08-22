"""Release comparison: raw vs trusted metrics, per unique user.

Raw funnels use every ingested event. Trusted funnels drop rows failing
block-level tracking contracts (see instrumentation.invalid_row_indices_for).
The comparison proves whether a release's apparent gain is real product
behavior or an instrumentation artifact. All rates are unique-user based and
strictly observational â€” no causal claims without an experiment flag.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.services.instrumentation import validate_release
from app.services.release_fixture import RELEASES, load_release_frame

ACTIVATION_STEPS = [
    "signup_started",
    "signup_completed",
    "profile_saved",
    "onboarding_completed",
    "activation_completed",
]

BASELINE_RELEASE = "v2.2.0-healthy"
RAW_GAIN_THRESHOLD = 1.05
TRUSTED_SURVIVAL_THRESHOLD = 1.05

OBSERVATIONAL_NOTICE = (
    "Observational comparison only. Rates describe what fired per unique user; "
    "no causal effect is claimed without a controlled experiment."
)


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion — never returns negative bounds."""
    if n <= 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(max(0.0, center - half), 4), round(min(1.0, center + half), 4))


@dataclass(frozen=True)
class ReleaseComparison:
    release: str
    total_events: int
    trusted_events: int
    raw_funnel: tuple[dict, ...]
    trusted_funnel: tuple[dict, ...]
    activation_raw_rate: float
    activation_trusted_rate: float
    verdict: dict


def _loose_funnel(frame) -> tuple[dict, ...]:
    """Per-event unique-user funnel relative to signup starters.

    Deliberately LOOSE on purpose: this mirrors what a naive dashboard counts
    ('did the event ever fire'). Contract-invalid rows are only removed in the
    trusted view, which is exactly how broken instrumentation fakes gains.
    """
    starters = frame.loc[frame["event_name"] == ACTIVATION_STEPS[0], "user_id"]
    start_count = int(starters.nunique())

    steps: list[dict] = []
    for name in ACTIVATION_STEPS:
        users = int(frame.loc[frame["event_name"] == name, "user_id"].nunique())
        conversion_from_start = round(users / start_count, 3) if start_count else 0.0
        steps.append(
            {
                "step": name,
                "users": users,
                "conversion_from_start": conversion_from_start,
                "unique_user_basis": True,
            }
        )
    return tuple(steps)


def _step_map(funnel: tuple[dict, ...]) -> dict[str, dict]:
    return {step["step"]: step for step in funnel}


def _trusted_frame(release: str):
    from app.services.instrumentation import invalid_row_indices_for

    frame = load_release_frame(release).reset_index(drop=True)
    invalid = invalid_row_indices_for(release)
    return frame.drop(index=list(invalid))


def compare_release(release: str) -> ReleaseComparison:
    raw_frame = load_release_frame(release).reset_index(drop=True)
    trusted_frame = _trusted_frame(release)

    raw_funnel = _loose_funnel(raw_frame)
    trusted_funnel = _loose_funnel(trusted_frame)

    def activation_rate(funnel: tuple[dict, ...]) -> float:
        start = _step_map(funnel)["signup_started"]["users"]
        activated = _step_map(funnel)["activation_completed"]["users"]
        return round(activated / start, 3) if start else 0.0

    baseline = _step_map(_loose_funnel(load_release_frame(BASELINE_RELEASE)))
    baseline_trusted = _step_map(
        _loose_funnel(_trusted_frame(BASELINE_RELEASE))
    )

    best_step, best_ratio = "", 1.0
    raw_now = _step_map(raw_funnel)
    for name in ACTIVATION_STEPS[1:]:
        base_users = max(baseline[name]["users"], 1)
        ratio = raw_now[name]["users"] / base_users
        if ratio > best_ratio:
            best_step, best_ratio = name, ratio

    if release == BASELINE_RELEASE or not best_step:
        verdict = {
            "classification": "baseline",
            "raw_looks_better": False,
            "survives_trusted_filter": False,
            "gain_step": None,
            "raw_gain_pct": 0.0,
            "trusted_gain_pct": 0.0,
        }
    else:
        trusted_now = _step_map(trusted_funnel)
        base_users = max(baseline[best_step]["users"], 1)
        trusted_base = max(baseline_trusted[best_step]["users"], 1)
        trusted_ratio = trusted_now[best_step]["users"] / trusted_base
        survives = bool(trusted_ratio > TRUSTED_SURVIVAL_THRESHOLD)
        verdict = {
            "classification": (
                "real_improvement" if survives else "instrumentation_artifact"
            ),
            "raw_looks_better": True,
            "survives_trusted_filter": survives,
            "gain_step": best_step,
            "raw_gain_pct": round((best_ratio - 1) * 100, 1),
            "trusted_gain_pct": round((trusted_ratio - 1) * 100, 1),
        }

    return ReleaseComparison(
        release=release,
        total_events=int(len(raw_frame)),
        trusted_events=int(len(trusted_frame)),
        raw_funnel=raw_funnel,
        trusted_funnel=trusted_funnel,
        activation_raw_rate=activation_rate(raw_funnel),
        activation_trusted_rate=activation_rate(trusted_funnel),
        verdict=verdict,
    )


def build_overview() -> dict:
    releases = []
    for release in RELEASES:
        comparison = compare_release(release)
        report = validate_release(release)
        starters = comparison.raw_funnel[0]["users"]
        activated_trusted = _step_map(comparison.trusted_funnel)["activation_completed"][
            "users"
        ]
        releases.append(
            {
                "release": release,
                "total_events": comparison.total_events,
                "trusted_events": comparison.trusted_events,
                "activation_raw_rate": comparison.activation_raw_rate,
                "activation_trusted_rate": comparison.activation_trusted_rate,
                "activation_trusted_ci": wilson_interval(activated_trusted, starters),
                "instrumentation_status": report.status,
                "verdict": comparison.verdict,
                "raw_funnel": list(comparison.raw_funnel),
                "trusted_funnel": list(comparison.trusted_funnel),
            }
        )
    return {
        "method": "unique_user_funnel",
        "baseline": BASELINE_RELEASE,
        "observational_notice": OBSERVATIONAL_NOTICE,
        "releases": releases,
    }
