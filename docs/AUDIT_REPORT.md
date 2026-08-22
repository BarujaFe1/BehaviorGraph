# BehaviorGraph — Audit Report

**Date:** 2026-07-13  
**Branch:** `chore/portfolio-quality-pass`  
**Auditor role:** senior full-stack + analytics + QA + portfolio recruiter

## Executive summary

BehaviorGraph is a credible portfolio lab for product analytics: synthetic events → taxonomy → nested activation funnel → retention cohorts → journey graph → friction → opportunity memo. The initial scaffold was runnable but analytically soft (non-nested funnel, incorrect cohort offsets), visually list-heavy, lightly tested, and missing CI/docs rigor.

**Pre-pass score: 6.4 / 10**  
**Target after this pass: 8.4–8.7 / 10** (lab scope, not Mixpanel clone)

## Stack (verified)

| Layer | Tech |
|---|---|
| Web | Next.js 15, React 19, TypeScript, Recharts |
| API | FastAPI, Pydantic v2, Pandas, NetworkX |
| Data | Synthetic CSV seed (`data/seed`) |
| Demo hosting | Static export + embedded JSON snapshot; GitHub Pages live |
| Deploy config | `vercel.json` (static `out/`) |

## Main risks found

1. **Analytical correctness:** activation funnel counted independent unique users (not nested). Cohort `week_offset` was an enumeration of observed weeks, not true offset from first-seen week.
2. **Security hygiene:** local `apps/web/.env.local` contained a Vercel OIDC token (gitignored; documented in `SECURITY_NOTES.md`).
3. **Deploy config mismatch:** root `vercel.json` pointed to `.next` while Next is configured with `output: "export"` → `out/`.
4. **DX:** `next lint` had no ESLint config (interactive prompt). DuckDB listed but unused.
5. **Tests:** only 2 shallow assertions — insufficient for funnel/cohort guarantees.
6. **UX/portfolio:** list-only cockpit, weak empty/loading/a11y states, unused chart libs.

## Quick wins (done in this pass)

- Nested unique-user funnel + conversion_from_start
- True cohort week offsets (W0–W4)
- Pydantic response models on API routes
- Expanded pytest coverage + TestClient checks
- Regenerated `demo-snapshot.json`
- Recharts funnel + cohort heat matrix + skeleton/nav/a11y
- ESLint flat config, CI workflow, deploy docs
- Removed unused DuckDB dependency (roadmap only)
- Portfolio-strength README + architecture docs

## Structural improvements

- Clear lab mode: frontend snapshot by default; optional FastAPI via `NEXT_PUBLIC_API_URL`
- Cached event load (`lru_cache`) for API performance on seed
- Component split (`FunnelChart`, `CohortMatrix`, `KpiCard`, `SkeletonGrid`)
- Explicit methodology copy in UI (responsible analytics)

## Bugs found

| Bug | Severity | Status |
|---|---|---|
| Non-nested funnel conversion | High | Fixed |
| Cohort week_offset incorrect | High | Fixed |
| Timezone Period warning | Low | Fixed (tz normalized) |
| Vercel outputDirectory wrong | Medium | Fixed |
| Lint interactive / no config | Medium | Fixed |
| Unused deps (duckdb / dead UI libs) | Low | Cleaned / used |

## Execution plan

1. Diagnose + branch ✅  
2. Fix analytics + tests ✅  
3. API models + snapshot refresh ✅  
4. UX + a11y polish ✅  
5. CI + docs + README ✅  
6. Verify build/lint/pytest ✅  
7. Commit + push branch ✅  

## Final checklist

- [x] Installs (web + api)
- [x] Tests pass
- [x] Build passes (static export)
- [x] Lint/typecheck configured
- [x] Secrets protected / noted
- [x] README portfolio-ready
- [x] CI added
- [x] Handoff written
