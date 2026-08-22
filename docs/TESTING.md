# Testing — BehaviorGraph

## API (pytest)

```bash
cd apps/api
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
ruff check app tests
```

### What is covered
- Demo summary shape and activation rate bounds
- Nested funnel monotonicity + conversion bounds
- Cohort week_offset sequence and W0 = 100%
- Journey graph weighted edges
- `/health` and `/api/funnel/activation` HTTP contracts

## Web (TypeScript)

```bash
cd apps/web
npm install
npm run lint
npm run typecheck
npm run build
```

## Regenerating the lab snapshot

After changing seed data or analytics logic:

```bash
# from repo root, with API venv installed
apps\api\.venv\Scripts\python -c "..."
# or use scripts / documented snapshot command in package.json
```

Prefer the helper used in CI docs / `scripts` when available. Snapshot path:

`apps/web/lib/demo-snapshot.json`

## CI
GitHub Actions (`.github/workflows/ci.yml`) runs API ruff+pytest and web lint+typecheck+build on push/PR.
