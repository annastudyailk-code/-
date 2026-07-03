---
name: sales-pipedrive
description: "Pipedrive (pipedrive.com) platform help — pipeline-first sales CRM with deals, leads, persons/organizations, activities, automation, and reporting. Mature REST API v1+v2 (base {company}.pipedrive.com/api/v2, x-api-token header or OAuth 2.0, cursor pagination, free webhooks; v1 shuts down 2026-07-31) plus OpenAPI specs. Use when building a Pipedrive API or webhook integration, deciding between API v1 and v2 or migrating before the July 2026 shutdown, hitting the daily token rate limit (429), custom fields showing as random 40-character hash keys, webhooks duplicating/missing or auto-deleting after failures, syncing deals or persons into a warehouse or Slack, choosing OAuth vs API token, or picking a plan (Lite/Growth/Premium/Ultimate) and understanding the token-budget multiplier. Do NOT use for CRM selection/comparison across tools (use /sales-crm-selection), CRM data cleanup/dedupe (use /sales-data-hygiene), or outbound sequence design (use /sales-cadence)."
argument-hint: "[describe what you need help with in Pipedrive]"
license: MIT
version: 1.0.0
tags: [sales, crm, platform]
github: "https://github.com/pipedrive"
---

# Pipedrive Platform Help

## Step 1 — Gather context

If `references/learnings.md` exists, read it first for accumulated platform knowledge.

1. **What are you trying to do?**
   - A) Build an API integration — create/update deals, persons, organizations, leads, activities
   - B) Set up webhooks to push CRM changes into a warehouse/CRM/Slack
   - C) Migrate from API v1 to v2 (before the 2026-07-31 v1 shutdown)
   - D) Fix a rate-limit / token-budget (429) problem
   - E) Work with custom fields (the 40-char hash keys)
   - F) Pick/understand a plan — Lite vs Growth vs Premium vs Ultimate, token multipliers, add-ons

2. **Auth model?** Single internal account/script → **API token** (`x-api-token`). Distributable Marketplace app installed by other accounts → **OAuth 2.0**.

3. **Which API version?** Default to **v2** (cursor pagination, cheaper tokens). Use **v1 only** for resources not yet on v2 (Leads, Notes, Webhooks, Files, Filters, Goals, Projects).

Skip-ahead rule: if the user's prompt already provides enough context, skip to Step 2.

## Step 2 — Route or answer directly

| If the question is about... | Route to... |
|---|---|
| CRM selection/comparison or migration strategy across tools | `/sales-crm-selection {question}` |
| CRM data cleanup, dedupe, record matching | `/sales-data-hygiene {question}` |
| Contact enrichment for CRM records | `/sales-enrich {question}` |
| Outbound sequence / cadence design across platforms | `/sales-cadence {question}` |
| Lead scoring model design | `/sales-lead-score {question}` |
| Revenue forecasting methodology | `/sales-forecast {question}` |
| Connecting Pipedrive to other tools generically (iPaaS) | `/sales-integration {question}` |

When routing, give the exact command, e.g. "This is a CRM-comparison question — run: `/sales-crm-selection should I move from Pipedrive to HubSpot at 25 people`".

## Step 3 — Pipedrive platform reference

