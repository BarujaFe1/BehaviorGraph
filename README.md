<div align="center">
  <img src="./assets/icon.png" alt="BehaviorGraph Logo" width="120" height="120" />

  <h1>BehaviorGraph</h1>

  <p><strong>Which paths lead to activation, abandonment, or habit?</strong></p>
  <p>Behavioral analytics lab: event taxonomy → nested funnel → retention cohorts → journey graph → product opportunity memo.</p>

  <p>
    <a href="https://barujafe1.github.io/BehaviorGraph/"><strong>🌐 Live Demo</strong></a> •
    <a href="#problem">Problem</a> •
    <a href="#solution">Solution</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#what-this-project-demonstrates">Portfolio value</a>
  </p>

  <p>
    <img alt="Next.js" src="https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=nextdotjs" />
    <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-React-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
    <img alt="Python" src="https://img.shields.io/badge/Python-Analytics-3776AB?style=for-the-badge&logo=python&logoColor=white" />
    <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
    <img alt="NetworkX" src="https://img.shields.io/badge/NetworkX-Journey%20Graph-FF6F61?style=for-the-badge" />
    <img alt="Responsible Analytics" src="https://img.shields.io/badge/Responsible-Analytics-22C55E?style=for-the-badge" />
  </p>
</div>

<p align="center">
  <img src="./assets/hero-cover.png" alt="BehaviorGraph product overview" width="100%" />
</p>

---

## Status

