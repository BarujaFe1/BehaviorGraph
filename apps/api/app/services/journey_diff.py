"""Journey diff: which session-transition edges appear or vanish per release.

Edges are counted from time-ordered events inside each synthetic session.
A minimum support threshold keeps one-off noise out of the narrative. The
diff is descriptive evidence for instrumentation conversations — not causal
attribution and not a Markov model.
"""

from __future__ import annotations

from collections import Counter

from app.services.release_fixture import load_release_frame

DIFF_NOTICE = (
    "Observational edge diff between release journey graphs. New edges show "
    "where tracking or behavior changed; they never prove causation."
)


def _session_transitions(frame) -> Counter[tuple[str, str]]:
    transitions: Counter[tuple[str, str]] = Counter()
    ordered = frame.sort_values(["ts", "event_id"])
    for _, session in ordered.groupby("session_id", sort=False):
        names = session["event_name"].tolist()
        for src, dst in zip(names, names[1:], strict=False):
            if src != dst:
                transitions[(src, dst)] += 1
    return transitions


def diff_journeys(baseline_release: str, target_release: str, min_support: int = 10) -> dict:
    min_support = max(1, int(min_support))
    baseline_edges = {
        edge: weight
        for edge, weight in _session_transitions(
            load_release_frame(baseline_release)
        ).items()
        if weight >= min_support
    }
    target_edges = {
        edge: weight
        for edge, weight in _session_transitions(
            load_release_frame(target_release)
        ).items()
        if weight >= min_support
    }

    added = sorted(target_edges.keys() - baseline_edges.keys())
    removed = sorted(baseline_edges.keys() - target_edges.keys())

    return {
        "baseline": baseline_release,
        "target": target_release,
        "min_support": min_support,
        "baseline_edges": [list(edge) for edge in sorted(baseline_edges)],
        "added": [
            {"source": src, "target": dst, "target_weight": target_edges[(src, dst)]}
            for src, dst in added
        ],
        "removed": [
            {
                "source": src,
                "target": dst,
                "baseline_weight": baseline_edges[(src, dst)],
            }
            for src, dst in removed
        ],
        "notice": DIFF_NOTICE,
    }
