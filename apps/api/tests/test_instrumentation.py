"""Release intelligence tests: tracking contracts + instrumentation validator."""

from __future__ import annotations

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
            for prerequisite in spec.must_follow or []:
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
        with pytest.raises(Exception):
            violation.event_name = "mutated"  # type: ignore[misc]
