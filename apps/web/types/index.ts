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
