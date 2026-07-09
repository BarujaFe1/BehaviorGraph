import type {
  DemoSummary,
  FunnelStep,
  JourneyGraph,
  OpportunityMemo,
  Segment,
} from "@/types";
import snapshot from "@/lib/demo-snapshot.json";

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
  severity: string;
};

export type FrictionPayload = {
  funnel_drops: FrictionDrop[];
  error_signals: { event_name: string; affected_users: number }[];
};

export const LAB_NOTICE =
  "Portfolio lab demo on synthetic SaaS onboarding events. Not production tracking, not Mixpanel, and not causal attribution.";

export function getDemoSummary(): DemoSummary {
  return {
    ...(snapshot.summary as DemoSummary),
    notice: LAB_NOTICE,
  };
}

export function getTaxonomy(): TaxonomyEvent[] {
  return (snapshot.taxonomy as { events: TaxonomyEvent[] }).events;
}

export function getFunnel(): FunnelStep[] {
  return (snapshot.funnel as { steps: FunnelStep[] }).steps;
}

export function getCohorts(): Cohort[] {
  return (snapshot.cohorts as { cohorts: Cohort[] }).cohorts;
}

export function getJourney(): JourneyGraph {
  return snapshot.journey as JourneyGraph;
}

export function getSegments(): Segment[] {
  return (snapshot.segments as { segments: Segment[] }).segments;
}

export function getFriction(): FrictionPayload {
  return snapshot.friction as FrictionPayload;
}

export function getOpportunities(): OpportunityMemo {
  const memo = snapshot.opportunities as OpportunityMemo;
  return {
    ...memo,
    summary: getDemoSummary(),
    limitations: [
      ...(memo.limitations ?? []),
      "Frontend lab snapshot — FastAPI remains available for local full-stack runs.",
    ],
  };
}
