"use client";

import type { ReleaseOverviewEntry } from "@/types";

const CLASSIFICATION_COPY: Record<string, { label: string; tone: string }> = {
  baseline: {
    label: "Baseline — contracts pass",
    tone: "var(--ok, #16a34a)",
  },
  instrumentation_artifact: {
    label: "Instrumentation artifact, not product",
    tone: "#dc2626",
  },
  real_improvement: {
    label: "Real improvement — survives trusted filter",
    tone: "#16a34a",
  },
};

export function VerdictBanner({ entry }: { entry: ReleaseOverviewEntry }) {
  const verdict = entry.verdict;
  const copy =
    CLASSIFICATION_COPY[verdict.classification] ??
    CLASSIFICATION_COPY.baseline;

  return (
    <div
      className="card"
      role="status"
      style={{ borderColor: copy.tone, borderWidth: 2 }}
    >
      <p className="section-copy" style={{ marginBottom: 4 }}>
        <strong>{entry.release}</strong> vs baseline
      </p>
      <h2 style={{ color: copy.tone }}>{copy.label}</h2>
      <div className="grid" style={{ marginTop: 12 }}>
        <div className="card span-6">
          <p className="section-copy">Raw dashboard says</p>
          <div className="kpi">
            {verdict.gain_step ? `${verdict.raw_gain_pct > 0 ? "+" : ""}${verdict.raw_gain_pct}%` : "—"}
          </div>
          <p className="hint">
            {verdict.gain_step
              ? `gain on ${verdict.gain_step} (unique users)`
              : "no step stands out"}
          </p>
        </div>
        <div className="card span-6">
          <p className="section-copy">Trusted metrics say</p>
          <div className="kpi">
            {verdict.gain_step
              ? `${verdict.trusted_gain_pct > 0 ? "+" : ""}${verdict.trusted_gain_pct}%`
              : "—"}
          </div>
          <p className="hint">
            after removing contract-invalid events (dedup, order, props)
          </p>
        </div>
      </div>
      {!verdict.survives_trusted_filter && verdict.raw_looks_better ? (
        <p className="notice" style={{ marginTop: 8 }}>
          The apparent gain disappears once tracking contracts are enforced:
          the release shipped broken instrumentation, not a better product.
        </p>
      ) : null}
      {verdict.survives_trusted_filter ? (
        <p className="notice" style={{ marginTop: 8 }}>
          The gain survives the trusted filter with valid instrumentation —
          consistent with real behavior change (observational, not causal).
        </p>
      ) : null}
    </div>
  );
}
