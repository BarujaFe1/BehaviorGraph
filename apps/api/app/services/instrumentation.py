"""Instrumentation health: tracking contracts + violation detection.

Contracts are declared in ``data/contracts/events.yml`` (versioned source of
truth). The validator inspects synthetic release event streams and reports
semantic breakage as evidence-backed violations — it never silently drops or
rewrites events.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[4]
CONTRACTS_PATH = ROOT / "data" / "contracts" / "events.yml"

BASELINE_RELEASE = "v2.2.0-healthy"
DRIFT_RATE_RATIO_THRESHOLD = 1.25
SEVERITY_RANK = {"block": 0, "warning": 1}


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
    validate_release.cache_clear()


@dataclass(frozen=True)
class InstrumentationReport:
    """Deterministic health verdict for one release's event stream."""

    release: str
    total_events: int
    trusted_events: int
    violations: tuple[InstrumentationViolation, ...]
    unknown_events: tuple[str, ...]
    status: str


def _load_release_frame(release: str) -> pd.DataFrame:
    from app.services.release_fixture import load_release_frame

    return load_release_frame(release)


def _row_properties(row: pd.Series) -> dict:
    try:
        parsed = json.loads(row["properties"]) if row["properties"] else {}
    except (TypeError, ValueError):
        parsed = {}
    return parsed if isinstance(parsed, dict) else {}


def _missing_props(frame: pd.DataFrame) -> pd.Index:
    """Row indices missing at least one contract-required property."""
    contract = load_tracking_contract()
    offenders: list[int] = []
    props_by_row = {idx: _row_properties(row) for idx, row in frame.iterrows()}
    for idx, row in frame.iterrows():
        spec = contract.events.get(str(row["event_name"]))
        if spec is None:
            continue
        available = set(props_by_row[idx]) | {
            key for key in frame.columns if pd.notna(row.get(key))
        }
        if any(prop not in available for prop in spec.required_properties):
            offenders.append(idx)
    return pd.Index(offenders)


def _order_violation_rows(frame: pd.DataFrame) -> pd.Index:
    """Rows whose must_follow prerequisites were not seen earlier in-session."""
    contract = load_tracking_contract()
    offenders: list[int] = []
    for _, session in frame.groupby("session_id", sort=False):
        ordered = session.sort_values(["ts", "event_id"])
        seen: set[str] = set()
        for idx, row in ordered.iterrows():
            name = str(row["event_name"])
            spec = contract.events.get(name)
            if spec and any(prerequisite not in seen for prerequisite in spec.must_follow):
                offenders.append(idx)
            seen.add(name)
    return pd.Index(offenders)


def _duplicate_insert_rows(frame: pd.DataFrame) -> tuple[pd.Index, int]:
    """Extra rows reusing an insert_id; returns their indices and user count."""
    counts = frame.groupby(["user_id", "insert_id"]).cumcount()
    extra = frame[counts > 0]
    if extra.empty:
        return pd.Index([]), 0
    users = int(extra["user_id"].nunique())
    return extra.index, users


def _cardinality_rows(frame: pd.DataFrame) -> pd.Index:
    contract = load_tracking_contract()
    offenders: list[int] = []
    grouped = frame.groupby(["user_id", "session_id", "event_name"], sort=False)
    for (_, _, event_name), group in grouped:
        spec = contract.events.get(str(event_name))
        if spec is None or spec.max_per_user_session is None:
            continue
        if len(group) <= spec.max_per_user_session:
            continue
        ordered = group.sort_values(["ts", "event_id"])
        offenders.extend(ordered.index[spec.max_per_user_session :])
    return pd.Index(offenders)


def _unknown_events(frame: pd.DataFrame) -> tuple[str, ...]:
    contract = load_tracking_contract()
    observed = set(frame["event_name"].astype(str))
    return tuple(sorted(observed - set(contract.events)))


@lru_cache(maxsize=8)
def invalid_row_indices_for(release: str) -> tuple[int, ...]:
    """Row positions failing any block-level contract check (stable order)."""
    frame = _load_release_frame(release)
    missing_idx = _missing_props(frame)
    order_idx = _order_violation_rows(frame)
    dup_idx, _ = _duplicate_insert_rows(frame)
    card_idx = _cardinality_rows(frame)
    return tuple(sorted(set(missing_idx) | set(order_idx) | set(dup_idx) | set(card_idx)))


