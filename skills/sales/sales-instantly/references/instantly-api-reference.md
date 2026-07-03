<!-- Source: https://developer.instantly.ai/ and https://developer.instantly.ai/llms.txt -->
<!-- Source: https://help.instantly.ai/en/articles/10432807-api-v2 -->
<!-- Source: https://instantly.ai/blog/api-webhooks-custom-integrations-for-outreach/ -->
<!-- Captured 2026-06-27. Base URL, auth, pagination, endpoint list, OpenAPI URL, and webhook event
     names are from the official docs. Request/response JSON is CONSTRUCTED from the documented REST
     conventions and marked — verify against the live docs / OpenAPI spec. -->

# Instantly API Reference (v2)

Instantly exposes a modern **REST API v2** (`developer.instantly.ai`) for managing cold-email campaigns,
leads, email accounts, analytics, inbox-placement tests, and webhooks. **v2 is completely incompatible
with v1** — you must generate a **new v2 key**. The interactive docs let you test endpoints in-browser,
and a machine-readable **OpenAPI 3 spec** is published — import it for exact schemas.

## Base URL & authentication

- **Base URL:** `https://api.instantly.ai/api/v2`
- **Auth:** **Bearer token** — `Authorization: Bearer {API_KEY}`.
- **Keys:** generate v2 keys in-app (Settings → Integrations / API); keys support **scopes** (granular
  per-key permissions) and can be **created multiple times and revoked**. **API access is available on all
  Email Outreach plans** (the entry Outreach plan and up).
- **OpenAPI spec:** `https://api.instantly.ai/openapi/api_v2.json`.

### Auth quick-start (simplest GET — list campaigns)

```bash
curl -s "https://api.instantly.ai/api/v2/campaigns?limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Pagination

Cursor-based: pass `limit` and `starting_after` (the id/cursor of the last item from the previous page);
keep paging until fewer than `limit` items return.

```python
import requests
def list_all(path, key, params=None):
    params = dict(params or {}); params.setdefault("limit", 100)
    url = f"https://api.instantly.ai/api/v2/{path.lstrip('/')}"
    h = {"Authorization": f"Bearer {key}"}
    out = []
    while True:
        body = requests.get(url, headers=h, params=params, timeout=30).json()
        items = body.get("items", body if isinstance(body, list) else [])
        out += items
        if len(items) < params["limit"]:
            break
        params["starting_after"] = items[-1]["id"]
    return out
```

## Resource groups & endpoints

Standard REST CRUD per resource: `GET /resource` (list), `POST /resource` (create), `GET /resource/{id}`,
`PATCH /resource/{id}`, `DELETE /resource/{id}`.

| Resource | Path | Notes |
|---|---|---|
| Campaigns | `/campaigns` | create/launch/pause campaigns; subsequences under `/campaigns/.../subsequences` |
| Leads | `/leads` | add/update leads, assign to campaigns/lists, set status |
| Lead Lists | `/lead-lists` | named lists of leads |
| Email Accounts | `/accounts` | connected sending inboxes (warmup status, daily limits) |
| Analytics | `/campaigns/analytics`, `/accounts/analytics` | reply/open/bounce/opportunity metrics |
| Emails | `/emails` | individual sent/received messages (the Unibox data) |
| Inbox Placement Tests | `/inbox-placement-tests` | seed-list deliverability tests |
| Webhooks | `/webhooks` | create/list/patch webhook subscriptions; events via the list-event-types endpoint |
| API Keys | `/api-keys` | manage keys/scopes |
| Also | Campaign Subsequences, Lead Labels, Custom Tags, Block List, Background Jobs, Audit Logs, Email Verification, Workspaces, OAuth Sessions, Webhook Events |

## Top-5 endpoint examples

<!-- JSON CONSTRUCTED from documented REST conventions — verify against the OpenAPI spec -->

### 1. List campaigns (GET `/campaigns`)
```bash
curl -s "https://api.instantly.ai/api/v2/campaigns?limit=50" -H "Authorization: Bearer $KEY"
```
```json
{ "items": [ { "id": "01h...", "name": "Q3 SaaS founders", "status": "active" } ],
  "next_starting_after": "01h..." }
