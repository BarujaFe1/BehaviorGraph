"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { FunnelStep } from "@/types";

function shortLabel(step: string) {
  return step.replaceAll("_", " ");
}

export function FunnelChart({ steps }: { steps: FunnelStep[] }) {
  const data = steps.map((s) => ({
    name: shortLabel(s.step),
    users: s.users,
    conv: Math.round(s.conversion_from_previous * 100),
  }));

  if (!data.length) {
    return <p className="empty">No funnel steps available.</p>;
  }

  return (
    <div className="chart-wrap" role="img" aria-label="Activation funnel bar chart">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 48 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#243047" vertical={false} />
          <XAxis
            dataKey="name"
            tick={{ fill: "#9db0d0", fontSize: 11 }}
            interval={0}
            angle={-25}
            textAnchor="end"
            height={60}
          />
          <YAxis tick={{ fill: "#9db0d0", fontSize: 12 }} width={40} />
          <Tooltip
            contentStyle={{
              background: "#121a2b",
              border: "1px solid #243047",
              borderRadius: 12,
              color: "#e8eefc",
            }}
            formatter={(value, name) =>
              name === "users"
                ? [value as number, "Users"]
                : [`${value}%`, "Conv. from previous"]
            }
          />
          <Bar dataKey="users" fill="#5eead4" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