| Item | State |
|---|---|
| Scope | Portfolio lab / MVP (synthetic seed) |
| Live Demo | [barujafe1.github.io/BehaviorGraph](https://barujafe1.github.io/BehaviorGraph/) |
| Repo homepage | configured |
| CI | GitHub Actions (API + Web) |
| Production tracking | **Out of scope** |

> **Responsible Product Analytics Notice**  
> Synthetic SaaS onboarding events only. Not production telemetry, not Mixpanel, and not causal attribution from path graphs.

---

## Problem

Digital products collect events, but teams still struggle to answer:

- Which activation steps lose users?
- Which session transitions dominate?
- Which cohorts retain after week 0?
- Where is friction high enough to deserve a product bet?

Conversion vanity metrics (“how many signed up?”) hide the path.

---

## Solution

**BehaviorGraph** converts a synthetic event stream into a product narrative:

1. **Event taxonomy** — owned contract (name, category, owner)
2. **Nested activation funnel** — unique users remaining in prior steps
3. **Retention cohorts** — first-seen week with true W0–W4 offsets
4. **Journey graph** — NetworkX session transitions
5. **Segments + friction radar** — activated / at-risk / power + drop severity
6. **Opportunity memo** — hypotheses with explicit limitations

---

## Core features

- Taxonomy center for instrumentation discussions
- Nested unique-user activation funnel (+ conversion from start)
- Retention cohort heat matrix
- Journey path edges with weights
- Friction severity bands (`low` / `medium` / `high`)
- Product opportunity memo (action + impact hypothesis + limits)
- Static lab snapshot for reliable public demos
- Optional FastAPI backend for local full-stack runs

---

## Architecture

```text
CSV seed → FastAPI analytics (Pandas/NetworkX/Pydantic)
                 ↓
        demo-snapshot.json (static)
                 ↓
     Next.js cockpit (Recharts + matrix)
```

Details: [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) · decisions: [docs/TECHNICAL_DECISIONS.md](./docs/TECHNICAL_DECISIONS.md)

<p align="center">
  <img src="./assets/architecture-pipeline.png" alt="BehaviorGraph architecture" width="100%" />
</p>

---

## Stack

| Layer | Choices |
|---|---|
| Frontend | Next.js 15, React 19, TypeScript, Recharts |
| Backend | FastAPI, Pydantic v2, Pandas, NetworkX |
| Data | Synthetic CSV seed (`data/seed`) |
| Quality | Pytest, Ruff, ESLint, `tsc`, GitHub Actions |
| Hosting | GitHub Pages (live) + Vercel-ready static export |

---

## Screenshots

<table>
  <tr>
    <td width="50%">
      <img src="./assets/screenshots/03-activation-funnel.png" alt="Activation Funnel" />
      <br /><sub><strong>Activation Funnel</strong> — nested unique-user conversion</sub>
    </td>
    <td width="50%">
      <img src="./assets/screenshots/04-retention-cohorts.png" alt="Retention Cohorts" />
      <br /><sub><strong>Retention Cohorts</strong> — first-seen week matrix</sub>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <img src="./assets/screenshots/05-journey-path-graph.png" alt="Journey Graph" />
      <br /><sub><strong>Journey Graph</strong> — session transitions</sub>
    </td>
    <td width="50%">
      <img src="./assets/screenshots/08-opportunity-memo.png" alt="Opportunity Memo" />
      <br /><sub><strong>Opportunity Memo</strong> — hypotheses + limits</sub>
    </td>
  </tr>
</table>

---

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.12 recommended
- Git

### Option A — Windows one-click
```bash
start.bat
```

### Option B — Static web lab only
```bash
cd apps/web
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) — uses embedded snapshot (no API required).

### Option C — Full-stack local
```bash
# API
cd apps/api
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Web (new terminal)
cd apps/web
# set NEXT_PUBLIC_API_URL=http://127.0.0.1:8000 in .env.local
npm install
npm run dev
```

### Environment variables
See [`.env.example`](./.env.example) and [`apps/web/.env.example`](./apps/web/.env.example).

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_URL` | Optional FastAPI base URL; empty = snapshot lab mode |
| `GITHUB_PAGES=true` | Adds `/BehaviorGraph` basePath for Pages builds |

Never commit `.env.local` or secrets. See [SECURITY_NOTES.md](./SECURITY_NOTES.md).

---

## Tests & quality

```bash
# API
cd apps/api
.venv\Scripts\python -m pytest -q
.venv\Scripts\ruff check app tests

# Web
cd apps/web
npm run lint
npm run typecheck
npm run build
```

More: [docs/TESTING.md](./docs/TESTING.md) · Deploy: [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)

---

## Trade-offs

| Choice | Gain | Cost |
|---|---|---|
| Static snapshot demo | Reliable public URL | Must regenerate after analytics changes |
| Nested funnel | Honest drop-offs | Stricter than independent counts |
| Transition graph | Clear journey story | Not attribution / not causal |
| Lab scope | Portfolio clarity | Not a full product-analytics suite |

---

## Roadmap

- **MVP (now):** taxonomy, nested funnel, cohorts, graph, friction, memo, static demo, CI
- **Phase 2:** orphan events, sequence analysis, behavioral cohorts, activation alerts
- **Phase 3:** minimal SDK, near-real-time ingest, experiment tags, product Q&A assistant

Non-goals: Mixpanel clone, generic metrics dashboard, production tracking in MVP.

---

## What this project demonstrates

- Product analytics thinking (instrumentation → narrative → decision)
- Correct funnel/cohort definitions (not vanity charts)
- Full-stack delivery (FastAPI + Next.js) with a resilient static demo mode
- Responsible analytics communication (limits stated in UI + docs)
- Engineering hygiene (Pydantic contracts, tests, CI, deploy docs)

---

## How I would present this in an interview

1. **Hook (20s):** “Conversion asks *how many*; BehaviorGraph asks *which paths*.”
2. **Taxonomy (40s):** Show owned events as a product contract.
3. **Funnel (60s):** Explain nested unique users and the largest drop.
4. **Cohorts (40s):** First-seen week + W1 retention — why offset math matters.
5. **Journey + friction (40s):** Transitions as exploration, not causation.
6. **Memo (40s):** Turn drops into hypotheses with limitations.
7. **Close (20s):** Lab scope honesty — what I’d build next vs what I refuse to overclaim.

Pitch notes: [docs/portfolio_pitch.md](./docs/portfolio_pitch.md)

---

## Author

**Felipe Alirio Baruja**

- Portfolio: [barujafe.vercel.app](https://barujafe.vercel.app/)
- GitHub: [@BarujaFe1](https://github.com/BarujaFe1)
- LinkedIn: [Gustavo Felipe Alirio Baruja](https://www.linkedin.com/in/barujafe/)

## License

MIT License © 2026 Felipe Alirio Baruja
