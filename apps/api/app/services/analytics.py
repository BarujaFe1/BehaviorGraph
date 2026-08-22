from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
SEED_EVENTS = ROOT / "data" / "seed" / "events_demo.csv"
SEED_TAXONOMY = ROOT / "data" / "seed" / "event_taxonomy.csv"

ACTIVATION_STEPS = [
    "signup_started",
    "signup_completed",
    "onboarding_step_viewed",
    "feature_used",
    "activation_completed",
]


@lru_cache(maxsize=1)
def _events() -> pd.DataFrame:
    """Load and normalize the synthetic event seed (cached per process)."""
    if not SEED_EVENTS.exists():
        return pd.DataFrame(
            columns=["event_id", "user_id", "event_name", "ts", "session_id", "properties"]
        )
    df = pd.read_csv(SEED_EVENTS)
    df["user_id"] = df["user_id"].astype(str)
    df["event_name"] = df["event_name"].astype(str)
    df["session_id"] = df["session_id"].astype(str)
    # Normalize to UTC-aware then drop tz for stable weekly Period math
    df["ts"] = pd.to_datetime(df["ts"], utc=True).dt.tz_convert(None)
    return df.sort_values(["ts", "event_id"]).reset_index(drop=True)


def clear_event_cache() -> None:
    _events.cache_clear()


def load_demo_summary() -> dict:
    df = _events()
    users = int(df["user_id"].nunique()) if not df.empty else 0
    events = int(len(df))
    sessions = int(df["session_id"].nunique()) if not df.empty else 0
    activated = (
        int(df.loc[df["event_name"] == "activation_completed", "user_id"].nunique())
        if not df.empty
        else 0
    )
    activation_rate = round(activated / users, 3) if users else 0.0
    return {
        "product": "BehaviorGraph",
        "dataset": "synthetic_saas_onboarding",
        "users": users,
        "events": events,
        "sessions": sessions,
        "activated_users": activated,
        "activation_rate": activation_rate,
        "notice": (
            "Demo uses synthetic events only — not production tracking, "
            "not Mixpanel, and not causal attribution."
        ),
    }


def load_event_taxonomy() -> dict:
    if SEED_TAXONOMY.exists():
        tax = pd.read_csv(SEED_TAXONOMY)
        return {"events": tax.to_dict(orient="records")}
    return {
        "events": [
            {
                "event_name": name,
                "category": "activation",
                "description": name.replace("_", " "),
                "owner": "product",
            }
            for name in ACTIVATION_STEPS
        ]
    }


def load_recent_events(limit: int = 50) -> list[dict]:
    limit = max(1, min(int(limit), 500))
    df = _events().tail(limit)
    records = df.to_dict(orient="records")
    for row in records:
        row["ts"] = pd.Timestamp(row["ts"]).isoformat() + "Z"
    return records


def build_activation_funnel() -> dict:
    """Nested unique-user funnel (users must remain in prior step set)."""
    df = _events()
    steps: list[dict] = []
    prev_users: set[str] | None = None
    start_users: set[str] | None = None

    for name in ACTIVATION_STEPS:
        fired = set(df.loc[df["event_name"] == name, "user_id"].astype(str))
        if prev_users is None:
            users = fired
            start_users = fired
            conversion_from_prev = 1.0
        else:
            users = fired & prev_users
            conversion_from_prev = (
                round(len(users) / len(prev_users), 3) if prev_users else 0.0
            )

        conversion_from_start = (
            round(len(users) / len(start_users), 3) if start_users else 0.0
        )
        steps.append(
            {
                "step": name,
                "users": len(users),
                "conversion_from_previous": conversion_from_prev,
                "conversion_from_start": conversion_from_start,
            }
        )
        prev_users = users

    return {
        "funnel": "activation",
        "method": "nested_unique_users",
        "steps": steps,
    }


def build_retention_cohorts() -> dict:
    """First-seen ISO week cohorts with true week_offset retention."""
    df = _events()
    if df.empty:
        return {"cohorts": [], "method": "first_seen_week"}

    first = df.groupby("user_id")["ts"].min().rename("first_ts")
    first_week = first.dt.to_period("W-MON")
    activity = df.merge(first_week.rename("cohort_week"), on="user_id")
    activity = activity.assign(activity_week=activity["ts"].dt.to_period("W-MON"))

    cohorts: list[dict] = []
    for cohort_week, group in activity.groupby("cohort_week"):
        size = int(group["user_id"].nunique())
        weeks: list[dict] = []
        for offset in range(0, 5):
            target = cohort_week + offset
            retained = int(
                group.loc[group["activity_week"] == target, "user_id"].nunique()
            )
            weeks.append(
                {
                    "week_offset": offset,
                    "week": str(target),
                    "retained_users": retained,
                    "retention_rate": round(retained / size, 3) if size else 0.0,
                }
            )
        cohorts.append(
            {
                "cohort_week": str(cohort_week),
                "cohort_size": size,
                "weeks": weeks,
            }
        )

    cohorts.sort(key=lambda c: c["cohort_week"])
    return {"cohorts": cohorts[:6], "method": "first_seen_week"}