@lru_cache(maxsize=8)
def validate_release(release: str) -> InstrumentationReport:
    """Run every deterministic instrumentation check against one release."""
    from app.services.release_fixture import RELEASE_PROFILES

    if release not in RELEASE_PROFILES:
        raise KeyError(f"unknown release '{release}'")

    frame = _load_release_frame(release)
    contract = load_tracking_contract()
    total = int(len(frame))
    violations: list[InstrumentationViolation] = []

    # 1. Unknown events — warning only, never silently dropped.
    unknown = _unknown_events(frame)
    for event_name in unknown:
        affected = frame[frame["event_name"] == event_name]
        violations.append(
            InstrumentationViolation(
                event_name=event_name,
                code="unknown_event",
                release=release,
                user_count=int(affected["user_id"].nunique()),
                evidence_count=int(len(affected)),
                severity="warning",
            )
        )

    # 2. Missing required properties.
    missing_idx = _missing_props(frame)
    if len(missing_idx):
        missing_frame = frame.loc[missing_idx]
        by_event = missing_frame.groupby("event_name")
        for event_name, group in by_event:
            violations.append(
                InstrumentationViolation(
                    event_name=str(event_name),
                    code="missing_required_property",
                    release=release,
                    user_count=int(group["user_id"].nunique()),
                    evidence_count=int(len(group)),
                    severity="block",
                )
            )

    # 3. Order violations (must_follow within session).
    order_idx = _order_violation_rows(frame)
    if len(order_idx):
        order_frame = frame.loc[order_idx]
        for event_name, group in order_frame.groupby("event_name"):
            violations.append(
                InstrumentationViolation(
                    event_name=str(event_name),
                    code="order_violation",
                    release=release,
                    user_count=int(group["user_id"].nunique()),
                    evidence_count=int(len(group)),
                    severity="block",
                )
            )

    # 4. Duplicate insert_ids (client retries shipping the same id).
    dup_idx, dup_users = _duplicate_insert_rows(frame)
    if len(dup_idx):
        dup_frame = frame.loc[dup_idx]
        violations.append(
            InstrumentationViolation(
                event_name=str(dup_frame["event_name"].mode().iat[0]),
                code="duplicate_insert_id",
                release=release,
                user_count=dup_users,
                evidence_count=int(len(dup_idx)),
                severity="block",
            )
        )

    # 5. Cardinality breaches (max_per_user_session).
    cardinality_idx = _cardinality_rows(frame)
    if len(cardinality_idx):
        card_frame = frame.loc[cardinality_idx]
        for event_name, group in card_frame.groupby("event_name"):
            violations.append(
                InstrumentationViolation(
                    event_name=str(event_name),
                    code="cardinality_breach",
                    release=release,
                    user_count=int(group["user_id"].nunique()),
                    evidence_count=int(len(group)),
                    severity="block",
                )
            )

    # 6. Event drift vs baseline release (heuristic rate comparison).
    baseline = _load_release_frame(BASELINE_RELEASE)
    baseline_users = max(int(baseline["user_id"].nunique()), 1)
    current_users = max(int(frame["user_id"].nunique()), 1)
    for name in sorted(set(contract.events) & set(frame["event_name"])):
        base_rate = int((baseline["event_name"] == name).sum()) / baseline_users
        curr_rate = int((frame["event_name"] == name).sum()) / current_users
        if base_rate > 0 and curr_rate / base_rate > DRIFT_RATE_RATIO_THRESHOLD:
            violations.append(
                InstrumentationViolation(
                    event_name=name,
                    code="event_drift",
                    release=release,
                    user_count=int(
                        frame.loc[frame["event_name"] == name, "user_id"].nunique()
                    ),
                    evidence_count=int((frame["event_name"] == name).sum()),
                    severity="warning",
                )
            )

    # Trusted view: drop block-invalid rows (union of flagged index sets).
    invalid = pd.Index(
        sorted(set(missing_idx) | set(order_idx) | set(dup_idx) | set(cardinality_idx))
    )
    trusted = total - int(len(invalid))

    violations.sort(key=lambda v: (SEVERITY_RANK[v.severity], v.code, v.event_name))
    has_block = any(v.severity == "block" for v in violations)
    status = "block" if has_block else ("warn" if violations else "pass")

    return InstrumentationReport(
        release=release,
        total_events=total,
        trusted_events=trusted,
        violations=tuple(violations),
        unknown_events=unknown,
        status=status,
    )
