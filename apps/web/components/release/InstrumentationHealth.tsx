"use client";

import type { ReleaseInstrumentation } from "@/types";

const SEVERITY_LABEL: Record<string, string> = {
  block: "BLOCK",
  warning: "warning",
};

export function InstrumentationHealth({
  report,
}: {
  report: ReleaseInstrumentation;
}) {
  const statusTone =
    report.status === "pass"
      ? "#16a34a"
      : report.status === "warn"
        ? "#d97706"
        : "#dc2626";

  return (
    <article className="card span-6">
      <h2>Instrumentation health</h2>
      <p className="section-copy">
        Every event stream is checked against the versioned tracking contract
        (<code>data/contracts/events.yml</code>): required properties, sequence
        constraints, insert_id uniqueness and cardinality.
      </p>
      <p>
        <span
          className="tag"
          style={{
            color: "#fff",
            background: statusTone,
            fontWeight: 700,
          }}
        >
          {report.status.toUpperCase()}
        </span>{" "}
        {report.trusted_events.toLocaleString()} of{" "}
        {report.total_events.toLocaleString()} events survive the trusted filter.
      </p>

      {report.violations.length ? (
        <ul className="list compact">
          {report.violations.map((v) => (
            <li key={`${v.code}-${v.event_name}`}>
              <span
                className="tag"
                style={{
                  color: v.severity === "block" ? "#fff" : undefined,
                  background: v.severity === "block" ? "#dc2626" : undefined,
                  fontWeight: 700,
                }}
              >
                {SEVERITY_LABEL[v.severity] ?? v.severity}
              </span>{" "}
              <strong>{v.code}</strong> on <code>{v.event_name}</code> —{" "}
              {v.evidence_count} events · {v.user_count} users
            </li>
          ))}
        </ul>
      ) : (
        <p className="empty">No violations — every contract check passed.</p>
      )}

      {report.unknown_events.length ? (
        <p className="notice">
          Unknown events observed (reported, never silently dropped):{" "}
          {report.unknown_events.join(", ")}. They stay in raw data and are
          excluded from contract-gated metrics.
        </p>
      ) : null}
    </article>
  );
}
