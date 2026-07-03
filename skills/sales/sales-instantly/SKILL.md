---
name: sales-instantly
description: "Instantly (instantly.ai) platform help — high-volume cold email outreach: campaigns/sequences across unlimited inboxes, free warmup, inbox-placement tests, Unibox, and separate Lead Finder (Credits) + CRM. REST API v2 (api.instantly.ai/api/v2, Bearer token, cursor pagination, OpenAPI spec; v2 incompatible with v1) plus webhooks (reply received, email events, meeting booked). Use when building an Instantly API or webhook integration, pushing leads into a campaign or syncing reply/opportunity events to a CRM, your warmup score looks healthy but emails still land in spam, DFY pre-warmed domains arriving burned, the real cost ballooning past the $47 headline once you add Credits and CRM, choosing Growth vs Hypergrowth vs Light Speed, or generating a v2 API key. Do NOT use for cold-email deliverability/warmup strategy across tools (use /sales-deliverability), outbound sequence/copy strategy (use /sales-cadence), or building a prospect list across tools (use /sales-prospect-list)."
argument-hint: "[describe what you need help with in Instantly]"
license: MIT
version: 1.0.0
tags: [sales, outbound, cold-email, platform]
---

# Instantly Platform Help

## Step 1 — Gather context

If `references/learnings.md` exists, read it first for accumulated platform knowledge.

1. **What are you trying to do?**
   - A) Build an API/webhook integration — push leads into a campaign, sync reply/opportunity events out
   - B) Fix deliverability — warmup looks healthy but emails land in spam, inbox placement, secondary domains
   - C) Configure a module — campaigns/sequences, email accounts/warmup, Unibox, Lead Finder, CRM
   - D) Understand cost — the $47 headline vs the real stack (Credits + CRM as separate paid products)
   - E) Generate a v2 API key (v1 keys don't work on v2) or pick a plan
   - F) Fix a problem — DFY domains arriving burned, support delays, buried settings

2. **API or strategy?** A concrete Instantly API/webhook/config task → stay here. A cross-tool *strategy* question (deliverability, sequence copy, list building) → route in Step 2.

Skip-ahead rule: if the user's prompt already provides enough context, skip to Step 2.

## Step 2 — Route or answer directly

| If the question is about... | Route to... |
|---|---|
| Cold-email **deliverability / warmup / inbox placement** strategy across tools | `/sales-deliverability {question}` |
| Outbound **sequence design / copywriting / cadence** across tools | `/sales-cadence {question}` |
| Building/sourcing a **prospect list** across tools | `/sales-prospect-list {question}` |
| Contact **enrichment / verification** strategy | `/sales-enrich {question}` |
| Connecting Instantly to a CRM/other tools generically (iPaaS) | `/sales-integration {question}` |

When routing, give the exact command, e.g. "This is a deliverability question — run: `/sales-deliverability my warmup score is green but I'm landing in spam`".

## Step 3 — Instantly platform reference

