# Architecture — BehaviorGraph

## Purpose

Portfolio lab for **behavioral / product analytics**: transform synthetic product events into taxonomy, nested activation funnel, retention cohorts, journey graph, segments, friction signals and a product opportunity memo.

## High-level diagram

```text
Synthetic CSV seed (data/seed)
        │
        ▼
 FastAPI analytics services (Pandas + NetworkX)
        │
        ├── /api/demo
        ├── /api/events/taxonomy
        ├── /api/funnel/activation   (nested unique users)
        ├── /api/cohorts/retention   (first-seen week offsets)
        ├── /api/journeys/graph
        ├── /api/segments
        ├── /api/friction
        └── /api/opportunities
        │
        ▼
 demo-snapshot.json (embedded for static hosting)
        │
        ▼
 Next.js lab cockpit (Recharts + cohort matrix)
```

## Runtime modes

### 1) Static lab (default for public demo)
- Next.js `output: "export"`
- Reads `apps/web/lib/demo-snapshot.json`
- No backend required
- Used by GitHub Pages and Vercel static deploy

### 2) Local full-stack
- FastAPI on `:8000`
- Next.js on `:3000` with `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`
- UI prefers API, falls back to snapshot if API is down

## Domain rules

| Concept | Rule |
|---|---|
| Activation funnel | Nested unique users; step N ⊆ step N-1 |
| Retention cohort | Cohort = first-seen ISO week (Mon); W0..W4 offsets |
| Journey graph | Ordered session transitions; edge weight = count |
| Opportunity memo | Hypotheses + explicit limitations (no causal claim) |

## Package layout

```text
apps/api/app/
  api/         # FastAPI routers
  models/      # Pydantic schemas
  services/    # Analytics engine
apps/web/
  app/         # Next.js App Router UI
  components/  # Charts / matrix / KPI
  lib/         # API client + lab snapshot accessors
  types/       # Shared TS types
data/seed/     # Synthetic events + taxonomy
docs/          # Architecture, methodology, handoff
```

## Non-goals (MVP)

- Production event ingest / SDK
- Competing with Mixpanel
- Causal attribution from path graphs
- Generic BI dashboard
