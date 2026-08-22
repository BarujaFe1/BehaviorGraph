import type {
  Cohort,
  DemoSummary,
  FrictionPayload,
  FunnelStep,
  JourneyGraph,
  OpportunityMemo,
  Segment,
  TaxonomyEvent,
} from "@/types";
import snapshot from "@/lib/demo-snapshot.json";

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
  return (snapshot.funnel as { steps: FunnelStep[]; method?: string }).steps;
}

export function getFunnelMethod(): string {
  return (snapshot.funnel as { method?: string }).method ?? "nested_unique_users";
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
