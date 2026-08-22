"""Instrumentation health: tracking contracts + violation detection.

Contracts are declared in ``data/contracts/events.yml`` (versioned source of
truth). The validator inspects synthetic release event streams and reports
semantic breakage as evidence-backed violations — it never silently drops or
rewrites events.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
CONTRACTS_PATH = ROOT / "data" / "contracts" / "events.yml"


@dataclass(frozen=True)
class EventContract:
    """Declarative tracking contract for a single event."""

    name: str
    owner: str
    required_properties: tuple[str, ...] = ()
    must_follow: tuple[str, ...] = ()
    max_per_user_session: int | None = None
    introduced_in: str | None = None


@dataclass(frozen=True)
class TrackingContract:
    version: int
    events: dict[str, EventContract]


@dataclass(frozen=True)
class InstrumentationViolation:
    """One semantic instrumentation finding, backed by evidence counts."""

    event_name: str
    code: str
    release: str
    user_count: int
    evidence_count: int
    severity: str


@lru_cache(maxsize=1)
def load_tracking_contract() -> TrackingContract:
    if not CONTRACTS_PATH.exists():
        raise FileNotFoundError(
            f"Tracking contract file not found: {CONTRACTS_PATH}. "
            "data/contracts/events.yml is required for release intelligence."
        )
    raw = yaml.safe_load(CONTRACTS_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "version" not in raw or "events" not in raw:
        raise ValueError("events.yml must declare top-level 'version' and 'events'")
    events_raw = raw["events"]
    if not isinstance(events_raw, dict) or not events_raw:
        raise ValueError("events.yml must declare at least one event")

    events: dict[str, EventContract] = {}
    for name, spec in events_raw.items():
        spec = spec or {}
        owner = spec.get("owner")
        required = tuple(spec.get("required_properties") or ())
        if not owner:
            raise ValueError(f"event '{name}' is missing an owner")
        if not required:
            raise ValueError(f"event '{name}' declares no required_properties")
        max_per_session = spec.get("max_per_user_session")
        events[str(name)] = EventContract(
            name=str(name),
            owner=str(owner),
            required_properties=required,
            must_follow=tuple(spec.get("must_follow") or ()),
            max_per_user_session=int(max_per_session)
            if max_per_session is not None
            else None,
            introduced_in=str(spec["introduced_in"])
            if spec.get("introduced_in")
            else None,
        )

    for name, spec in events.items():
        for prerequisite in spec.must_follow:
            if prerequisite not in events:
                raise ValueError(
                    f"event '{name}' must_follow references undeclared '{prerequisite}'"
                )

    return TrackingContract(version=int(raw["version"]), events=events)


def clear_contract_cache() -> None:
    load_tracking_contract.cache_clear()
