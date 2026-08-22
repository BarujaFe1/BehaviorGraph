"use client";

import type { Cohort } from "@/types";

export function CohortMatrix({ cohorts }: { cohorts: Cohort[] }) {
  if (!cohorts.length) {
    return <p className="empty">No cohorts in the demo window.</p>;
  }

  const offsets = cohorts[0]?.weeks.map((w) => w.week_offset) ?? [];

  return (
    <div className="table-wrap" role="region" aria-label="Retention cohort matrix">
      <table className="matrix">
        <thead>
          <tr>
            <th scope="col">Cohort</th>
            <th scope="col">Size</th>
            {offsets.map((o) => (
              <th key={o} scope="col">
                W{o}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {cohorts.slice(0, 6).map((c) => (
            <tr key={c.cohort_week}>
              <th scope="row">{c.cohort_week}</th>
              <td>{c.cohort_size}</td>
              {c.weeks.map((w) => {
                const pct = Math.round(w.retention_rate * 100);
                const intensity = Math.min(100, pct);
                return (
                  <td key={w.week_offset}>
                    <span
                      className="heat"
                      style={{
                        background: `rgba(94, 234, 212, ${0.12 + intensity / 140})`,
                      }}
                      title={`${w.retained_users} users`}
                    >
                      {pct}%
                    </span>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
