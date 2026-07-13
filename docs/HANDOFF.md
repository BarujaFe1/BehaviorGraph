# Handoff — BehaviorGraph portfolio quality pass

**Branch:** `chore/portfolio-quality-pass`  
**Date:** 2026-07-13

## What was found
- Credible lab scaffold, but funnel/cohort math was misleading for interviews
- Thin tests, no CI, weak ESLint setup (`next lint` interactive)
- UX was list-only despite Recharts being installed
- Vercel output directory mismatched static export (`out` vs `.next`)
- Local `.env.local` held a Vercel OIDC token (gitignored; documented)
- DuckDB declared but unused

## What was fixed / improved
- Nested unique-user activation funnel + `conversion_from_start`
- True cohort week offsets (W0–W4 from first-seen week)
- Timezone-normalized timestamps for Period math
- Pydantic response models on API routes
- Expanded pytest (6 tests) + Ruff config
- Regenerated `apps/web/lib/demo-snapshot.json`
- Lab UI: section nav, KPI cards, funnel chart, cohort heat matrix, skeletons, a11y skip-link, severity badges, memo cards
- ESLint flat config; lint/typecheck/build scripts
- GitHub Actions CI for API + Web
- Docs: AUDIT_REPORT, ARCHITECTURE, TECHNICAL_DECISIONS, TESTING, DEPLOYMENT, SECURITY_NOTES
- Portfolio README rewrite
- `vercel.json` output → `apps/web/out`

## Commands run
```bash
git checkout -b chore/portfolio-quality-pass
python -m venv apps/api/.venv
pip install -r apps/api/requirements.txt
pytest -q
ruff check app tests
# regenerate snapshot via analytics imports
npm install   # apps/web
npm run lint
npm run typecheck
npm run build
```

## Tests executed
- API: pytest (nested funnel, cohorts, journey, health, funnel endpoint)
- Web: lint + typecheck + static export build (verify before merge)

## Still missing / next steps
1. Redeploy GitHub Pages (`gh-pages`) with the improved UI export
2. Vercel production deploy when daily quota allows (`behaviorgraph` project already linked)
3. Replace placeholder screenshots with real UI captures
4. Optional: Playwright smoke against static `out/`
5. Optional Phase 2: orphan-event detector

## Remaining risks
- Snapshot can drift if seed/analytics change without regeneration
- Public demo on Pages may lag `main` until `gh-pages` is refreshed
- Free Vercel deploy quota previously blocked production pushes

## Portfolio suggestions
- Keep card as **Lab demo** with Live Demo link
- Interview story: taxonomy → nested funnel drop → cohort W1 → memo limits
- Emphasize responsible analytics honesty as a differentiator

## Suggested commit message
```text
chore: improve portfolio quality, docs, tests and stability
```