```

### 2. Add a lead to a campaign (POST `/leads`)
```bash
curl -s -X POST "https://api.instantly.ai/api/v2/leads" -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{ "email": "sam@acme.com", "first_name": "Sam", "last_name": "Rivera",
        "company_name": "Acme", "campaign": "01h...", "custom_variables": {"icebreaker": "loved your launch"} }'
```
```json
{ "id": "lead_01h...", "email": "sam@acme.com", "campaign": "01h...", "status": "active" }
```

### 3. Get a single lead (GET `/leads/{id}`)
```bash
curl -s "https://api.instantly.ai/api/v2/leads/lead_01h..." -H "Authorization: Bearer $KEY"
```
```json
{ "id": "lead_01h...", "email": "sam@acme.com", "status": "interested", "campaign": "01h..." }
```

### 4. Update lead status (PATCH `/leads/{id}`)
```bash
curl -s -X PATCH "https://api.instantly.ai/api/v2/leads/lead_01h..." -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" -d '{ "status": "not_interested" }'
```
```json
{ "id": "lead_01h...", "status": "not_interested" }
```

### 5. Campaign analytics (GET `/campaigns/analytics`)
```bash
curl -s "https://api.instantly.ai/api/v2/campaigns/analytics?campaign_id=01h..." -H "Authorization: Bearer $KEY"
```
```json
{ "campaign_id": "01h...", "sent": 4200, "opens": 1800, "replies": 210, "bounces": 63, "opportunities": 24 }
```

## Webhooks

Configure in **Settings → Integrations → Webhooks** (or via `POST /webhooks`): paste your **HTTPS**
endpoint, choose campaign scope + event types, save and send a test. Instantly POSTs a JSON payload per
event. **Implement retries + idempotency on your side** and monitor deliveries.

**Event types** (from the docs; full enum via `GET /webhooks/.../event-types`):
`email_sent`, `email_opened`, `email_clicked` (link click), `email_bounced`, `reply_received`,
`lead_unsubscribed`, and **status updates** (e.g. **meeting booked**, **not interested**).

<!-- Constructed payload from event names — verify against a live webhook delivery -->
```json
{
  "event_type": "reply_received",
  "timestamp": "2026-06-27T10:00:00Z",
  "campaign_id": "01h...",
  "lead": { "email": "sam@acme.com", "first_name": "Sam", "status": "interested" },
  "email": { "subject": "Re: quick question", "from": "you@yourdomain.com", "to": "sam@acme.com" }
}
```
> Some sources report webhooks require a higher Outreach tier than the entry plan — verify against your
> plan before building. Webhooks are the right tool for reply/opportunity events; avoid polling `/emails`.

## Rate limits & errors

The public docs don't publish a fixed rate-limit number; treat 429 as retryable with backoff and otherwise
trust standard HTTP status codes. Defensive wrapper:

```python
import requests, time
def inst(method, path, key, **kw):
    url = f"https://api.instantly.ai/api/v2/{path.lstrip('/')}"
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    for attempt in range(5):
        r = requests.request(method, url, headers=h, timeout=30, **kw)
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(2 ** attempt); continue
        r.raise_for_status(); return r.json()
    r.raise_for_status()
```

## Gaps / not documented

- Exact request/response field schemas: import the **OpenAPI spec** (`/openapi/api_v2.json`) rather than
  relying on the constructed JSON above.
- Published numeric rate limits and the full webhook event enum aren't in the public marketing docs — read
  them from the interactive reference / list-event-types endpoint.
- Webhook plan-gating is reported inconsistently across third-party sources — verify on your plan.
- No official MCP server found at capture time.
