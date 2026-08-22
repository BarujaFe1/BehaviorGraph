"""Deterministic synthetic release fixtures for release intelligence.

Three releases tell one honest story:

* ``v2.2.0-healthy`` — clean instrumentation, baseline product behavior.
* ``v2.3.0-buggy``   — SAME product behavior, but the client shipped broken
  instrumentation: ``onboarding_completed`` fires before ``profile_saved``
  (order violation + missing ``completed_at``), some events repeat an
  ``insert_id``, and an undeclared event appears.
* ``v2.3.0-fixed``   — genuinely better product AND corrected instrumentation.

Raw metrics make v2.3-buggy look like a win; trusted metrics prove it wasn't.
All identifiers are synthetic and PII-free. Same seed ⇒ byte-identical output.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import cache

import pandas as pd

COLUMNS = [
    "event_id",
    "user_id",
    "event_name",
    "ts",
    "session_id",
    "insert_id",
    "properties",
    "release",
]

KNOWN_EVENTS = {
    "signup_started",
    "signup_completed",
    "profile_saved",
    "onboarding_step_viewed",
    "onboarding_completed",
    "activation_completed",
    "feature_used",
    "session_abandoned",
    "error_shown",
    "return_visit",
}


@dataclass(frozen=True)
class ReleaseProfile:
    release: str
    started_at: str
    ended_at: str
    seed: int
    n_users: int
    activation_rate: float
    premature_onboarding_p: float
    duplicate_insert_id_p: float
    unknown_event_p: float


RELEASE_PROFILES: dict[str, ReleaseProfile] = {
    "v2.2.0-healthy": ReleaseProfile(
        release="v2.2.0-healthy",
        started_at="2026-06-01T00:00:00Z",
        ended_at="2026-06-07T23:59:59Z",
        seed=2201,
        n_users=800,
        activation_rate=0.42,
        premature_onboarding_p=0.0,
        duplicate_insert_id_p=0.0,
        unknown_event_p=0.0,
    ),
    "v2.3.0-buggy": ReleaseProfile(
        release="v2.3.0-buggy",
        started_at="2026-06-08T00:00:00Z",
        ended_at="2026-06-14T23:59:59Z",
        seed=2301,
        n_users=800,
        activation_rate=0.42,
        premature_onboarding_p=0.55,
        duplicate_insert_id_p=0.02,
        unknown_event_p=0.05,
    ),
    "v2.3.0-fixed": ReleaseProfile(
        release="v2.3.0-fixed",
        started_at="2026-06-15T00:00:00Z",
        ended_at="2026-06-21T23:59:59Z",
        seed=2401,
        n_users=800,
        activation_rate=0.50,
        premature_onboarding_p=0.0,
        duplicate_insert_id_p=0.0,
        unknown_event_p=0.0,
    ),
}

RELEASES = tuple(RELEASE_PROFILES)


def _iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def build_release_frame(release: str) -> pd.DataFrame:
    """Build the synthetic event frame for one release (pure, cached-free)."""
    profile = RELEASE_PROFILES.get(release)
    if profile is None:
        raise KeyError(
            f"unknown release '{release}'. Known releases: {', '.join(RELEASES)}"
        )

    rng = random.Random(profile.seed)
    window_start = datetime.fromisoformat(profile.started_at.replace("Z", "+00:00"))
    rows: list[dict] = []

    def emit(
        user_id: str,
        name: str,
        ts: datetime,
        session_id: str,
        insert_id: str,
        properties: dict | None = None,
        force_duplicate: bool = False,
    ) -> None:
        rows.append(
            {
                "user_id": user_id,
                "event_name": name,
                "ts": _iso(ts),
                "session_id": session_id,
                "insert_id": insert_id,
                "properties": json.dumps(properties or {}, sort_keys=True),
            }
        )
        if (
            force_duplicate or rng.random() < profile.duplicate_insert_id_p
        ) and name != "signup_started":
            # Client retry shipped the same insert_id twice (duplicate evidence).
            rows.append(
                {
                    "user_id": user_id,
                    "event_name": name,
                    "ts": _iso(ts + timedelta(minutes=1)),
                    "session_id": session_id,
                    "insert_id": insert_id,
                    "properties": json.dumps(properties or {}, sort_keys=True),
                }
            )

    for index in range(1, profile.n_users + 1):
        user_id = f"u_{index:04d}"
        base = window_start + timedelta(
            days=rng.randint(0, 6),
            hours=rng.randint(8, 20),
            minutes=rng.randint(0, 59),
        )
        s1 = f"{user_id}_s01"
        seq = 0

        def next_insert(owner: str = user_id) -> str:
            nonlocal seq
            seq += 1
            return f"ins_{owner}_{seq:03d}"

        emit(user_id, "signup_started", base, s1, next_insert())

        t = base + timedelta(minutes=rng.randint(1, 8))
        if rng.random() >= 0.82:
            emit(user_id, "session_abandoned", t, s1, next_insert())
            continue
        emit(user_id, "signup_completed", t, s1, next_insert())

        if rng.random() < profile.unknown_event_p:
            emit(
                user_id,
                "upsell_modal_shown",
                t + timedelta(minutes=1),
                s1,
                next_insert(),
            )

        saved_profile = rng.random() < 0.72
        if not saved_profile:
            # Buggy clients fired completion before the profile existed at all:
            # an order violation that also lacks its required completed_at prop.
            if rng.random() < profile.premature_onboarding_p:
                emit(
                    user_id,
                    "onboarding_completed",
                    t + timedelta(minutes=rng.randint(1, 3)),
                    s1,
                    next_insert(),
                )
            emit(
                user_id,
                "session_abandoned",
                t + timedelta(minutes=rng.randint(4, 9)),
                s1,
                next_insert(),
            )
            continue

        t += timedelta(minutes=rng.randint(2, 10))
        emit(user_id, "profile_saved", t, s1, next_insert())

        if rng.random() < 0.12:
            emit(
                user_id,
                "error_shown",
                t + timedelta(minutes=1),
                s1,
                next_insert(),
                {"code": "onboarding_timeout"},
            )

        if rng.random() < 0.85:
            emit(
                user_id,
                "onboarding_step_viewed",
                t + timedelta(minutes=rng.randint(2, 6)),
                s1,
                next_insert(),
            )

        if rng.random() < 0.62:
            emit(
                user_id,
                "feature_used",
                t + timedelta(minutes=rng.randint(7, 25)),
                s1,
                next_insert(),
                {"feature": "board" if index % 2 == 0 else "insights"},
            )

        if rng.random() < 0.88:
            emit(
                user_id,
                "onboarding_completed",
                t + timedelta(minutes=rng.randint(26, 45)),
                s1,
                next_insert(),
                {"completed_at": _iso(t + timedelta(minutes=rng.randint(26, 40)))},
            )

        activated = rng.random() < profile.activation_rate
        if activated:
            emit(
                user_id,
                "activation_completed",
                t + timedelta(minutes=rng.randint(46, 80)),
                s1,
                next_insert(),
            )

        if rng.random() < 0.45:
            s2 = f"{user_id}_s02"
            t2 = base + timedelta(days=rng.randint(2, 9), hours=rng.randint(9, 19))
            emit(user_id, "return_visit", t2, s2, next_insert())
            if rng.random() < 0.5:
                emit(
                    user_id,
                    "feature_used",
                    t2 + timedelta(minutes=5),
                    s2,
                    next_insert(),
                    {"feature": "insights"},
                )

        if activated and rng.random() < 0.30:
            s3 = f"{user_id}_s03"
            t3 = base + timedelta(days=rng.randint(14, 20), hours=rng.randint(10, 17))
            emit(user_id, "return_visit", t3, s3, next_insert())
            emit(
                user_id,
                "feature_used",
                t3 + timedelta(minutes=4),
                s3,
                next_insert(),
                {"feature": "board"},
            )

    rows.sort(key=lambda r: (r["ts"], r["user_id"], r["insert_id"]))
    for position, row in enumerate(rows, start=1):
        row["event_id"] = f"evt_{position:06d}"
        row["release"] = profile.release

    frame = pd.DataFrame(rows, columns=COLUMNS)
    return frame


@cache
def load_release_frame(release: str) -> pd.DataFrame:
    return build_release_frame(release)


def release_manifest(release: str) -> dict:
    profile = RELEASE_PROFILES[release]
    frame = build_release_frame(release)
    return {
        "release": profile.release,
        "started_at": profile.started_at,
        "ended_at": profile.ended_at,
        "experiment": False,
        "users": int(frame["user_id"].nunique()),
        "events": int(len(frame)),
        "generator_seed": profile.seed,
    }
