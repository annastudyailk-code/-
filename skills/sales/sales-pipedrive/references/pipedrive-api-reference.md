<!-- Source: https://developers.pipedrive.com/docs/api/v1 -->
<!-- Source: https://pipedrive.readme.io/docs/pipedrive-api-v2 -->
<!-- Source: https://pipedrive.readme.io/docs/core-api-concepts-rate-limiting -->
<!-- Source: https://pipedrive.readme.io/docs/guide-for-webhooks -->
<!-- Captured 2026-06-27. Auth, base URLs, the v2 resource list, the rate-limit formula, the webhook
     payload/retry rules, and the hashed-custom-field fact are from the official docs. Endpoint
     request/response JSON is CONSTRUCTED from documented fields and marked — verify against the live
     reference. Pipedrive publishes OpenAPI 3 specs for v1 and v2; import those for exact schemas. -->

# Pipedrive API Reference

Pipedrive has a mature RESTful API with **two live versions**: **v1** (legacy, **full shutdown
2026-07-31**) and **v2** (faster, cursor-paginated, ~50% cheaper token cost — use this for new work).
Some resources (notably **Leads**, **Notes**, **Webhooks**, **Files**) still live only on v1. There are
**OpenAPI 3 specs** for both versions and a Postman collection; sandbox accounts are free.

## Base URL & authentication

- **Base URL:** `https://{company-domain}.pipedrive.com/api/v2` (v2) or `/api/v1` (v1).
  `{company-domain}` is the account's subdomain (find it in the in-app URL).
- **API token auth:**
  - **v2:** send the token in the **`x-api-token`** header.
  - **v1:** send it as the **`?api_token=`** query parameter.
  - Token is per-user, from **Settings → Personal preferences → API**.
- **OAuth 2.0:** required for **Marketplace apps** (multi-account). Authorization-code flow; tokens via
  `https://oauth.pipedrive.com/oauth/token`; the base URL for calls comes from the `api_domain` returned
  at token exchange.

### Auth quick-start (simplest GET — list deals, v2)

```bash
curl -s "https://YOURCOMPANY.pipedrive.com/api/v2/deals?limit=10" \
  -H "x-api-token: YOUR_API_TOKEN"
```

## Response envelope

Every response is wrapped:

```json
{
  "success": true,
  "data": { "...": "entity or array" },
  "additional_data": { "pagination": { "next_cursor": "eyJ..." } }
}
```

- **v2 pagination:** cursor-based — pass `limit` (max 500) and `cursor` (from
  `additional_data.next_cursor`); stop when `next_cursor` is null.
- **v1 pagination:** offset-based — `start` + `limit`, with `additional_data.pagination.more_items_in_collection`.
- **Incremental sync:** many endpoints accept `updated_since` / `updated_until` (RFC 3339) and
  `sort_by`/`sort_direction` — prefer these over full scans to save tokens.

## Core resources

v2 covers: **Activities, Deals (+ Deal Products, Deal Followers), Persons (+ Followers), Organizations
(+ Followers), Products (+ Variations, Followers), Pipelines, Stages, Fields (deal/person/org/product/
activity), Users (+ Followers), Search.** Still v1-only: **Leads, Lead Labels/Sources, Notes, Files,
Filters, Goals, Webhooks, Mailbox, Projects/Tasks, Roles, Permission Sets, Billing.**

### Deals — CRUD (v2)
| Operation | Method | Path |
|---|---|---|
| List | GET | `/api/v2/deals` |
| Get one | GET | `/api/v2/deals/{id}` |
| Create | POST | `/api/v2/deals` |
| Update | PATCH | `/api/v2/deals/{id}` |
| Delete | DELETE | `/api/v2/deals/{id}` |
| List deal products | GET | `/api/v2/deals/{id}/products` |

> v1 used `PUT` for updates; **v2 uses `PATCH`**. Persons, Organizations, Products, Activities follow the
> same CRUD shape on v2 (`/api/v2/persons`, `/organizations`, `/products`, `/activities`).

### Leads — CRUD (v1 only)
| Operation | Method | Path |
|---|---|---|
| List | GET | `/api/v1/leads` |
| Get one | GET | `/api/v1/leads/{id}` |
| Create | POST | `/api/v1/leads` |
| Update | PATCH | `/api/v1/leads/{id}` |
| Delete | DELETE | `/api/v1/leads/{id}` |

## Top-5 endpoint examples

<!-- JSON below CONSTRUCTED from documented fields — verify against the live reference / OpenAPI spec -->

### 1. List deals (GET `/api/v2/deals`)
```bash
curl -s "https://YOURCOMPANY.pipedrive.com/api/v2/deals?limit=50&updated_since=2026-06-01T00:00:00Z" \
  -H "x-api-token: YOUR_API_TOKEN"
```
```json
{
  "success": true,
  "data": [
    { "id": 1, "title": "Acme - 25 seats", "value": 5000, "currency": "USD",
      "status": "open", "stage_id": 2, "pipeline_id": 1, "person_id": 123, "org_id": 456,
      "owner_id": 9, "add_time": "2026-06-15T10:00:00Z", "update_time": "2026-06-20T09:00:00Z" }
  ],
  "additional_data": { "next_cursor": "eyJpZCI6MX0" }
}
```

