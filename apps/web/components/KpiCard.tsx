type Props = {
  label: string;
  value: string | number;
  hint?: string;
};

export function KpiCard({ label, value, hint }: Props) {
  return (
    <article className="card span-3 kpi-card">
      <p className="muted">{label}</p>
      <div className="kpi" aria-live="polite">
        {value}
      </div>
      {hint ? <p className="hint">{hint}</p> : null}
    </article>
  );
}
