export type DemoSummary = {
  product: string;
  dataset: string;
  users: number;
  events: number;
  sessions: number;
  activated_users: number;
  activation_rate: number;
  notice: string;
};

export type FunnelStep = {
  step: string;
  users: number;
  conversion_from_previous: number;
  conversion_from_start?: number;
};

export type JourneyGraph = {
  nodes: { id: string; label: string }[];
  edges: { source: string; target: string; weight: number }[];
  engine?: string;
};

export type Segment = {
  id: string;
  name: string;
  users: number;
  definition: string;
};

export type OpportunityMemo = {
  headline: string;
  summary: DemoSummary;
  opportunities: {
    title: string;
    why: string;
    suggested_action: string;
    impact_hypothesis: string;
  }[];
  limitations: string[];
};

export type TaxonomyEvent = {
  event_name: string;
  category: string;
  description: string;
  owner: string;
};

export type CohortWeek = {
  week_offset: number;
  week: string;
  retained_users: number;
  retention_rate: number;
};

export type Cohort = {
  cohort_week: string;
  cohort_size: number;
  weeks: CohortWeek[];
};

export type FrictionDrop = {
  from_step: string;
  to_step: string;
  drop_users: number;
  drop_rate: number;
  severity: "low" | "medium" | "high" | string;
};

export type FrictionPayload = {
  funnel_drops: FrictionDrop[];
  error_signals: { event_name: string; affected_users: number }[];
};

export type ReleaseFunnelStep = {
  step: string;
  users: number;
  conversion_from_start: number;
  unique_user_basis: boolean;
};

export type ReleaseVerdict = {
  classification:
    | "baseline"
    | "instrumentation_artifact"
    | "real_improvement"
    | string;
  raw_looks_better: boolean;
  survives_trusted_filter: boolean;
  gain_step: string | null;
  raw_gain_pct: number;
  trusted_gain_pct: number;
};

export type InstrumentationViolation = {
  event_name: string;
  code: string;
  severity: "block" | "warning" | string;
  user_count: number;
  evidence_count: number;
};

export type ReleaseInstrumentation = {
  release: string;
  total_events: number;
  trusted_events: number;
  status: "pass" | "warn" | "block" | string;
  unknown_events: string[];
  violations: InstrumentationViolation[];
};

export type ReleaseOverviewEntry = {
  release: string;
  total_events: number;
  trusted_events: number;
  activation_raw_rate: number;
  activation_trusted_rate: number;
  activation_trusted_ci: [number, number];
  instrumentation_status: string;
  verdict: ReleaseVerdict;
  raw_funnel: ReleaseFunnelStep[];
  trusted_funnel: ReleaseFunnelStep[];
};

export type JourneyEdgeDiff = {
  source: string;
  target: string;
  target_weight?: number | null;
  baseline_weight?: number | null;
};

export type JourneyDiff = {
  baseline: string;
  target: string;
  min_support: number;
  baseline_edges: string[][];
  added: JourneyEdgeDiff[];
  removed: JourneyEdgeDiff[];
  notice: string;
};

export type ReleaseIntelligence = {
  method: string;
  baseline: string;
  observational_notice: string;
  releases: ReleaseOverviewEntry[];
  instrumentation: Record<string, ReleaseInstrumentation>;
  journey_diffs: Record<string, JourneyDiff>;
  limitations: string[];
};
