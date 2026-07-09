"use client";

import { useEffect, useState, useTransition } from "react";
import {
  fetchDemo,
  fetchFunnel,
  fetchJourney,
  fetchOpportunities,
  fetchSegments,
} from "@/lib/api";
import type {
  DemoSummary,
  FunnelStep,
  JourneyGraph,
  OpportunityMemo,
  Segment,
} from "@/types";

export default function HomePage() {
  const [demo, setDemo] = useState<DemoSummary | null>(null);
  const [funnel, setFunnel] = useState<FunnelStep[]>([]);
  const [journey, setJourney] = useState<JourneyGraph | null>(null);
  const [segments, setSegments] = useState<Segment[]>([]);
  const [memo, setMemo] = useState<OpportunityMemo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  useEffect(() => {
    startTransition(async () => {
      try {
        const [d, f, j, s, o] = await Promise.all([
          fetchDemo(),
          fetchFunnel(),
          fetchJourney(),
          fetchSegments(),
          fetchOpportunities(),
        ]);
        setDemo(d);
        setFunnel(f);
        setJourney(j);
        setSegments(s);
        setMemo(o);
      } catch (e) {
        setError(
          e instanceof Error ? e.message : "Failed to load BehaviorGraph API",
        );
      }
    });
  }, []);

  const maxFunnel = Math.max(...funnel.map((s) => s.users), 1);

  return (
    <main>
      <section className="hero">
        <p className="muted">Event taxonomy · journeys · cohorts · friction</p>
        <h1 className="brand">BehaviorGraph</h1>
        <p className="lede">
          Transforma eventos de uso em jornadas, funis de ativação, cohorts de
          retenção, segmentos e sinais de fricção — para responder quais caminhos
          levam à ativação, abandono ou uso recorrente.
        </p>
      </section>

      {error ? <div className="error">{error}</div> : null}
      {pending && !demo ? <p className="muted">Loading demo analytics…</p> : null}

      <section className="grid">
        <article className="card span-3">
          <p className="muted">Users</p>
          <div className="kpi">{demo?.users ?? "—"}</div>
        </article>
        <article className="card span-3">
          <p className="muted">Events</p>
          <div className="kpi">{demo?.events ?? "—"}</div>
        </article>
        <article className="card span-3">
          <p className="muted">Sessions</p>
          <div className="kpi">{demo?.sessions ?? "—"}</div>
        </article>
        <article className="card span-3">
          <p className="muted">Activation rate</p>
          <div className="kpi">
            {demo ? `${Math.round(demo.activation_rate * 100)}%` : "—"}
          </div>
        </article>

        <article className="card span-6">
          <h2>Activation funnel</h2>
          {funnel.map((step) => (
            <div className="bar-row" key={step.step}>
              <span>{step.step}</span>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${(step.users / maxFunnel) * 100}%` }}
                />
              </div>
              <strong>{step.users}</strong>
            </div>
          ))}
        </article>

        <article className="card span-6">
          <h2>Segments</h2>
          <ul className="list">
            {segments.map((s) => (
              <li key={s.id}>
                <strong>{s.name}</strong> — {s.users} users · {s.definition}
              </li>
            ))}
          </ul>
        </article>

        <article className="card span-8">
          <h2>Journey path graph</h2>
          <p className="muted" style={{ marginBottom: 12 }}>
            Top transitions (NetworkX) · {journey?.edges.length ?? 0} edges
          </p>
          <ul className="list">
            {(journey?.edges ?? []).slice(0, 12).map((e) => (
              <li key={`${e.source}-${e.target}`}>
                {e.source} → {e.target}{" "}
                <span className="tag">w={e.weight}</span>
              </li>
            ))}
          </ul>
        </article>

        <article className="card span-4">
          <h2>Opportunity memo</h2>
          <ul className="list">
            {(memo?.opportunities ?? []).map((o) => (
              <li key={o.title}>
                <strong>{o.title}</strong>
                <br />
                {o.why}
              </li>
            ))}
          </ul>
        </article>

        <article className="card span-12">
          <h2>Limitations</h2>
          <p className="lede" style={{ margin: 0 }}>
            {demo?.notice ??
              "Synthetic demo only. MVP does not ship production tracking."}
          </p>
          <ul className="list" style={{ marginTop: 12 }}>
            {(memo?.limitations ?? []).map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
        </article>
      </section>
    </main>
  );
}
