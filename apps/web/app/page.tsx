"use client";

import { useEffect, useState, useTransition } from "react";
import { CohortMatrix } from "@/components/CohortMatrix";
import { FunnelChart } from "@/components/FunnelChart";
import { KpiCard } from "@/components/KpiCard";
import { SkeletonGrid } from "@/components/SkeletonGrid";
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
import type {
  Cohort,
  DemoSummary,
  FrictionPayload,
  FunnelStep,
  JourneyGraph,
  OpportunityMemo,
  Segment,
  TaxonomyEvent,
} from "@/types";

const NAV = [
  { id: "overview", label: "Overview" },
  { id: "taxonomy", label: "Taxonomy" },
  { id: "funnel", label: "Funnel" },
  { id: "cohorts", label: "Cohorts" },
  { id: "journey", label: "Journey" },
  { id: "friction", label: "Friction" },
  { id: "memo", label: "Memo" },
] as const;

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

  const topDrop = friction?.funnel_drops.reduce(
    (best, d) => (!best || d.drop_rate > best.drop_rate ? d : best),
    null as (typeof friction.funnel_drops)[number] | null,
  );

  return (
    <main>
      <a className="skip-link" href="#overview">
        Skip to content
      </a>

      <header className="hero" id="overview">
        <p className="muted">Portfolio lab · synthetic events · responsible analytics</p>
        <h1 className="brand">BehaviorGraph</h1>
        <p className="lede">
          Turns product events into taxonomy, nested activation funnel, retention
          cohorts, journey graph and an opportunity memo — answering which paths
          lead to activation, abandonment or recurring use.
        </p>
        <div className="badge-row" role="list">
          <span className="badge" role="listitem">
            Synthetic seed
          </span>
          <span className="badge" role="listitem">
            Nested unique-user funnel
          </span>
          <span className="badge" role="listitem">
            No causal overclaim
          </span>
        </div>
        <p className="notice">{demo?.notice}</p>
      </header>

      <nav className="toc" aria-label="Lab sections">
        {NAV.map((item) => (
          <a key={item.id} href={`#${item.id}`}>
            {item.label}
          </a>
        ))}
      </nav>

      {error ? (
        <div className="error" role="alert">
          {error}
        </div>
      ) : null}

      {pending && !demo ? <SkeletonGrid /> : null}

      {demo ? (
        <section className="grid" aria-label="Key metrics">
          <KpiCard label="Users" value={demo.users} hint="Unique user_ids" />
          <KpiCard label="Events" value={demo.events} hint="Synthetic stream" />
          <KpiCard label="Sessions" value={demo.sessions} hint="Session groups" />
          <KpiCard
            label="Activation rate"
            value={`${Math.round(demo.activation_rate * 100)}%`}
            hint={`${demo.activated_users} activated`}
          />
        </section>
      ) : null}

      <section className="grid" style={{ marginTop: 16 }}>
        <article className="card span-6" id="taxonomy">
          <h2>Event taxonomy</h2>
          <p className="section-copy">
            Owned event contract — category, description and owner before volume.
          </p>
          {taxonomy.length ? (
            <ul className="list">
              {taxonomy.map((ev) => (
                <li key={ev.event_name}>
                  <strong>{ev.event_name}</strong>{" "}
                  <span className="tag">{ev.category}</span>
                  <br />
                  {ev.description} · owner: {ev.owner}
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty">Taxonomy not loaded.</p>
          )}
        </article>

        <article className="card span-6" id="funnel">
          <h2>Activation funnel</h2>
          <p className="section-copy">
            Nested unique users (must remain in the previous step set). Method is
            explicit — not raw event counts.
          </p>
          <FunnelChart steps={funnel} />
          <ul className="list compact">
            {funnel.map((step) => (
              <li key={step.step}>
                <strong>{step.step}</strong> — {step.users} users ·{" "}
                {Math.round(step.conversion_from_previous * 100)}% from previous
                {typeof step.conversion_from_start === "number"
                  ? ` · ${Math.round(step.conversion_from_start * 100)}% from start`
                  : ""}
              </li>
            ))}
          </ul>
        </article>

        <article className="card span-6" id="cohorts">
          <h2>Retention cohorts</h2>
          <p className="section-copy">
            First-seen week cohorts with true week offsets (W0–W4).
          </p>
          <CohortMatrix cohorts={cohorts} />
        </article>

        <article className="card span-6" id="segments">
          <h2>Segments</h2>
          <p className="section-copy">
            Lightweight behavioral slices for product conversation — not ML scoring.
          </p>
          <ul className="list">
            {segments.map((s) => (
              <li key={s.id}>
                <strong>{s.name}</strong> — {s.users} users
                <br />
                {s.definition}
              </li>
            ))}
          </ul>
        </article>

        <article className="card span-8" id="journey">
          <h2>Journey path graph</h2>
          <p className="section-copy">
            Top session transitions via NetworkX. Exploratory map — not Markov
            attribution or causal path proof.
          </p>
          <p className="muted" style={{ marginBottom: 12, textTransform: "none" }}>
            {journey?.edges.length ?? 0} edges · engine {journey?.engine ?? "snapshot"}
          </p>
          <ul className="list">
            {(journey?.edges ?? []).slice(0, 12).map((e) => (
              <li key={`${e.source}-${e.target}`}>
                {e.source} → {e.target} <span className="tag">w={e.weight}</span>
              </li>
            ))}
          </ul>
        </article>

        <article className="card span-4" id="friction">
          <h2>Friction radar</h2>
          <p className="section-copy">
            Drop severity on the nested funnel plus error-like signals.
          </p>
          {topDrop ? (
            <p className="callout">
              Largest drop: <strong>{topDrop.from_step}</strong> →{" "}
              <strong>{topDrop.to_step}</strong> (
              {Math.round(topDrop.drop_rate * 100)}%, {topDrop.severity})
            </p>
          ) : null}
          <ul className="list">
            {(friction?.funnel_drops ?? []).map((d) => (
              <li key={`${d.from_step}-${d.to_step}`}>
                <strong>
                  {d.from_step} → {d.to_step}
                </strong>
                <br />
                drop {Math.round(d.drop_rate * 100)}% ·{" "}
                <span className={`sev sev-${d.severity}`}>{d.severity}</span>
              </li>
            ))}
          </ul>
          {(friction?.error_signals?.length ?? 0) > 0 ? (
            <>
              <h3 className="subhead">Error-like signals</h3>
              <ul className="list">
                {friction!.error_signals.map((s) => (
                  <li key={s.event_name}>
                    {s.event_name}: {s.affected_users} users
                  </li>
                ))}
              </ul>
            </>
          ) : null}
        </article>

        <article className="card span-12" id="memo">
          <h2>Product opportunity memo</h2>
          <p className="section-copy">
            Hypotheses tied to observed drops — with explicit analytical limits.
          </p>
          <div className="memo-grid">
            {(memo?.opportunities ?? []).map((o) => (
              <div key={o.title} className="memo-card">
                <h3>{o.title}</h3>
                <p>{o.why}</p>
                <p>
                  <strong>Action:</strong> {o.suggested_action}
                </p>
                <p className="hint">{o.impact_hypothesis}</p>
              </div>
            ))}
          </div>
          <h3 className="subhead">Limitations</h3>
          <ul className="list">
            {(memo?.limitations ?? []).map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
        </article>
      </section>

      <footer className="footer">
        <p>
          BehaviorGraph · portfolio lab by Felipe Alirio Baruja ·{" "}
          <a href="https://github.com/BarujaFe1/BehaviorGraph">GitHub</a>
        </p>
      </footer>
    </main>
  );
}
