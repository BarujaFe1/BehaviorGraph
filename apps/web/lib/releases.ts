import { tryBackend } from "@/lib/api";
import snapshot from "@/lib/release-intelligence.json";
import type { ReleaseIntelligence } from "@/types";

export const RELEASE_INTELLIGENCE_NOTICE =
  "Release intelligence lab on synthetic fixtures. Raw vs trusted metrics are observational — no causal claims without an experiment.";

export async function fetchReleaseIntelligence(): Promise<ReleaseIntelligence> {
  const remote = await tryBackend<ReleaseIntelligence>("/api/releases/overview");
  if (remote) {
    return {
      ...(snapshot as unknown as ReleaseIntelligence),
      ...remote,
      instrumentation: (snapshot as unknown as ReleaseIntelligence).instrumentation,
      journey_diffs: (snapshot as unknown as ReleaseIntelligence).journey_diffs,
      limitations: (snapshot as unknown as ReleaseIntelligence).limitations,
    };
  }
  return snapshot as unknown as ReleaseIntelligence;
}
