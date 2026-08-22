"""Pre-compute the release-intelligence demo snapshot for the static web lab.

Writes one payload to two destinations:
* apps/web/public/data/release-intelligence.json  (public artifact / download)
* apps/web/lib/release-intelligence.json          (bundled import, Pages-safe)

Backend services remain the single source of truth.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.services.instrumentation import validate_release  # noqa: E402
from app.services.journey_diff import diff_journeys  # noqa: E402
from app.services.release_compare import BASELINE_RELEASE, build_overview  # noqa: E402
from app.services.release_fixture import RELEASES  # noqa: E402


def build_payload() -> dict:
    overview = build_overview()
    instrumentation = {}
    for release in RELEASES:
        report = validate_release(release)
        instrumentation[release] = {
            "release": release,
            "total_events": report.total_events,
            "trusted_events": report.trusted_events,
            "status": report.status,
            "unknown_events": list(report.unknown_events),
            "violations": [
                {
                    "event_name": v.event_name,
                    "code": v.code,
                    "severity": v.severity,
                    "user_count": v.user_count,
                    "evidence_count": v.evidence_count,
                }
                for v in report.violations
            ],
        }
    journey_diffs = {}
    for release in RELEASES:
        if release == BASELINE_RELEASE:
            continue
        journey_diffs[release] = diff_journeys(
            BASELINE_RELEASE, release, min_support=20
        )
    return {
        **overview,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "instrumentation": instrumentation,
        "journey_diffs": journey_diffs,
        "limitations": [
            "Synthetic fixtures only — no real user tracking, no PII.",
            "Rates are observational; no causal effect without an experiment flag.",
            "Trusted funnel drops contract-invalid rows; unknown events are reported, never silently dropped.",
            "Event drift compares per-user rates against the baseline release (heuristic threshold).",
        ],
    }


def main() -> None:
    payload = build_payload()
    public_dir = ROOT / "apps" / "web" / "public" / "data"
    lib_dir = ROOT / "apps" / "web" / "lib"
    public_dir.mkdir(parents=True, exist_ok=True)

    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    public_path = public_dir / "release-intelligence.json"
    lib_path = lib_dir / "release-intelligence.json"
    public_path.write_text(text, encoding="utf-8")
    lib_path.write_text(text, encoding="utf-8")
    print(f"snapshot -> {public_path.relative_to(ROOT)} ({len(text)} bytes)")
    print(f"snapshot -> {lib_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
