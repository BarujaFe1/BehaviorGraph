"""Release intelligence tests: tracking contracts + instrumentation validator."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pandas as pd
import pytest

from app.services.instrumentation import (
    InstrumentationViolation,
    load_tracking_contract,
)


class TestTrackingContracts:
    """Phase 2 — versioned YAML contracts are the source of truth."""

    def test_contract_file_loads_and_is_versioned(self) -> None:
        contract = load_tracking_contract()
        assert contract.version == 1
        assert len(contract.events) > 0

    def test_canonical_onboarding_completed_contract(self) -> None:
        contract = load_tracking_contract()
        spec = contract.events["onboarding_completed"]
        assert spec.owner == "growth"
        assert "user_id" in spec.required_properties
        assert "session_id" in spec.required_properties
        assert "insert_id" in spec.required_properties
        assert "release" in spec.required_properties
        assert spec.must_follow == ("profile_saved",)
        assert spec.max_per_user_session == 1
        assert spec.introduced_in == "2.1.0"

    def test_every_declared_event_has_owner_and_required_props(self) -> None:
        contract = load_tracking_contract()
        for name, spec in contract.events.items():
            assert spec.owner, f"{name} missing owner"
            assert spec.required_properties, f"{name} missing required_properties"

    def test_must_follow_references_declared_events(self) -> None:
        contract = load_tracking_contract()
        for name, spec in contract.events.items():
            for prerequisite in spec.must_follow:
                assert (
                    prerequisite in contract.events
                ), f"{name}.must_follow references undeclared event {prerequisite}"

    def test_violation_dataclass_is_frozen_with_canonical_fields(self) -> None:
        violation = InstrumentationViolation(
            event_name="onboarding_completed",
            code="order_violation",
            release="2.3.0-buggy",
            user_count=10,
            evidence_count=10,
            severity="block",
        )
        assert violation.event_name == "onboarding_completed"
        with pytest.raises(FrozenInstanceError):
            violation.event_name = "mutated"  # type: ignore[misc]


class TestReleaseFixtures:
    """Phase 3 — deterministic synthetic releases, no PII."""

    def test_known_releases_are_declared(self) -> None:
        from app.services.release_fixture import RELEASES

        assert set(RELEASES) == {"v2.2.0-healthy", "v2.3.0-buggy", "v2.3.0-fixed"}

    def test_generation_is_deterministic(self) -> None:
        from app.services.release_fixture import build_release_frame

        first = build_release_frame("v2.3.0-buggy")
        second = build_release_frame("v2.3.0-buggy")
        pd.testing.assert_frame_equal(first, second)

    def test_every_row_is_tagged_with_its_release(self) -> None:
        from app.services.release_fixture import RELEASES, build_release_frame

        for release in RELEASES:
            frame = build_release_frame(release)
            assert (frame["release"] == release).all()

    def test_frames_carry_required_columns(self) -> None:
        from app.services.release_fixture import build_release_frame

        frame = build_release_frame("v2.2.0-healthy")
        for column in (
            "event_id",
            "user_id",
            "event_name",
            "ts",
            "session_id",
            "insert_id",
            "properties",
            "release",
        ):
            assert column in frame.columns, f"missing column {column}"

    def test_healthy_fixture_has_no_premature_onboarding(self) -> None:
        from app.services.release_fixture import build_release_frame

        frame = build_release_frame("v2.2.0-healthy")
        bad = _premature_onboarding_users(frame)
        assert len(bad) == 0

    def test_buggy_fixture_has_premature_onboarding_duplicates_and_unknown(
        self,
    ) -> None:
        from app.services.release_fixture import build_release_frame

        frame = build_release_frame("v2.3.0-buggy")
        assert len(_premature_onboarding_users(frame)) > 20
        duplicated = frame["insert_id"].duplicated(keep=False)
        assert int(duplicated.sum()) > 0
        assert (frame["event_name"] == "upsell_modal_shown").any()


def _premature_onboarding_users(frame: pd.DataFrame) -> set[str]:
    """Users whose onboarding_completed precedes any profile_saved in-session."""
    offenders: set[str] = set()
    for _, session in frame.groupby("session_id", sort=False):
        ordered = session.sort_values("ts")
        names = ordered["event_name"].tolist()
        for position, name in enumerate(names):
            if name != "onboarding_completed":
                continue
            prior = set(names[:position])
            if "profile_saved" not in prior:
                offenders.add(str(session["user_id"].iloc[0]))
    return offenders
