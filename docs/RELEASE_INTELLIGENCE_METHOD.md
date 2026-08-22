# Release Intelligence — Method

> How BehaviorGraph decides whether a release actually improved behavior or just broke instrumentation.

## Problem

After a release, dashboards compare funnels and cohorts across versions. If a client bug makes an event fire early (or fire twice), conversion **looks** different and teams ship wrong conclusions. Dashboards count events; they rarely validate what events mean first.

## Approach: contracts gate comparisons

Every comparison runs against a versioned tracking contract (`data/contracts/events.yml`). The contract declares, per event:

| Field | Meaning |
|---|---|
| `owner` | Accountable team |
| `required_properties` | Props that must be present on every occurrence |
| `must_follow` | Events that must occur earlier in the same session |
| `max_per_user_session` | Cardinality ceiling per session |
| `introduced_in` | Release that introduced the event |

## Violation codes

| Code | Severity | Meaning |
|---|---|---|
| `missing_required_property` | block | Occurrence lacks a required prop |
| `order_violation` | block | `must_follow` prerequisite not seen earlier in-session |
| `duplicate_insert_id` | block | Client retry reused an insert_id (dedup keeps first) |
| `cardinality_breach` | block | More than `max_per_user_session` occurrences in one session |
| `event_drift` | warning | Per-user rate >1.25× baseline release (heuristic) |
| `unknown_event` | warning | Event not declared in the contract — reported, never silently dropped |

**Trusted view** = raw stream minus rows failing any block-level check. Unknown events stay in raw data; they are excluded only from contract-gated metrics.

## Raw vs trusted funnels

Both funnels count **unique users per step**, relative to signup starters:

- **Raw**: every ingested event counts — exactly what a naive dashboard shows.
- **Trusted**: same counting after removing contract-invalid rows.

The deliberate looseness of the raw view is the point: it is the view that gets fooled. When buggy release v2.3 fires `onboarding_completed` before `profile_saved`, raw metrics inflate while trusted metrics do not move.

## Verdicts

For each release vs baseline (`v2.2.0-healthy`), find the step with the largest raw user gain:

- gain ≤ threshold → `baseline`/`no_change`
- raw gain present AND trusted gain survives (>+5%) → **`real_improvement`**
- raw gain present AND trusted gain vanishes → **`instrumentation_artifact`**

## Uncertainty

Activation rates carry **Wilson score intervals** (95%). All statements are observational; causal language requires an explicit experiment flag (`experiment: false` in every fixture manifest).

## Golden scenarios (fixtures are deterministic, seeds fixed)

| ID | Scenario | Expected |
|---|---|---|
| G1 | v2.2 healthy contracts | status `pass`, zero violations |
| G2 | v2.3 buggy order bug | `order_violation` BLOCK, ≥20 users with evidence |
| G3 | Raw looks better, trusted removes it | buggy raw `onboarding_completed` +24.3% → trusted −0.9%, classification `instrumentation_artifact` |
| G4 | Duplicate insert_id | `duplicate_insert_id` violation + dedup shrinks trusted stream |
| G5 | Real improvement survives filter | fixed activation +9.1% raw AND +9.1% trusted, classification `real_improvement` |
| G6 | Unknown event | `upsell_modal_shown` warning; rows kept in raw |

All six are asserted in `apps/api/tests/test_instrumentation.py` and `test_release_compare.py`. Mutation sanity was performed locally: disabling order detection breaks G2; disabling dedup breaks G4 (mutations never committed).

## Limitations

- Synthetic fixtures only — no real users, no PII.
- Drift detection is a heuristic rate comparison, not anomaly modeling.
- Journey diff is descriptive evidence, not attribution.
- Session scope: sequence constraints apply within sessions.
