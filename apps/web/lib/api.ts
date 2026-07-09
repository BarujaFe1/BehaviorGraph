import type {
  DemoSummary,
  FunnelStep,
  JourneyGraph,
  OpportunityMemo,
  Segment,
} from "@/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function fetchDemo() {
  return getJson<DemoSummary>("/api/demo");
}

export async function fetchFunnel() {
  const data = await getJson<{ funnel: string; steps: FunnelStep[] }>(
    "/api/funnel/activation",
  );
  return data.steps;
}

export function fetchJourney() {
  return getJson<JourneyGraph>("/api/journeys/graph");
}

export async function fetchSegments() {
  const data = await getJson<{ segments: Segment[] }>("/api/segments");
  return data.segments;
}

export function fetchOpportunities() {
  return getJson<OpportunityMemo>("/api/opportunities");
}
