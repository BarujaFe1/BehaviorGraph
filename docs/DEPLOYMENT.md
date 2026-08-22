# Deployment — BehaviorGraph

## Public Live Demo (current)
**URL:** https://barujafe1.github.io/BehaviorGraph/

GitHub Pages serves the static Next export from branch `gh-pages` with `basePath=/BehaviorGraph`.

### Rebuild Pages payload

```bash
# 1) regenerate the release-intelligence snapshot from backend services
python scripts/generate_release_snapshot.py

cd apps/web
set GITHUB_PAGES=true   # Windows PowerShell: $env:GITHUB_PAGES="true"
npm run build
# publish apps/web/out contents to gh-pages branch (orphan/static)
```

## Vercel (recommended production path)

Project `behaviorgraph` is linked. Root `vercel.json`:

- install: `cd apps/web && npm install`
- build: `cd apps/web && npm run build`
- output: `apps/web/out` (static export)

```bash
cd apps/web
npx vercel --prod
```

If the free-tier daily deployment quota is exhausted, prefer GitHub Pages until reset.

### Env
For static lab mode, leave `NEXT_PUBLIC_API_URL` empty.  
Only set it when a public FastAPI backend exists.

## Local full-stack

```bash
# API
cd apps/api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Web
cd apps/web
# .env.local
# NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
npm install
npm run dev
```

Or Windows: `start.bat` from repo root.
