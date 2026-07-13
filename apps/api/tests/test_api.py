from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.services.analytics import (
    build_activation_funnel,
    build_journey_graph,
    build_retention_cohorts,
    load_demo_summary,
)

client = TestClient(app)


def test_demo_summary_shape():
    summary = load_demo_summary()
    assert summary["product"] == "BehaviorGraph"
    assert summary["users"] > 0
    assert 0 <= summary["activation_rate"] <= 1


def test_activation_funnel_is_nested_and_monotonic():
    funnel = build_activation_funnel()
    assert funnel["method"] == "nested_unique_users"
    steps = funnel["steps"]
    assert len(steps) == 5
    counts = [s["users"] for s in steps]
    assert counts == sorted(counts, reverse=True)
    assert all(0 <= s["conversion_from_previous"] <= 1 for s in steps)
    assert all(0 <= s["conversion_from_start"] <= 1 for s in steps)


def test_retention_cohorts_week_offsets():
    payload = build_retention_cohorts()
    assert payload["method"] == "first_seen_week"
    assert payload["cohorts"]
    for cohort in payload["cohorts"]:
        offsets = [w["week_offset"] for w in cohort["weeks"]]
        assert offsets == list(range(len(offsets)))
        assert cohort["weeks"][0]["retention_rate"] == 1.0


def test_journey_graph_has_weighted_edges():
    graph = build_journey_graph(limit_edges=20)
    assert graph["engine"] == "networkx"
    assert graph["edges"]
    assert all(e["weight"] >= 1 for e in graph["edges"])


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_funnel_endpoint_schema():
    response = client.get("/api/funnel/activation")
    assert response.status_code == 200
    body = response.json()
    assert body["method"] == "nested_unique_users"
    assert len(body["steps"]) == 5
