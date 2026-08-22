"""Generate deterministic release fixtures into data/seed/releases/.

Usage:
    python scripts/generate_release_fixture.py            # all releases
    python scripts/generate_release_fixture.py v2.3.0-buggy
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.services.release_fixture import (  # noqa: E402
    RELEASE_PROFILES,
    RELEASES,
    build_release_frame,
    release_manifest,
)

OUT_DIR = ROOT / "data" / "seed" / "releases"


def write_release(release: str) -> None:
    target = OUT_DIR / release
    target.mkdir(parents=True, exist_ok=True)
    frame = build_release_frame(release)
    csv_path = target / "events.csv"
    frame.to_csv(csv_path, index=False, lineterminator="\n")
    manifest_path = target / "manifest.json"
    manifest_path.write_text(
        json.dumps(release_manifest(release), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"{release}: {len(frame)} events -> {csv_path.relative_to(ROOT)}")


if __name__ == "__main__":
    requested = sys.argv[1:]
    selected = [r for r in RELEASES if not requested or r in requested]
    unknown = [r for r in requested if r not in RELEASE_PROFILES]
    if unknown:
        raise SystemExit(f"unknown releases: {', '.join(unknown)}")
    for release in selected:
        write_release(release)