### 2. Create a deal (POST `/api/v2/deals`)
```bash
curl -s -X POST "https://YOURCOMPANY.pipedrive.com/api/v2/deals" \
  -H "x-api-token: YOUR_API_TOKEN" -H "Content-Type: application/json" \
  -d '{ "title": "Acme - 25 seats", "value": 5000, "currency": "USD", "person_id": 123, "pipeline_id": 1, "stage_id": 2 }'
```
```json
{ "success": true, "data": { "id": 1, "title": "Acme - 25 seats", "status": "open" } }
```

### 3. Create a person (POST `/api/v2/persons`)
```bash
curl -s -X POST "https://YOURCOMPANY.pipedrive.com/api/v2/persons" \
  -H "x-api-token: YOUR_API_TOKEN" -H "Content-Type: application/json" \
  -d '{ "name": "Sam Rivera", "emails": [{"value":"sam@acme.com","primary":true}], "org_id": 456 }'
```
```json
{ "success": true, "data": { "id": 123, "name": "Sam Rivera", "org_id": 456 } }
```

### 4. Update a deal — set a hashed custom field (PATCH `/api/v2/deals/{id}`)
```bash
curl -s -X PATCH "https://YOURCOMPANY.pipedrive.com/api/v2/deals/1" \
  -H "x-api-token: YOUR_API_TOKEN" -H "Content-Type: application/json" \
  -d '{ "stage_id": 3, "dcf558aac1ae4e8c4f849ba5e668430d8df9be12": "Enterprise" }'
```
> **Custom fields are referenced by a random 40-char hash key**, not their display name. Get the mapping
> from `GET /api/v1/dealFields` (or `/personFields`, `/organizationFields`) — the `key` field is the hash.

### 5. Create a webhook (POST `/api/v1/webhooks`)
```bash
curl -s -X POST "https://YOURCOMPANY.pipedrive.com/api/v1/webhooks" \
  -H "Content-Type: application/json" \
  -d '{ "subscription_url": "https://my.app/hooks/pipedrive",
        "event_action": "updated", "event_object": "deal",
        "http_auth_user": "u", "http_auth_password": "p" }'
```

## Webhooks

- **Create** with an `event_action` + `event_object` (e.g. `added`/`updated`/`deleted`/`merged` ×
  `deal`/`person`/`organization`/`activity`/`note`/`pipeline`/`product`/`stage`/`user`). Wildcards: `*`.
- **Receiver** must be public HTTPS; optional **HTTP Basic Auth** (`http_auth_user`/`password`).
- **v2 payload shape:**
```json
{
  "meta": { "action": "updated", "object": "deal", "change_source": "app",
            "timestamp": 1523440213, "webhook_id": 12345, "company_id": 77, "user_id": 9 },
  "data": { "current": { "id": 1, "title": "Acme - 25 seats", "status": "won" },
            "previous": { "id": 1, "title": "Acme - 25 seats", "status": "open" } }
}
```
  On `deleted`, `current` is null. **Webhooks are free — they do not consume API tokens.**
- **Retries:** non-2xx or >10s timeout retried after **3s, 30s, 150s**. 10 first-attempt failures → a
  **30-minute ban**. **No successful delivery for 3 consecutive days → the webhook is auto-deleted.** Make
  receivers fast (ACK 200 immediately, process async) and idempotent on `meta.id`/object id.

## Rate limits (token-based)

- **Daily budget = 30,000 base tokens × plan multiplier × number of seats** (+ purchased top-ups).
  Multipliers: **Lite 1× · Growth 2× · Premium 5× · Ultimate 7×**.
- Each endpoint costs a number of tokens by complexity; **v2 costs ≈50% of the v1 equivalent**. Exceeding
  the daily budget returns **HTTP 429** until reset.
- A separate **burst limit** applies per user on a rolling **2-second** window.
- Budget headers are returned (`x-daily-requests-left` / `x-ratelimit-*`); webhooks are free; cache and use
  `updated_since` to minimize spend.

```python
import requests, time

def pd_get(path, token, company, params=None):
    url = f"https://{company}.pipedrive.com/api/v2/{path.lstrip('/')}"
    h = {"x-api-token": token}
    for attempt in range(6):
        r = requests.get(url, headers=h, params=params, timeout=30)
        if r.status_code == 429:
            time.sleep(2 ** attempt)        # back off; daily budget may need until reset
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()
```

## Migration & gaps

- **v1 → v2:** v1 endpoints began deprecating 2026-01-01; **full v1 shutdown 2026-07-31**. Move list/get/
  create/update to v2 (cursor pagination, `x-api-token` header, `PATCH` for updates). Keep using v1 only
  for resources not yet on v2 (Leads, Notes, Webhooks, Files, Filters, Goals, Projects).
- **No official MCP server** at capture time (third-party community servers exist).
- Exact field-level schemas: import the published **OpenAPI 3 specs** (v1 and v2) rather than relying on
  the constructed JSON above.
