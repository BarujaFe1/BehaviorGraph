"use client";

import { useEffect, useState, useTransition } from "react";
import {
  fetchCohorts,
  fetchDemo,
  fetchFriction,
  fetchFunnel,
  fetchJourney,
  fetchOpportunities,
  fetchSegments,
  fetchTaxonomy,
} from "@/lib/api";
import type { Cohort, FrictionPayload, TaxonomyEvent } from "@/lib/lab";
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
  const [taxonomy, setTaxonomy] = useState<TaxonomyEvent[]>([]);
  const [cohorts, setCohorts] = useState<Cohort[]>([]);
  const [friction, setFriction] = useState<FrictionPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  useEffect(() => {
    startTransition(async () => {
      try {
        const [d, f, j, s, o, t, c, fr] = await Promise.all([
          fetchDemo(),
          fetchFunnel(),
          fetchJourney(),
          fetchSegments(),
          fetchOpportunities(),
          fetchTaxonomy(),
          fetchCohorts(),
          fetchFriction(),
        ]);
        setDemo(d);
        setFunnel(f);
        setJourney(j);
        setSegments(s);
        setMemo(o);
        setTaxonomy(t);
        setCohorts(c);
        setFriction(fr);
      } catch (e) {
        setError(
          e instanceof Error ? e.message : "Failed to load BehaviorGraph lab",
        );
      }
    });
  }, []);

  const maxFunnel = Math.max(...funnel.map((step) => step.users), 1);

  return (
    <main>
      <section className="hero">
        <p className="muted">Portfolio lab · synthetic events · responsible analytics</p>
        <h1 className="brand">BehaviorGraph</h1>
        <p className="lede">
          MVP lab that turns product events into taxonomy, activation funnel,
          retention cohorts, journey graph and an opportunity memo — answering
          which paths lead to activation, abandonment or recurring use.
        </p>
        <p className="lede" style={{ marginTop: 10 }}>
          {demo?.notice}
        </p>
      </section>

      {error ? <div className="error">{error}</div> : null}
      {pending && !demo ? <p className="muted">Loading lab snapshot…</p> : null}

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
          <h2>Event taxonomy</h2>
          <ul className="list">
            {taxonomy.slice(0, 8).map((ev) => (
              <li key={ev.event_name}>
                <strong>{ev.event_name}</strong>{" "}
                <span className="tag">{ev.category}</span>
                <br />
                {ev.description} · owner: {ev.owner}
              </li>
            ))}
          </ul>
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
          <h2>Retention cohorts</h2>
          <ul className="list">
            {cohorts.slice(0, 5).map((c) => {
              const w1 = c.weeks.find((w) => w.week_offset === 1);
              return (
                <li key={c.cohort_week}>
                  <strong>{c.cohort_week}</strong> — size {c.cohort_size}
                  {w1
                    ? ` · W1 retention ${Math.round(w1.retention_rate * 100)}%`
                    : ""}
                </li>
              );
            })}
          </ul>
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
            Top session transitions · {journey?.edges.length ?? 0} edges · engine{" "}
            {journey?.engine ?? "snapshot"}
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
          <h2>Friction radar</h2>
          <ul className="list">
            {(friction?.funnel_drops ?? []).map((d) => (
              <li key={`${d.from_step}-${d.to_step}`}>
                <strong>
                  {d.from_step} → {d.to_step}
                </strong>
                <br />
                drop {Math.round(d.drop_rate * 100)}% · severity {d.severity}
              </li>
            ))}
          </ul>
        </article>

        <article className="card span-12">
          <h2>Product opportunity memo</h2>
          <ul className="list">
            {(memo?.opportunities ?? []).map((o) => (
              <li key={o.title}>
                <strong>{o.title}</strong>
                <br />
                {o.why}
                <br />
                Action: {o.suggested_action}
              </li>
            ))}
          </ul>
          <h2 style={{ marginTop: 18 }}>Limitations</h2>
          <ul className="list">
            {(memo?.limitations ?? []).map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
        </article>
      </section>
    </main>
  );
}
