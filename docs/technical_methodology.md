# BehaviorGraph — Technical Methodology

## Event schema (simplified PostHog-like)

| Field | Type | Notes |
|---|---|---|
| `event_id` | string | Unique event id |
| `user_id` | string | Anonymous or known user key |
| `event_name` | string | Taxonomy-controlled name |
| `ts` | ISO datetime | Event timestamp (UTC) |
| `session_id` | string | Session grouping key |
| `properties` | JSON/string | Optional payload |

## Activation funnel

Ordered steps:

1. `signup_started`
2. `signup_completed`
3. `onboarding_step_viewed`
4. `feature_used`
5. `activation_completed`

Conversion between steps is unique-user based (not event-count based).

## Retention cohorts

- Cohort key: first-seen week of each `user_id`
- Retention: share of cohort users active in subsequent weeks
- Demo window is intentionally short and synthetic

## Journey graph

- Built with NetworkX from ordered session transitions
- Edge weight = transition count
- Exploratory map — not Markov attribution or causal path proof

## Friction & opportunities

- Funnel drop severity bands (low / medium / high)
- Error-like events (`error_shown`, `session_abandoned`) as friction signals
- Opportunity memo pairs drops with product hypotheses and limitations

## Out of scope (MVP)

- Production SDK ingest
- Real-time streaming
- Competing with full product-analytics suites
