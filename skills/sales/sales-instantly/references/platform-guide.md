# Instantly Platform Reference

## Overview

Instantly (instantly.ai) is a **high-volume cold-email outreach platform** for SDRs, agencies, and
founders — its edge is sending across **unlimited connected inboxes** with built-in **warmup** and
deliverability infrastructure (server/IP sharding & rotation). Best for outbound teams running multi-inbox
cold campaigns at scale. Watch-outs: the headline price excludes the **Lead Finder (Credits)** and **CRM**
(separate paid products), and the single most-cited complaint is **warmup scores that look healthy while
real campaigns still land in spam**.

## Capabilities & automation surface

| Module | What it does | Automation surface |
|---|---|---|
| Campaigns & sequences | Multi-step cold email + A/Z subsequences | Full CRUD via **API** (`/campaigns`); launch/pause |
| Leads & lead lists | Add/segment leads, set status (interested, etc.) | **API** (`/leads`, `/lead-lists`); webhook status events |
| Email accounts | Connect unlimited sending inboxes, daily limits | **API** (`/accounts`); warmup status |
| Email Warmup | Free auto-warmup on every plan (warmup pool) | **UI-only** (status readable via API) |
| Inbox Placement / SISR | Seed-list placement tests; IP/server sharding+rotation | Tests via **API** (`/inbox-placement-tests`) |
| Unibox | Unified reply inbox across all accounts (Hyper-Growth+) | Messages via **API** (`/emails`); replies via webhook |
| Lead Finder (Credits) | B2B lead database — **separate paid product** | **API** (search/export); billed in credits |
| CRM | Pipeline/opportunities — **separate paid product** | **API** (CRM objects) |
| AI agents / WARP | AI sales/reply agents, auto lead-find + campaign gen | Largely **UI-only** |
| Analytics | Reply/open/bounce/opportunity metrics | **API** (`/campaigns/analytics`, `/accounts/analytics`) |
| Webhooks | Real-time event push | **Webhook** (`/webhooks`) — may need a higher tier |

**Programmatic interfaces:** REST **API v2** (`https://api.instantly.ai/api/v2`, Bearer token, cursor
pagination, OpenAPI spec), **webhooks**, native CRM/Zapier integrations. v1 exists but is deprecated and
incompatible with v2. No official MCP server. See `references/instantly-api-reference.md`.

## Pricing, limits & plan gates

*Best-effort from research (2026-06) — verify on the live pricing page.*

| Outreach plan | ~Price/mo | Emails/mo | Contacts | Notable |
|---|---|---|---|---|
| Growth | ~$47 | 5,000 | 1,000 | unlimited accounts + warmup, **API**, CRM integrations |
| Hypergrowth | ~$97 | 100,000 | 25,000 | **Unibox**, more analytics |
| Light Speed | ~$358 | 500,000+ | 100,000+ | high-volume |
| Enterprise | custom | — | — | managed |

- **Warmup is free on all plans** — there is no separate warmup fee.
- **Lead database (Credits) and CRM are separate paid add-ons** — the real "functional stack" cost is well
  above the $47 headline (≈$118/mo for Growth + Credits + CRM). Set expectations on total cost.
- **API is on all Outreach plans**; **Unibox is Hyper-Growth+**; webhooks may require a higher tier (verify).

## Integrations

- **Direction:** API writes leads/campaigns in and reads analytics/emails out; webhooks push reply,
  open, bounce, unsubscribe, and status events (meeting booked / not interested) in real time.
- **Auth:** Bearer token (scoped, revocable). Generate a **new v2 key** — v1 keys don't work on v2.
- **iPaaS / native:** Zapier + native CRM connectors; for custom flows use the REST API + webhooks.

## Data model

Identity is **email**. Ids are opaque strings.

**Lead** <!-- Constructed from docs — verify against OpenAPI -->
```json
{ "id": "lead_01h...", "email": "sam@acme.com", "first_name": "Sam", "company_name": "Acme",
  "campaign": "01h...", "status": "interested", "custom_variables": { "icebreaker": "loved your launch" } }
```

**Campaign analytics** <!-- Constructed — verify -->
```json
{ "campaign_id": "01h...", "sent": 4200, "opens": 1800, "replies": 210, "bounces": 63, "opportunities": 24 }
```

**Webhook event** <!-- Constructed from event names — verify -->
```json
{ "event_type": "reply_received", "campaign_id": "01h...",
  "lead": { "email": "sam@acme.com", "status": "interested" } }
```

## Quick-start recipes

### Recipe 1 — Push leads into a campaign from your app (API)

**Trigger:** new signup/list → **steps:** `POST /leads` with email + custom variables + `campaign` id.

```bash
curl -s -X POST "https://api.instantly.ai/api/v2/leads" -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{ "email":"sam@acme.com","first_name":"Sam","company_name":"Acme","campaign":"01h...",
        "custom_variables":{"icebreaker":"loved your launch"} }'
```
```python
import requests
requests.post("https://api.instantly.ai/api/v2/leads",
  headers={"Authorization": f"Bearer {KEY}"},
  json={"email":"sam@acme.com","first_name":"Sam","campaign":"01h...",
        "custom_variables":{"icebreaker":"loved your launch"}}, timeout=30).raise_for_status()
```
**Gotchas:** generate a **v2** key (v1 won't work); reference the campaign by its id; put personalization in
`custom_variables` so your sequence merge tags resolve.

### Recipe 2 — React to replies in real time (webhook, not polling)

**Trigger:** register a `reply_received` (and `meeting booked`/`not interested`) webhook in Settings →
Integrations → Webhooks (or `POST /webhooks`) → on each event, create a CRM task/deal and notify Slack.
**Implement retries + idempotency on your side** (dedupe on lead email + event_type + timestamp). Prefer
webhooks over polling `/emails`. Note webhooks may need a higher Outreach tier.

### Recipe 3 — Nightly analytics export

**Trigger:** cron → `GET /campaigns/analytics` per campaign and cursor-page `/leads?campaign=...` for
status breakdowns; load into your warehouse.
```python
a = requests.get("https://api.instantly.ai/api/v2/campaigns/analytics",
      headers={"Authorization": f"Bearer {KEY}"}, params={"campaign_id":"01h..."}, timeout=30).json()
```
**Gotchas:** cursor pagination uses `starting_after`+`limit`; back off on 429.

## Integration patterns

- **Deliverability is the real game** — Instantly's warmup pool produces *synthetic* engagement that
  doesn't always equal real-prospect inbox placement. Validate with **inbox-placement (seed-list) tests**,
  not just the warmup heat score, before scaling volume. (For strategy, see `/sales-deliverability`.)
- **Spread sending** across many low-volume inboxes/domains (secondary domains) rather than blasting one;
  Instantly's SISR rotates IPs/servers, but per-account daily caps still matter.
- **Webhook reliability:** ACK fast, retry + dedupe on your side; Instantly expects your endpoint to be
  idempotent.
- **Cost modeling:** budget Credits (lead data) + CRM separately from the Outreach seat price.
- **CRM sync:** map on email; push leads in via `/leads`, pull reply/opportunity signals via webhooks into
  HubSpot/Pipedrive/your CRM.