**Read `references/platform-guide.md`** for the full reference — the module map (what's API v2 vs v1-only vs UI-only), the pricing model (API is on **every** plan; only the **token budget** scales by multiplier), the data model with JSON shapes, and quick-start recipes (create a deal from a form; listen for deal-won via webhook; nightly incremental export).

**Read `references/pipedrive-api-reference.md`** for the integration surface — base URLs, `x-api-token` vs OAuth auth, the `{success, data, additional_data}` envelope, v2 cursor pagination, the resource list (and which are v1-only), the webhook payload/retry rules, the token-based rate-limit formula, and the **custom-field hash-key** mechanics.

Answer using only the relevant section. Don't dump the full reference.

## Step 4 — Actionable guidance

Focus on the user's specific situation:

- **Default to v2; the clock is real.** v1 fully shuts down **2026-07-31**. v2 uses the `x-api-token`
  header, **cursor** pagination (`limit`+`cursor`), and `PATCH` for updates, and costs ~half the tokens.
  Keep v1 only for Leads/Notes/Webhooks/Files/Filters/Goals/Projects.
- **Custom fields are 40-char hashes, not names.** Pull the hash→label map from `GET /api/v1/dealFields`
  (or `personFields`/`organizationFields`) and cache it; never hard-code a label. Hashes differ per account.
- **Budget tokens, don't just retry.** Daily budget = `30,000 × plan-multiplier × seats`. On `429` you're
  out for the day unless you top up — so migrate to v2, prefer **free webhooks** over polling, and use
  `updated_since` for incremental pulls.
- **Make webhook receivers bulletproof.** ACK `200` immediately and process async; retries are 3/30/150s,
  10 first-attempt fails → 30-min ban, and **3 days with no success auto-deletes the webhook**. Dedupe on
  object id + `meta.timestamp`.
- **Pick auth by distribution.** API token for your own account; OAuth 2.0 for a Marketplace app (use the
  returned `api_domain` as the base URL).
- **Plan choice is about token budget + features, not API access.** Every plan has the API; higher tiers
  add email sync/automation/forecasting and a bigger token multiplier. Watch the paid add-ons.

If you discover a gotcha, workaround, or tip not covered in `references/learnings.md`, append it there.

## Gotchas

> *Best-effort from research (2026-06) — review these, especially pricing and the v1 shutdown date, which change.*

1. **API v1 shuts down 2026-07-31.** New integrations must target v2; existing v1 code needs migration. Don't build new work on v1.
2. **Custom fields are random 40-char hash keys.** A field labeled "Tier" is referenced as e.g. `dcf558aac1ae4e8c4f849ba5e668430d8df9be12` — map via the `*Fields` endpoints.
3. **Token-based daily rate limit, not per-second.** Hit the daily budget and you get `429` until reset. v2 is ~50% cheaper than v1; webhooks are free.
4. **Webhooks auto-delete after 3 days of failures** (and ban for 30 min after 10 first-attempt fails). A downstream outage can silently kill your integration.
5. **Leads ≠ Deals, and Leads are v1-only.** The Leads inbox is a pre-deal stage with its own v1 API; don't expect a v2 `/leads` endpoint yet.
6. **v2 uses `PATCH` (v1 used `PUT`) and cursor pagination** (`additional_data.next_cursor`), not v1's `start`/`limit` offset. Porting code requires both changes.
7. **Costly add-ons.** LeadBooster, Web Visitors, Campaigns, Smart Docs, and Projects are paid extras on top of seats — total cost can exceed the headline per-seat price.
8. **Base URL is company-specific.** Calls go to `https://{your-company}.pipedrive.com/api/...`; for OAuth apps use the `api_domain` returned at token exchange, not a hard-coded domain.

## Related skills

- `/sales-crm-selection` — CRM comparison, selection, and migration strategy across tools (is Pipedrive the right CRM, or time to switch?)
- `/sales-data-hygiene` — CRM data quality: dedupe, record matching, enrichment automation
- `/sales-enrich` — Contact enrichment (emails, phones, company data) for Pipedrive records
- `/sales-cadence` — Outbound sequence/cadence design across platforms (Pipedrive isn't a sequencer)
- `/sales-integration` — Connecting Pipedrive to other tools via webhooks/Zapier/Make
- `/sales-do` — Not sure which skill to use? The router matches any sales objective to the right skill. Install: `npx skills add sales-skills/sales --skill sales-do -a claude-code`

## Examples

### Example 1: Create a deal when a form is submitted (developer/automation)
**User says**: "When someone fills out my pricing form, I want a deal created in Pipedrive in the right pipeline."
**Skill does**: Walks Recipe 1 — upsert the **person** (`POST /api/v2/persons`), then create the **deal** (`POST /api/v2/deals`) with `person_id`, `pipeline_id`, `stage_id`, authenticated with the `x-api-token` header. Notes to target **v2** (v1 dies 2026-07-31), and that setting a custom field requires its **40-char hash** from `GET /api/v1/dealFields`. Offers the no-code Zapier path as an alternative.
**Result**: Form submissions create properly-staged deals via the API.

### Example 2: My integration started returning 429
**User says**: "My nightly sync to BigQuery suddenly fails with 429 errors."
**Skill does**: Explains Pipedrive's **token-based daily budget** (`30,000 × plan-multiplier × seats`) — you've exhausted it, not a per-second cap. Fixes: migrate the sync to **v2** (~50% cheaper tokens), use `updated_since` cursor pulls instead of full scans, replace polling with **free webhooks** where possible, and buy a token top-up or raise the plan multiplier if still tight. Shows the backoff loop from the API reference.
**Result**: The sync fits within budget and stops 429-ing.

### Example 3: Should I stay on Pipedrive?
**User says**: "We're 30 people now and Pipedrive's reporting feels limiting — move to HubSpot?"
**Skill does**: Recognizes this as a cross-tool selection question and routes: "run: `/sales-crm-selection we're 30 people outgrowing Pipedrive's reporting, HubSpot vs alternatives`." Briefly notes Pipedrive's reporting limits and add-on costs are common switch triggers, but defers the comparison/migration plan to the strategy skill.
**Result**: User is handed to the right strategy skill with a ready prompt.

## Troubleshooting

### My API token works on some calls but a create/update fails
**Symptom**: GETs succeed but POST/PATCH returns errors, or a custom field won't set.
**Cause**: Using the field's display name instead of its **40-char hash key**, sending to v1 with v2 syntax (or vice-versa), or using `PUT` on v2 (v2 wants `PATCH`).
**Solution**: Fetch the field map from `GET /api/v1/dealFields` and use the `key` hash. Confirm the version: v2 base `/api/v2`, `x-api-token` header, `PATCH` for updates; v1 base `/api/v1`, `?api_token=`. Match the request body to the OpenAPI spec for that version.

### My webhook stopped firing
**Symptom**: Events arrive for a while, then nothing.
**Cause**: Pipedrive bans a webhook for 30 minutes after 10 first-attempt failures and **auto-deletes** it after 3 consecutive days with no successful (2xx) delivery — usually a downstream outage or slow (>10s) endpoint.
**Solution**: Make the receiver ACK `200` instantly and process async; verify HTTP Basic Auth matches; check it's reachable over public HTTPS. Recreate the webhook (`POST /api/v1/webhooks`) and add monitoring/alerting so a future outage doesn't silently delete it. Remember webhooks are free — they don't consume tokens.

### Hitting the daily rate limit
**Symptom**: `429 Too Many Requests`, often later in the day.
**Cause**: The **daily token budget** is exhausted (`30,000 × plan-multiplier × seats`), not a per-second throttle.
**Solution**: Migrate to **v2** (~half the token cost), switch full scans to `updated_since` incremental pulls, move polling to **webhooks**, cache reference data, and—if still constrained—buy API token top-ups or move to a higher plan multiplier (Lite 1× → Growth 2× → Premium 5× → Ultimate 7×).
