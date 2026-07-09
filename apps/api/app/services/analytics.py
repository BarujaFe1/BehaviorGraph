from __future__ import annotations

from collections import Counter
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


def _events() -> pd.DataFrame:
    if not SEED_EVENTS.exists():
        return pd.DataFrame(
            columns=["event_id", "user_id", "event_name", "ts", "session_id", "properties"]
        )
    df = pd.read_csv(SEED_EVENTS)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    return df.sort_values("ts")


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
        "notice": "Demo uses synthetic events only — not production tracking.",
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
    df = _events().tail(limit)
    records = df.to_dict(orient="records")
    for row in records:
        row["ts"] = row["ts"].isoformat()
    return records


def build_activation_funnel() -> dict:
    df = _events()
    steps = []
    prev_users: set[str] | None = None
    for name in ACTIVATION_STEPS:
        users = set(df.loc[df["event_name"] == name, "user_id"].astype(str))
        count = len(users)
        conversion_from_prev = (
            round(count / len(prev_users), 3) if prev_users else 1.0
        )
        steps.append(
            {
                "step": name,
                "users": count,
                "conversion_from_previous": conversion_from_prev,
            }
        )
        prev_users = users
    return {"funnel": "activation", "steps": steps}


def build_retention_cohorts() -> dict:
    df = _events()
    if df.empty:
        return {"cohorts": []}

    first = df.groupby("user_id")["ts"].min().rename("cohort_week")
    first = first.dt.to_period("W").astype(str)
    activity = df.assign(activity_week=df["ts"].dt.to_period("W").astype(str))
    activity = activity.merge(first, on="user_id")

    cohorts: list[dict] = []
    for cohort_week, group in activity.groupby("cohort_week"):
        size = group["user_id"].nunique()
        weeks = []
        for offset, week in enumerate(sorted(group["activity_week"].unique())):
            retained = group.loc[group["activity_week"] == week, "user_id"].nunique()
            weeks.append(
                {
                    "week_offset": offset,
                    "week": week,
                    "retained_users": int(retained),
                    "retention_rate": round(retained / size, 3) if size else 0.0,
                }
            )
        cohorts.append(
            {
                "cohort_week": cohort_week,
                "cohort_size": int(size),
                "weeks": weeks[:5],
            }
        )
    return {"cohorts": cohorts[:6]}


def build_journey_graph(limit_edges: int = 40) -> dict:
    df = _events()
    if df.empty:
        return {"nodes": [], "edges": []}

    transitions: Counter[tuple[str, str]] = Counter()
    for _, session in df.groupby("session_id"):
        names = session.sort_values("ts")["event_name"].tolist()
        for a, b in zip(names, names[1:]):
            if a != b:
                transitions[(a, b)] += 1

    G = nx.DiGraph()
    for (src, dst), weight in transitions.most_common(limit_edges):
        G.add_edge(src, dst, weight=weight)

    nodes = [{"id": n, "label": n} for n in G.nodes]
    edges = [
        {"source": u, "target": v, "weight": int(d["weight"])}
        for u, v, d in G.edges(data=True)
    ]
    return {"nodes": nodes, "edges": edges, "engine": "networkx"}


def build_segments() -> dict:
    df = _events()
    if df.empty:
        return {"segments": []}

    activated = set(df.loc[df["event_name"] == "activation_completed", "user_id"])
    churn_signal = set(df.loc[df["event_name"] == "session_abandoned", "user_id"])
    power = (
        df.groupby("user_id").size().sort_values(ascending=False).head(20).index
    )
    power_users = set(power)

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
        drops.append(
            {
                "from_step": prev["step"],
                "to_step": cur["step"],
                "drop_users": drop,
                "drop_rate": drop_rate,
                "severity": "high" if drop_rate >= 0.35 else "medium" if drop_rate >= 0.2 else "low",
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
                "why": f"Drop rate {top_drop['drop_rate']:.0%} on the activation path.",
                "suggested_action": "Simplify the step UX, add progressive disclosure, instrument micro-errors.",
                "impact_hypothesis": "Improving this transition should lift activation_rate without new acquisition.",
            }
        )
    opportunities.append(
        {
            "title": "Close taxonomy gaps before production tracking",
            "why": "Orphan or inconsistently named events hide journey truth.",
            "suggested_action": "Enforce event taxonomy ownership and reject unknown events in ingest.",
            "impact_hypothesis": "Cleaner schema improves funnel and cohort reliability.",
        }
    )
    opportunities.append(
        {
            "title": "Protect activated cohort with early habit loops",
            "why": f"Activation rate is {summary['activation_rate']:.0%} in the demo window.",
            "suggested_action": "Trigger day-1 / day-7 nudges only for activated users with low feature_used density.",
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
        ],
    }