**Read `references/platform-guide.md`** for the full reference — the module map (what's API vs webhook vs UI-only), the pricing model (warmup free on all plans; **Lead Finder Credits and CRM are separate paid products**; Unibox is Hyper-Growth+), the data model with JSON shapes, and quick-start recipes (push leads to a campaign; react to replies via webhook; nightly analytics export).

**Read `references/instantly-api-reference.md`** for the integration surface — base `https://api.instantly.ai/api/v2`, Bearer-token auth (scoped, revocable; **generate a new v2 key**), cursor pagination (`starting_after`+`limit`), the endpoint list (campaigns, leads, lead-lists, accounts, analytics, emails, inbox-placement-tests, webhooks, api-keys), the OpenAPI spec URL, and the webhook event types + setup.

Answer using only the relevant section. Don't dump the full reference.

## Step 4 — Actionable guidance

Focus on the user's specific situation:

- **Trust seed tests, not the heat score.** Instantly's warmup pool creates *synthetic* engagement; a green
  warmup score can coexist with real campaigns landing in spam. Validate with **inbox-placement (seed-list)
  tests** before scaling volume, and treat deliverability strategy as `/sales-deliverability`.
- **API is v2 + Bearer.** Generate a **new v2 key** (v1 keys are incompatible), call
  `https://api.instantly.ai/api/v2` with `Authorization: Bearer`, and import the **OpenAPI spec** for exact
  schemas. API is on all Outreach plans.
- **Webhooks over polling.** Subscribe to `reply_received` / status events (meeting booked, not interested)
  and make your endpoint idempotent with retries; don't poll `/emails`. Webhooks may need a higher tier.
- **Model the true cost.** The Outreach seat price excludes **Lead Finder (Credits)** and **CRM** — both
  separate paid products. The real Growth stack is ≈$118/mo, not $47.
- **Vet DFY infrastructure.** Done-for-you pre-warmed domains/inboxes sometimes arrive with poor reputation
  (or get provider-disabled). Run your own placement test on them before trusting the heat score.
- **Spread the sending.** Many low-volume inboxes across secondary domains beat blasting one; SISR rotates
  IPs/servers but per-account daily caps still apply.

If you discover a gotcha, workaround, or tip not covered in `references/learnings.md`, append it there.

## Gotchas

> *Best-effort from research (2026-06) — review these, especially pricing and plan-gated features, which change.*

1. **Warmup score ≠ real inbox placement.** The #1 complaint: green heat scores while live emails hit spam. The warmup pool's synthetic engagement doesn't guarantee placement with real prospects — verify with seed tests.
2. **The $47 price is not the real cost.** Lead Finder (Credits) and CRM are **separate paid products**; a functional stack is ~$118/mo on Growth. Budget accordingly.
3. **API v2 is incompatible with v1.** You must generate a brand-new v2 key; v1 keys and payloads won't work on v2 endpoints.
4. **DFY pre-warmed domains can arrive burned.** A frequently-cited issue — heat scores read 90+ while real placement collapses; some Google accounts get disabled. Test before sending at volume.
5. **Unibox and (likely) webhooks are tier-gated.** Unibox is Hyper-Growth+; webhook access is reported to need a higher tier than the entry plan — verify on your plan before building.
6. **Support and UX friction.** Slow support and settings buried across panels are common review themes; budget time for setup and don't expect fast ticket resolution.
7. **Pagination is cursor-based.** Use `starting_after`+`limit`, not page numbers; back off on 429.
8. **Custom variables drive personalization.** Put merge data in `custom_variables` on the lead so sequence merge tags resolve — missing variables send blank or fallback text.

## Related skills

- `/sales-deliverability` — Cold-email deliverability, warmup, and inbox-placement strategy across tools (Instantly's biggest strength and its #1 pain point)
- `/sales-cadence` — Outbound sequence design, multichannel cadences, and copywriting across tools
- `/sales-prospect-list` — Building and sourcing prospect lists (Instantly's Lead Finder is one source)
- `/sales-enrich` — Contact enrichment and email verification
- `/sales-integration` — Connecting Instantly to a CRM/other tools via webhooks/Zapier
- `/sales-do` — Not sure which skill to use? The router matches any sales objective to the right skill. Install: `npx skills add sales-skills/sales --skill sales-do -a claude-code`

## Examples

### Example 1: Push leads into a campaign and react to replies (developer/automation)
**User says**: "When someone downloads my lead magnet, add them to my Instantly campaign and notify me when they reply."
**Skill does**: Walks Recipe 1 — `POST /api/v2/leads` with email + `custom_variables` + the `campaign` id, authed with `Authorization: Bearer` (a **v2** key). Then Recipe 2 — register a `reply_received` webhook (Settings → Integrations → Webhooks) that posts to Slack/creates a CRM task, with idempotent handling. Notes v1 keys won't work and webhooks may need a higher tier.
**Result**: Leads flow into the campaign and replies trigger real-time follow-up.

### Example 2: Warmup is green but I'm landing in spam
**User says**: "Instantly says my warmup health is 95% but my campaign still goes to spam."
**Skill does**: Explains the warmup pool generates **synthetic** engagement that doesn't equal real-prospect placement — the platform's most-reported gap. Recommends running an **inbox-placement (seed-list) test**, checking SPF/DKIM/DMARC + custom tracking domain, lowering per-inbox volume, and spreading across secondary domains. Routes the deeper playbook: "run: `/sales-deliverability warmup is green but I'm in spam on Instantly`."
**Result**: User stops trusting the heat score alone and gets a real placement-diagnosis path.

### Example 3: Is the $47 plan really $47?
**User says**: "Growth is $47/mo — is that all I'll pay to run cold email?"
**Skill does**: Clarifies that warmup is free, but the **Lead Finder (Credits)** and **CRM** are separate paid products, so a working stack is ~$118/mo on Growth. Breaks down what each add-on buys, notes Unibox is Hyper-Growth+, and frames pricing as best-effort to verify on the live page.
**Result**: User budgets the true cost instead of the headline.

## Troubleshooting

### My API calls return 401/unauthorized
**Symptom**: Every request is rejected.
**Cause**: Using a **v1 key on v2** (they're incompatible), a missing `Authorization: Bearer` header, or a key without the needed scope.
**Solution**: Generate a fresh **v2** key in-app with the right scopes, send it as `Authorization: Bearer YOUR_KEY` against `https://api.instantly.ai/api/v2`, and confirm API access is enabled on your Outreach plan. Import the OpenAPI spec to match request shapes.

### My emails land in spam despite a healthy warmup score
**Symptom**: Warmup dashboard is green; real campaigns hit spam.
**Cause**: The warmup pool's engagement is synthetic and doesn't guarantee placement with actual prospects; auth records, sending volume, or a burned domain can still tank you.
**Solution**: Run an **inbox-placement seed test**, verify SPF/DKIM/DMARC + a custom tracking domain, reduce per-inbox daily volume, warm new domains longer, and spread across secondary domains. For the full diagnosis, use `/sales-deliverability`.

### My webhook isn't firing / I can't find it
**Symptom**: No events arrive, or there's no webhook option.
**Cause**: Webhook access may be gated to a higher Outreach tier, the endpoint isn't public HTTPS, or no events were selected for the campaign scope.
**Solution**: Confirm your plan includes webhooks, add the webhook under Settings → Integrations → Webhooks (or `POST /api/v2/webhooks`) with an HTTPS endpoint and the right event types, send a test, and implement retries + idempotency on your side so transient failures don't drop events.
