"""Generate synthetic SaaS onboarding events + taxonomy for BehaviorGraph."""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "seed"
SEED.mkdir(parents=True, exist_ok=True)

TAXONOMY = [
    ("signup_started", "acquisition", "User opens signup form", "growth"),
    ("signup_completed", "acquisition", "User finishes signup", "growth"),
    ("onboarding_step_viewed", "activation", "User views an onboarding step", "product"),
    ("feature_used", "activation", "User uses a core feature", "product"),
    ("activation_completed", "activation", "User reaches activation milestone", "product"),
    ("session_abandoned", "friction", "Session ends without progress", "product"),
    ("error_shown", "friction", "UI error or blocker shown", "engineering"),
    ("billing_viewed", "monetization", "User opens billing page", "growth"),
    ("invite_sent", "expansion", "User invites a teammate", "product"),
    ("return_visit", "retention", "User returns in a later session", "product"),
]

rng = random.Random(42)


def write_taxonomy() -> None:
    path = SEED / "event_taxonomy.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["event_name", "category", "description", "owner"])
        w.writerows(TAXONOMY)


def write_events(n_users: int = 220) -> None:
    path = SEED / "events_demo.csv"
    start = datetime(2026, 5, 1, tzinfo=timezone.utc)
    rows: list[list[str]] = []
    event_id = 0

    for u in range(1, n_users + 1):
        user_id = f"user_{u:04d}"
        cohort_day = rng.randint(0, 28)
        base = start + timedelta(days=cohort_day, hours=rng.randint(8, 20))
        session = f"s_{u:04d}_01"

        def emit(name: str, ts: datetime, sid: str, props: str = "{}") -> None:
            nonlocal event_id
            event_id += 1
            rows.append(
                [
                    f"evt_{event_id:06d}",
                    user_id,
                    name,
                    ts.isoformat().replace("+00:00", "Z"),
                    sid,
                    props,
                ]
            )

        # Everyone starts signup
        t = base
        emit("signup_started", t, session)

        if rng.random() < 0.82:
            t += timedelta(minutes=rng.randint(1, 8))
            emit("signup_completed", t, session)
        else:
            t += timedelta(minutes=rng.randint(1, 5))
            emit("session_abandoned", t, session)
            continue

        if rng.random() < 0.78:
            t += timedelta(minutes=rng.randint(2, 15))
            emit("onboarding_step_viewed", t, session, '{"step":1}')
        else:
            emit("session_abandoned", t + timedelta(minutes=2), session)
            continue

        if rng.random() < 0.18:
            emit("error_shown", t + timedelta(minutes=1), session, '{"code":"onboarding_timeout"}')

        if rng.random() < 0.65:
            t += timedelta(minutes=rng.randint(3, 25))
            emit("feature_used", t, session, '{"feature":"board"}')
        else:
            emit("session_abandoned", t + timedelta(minutes=3), session)
            continue

        activated = rng.random() < 0.55
        if activated:
            t += timedelta(minutes=rng.randint(2, 20))
            emit("activation_completed", t, session)

        # Second session for retention / expansion
        if rng.random() < 0.48:
            sid2 = f"s_{u:04d}_02"
            t2 = base + timedelta(days=rng.randint(2, 10), hours=rng.randint(9, 18))
            emit("return_visit", t2, sid2)
            if activated and rng.random() < 0.4:
                emit("feature_used", t2 + timedelta(minutes=5), sid2, '{"feature":"board"}')
            if activated and rng.random() < 0.25:
                emit("invite_sent", t2 + timedelta(minutes=12), sid2)
            if rng.random() < 0.2:
                emit("billing_viewed", t2 + timedelta(minutes=18), sid2)

        # Third week activity for some activated users
        if activated and rng.random() < 0.35:
            sid3 = f"s_{u:04d}_03"
            t3 = base + timedelta(days=rng.randint(14, 21), hours=rng.randint(10, 17))
            emit("return_visit", t3, sid3)
            emit("feature_used", t3 + timedelta(minutes=4), sid3, '{"feature":"insights"}')

    rows.sort(key=lambda r: r[3])
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["event_id", "user_id", "event_name", "ts", "session_id", "properties"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} events for {n_users} users -> {path}")


if __name__ == "__main__":
    write_taxonomy()
    write_events()
    print(f"Taxonomy -> {SEED / 'event_taxonomy.csv'}")
