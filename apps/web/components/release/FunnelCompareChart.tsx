"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ReleaseFunnelStep } from "@/types";

export function FunnelCompareChart({
  raw,
  trusted,
}: {
  raw: ReleaseFunnelStep[];
  trusted: ReleaseFunnelStep[];
}) {
  const data = raw.map((step, index) => ({
    step: step.step,
    Raw: step.users,
    Trusted: trusted[index]?.users ?? 0,
  }));

  return (
    <div style={{ width: "100%", height: 280 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="step"
            tick={{ fontSize: 11 }}
            interval={0}
            angle={-18}
            textAnchor="end"
            height={60}
          />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Legend />
          <Bar dataKey="Raw" fill="#94a3b8" radius={[3, 3, 0, 0]} />
          <Bar dataKey="Trusted" fill="#2563eb" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
