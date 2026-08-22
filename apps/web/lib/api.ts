import {
  getCohorts,
  getDemoSummary,
  getFriction,
  getFunnel,
  getJourney,
  getOpportunities,
  getSegments,
  getTaxonomy,
} from "@/lib/lab";
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

const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");

/**
 * Prefer optional FastAPI when NEXT_PUBLIC_API_URL is set.
 * Static/Vercel lab demo falls back to the embedded synthetic snapshot.
 */
export async function tryBackend<T>(path: string): Promise<T | null> {
  if (!API_URL) return null;
  try {
    const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function fetchDemo(): Promise<DemoSummary> {
  const remote = await tryBackend<DemoSummary>("/api/demo");
  return remote ?? getDemoSummary();
}

export async function fetchFunnel(): Promise<FunnelStep[]> {
  const remote = await tryBackend<{ steps: FunnelStep[] }>("/api/funnel/activation");
  return remote?.steps ?? getFunnel();
}

export async function fetchJourney(): Promise<JourneyGraph> {
  const remote = await tryBackend<JourneyGraph>("/api/journeys/graph");
  return remote ?? getJourney();
}

export async function fetchSegments(): Promise<Segment[]> {
  const remote = await tryBackend<{ segments: Segment[] }>("/api/segments");
  return remote?.segments ?? getSegments();
}

export async function fetchOpportunities(): Promise<OpportunityMemo> {
  const remote = await tryBackend<OpportunityMemo>("/api/opportunities");
  return remote ?? getOpportunities();
}

export async function fetchTaxonomy(): Promise<TaxonomyEvent[]> {
  const remote = await tryBackend<{ events: TaxonomyEvent[] }>("/api/events/taxonomy");
  return remote?.events ?? getTaxonomy();
}

export async function fetchCohorts(): Promise<Cohort[]> {
  const remote = await tryBackend<{ cohorts: Cohort[] }>("/api/cohorts/retention");
  return remote?.cohorts ?? getCohorts();
}

export async function fetchFriction(): Promise<FrictionPayload> {
  const remote = await tryBackend<FrictionPayload>("/api/friction");
  return remote ?? getFriction();
}
