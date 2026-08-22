"""Release intelligence API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_releases_overview_endpoint() -> None:
    response = client.get("/api/releases/overview")
    assert response.status_code == 200
    body = response.json()
    assert body["method"] == "unique_user_funnel"
    assert [r["release"] for r in body["releases"]] == [
        "v2.2.0-healthy",
        "v2.3.0-buggy",
        "v2.3.0-fixed",
    ]
    buggy = next(r for r in body["releases"] if r["release"] == "v2.3.0-buggy")
    assert buggy["instrumentation_status"] == "block"


def test_release_instrumentation_endpoint() -> None:
    response = client.get("/api/releases/v2.3.0-buggy/instrumentation")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "block"
    codes = {v["code"] for v in body["violations"]}
    assert {"order_violation", "duplicate_insert_id", "unknown_event"} <= codes


def test_release_comparison_endpoint() -> None:
    response = client.get("/api/releases/v2.3.0-fixed/comparison")
    assert response.status_code == 200
    body = response.json()
    assert body["verdict"]["classification"] == "real_improvement"
    assert len(body["raw_funnel"]) == 5


def test_journey_diff_endpoint_defaults_to_baseline_pair() -> None:
    response = client.get("/api/releases/diff")
    assert response.status_code == 200
    body = response.json()
    assert body["baseline"] == "v2.2.0-healthy"
    assert body["target"] == "v2.3.0-buggy"


def test_unknown_release_returns_actionable_404() -> None:
    response = client.get("/api/releases/v9.9.9-nope/instrumentation")
    assert response.status_code == 404
    body = response.json()
    assert "known releases" in body["detail"].lower()
