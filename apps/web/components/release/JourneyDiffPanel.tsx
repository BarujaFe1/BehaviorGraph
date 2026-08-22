"use client";

import type { JourneyDiff } from "@/types";

export function JourneyDiffPanel({ diff }: { diff: JourneyDiff }) {
  return (
    <article className="card span-6">
      <h2>Journey diff vs baseline</h2>
      <p className="section-copy">
        Session-transition edges with support ≥ {diff.min_support} that appear or
        vanish in <strong>{diff.target}</strong> compared to{" "}
        <strong>{diff.baseline}</strong>.
      </p>

      {diff.added.length ? (
        <>
          <p className="section-copy">Added edges</p>
          <ul className="list compact">
            {diff.added.map((edge) => (
              <li key={`added-${edge.source}-${edge.target}`}>
                <span className="tag" style={{ color: "#fff", background: "#dc2626", fontWeight: 700 }}>
                  new
                </span>{" "}
                <code>
                  {edge.source} → {edge.target}
                </code>{" "}
                ({edge.target_weight ?? 0} sessions)
              </li>
            ))}
          </ul>
        </>
      ) : (
        <p className="empty">No new edges above support threshold.</p>
      )}

      {diff.removed.length ? (
        <>
          <p className="section-copy">Removed edges</p>
          <ul className="list compact">
            {diff.removed.map((edge) => (
              <li key={`removed-${edge.source}-${edge.target}`}>
                <span className="tag" style={{ fontWeight: 700 }}>
                  gone
                </span>{" "}
                <code>
                  {edge.source} → {edge.target}
                </code>{" "}
                (was {edge.baseline_weight ?? 0} sessions)
              </li>
            ))}
          </ul>
        </>
      ) : null}

      <p className="notice">{diff.notice}</p>
    </article>
  );
}
