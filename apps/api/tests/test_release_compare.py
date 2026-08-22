"""Release comparison tests: raw vs trusted funnels per release (G3, G5)."""

from __future__ import annotations

import pytest

from app.services.release_compare import (
    ACTIVATION_STEPS,
    build_overview,
    compare_release,
)


class TestReleaseCompare:
    def test_activation_steps_match_canonical_path(self) -> None:
        assert ACTIVATION_STEPS == [
            "signup_started",
            "signup_completed",
            "profile_saved",
            "onboarding_completed",
            "activation_completed",
        ]

    @staticmethod
    def _step(funnel, name: str) -> dict:
        return next(step for step in funnel if step["step"] == name)

    def test_healthy_raw_and_trusted_are_equivalent(self) -> None:
        comparison = compare_release("v2.2.0-healthy")
        assert comparison.total_events == comparison.trusted_events or (
            comparison.trusted_events / comparison.total_events > 0.98
        )
        raw = self._step(comparison.raw_funnel, "activation_completed")
        trusted = self._step(comparison.trusted_funnel, "activation_completed")
        assert raw["users"] == trusted["users"]

    def test_g3_buggy_raw_gain_vanishes_under_trusted_filter(self) -> None:
        healthy = compare_release("v2.2.0-healthy")
        buggy = compare_release("v2.3.0-buggy")

        raw_onboarding_h = self._step(healthy.raw_funnel, "onboarding_completed")["users"]
        raw_onboarding_b = self._step(buggy.raw_funnel, "onboarding_completed")["users"]
        assert raw_onboarding_b / max(raw_onboarding_h, 1) > 1.10, (
            "fixture bug: buggy release must LOOK better on raw onboarding"
        )

        trusted_onboarding_h = self._step(
            healthy.trusted_funnel, "onboarding_completed"
        )["users"]
        trusted_onboarding_b = self._step(
            buggy.trusted_funnel, "onboarding_completed"
        )["users"]
        assert trusted_onboarding_b <= trusted_onboarding_h * 1.05, (
            "trusted filter must remove the artificial improvement"
        )

        verdict = buggy.verdict
        assert verdict["raw_looks_better"] is True
        assert verdict["survives_trusted_filter"] is False
        assert verdict["classification"] == "instrumentation_artifact"

    def test_g5_real_improvement_survives_trusted_filter(self) -> None:
        healthy = compare_release("v2.2.0-healthy")
        fixed = compare_release("v2.3.0-fixed")
        assert fixed.activation_trusted_rate > healthy.activation_trusted_rate
        assert fixed.verdict["raw_looks_better"] is True
        assert fixed.verdict["survives_trusted_filter"] is True
        assert fixed.verdict["classification"] == "real_improvement"

    def test_overview_covers_all_releases_with_deterministic_order(self) -> None:
        overview = build_overview()
        assert [entry["release"] for entry in overview["releases"]] == [
            "v2.2.0-healthy",
            "v2.3.0-buggy",
            "v2.3.0-fixed",
        ]
        assert overview["method"] == "unique_user_funnel"
        assert overview["observational_notice"].startswith("Observational")

    def test_metrics_count_unique_users_not_events(self) -> None:
        comparison = compare_release("v2.3.0-buggy")
        for step in comparison.raw_funnel:
            users = step["users"]
            assert step["unique_user_basis"] is True
            assert 0 < users <= 800

    @pytest.mark.parametrize(
        ("release", "expected_status"),
        [
            ("v2.2.0-healthy", "pass"),
            ("v2.3.0-buggy", "block"),
            ("v2.3.0-fixed", "pass"),
        ],
    )
    def test_overview_carries_instrumentation_status(
        self, release: str, expected_status: str
    ) -> None:
        overview = build_overview()
        entry = next(e for e in overview["releases"] if e["release"] == release)
        assert entry["instrumentation_status"] == expected_status
