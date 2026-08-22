# Security Notes — BehaviorGraph

## Scope
Portfolio lab demo. Synthetic SaaS onboarding events only. No production user tracking.

## Findings (quality pass)

### Local Vercel OIDC token (handled)
- **Location:** `apps/web/.env.local` (developer machine only)
- **Content type:** Vercel CLI OIDC token for local project linking
- **Git status:** Ignored by `apps/web/.gitignore` (`.env.local`) and root `.gitignore`
- **Action taken:** Confirmed not tracked by git. Do not commit. Rotate via Vercel if the token was ever pasted into chat/logs.
- **Do not republish** the token value in issues, PRs, or docs.

### Secrets policy
- Never commit `.env`, `.env.local`, service role keys, or Supabase credentials.
- Use `.env.example` templates only.
- Demo data under `data/seed/` is synthetic and safe to publish.

### Responsible analytics
- The product must not claim causal attribution from journey graphs.
- Activation/retention metrics are exploratory on synthetic data.
- No PII is present in the seed CSVs (`user_XXXX` ids only).
