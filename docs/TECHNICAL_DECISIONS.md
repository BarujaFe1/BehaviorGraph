# Technical Decisions — BehaviorGraph

## 1. Nested funnel over independent counts
**Decision:** Activation steps use nested unique-user sets.  
**Why:** Independent counts can inflate later steps and allow non-monotonic funnels, which misleads product conversations.  
**Trade-off:** Stricter funnel; skips are treated as drop-offs.

## 2. First-seen week cohorts with explicit offsets
**Decision:** Cohort key = first event week; retention evaluated at W0–W4 relative offsets.  
**Why:** Enumerating observed weeks as “offsets” overstated early retention.  
**Trade-off:** Sparse later weeks are expected on a short synthetic window.

## 3. Static snapshot for public demo
**Decision:** Embed analytics JSON for frontend-only hosting.  
**Why:** Stable Live Demo without paying for always-on Python workers.  
**Trade-off:** Snapshot must be regenerated when seed/analytics change.

## 4. NetworkX transition graph (not attribution)
**Decision:** Session pairwise transitions only.  
**Why:** Communicates journey shape for interviews without fake causal certainty.  
**Trade-off:** Not a Markov model; not multi-touch attribution.

## 5. Pydantic on every analytics response
**Decision:** Validate API payloads with Pydantic v2 models.  
**Why:** Prevents silent schema drift between Python and TypeScript consumers.  
**Trade-off:** Slight boilerplate; worth it for portfolio rigor.

## 6. Remove unused DuckDB from MVP deps
**Decision:** Drop DuckDB until exploration features exist.  
**Why:** Declared-but-unused deps hurt recruiter trust.  
**Trade-off:** Roadmap still mentions DuckDB for Phase 2 exploration.
