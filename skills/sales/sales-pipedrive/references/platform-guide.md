# Pipedrive Platform Reference

## Overview

Pipedrive (pipedrive.com) is a **pipeline-first sales CRM** for SMB sales teams — its strength is a clean,
visual deal pipeline and ease of adoption, not marketing automation. Best for outbound/deal-centric teams
of ~3–50 who want a fast, affordable CRM with a solid REST API. Weak spots: native reporting depth and
costly add-ons (LeadBooster, Campaigns, etc.) for capabilities that are built-in elsewhere.

## Capabilities & automation surface

| Module | What it does | Automation surface |
|---|---|---|
| Deals & pipelines | Visual Kanban, stages, rotting alerts, products | Full CRUD via **API v2** (`/deals`); `*.deal` **webhooks** |
| Persons & organizations | Contacts + company records, relationships | **API v2** (`/persons`, `/organizations`); webhooks |
| Leads | Lead inbox before deals (LeadBooster) | **API v1 only** (`/leads`); webhooks |
| Activities | Tasks, calls, meetings, calendar sync | **API v2** (`/activities`); webhooks |
| Custom fields | Per-object custom data | **API** (referenced by **40-char hash key**, from `*Fields` endpoints) |
| Workflow automation | Trigger→action rules | Config **UI-only**; events observable via webhooks |
| Email sync & Campaigns | 2-way email, bulk email (add-on) | Mailbox is **v1 API**; Campaigns largely **UI-only** |
| Reporting & forecasting | Dashboards, revenue forecast | **UI-only** (export or pull raw records via API) |
| Marketplace apps | 500+ integrations | **OAuth 2.0** apps; webhooks |

**Programmatic interfaces:** REST API **v1 + v2** (`{company}.pipedrive.com/api/{v1,v2}`, `x-api-token`
header or OAuth), **webhooks** (free), OpenAPI 3 specs, Postman, sandbox accounts. No official MCP server.
See `references/pipedrive-api-reference.md`.

## Pricing, limits & plan gates

*Best-effort from research (2026-06) — plan names changed in late 2025; verify on the live pricing page.*

| Plan (new name) | ~Price/seat/mo (annual) | Old name | API token multiplier |
|---|---|---|---|
| Lite | ~$14 | Essential | 1× |
| Growth | ~$39 | Advanced | 2× |
| Premium | ~$59 | Professional | 5× |
| Ultimate | ~$79 | Power / Enterprise | 7× |

- **The API and webhooks are available on every plan — they are NOT plan-gated.** What scales with plan is
  the **daily API token budget** (`30,000 × multiplier × seats`), not access.
- Higher tiers add email sync + automation (Growth), forecasting + custom reports (Premium), and security
  + admin controls (Ultimate). Many capabilities are **paid add-ons**: LeadBooster, Web Visitors,
  Campaigns, Smart Docs, Projects — budget for these on top of seats.

## Integrations

- **Direction:** the API is fully bidirectional (read + write all core CRM objects); webhooks push changes
  out in near-real-time and are free.
- **Auth choice:** use an **API token** for a single account/internal script; use **OAuth 2.0** if you're
  building a Marketplace app that other accounts install.
- **iPaaS:** Zapier, Make, native marketplace (500+). For incremental sync prefer API `updated_since`.

## Data model

Core objects, all addressable by numeric `id`; identity for people is typically email. Custom fields are
**hashed keys**.

**Deal** <!-- Constructed from docs — verify against OpenAPI -->
```json
{ "id": 1, "title": "Acme - 25 seats", "value": 5000, "currency": "USD", "status": "open",
  "pipeline_id": 1, "stage_id": 2, "person_id": 123, "org_id": 456, "owner_id": 9,
  "add_time": "2026-06-15T10:00:00Z", "update_time": "2026-06-20T09:00:00Z" }
```

**Person** <!-- Constructed — verify -->
```json
{ "id": 123, "name": "Sam Rivera", "emails": [{"value":"sam@acme.com","primary":true}],
  "phones": [{"value":"+15551234567","primary":true}], "org_id": 456, "owner_id": 9 }
```

