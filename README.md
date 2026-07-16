<div align="center">
  <img src="./assets/icon.png" alt="BehaviorGraph Logo" width="120" height="120" />

  <h1>BehaviorGraph</h1>

  <p><strong>Estúdio de analytics comportamental — taxonomia, funis, cohorts, jornadas e memos de oportunidade.</strong></p>
  <p><strong>Behavioral analytics studio — taxonomy, funnels, cohorts, journeys and opportunity memos.</strong></p>

  <p>
    <a href="#pt-br">PT-BR</a> ·
    <a href="#en">English</a> ·
    <a href="#live-demo">Live Demo</a> ·
    <a href="#stack--tecnologias">Stack</a> ·
    <a href="#arquitetura--architecture">Architecture</a> ·
    <a href="#quick-start--início-rápido">Quick Start</a> ·
    <a href="#autor--author">Author</a>
  </p>

  <p>
    <a href="https://barujafe1.github.io/BehaviorGraph/"><img alt="Live Demo" src="https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-181717?style=for-the-badge&logo=github&logoColor=white" /></a>
    <img alt="Next.js" src="https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=nextdotjs" />
    <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-React-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
    <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" />
    <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
    <img alt="Lab Demo" src="https://img.shields.io/badge/Status-Lab%20demo-2563EB?style=for-the-badge" />
    <img alt="MIT" src="https://img.shields.io/badge/License-MIT-111827?style=for-the-badge" />
  </p>

  <p>
    <a href="https://barujafe1.github.io/BehaviorGraph/"><strong>Live Demo</strong></a> ·
    <a href="https://github.com/BarujaFe1/BehaviorGraph"><strong>Repositório</strong></a> ·
    <a href="https://barujafe.vercel.app/"><strong>Portfólio</strong></a> ·
    <a href="https://www.linkedin.com/in/barujafe/"><strong>LinkedIn</strong></a>
  </p>
</div>

<p align="center">
  <img src="./assets/hero-cover.png" alt="BehaviorGraph overview" width="100%" />
</p>

---

<a id="pt-br"></a>

## PT-BR

## Visão geral

**BehaviorGraph** conecta taxonomia de eventos, funis de ativação, cohorts de retenção, grafos de jornada e memos de oportunidade de produto em um estúdio analítico de lab.

> **Aviso de lab:** demo de portfólio com dados sintéticos/amostra. Não é produto em produção com SLA, integrações reais de clientes ou garantia operacional.

---

## Problema

Eventos de produto ficam em warehouses sem narrativa: sem taxonomia clara, funil e jornada não conversam com a decisão de produto.

---

## Para quem

- Product analysts e PMs analíticos
- Growth / activation
- Engenheiros de analytics

---

## Funcionalidades

- Taxonomia de eventos
- Funis de ativação
- Cohorts de retenção
- Grafo de jornada (NetworkX)
- Memos de oportunidade
- DuckDB no backend para consultas

---

## Escopo e limites

- **É:** estúdio lab de behavioral analytics.
- **Não é:** Amplitude/Mixpanel clone, CDP, tracking SDK de produção.

---

<a id="en"></a>

## English

## Overview

**BehaviorGraph** connects event taxonomy, activation funnels, retention cohorts, journey graphs and product opportunity memos in one analytics studio lab.

> **Lab notice:** portfolio demo with synthetic/sample data. Not a production product with SLA, real customer integrations, or operational guarantees.

---

## Problem

Product events sit in warehouses without narrative: without clear taxonomy, funnel and journey never meet product decisions.

---

## Who it is for

- Product analysts and analytical PMs
- Growth / activation
- Analytics engineers

---

## Features

- Event taxonomy
- Activation funnels
- Retention cohorts
- Journey graph (NetworkX)
- Opportunity memos
- DuckDB on the backend for queries

---

## Scope and limits

- **Is:** behavioral analytics studio lab.
- **Is not:** Amplitude/Mixpanel clone, CDP, production tracking SDK.

---

<a id="live-demo"></a>

## Live Demo

**URL:** [https://barujafe1.github.io/BehaviorGraph/](https://barujafe1.github.io/BehaviorGraph/)

Demo hospedada para avaliação de portfólio / Hosted for portfolio review.

> Lab demo — synthetic / sample data unless noted. Not a production SLA product.

---

<a id="stack--tecnologias"></a>

## Stack / Tecnologias

| Tecnologia | Uso no projeto |
|---|---|
| Next.js 15 / React 19 / TypeScript | UI + export estático |
| Recharts / Lucide | Charts |
| FastAPI / Pandas / NetworkX / DuckDB | Analytics API |
| Pytest / Ruff | Testes |

---

<a id="arquitetura--architecture"></a>

## Arquitetura / Architecture

Monorepo API + web com seeds/uploads e docs de metodologia/roadmap.

`	xt
BehaviorGraph/
├── apps/
│   ├── api/
│   └── web/
├── assets/
├── data/seed/
├── docs/
├── scripts/
├── start.bat
└── vercel.json
`

---

<a id="quick-start--início-rápido"></a>

## Quick Start / Início rápido

### Pré-requisitos / Requirements

- Node.js 20+
- Python 3.12+
- npm

### Clonar / Clone

`ash
git clone https://github.com/BarujaFe1/BehaviorGraph.git
cd BehaviorGraph
`

### Windows (atalho)

`at
start.bat
`

Sobe API em :8000 e web em :3000.

### Manual

`ash
# API
cd apps/api
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
`

`ash
# Web (outro terminal)
cd apps/web
npm install
npm run dev
`

Abra http://localhost:3000

Copie .env.example se precisar de NEXT_PUBLIC_API_URL.


---

## Technical decisions / Decisões técnicas

- **Taxonomia primeiro** — eventos sem contrato viram ruído.
- **NetworkX** para jornadas explicáveis.
- **Pages demo** para revisão estável de portfólio.

---

## Roadmap

### Implementado
- Taxonomia, funis, cohorts, journey graph, memo, Pages demo

### Planejado
- Mais templates de memo
- Upload de eventos CSV
- Comparação de releases

---

<a id="autor--author"></a>

## Autor / Author

Developed by **Felipe Alirio Baruja**.

- **Portfolio:** [https://barujafe.vercel.app/](https://barujafe.vercel.app/)
- **GitHub:** [github.com/BarujaFe1](https://github.com/BarujaFe1)
- **LinkedIn:** [linkedin.com/in/barujafe](https://www.linkedin.com/in/barujafe/)
- **Repository:** [github.com/BarujaFe1/BehaviorGraph](https://github.com/BarujaFe1/BehaviorGraph)

---

## License / Licença

MIT License.

See [LICENSE](./LICENSE) for details.

---

<div align="center">
  <p><strong>BehaviorGraph</strong></p>
  <p>De eventos brutos a oportunidades de produto.</p>
  <p><em>From raw events to product opportunities.</em></p>
</div>
