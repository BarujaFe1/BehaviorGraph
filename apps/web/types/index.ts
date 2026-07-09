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