**Webhook event (v2)** <!-- from docs -->
```json
{ "meta": { "action": "updated", "object": "deal", "timestamp": 1523440213, "webhook_id": 12345 },
  "data": { "current": { "id": 1, "status": "won" }, "previous": { "id": 1, "status": "open" } } }
```

## Quick-start recipes

### Recipe 1 — Create a deal from an external lead/form (API v2)

**Trigger:** new signup/form → **steps:** upsert the person, then create the deal in the right pipeline/stage.

```bash
PID=$(curl -s -X POST "https://$CO.pipedrive.com/api/v2/persons" -H "x-api-token: $TOK" \
  -H "Content-Type: application/json" \
  -d '{"name":"Sam Rivera","emails":[{"value":"sam@acme.com","primary":true}]}' | jq -r .data.id)
curl -s -X POST "https://$CO.pipedrive.com/api/v2/deals" -H "x-api-token: $TOK" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Acme inbound\",\"person_id\":$PID,\"pipeline_id\":1,\"stage_id\":1}"
```
```python
import requests
H = {"x-api-token": TOK, "Content-Type": "application/json"}
B = f"https://{CO}.pipedrive.com/api/v2"
pid = requests.post(f"{B}/persons", headers=H, json={"name":"Sam Rivera",
       "emails":[{"value":"sam@acme.com","primary":True}]}).json()["data"]["id"]
requests.post(f"{B}/deals", headers=H, json={"title":"Acme inbound","person_id":pid,
       "pipeline_id":1,"stage_id":1}).raise_for_status()
```
**Gotchas:** use **v2** + `x-api-token` (v1 shuts down 2026-07-31). To set a custom field, look up its
40-char hash via `GET /api/v1/dealFields` first.

### Recipe 2 — Listen for "deal won" and sync to your warehouse/Slack (webhook)

**Trigger:** register a `updated.deal` webhook → on each event, check `data.current.status == "won"` and
`data.previous.status != "won"`, then post to Slack / insert into your DB. ACK 200 immediately and process
async; webhooks retry at 3/30/150s and **auto-delete after 3 days of failures**, so keep the endpoint up.
Webhooks are **free** (no token cost) — prefer them over polling.

### Recipe 3 — Nightly incremental export without blowing the token budget

**Trigger:** cron → cursor-page `GET /api/v2/deals?updated_since=<last_run>&limit=500`, following
`additional_data.next_cursor` until null; repeat for persons/orgs/activities.
```python
def export(resource, since):
    rows, cursor = [], None
    while True:
        p = {"limit": 500, "updated_since": since}
        if cursor: p["cursor"] = cursor
        b = requests.get(f"{B}/{resource}", headers={"x-api-token": TOK}, params=p, timeout=30).json()
        rows += b["data"] or []
        cursor = b["additional_data"].get("next_cursor")
        if not cursor: break
    return rows
```
**Gotchas:** daily budget = `30,000 × plan-multiplier × seats`; **v2 costs ~half of v1**. On `429`, back
off until reset. Use `updated_since` so you never full-scan.

## Integration patterns

- **CRM as source of truth:** map external identities on email; write deals/persons via v2; observe changes
  via webhooks rather than polling.
- **Custom-field discipline:** cache the hash→label map from the `*Fields` endpoints; never hard-code a
  label. Hashes are stable per field but differ across accounts.
- **Rate-limit budgeting:** estimate tokens/day = calls × per-endpoint cost; if tight, migrate v1→v2,
  lean on webhooks, batch with `updated_since`, or buy token top-ups.
- **Webhook reliability:** respond 200 fast, verify Basic Auth, dedupe on object id + `meta.timestamp`,
  and monitor for the 30-min ban / 3-day auto-delete so a downstream outage doesn't silently kill the hook.
- **OAuth vs token:** internal script → API token; distributable Marketplace app → OAuth 2.0 (use the
  returned `api_domain` as the base URL).
