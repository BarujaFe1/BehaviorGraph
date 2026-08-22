"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { FunnelCompareChart } from "@/components/release/FunnelCompareChart";
import { InstrumentationHealth } from "@/components/release/InstrumentationHealth";
import { JourneyDiffPanel } from "@/components/release/JourneyDiffPanel";
import { VerdictBanner } from "@/components/release/VerdictBanner";
import { SkeletonGrid } from "@/components/SkeletonGrid";
import {
  RELEASE_INTELLIGENCE_NOTICE,
  fetchReleaseIntelligence,
} from "@/lib/releases";
import type { ReleaseIntelligence } from "@/types";

const DEFAULT_RELEASE = "v2.3.0-buggy";

export default function ReleasesPage() {
  const [data, setData] = useState<ReleaseIntelligence | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string>(DEFAULT_RELEASE);

  useEffect(() => {
    let active = true;
    fetchReleaseIntelligence()
      .then((payload) => {
        if (active) setData(payload);
      })
      .catch((e: unknown) => {
        if (active) {
          setError(
            e instanceof Error
              ? e.message
              : "Failed to load release intelligence snapshot",
          );
        }
      });
    return () => {
      active = false;
    };
  }, []);

  const entry = data?.releases.find((r) => r.release === selected) ?? null;
  const report = data?.instrumentation[selected] ?? null;
  const diff = data?.journey_diffs[selected] ?? null;

  return (
    <main>
      <header>
        <h1>Release Intelligence</h1>
        <p className="section-copy">
          Tracking contracts gate every comparison. When a release &quot;improves&quot;
          the funnel, this lab proves whether the gain is real product behavior or
          broken instrumentation.
        </p>
        <div className="badge-row">
          <span className="badge">Synthetic fixtures</span>
          <span className="badge">Unique-user metrics</span>
          <span className="badge">Observational only</span>
        </div>
        <p className="notice">{RELEASE_INTELLIGENCE_NOTICE}</p>
        <p className="hint">
          <Link href="/">← Back to BehaviorGraph cockpit</Link>
        </p>
      </header>

      {error ? (
        <div className="error" role="alert">
          {error}
        </div>
      ) : null}

      {!data && !error ? <SkeletonGrid /> : null}

      {data ? (
        <>
          <nav className="toc" aria-label="Releases">
            {data.releases.map((release) => (
              <button
                key={release.release}
                type="button"
                onClick={() => setSelected(release.release)}
                style={{
                  fontWeight: release.release === selected ? 700 : 400,
                  textDecoration: release.release === selected ? "underline" : "none",
                }}
              >
                {release.release}
                {release.instrumentation_status === "block" ? " ⛔" : ""}
              </button>
            ))}
          </nav>

          {entry ? <VerdictBanner entry={entry} /> : null}

          <section className="grid" style={{ marginTop: 16 }}>
            <article className="card span-6">
              <h2>Funnel compare — raw vs trusted</h2>
              <p className="section-copy">
                Unique users per activation step. Raw counts everything ingested;
                trusted removes contract-invalid events first.
              </p>
              {entry ? (
                <>
                  <FunnelCompareChart
                    raw={entry.raw_funnel}
                    trusted={entry.trusted_funnel}
                  />
                  <ul className="list compact">
                    {entry.trusted_funnel.map((step) => (
                      <li key={step.step}>
                        <strong>{step.step}</strong> — trusted {step.users} users ·{" "}
                        {Math.round(step.conversion_from_start * 100)}% of starters
                      </li>
                    ))}
                  </ul>
                  <p className="notice">
                    Trusted activation rate {Math.round(entry.activation_trusted_rate * 100)}% (95% CI{" "}
                    {Math.round(entry.activation_trusted_ci[0] * 100)}–
                    {Math.round(entry.activation_trusted_ci[1] * 100)}%) · observational,
                    not causal.
                  </p>
                </>
              ) : (
                <p className="empty">Select a release.</p>
              )}
            </article>

            {report ? <InstrumentationHealth report={report} /> : null}

            {diff ? <JourneyDiffPanel diff={diff} /> : null}

            <article className="card span-6">
              <h2>Method and limits</h2>
              <ul className="list compact">
                {(data?.limitations ?? []).map((limitation) => (
                  <li key={limitation}>{limitation}</li>
                ))}
              </ul>
              <p className="hint">
                Snapshot pre-computed by the FastAPI services — same code path
                as the API, regenerated by <code>scripts/generate_release_snapshot.py</code>.
              </p>
            </article>
          </section>
        </>
      ) : null}
    </main>
  );
}