def build_journey_graph(limit_edges: int = 40) -> dict:
    """Session-ordered transition graph (exploratory, not attribution)."""
    df = _events()
    if df.empty:
        return {"nodes": [], "edges": [], "engine": "networkx"}

    limit_edges = max(1, min(int(limit_edges), 200))
    transitions: Counter[tuple[str, str]] = Counter()
    for _, session in df.groupby("session_id", sort=False):
        names = session.sort_values("ts")["event_name"].tolist()
        for a, b in zip(names, names[1:], strict=False):
            if a != b:
                transitions[(a, b)] += 1

    graph = nx.DiGraph()
    for (src, dst), weight in transitions.most_common(limit_edges):
        graph.add_edge(src, dst, weight=weight)

    nodes = [{"id": n, "label": n} for n in graph.nodes]
    edges = [
        {"source": u, "target": v, "weight": int(data["weight"])}
        for u, v, data in graph.edges(data=True)
    ]
    return {"nodes": nodes, "edges": edges, "engine": "networkx"}


def build_segments() -> dict:
    df = _events()
    if df.empty:
        return {"segments": []}

    activated = set(df.loc[df["event_name"] == "activation_completed", "user_id"])
    churn_signal = set(df.loc[df["event_name"] == "session_abandoned", "user_id"])
    power_users = set(
        df.groupby("user_id").size().sort_values(ascending=False).head(20).index
    )

    segments = [
        {
            "id": "activated",
            "name": "Activated",
            "users": len(activated),
            "definition": "Users who fired activation_completed",
        },
        {
            "id": "at_risk",
            "name": "At-risk / friction",
            "users": len(churn_signal - activated),
            "definition": "Users with session_abandoned who never activated",
        },
        {
            "id": "power",
            "name": "Power explorers",
            "users": len(power_users),
            "definition": "Top 20 users by event volume in the demo window",
        },
    ]
    return {"segments": segments}


def build_friction_points() -> dict:
    df = _events()
    funnel = build_activation_funnel()["steps"]
    drops = []
    for i in range(1, len(funnel)):
        prev, cur = funnel[i - 1], funnel[i]
        drop = prev["users"] - cur["users"]
        drop_rate = round(drop / prev["users"], 3) if prev["users"] else 0.0
        severity = (
            "high" if drop_rate >= 0.35 else "medium" if drop_rate >= 0.2 else "low"
        )
        drops.append(
            {
                "from_step": prev["step"],
                "to_step": cur["step"],
                "drop_users": drop,
                "drop_rate": drop_rate,
                "severity": severity,
            }
        )

    error_counts = (
        df.loc[df["event_name"].isin(["error_shown", "session_abandoned"])]
        .groupby("event_name")["user_id"]
        .nunique()
        .to_dict()
        if not df.empty
        else {}
    )
    return {
        "funnel_drops": drops,
        "error_signals": [
            {"event_name": k, "affected_users": int(v)} for k, v in error_counts.items()
        ],
    }


def build_opportunity_memo() -> dict:
    summary = load_demo_summary()
    friction = build_friction_points()
    top_drop = max(friction["funnel_drops"], key=lambda x: x["drop_rate"], default=None)
    opportunities = []
    if top_drop:
        opportunities.append(
            {
                "title": f"Reduce drop {top_drop['from_step']} → {top_drop['to_step']}",
                "why": f"Drop rate {top_drop['drop_rate']:.0%} on the nested activation path.",
                "suggested_action": (
                    "Simplify the step UX, add progressive disclosure, instrument micro-errors."
                ),
                "impact_hypothesis": (
                    "Improving this transition should lift activation_rate without new acquisition."
                ),
            }
        )
    opportunities.append(
        {
            "title": "Close taxonomy gaps before production tracking",
            "why": "Orphan or inconsistently named events hide journey truth.",
            "suggested_action": (
                "Enforce event taxonomy ownership and reject unknown events in ingest."
            ),
            "impact_hypothesis": "Cleaner schema improves funnel and cohort reliability.",
        }
    )
    opportunities.append(
        {
            "title": "Protect activated cohort with early habit loops",
            "why": f"Activation rate is {summary['activation_rate']:.0%} in the demo window.",
            "suggested_action": (
                "Trigger day-1 / day-7 nudges only for activated users with low feature_used density."
            ),
            "impact_hypothesis": "Retention lift comes from habit, not more signup volume.",
        }
    )
    return {
        "headline": "Product opportunity memo (synthetic demo)",
        "summary": summary,
        "opportunities": opportunities,
        "limitations": [
            "Synthetic dataset — not causal proof.",
            "No production SDK ingest in MVP.",
            "Path graph is session-local transition counts, not Markov attribution.",
            "Nested funnel counts unique users remaining in the prior step set.",
        ],
    }
