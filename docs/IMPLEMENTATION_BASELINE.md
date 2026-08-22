# Implementation Baseline — Release Intelligence

> Data: 2026-08-22 · Branch base: `main @ 5f8dd3c` (merge do PR #1 `chore/portfolio-quality-pass`)
> Context pack: `PROJECT_CONTEXT_PACK.zip` (HEAD observado na coleta: `e814b9d`)

## 1. Arquitetura atual (verificada no código, não no pack)

```text
data/seed/events_demo.csv  (~970 eventos sintéticos; colunas:
                            event_id,user_id,event_name,ts,session_id,properties)
        │
        ▼
apps/api/app/services/analytics.py   (loader com lru_cache, funil aninhado
        │                             unique-user, cohorts semanais W0–W4,
        │                             journey graph NetworkX, segments,
        │                             friction, opportunity memo)
        ▼
apps/api/app/api/*.py  → FastAPI + schemas Pydantic (app/models/schemas.py)
        │
        ├─► apps/web/lib/demo-snapshot.json (snapshot estático, lab.ts)
        │        └─► Next.js App Router (page.tsx, Recharts)
        └─► CI: .github/workflows/ci.yml (pytest+ruff / lint+typecheck+build)

Deploy: GitHub Pages (branch gh-pages, legacy) + Vercel-ready web app.
```

## 2. O que será reutilizado (reuse-first)

| Ativo | Uso no Release Intelligence |
|---|---|
| `analytics.py::_events()` | Padrão de loader estendido para fixtures por release |
| Funil nested-unique-users | Método canônico reusado em `release_compare.py` (raw vs trusted) |
| Journey graph (Counter de transições por sessão) | Base para `journey_diff.py` |
| `models/schemas.py` (Pydantic v2) | Padrão para `schemas/release.py` |
| `tests/test_api.py` (TestClient) | Padrão para novos testes |
| Componentes web (`KpiCard`, `FunnelChart`, `CohortMatrix`) | Reuso nas telas de release |
| CI existente (2 jobs) | Estendido com golden scenarios + secret scan |

## 3. O que será criado (não existe em nenhum estado do repo)

- `data/contracts/events.yml` — contratos versionados de tracking
- `scripts/generate_release_fixture.py` — fixtures determinísticas por release
- `data/seed/releases/` — v2.2.0-healthy, v2.3.0-buggy, v2.3.0-fixed
- `apps/api/app/services/instrumentation.py` — validador de instrumentação
- `apps/api/app/services/release_compare.py` — comparação raw vs trusted
- `apps/api/app/services/journey_diff.py` — diff de grafos de jornada
- `apps/api/app/schemas/release.py` — modelos Pydantic de release
- `apps/api/tests/test_instrumentation.py`, `test_release_compare.py`
- `apps/web/app/releases/` + `apps/web/components/release/`
- `apps/web/public/data/release-intelligence.json`
- `docs/RELEASE_INTELLIGENCE_METHOD.md`

## 4. Divergências repo vs PROJECT_CONTEXT_PACK

1. **Colunas ausentes:** o CSV atual não tem `release` nem `insert_id`. O gerador novo emite essas colunas; o loader legado permanece intacto (compatibilidade).
2. **Pack interno inconsistente:** Task 6 ("Uncertainty") aponta `journey_diff.py` como arquivo primário e Task 7 aponta `schemas/release.py`. Resolução: ICs (Wilson) vivem em `release_compare.py`; diff de grafos em `journey_diff.py`. Contratos semânticos do design spec preservados.
3. **CI já existe** no pós-merge (o pack presumia ausência) → estender, não criar.
4. **README do main citava DuckDB** sem dependência real em `requirements.txt` — claim falso removido durante a resolução do merge do PR #1.

## 5. Riscos

| Nível | Risco | Mitigação |
|---|---|---|
| P0 | Golden scenario mal calibrado (buggy release não detectada) | Fixtures com counts esperados asseridos byte-a-byte + mutation sanity |
| P0 | Claim causal indevido em UI/docs | Flag `experiment:false`; testes bloqueiam linguagem causal |
| P1 | Snapshot estático divergir do backend | JSON gerado pelos mesmos services do backend (fonte única) |
| P1 | Regressão no pipeline legado ao tocar loader | Loader novo isolado; suite existente deve continuar verde |
| P2 | Pages desatualizado após merge | Script de regeração documentado + smoke pós-merge |

## 6. Trabalho prévio recuperado

PR #1 (`chore/portfolio-quality-pass`) continha CI, ruff.toml, schemas Pydantic,
componentes web e docs de arquitetura — **mergeado em `5f8dd3c`** após resolução
de conflito de README (mantido template bilíngue PT-BR/EN do main + conteúdo do PR).
Nenhum trabalho foi descartado.
