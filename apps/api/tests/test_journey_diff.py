"""Journey diff tests: release-over-release graph edge changes."""

from __future__ import annotations

from app.services.journey_diff import diff_journeys


class TestJourneyDiff:
    def test_diff_is_deterministic(self) -> None:
        first = diff_journeys("v2.2.0-healthy", "v2.3.0-buggy", min_support=5)
        second = diff_journeys("v2.2.0-healthy", "v2.3.0-buggy", min_support=5)
        assert first == second

    def test_buggy_release_adds_shortcut_edge_bypassing_profile_saved(self) -> None:
        diff = diff_journeys("v2.2.0-healthy", "v2.3.0-buggy", min_support=20)
        assert ("signup_completed", "onboarding_completed") not in diff["baseline_edges"]
        shortcut = next(
            (
                edge
                for edge in diff["added"]
                if edge["source"] == "signup_completed"
                and edge["target"] == "onboarding_completed"
            ),
            None,
        )
        assert shortcut is not None
        assert shortcut["target_weight"] >= 20

    def test_removed_edges_carry_baseline_evidence(self) -> None:
        diff = diff_journeys("v2.3.0-buggy", "v2.2.0-healthy", min_support=20)
        for edge in diff["removed"]:
            assert edge["baseline_weight"] >= 20

    def test_min_support_filters_noise(self) -> None:
        strict = diff_journeys("v2.2.0-healthy", "v2.3.0-fixed", min_support=500)
        loose = diff_journeys("v2.2.0-healthy", "v2.3.0-fixed", min_support=1)
        assert len(loose["added"] + loose["removed"]) >= len(
            strict["added"] + strict["removed"]
        )

    def test_payload_declares_observational_scope(self) -> None:
        diff = diff_journeys("v2.2.0-healthy", "v2.3.0-fixed", min_support=10)
        assert diff["notice"].startswith("Observational")
