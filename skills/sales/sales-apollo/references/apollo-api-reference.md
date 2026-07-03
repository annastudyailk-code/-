### Apollo.io REST API v1 — Comprehensive Reference

**Base URL**: `https://api.apollo.io/api/v1`
**Docs**: https://docs.apollo.io/
**API version**: v1 (all endpoints prefixed `/api/v1/`)

---

## Authentication

Apollo supports two authentication methods.

### API Key Authentication

| Detail | Value |
|---|---|
| Header | `X-Api-Key: YOUR_API_KEY` (case-insensitive; docs use `X-Api-Key`) |
| Also send | `Content-Type: application/json`, `Cache-Control: no-cache` |
| Where to find | Settings > Integrations > API Keys > "Create new key" |
| Test key | `GET https://api.apollo.io/v1/auth/health` with the headers above |

Header-based auth is recommended. (Apollo's current docs document the header method; passing the key as a query param or JSON body field is undocumented — prefer the header.)

### OAuth 2.0 — Authorization Code

| Step | Detail |
|---|---|
| Authorization URL | `https://app.apollo.io/#/oauth/authorize` |
| Token URL | `https://app.apollo.io/api/v1/oauth/token` |
| Grant type | `authorization_code` (use `refresh_token` to renew) |
| Scopes | **Granular** — each scope grants access to specific endpoints. Add only the scopes your app needs. Examples: `contacts_search`, `person_read`, `opportunity_write`. Apollo automatically includes `read_user_profile` and `app_scopes`. |

**Authorization request parameters**: `client_id`, `redirect_uri`, `response_type=code`, `scope` (space-separated), `state`. Example: `https://app.apollo.io/#/oauth/authorize?client_id=<id>&redirect_uri=<uri>&response_type=code&scope=contacts_search%20person_read&state=xxxx`

**Token exchange POST body**:
```
client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
code=AUTHORIZATION_CODE
grant_type=authorization_code
redirect_uri=YOUR_REDIRECT_URI
```

**Token response**:
```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 7200,
  "refresh_token": "...",
  "created_at": 1700000000
}
```

Use `Authorization: Bearer <access_token>` header for OAuth-authenticated requests.

---

## Request & Response Format

### Requests
- **Content-Type**: `application/json`
- Most search/create endpoints use **POST** with a JSON body (not GET with query params)
- GET endpoints accept query parameters

### Response Format

Apollo does not use a consistent envelope. Responses vary by endpoint:

**Search endpoints** return:
```json
{
  "people": [ ... ],
  "pagination": {
    "page": 1,
    "per_page": 25,
    "total_entries": 1500,
    "total_pages": 60
  }
}
```

**Single record endpoints** return:
```json
{
  "contact": { ... }
}
```

**Enrichment endpoints** return:
```json
{
  "person": { ... },
  "organization": { ... }
}
```

### Error Responses

**400** — bad request:
```json
{
  "error": "Description of the error"
}
```

**401** — unauthorized:
```json
{
  "error": "API key is invalid or missing"
}
```

**422** — validation:
```json
{
  "error": "Validation failed",
  "message": "email is required"
}
```

**429** — rate limit exceeded:
```json
{
  "error": "Rate limit exceeded"
}
```

---

## Pagination

**Type**: Page-based (1-indexed)

| Parameter | Default | Range | Description |
|---|---|---|---|
| `page` | 1 | 1+ | Page number (1-based) |
| `per_page` | 25 | 1–100 | Records per page (some endpoints cap at 100) |

**Pagination response object** (in `pagination`):

| Field | Description |
|---|---|
| `page` | Current page number |
| `per_page` | Records per page |
| `total_entries` | Total record count |
| `total_pages` | Total number of pages |

**Notes**:
- Search endpoints (people search, org search) are capped at **100 pages** (10,000 results max per query). Refine filters to access more data.
- Some endpoints use `num_fetch_result` instead of `per_page`.

---

## Rate Limits

| Detail | Value |
|---|---|
| Model | **Fixed-window**. Every endpoint has a separate per-minute, per-hour, AND per-day limit. |
| Scope | Per API key / per account; **limits vary by pricing plan and by endpoint** |
| Typical per-minute | ~50/min on the free plan; ~200/min on paid plans (indicative; exact value is per-endpoint and plan-dependent) |
| Typical per-day | ~600/day free, ~2,000/day on Basic/Pro (indicative; varies per endpoint) |
| Higher limits | Contact Apollo sales for a custom plan with raised limits |
| Enrichment daily cap | Plan-dependent daily credit limits apply separately |

**Check your exact limits programmatically** — `POST /usage_stats/api_usage_stats` (full path `https://api.apollo.io/api/v1/usage_stats/api_usage_stats`). **Requires a master API key** (a non-master key returns `403`). The response lists, per endpoint, the `day`/`hour`/`minute` windows, each with `limit`, `consumed`, and `left_over` fields.

When a limit is exceeded, the API returns `429` with a message indicating you've been rate limited. Retry after the window resets. (Apollo's docs do not publish a fixed table of `x-rate-limit-*` response headers — use the `/usage_stats/api_usage_stats` endpoint to read current limits and remaining quota.)

---

## Credit Consumption

Apollo uses a credit system for enrichment and search operations. Credits are plan-dependent and reset monthly.

| Operation | Credit Cost | Notes |
|---|---|---|
| People enrichment — verified email (match) | 1 credit per email | Only charged when new data is returned |
| People enrichment — mobile phone reveal | **~8 credits per phone** (≈8× an email) | `reveal_phone_number=true` returns numbers asynchronously to your `webhook_url` |
| Organization enrichment | 1 credit per org | Only charged when new data is returned |
| People search (API `/mixed_people/api_search`) | 0 credits | **The API search endpoint does NOT consume credits and never returns emails/phones** — reveal via the enrichment endpoints |
| Organization search | 0 credits | Free to search |
| Bulk people match | per-record (email ≈1, phone ≈8) | Same matching/cost rules as single match, applied per record |
| Bulk org enrichment | 1 credit per org enriched | Same as single, applied per record |
| Contact creation | 0 credits | Free |
| Sequence operations | 0 credits | Free |
| Export | 1 credit per record exported | |

Mobile credits, email credits, and export credits are separate buckets and **expire at the end of each billing cycle (no rollover)**.

**Credit / usage check**: Use `POST /usage_stats/api_usage_stats` (master API key required) to read per-endpoint usage and remaining quota.

---

## All API Endpoints

All paths are relative to `https://api.apollo.io/api/v1`.

---

### Enrichment

| Endpoint | Method | Description |
|---|---|---|
| `/people/match` | POST | Enrich a single person — match by email, name+company, LinkedIn URL, or domain. Returns person profile, employment history, social links. Costs 1 credit if matched. |
| `/people/bulk_match` | POST | Enrich up to 10 people in a single request. Same matching logic as `/people/match`. Costs 1 credit per matched person. |
| `/organizations/enrich` | GET | Enrich a single organization by domain. Returns company profile, technographics, funding data, headcount. Costs 1 credit. |
| `/organizations/bulk_enrich` | POST | Enrich multiple organizations by domain in a single request. Costs 1 credit per matched org. |

**`POST /people/match` — Key Parameters**:

| Parameter | Type | Description |
|---|---|---|
| `first_name` | string | Person's first name |
| `last_name` | string | Person's last name |
| `name` | string | Full name (alternative to first/last) |
| `email` | string | Email address (best match key) |
| `hashed_email` | string | MD5/SHA-256 hashed email (alternative match key) |
| `id` | string | Apollo person ID |
| `organization_name` | string | Company name |
| `domain` | string | Company domain |
| `linkedin_url` | string | LinkedIn profile URL |
| `reveal_personal_emails` | boolean | Include personal emails (default `false`; costs additional credit) |
| `reveal_phone_number` | boolean | Include direct phone numbers (default `false`). **When `true`, `webhook_url` is REQUIRED** — phone numbers are returned asynchronously to that webhook. |
| `webhook_url` | string | Webhook to receive phone numbers asynchronously. Required when `reveal_phone_number` is `true`. |
| `run_waterfall_email` | boolean | Run multi-provider waterfall to find an email |
| `run_waterfall_phone` | boolean | Run multi-provider waterfall to find a phone number |

**`POST /people/bulk_match` — Body**:
```json
{
  "details": [
    { "email": "person1@company.com" },
    { "first_name": "Jane", "last_name": "Doe", "organization_name": "Acme" }
  ],
  "reveal_personal_emails": false
}
```

**`GET /organizations/enrich` — Query Parameters**:

| Parameter | Type | Description |
|---|---|---|
| `domain` | string | Company domain to enrich (required) |

**`POST /organizations/bulk_enrich` — Body** (up to 10 companies):
```json
{
  "details": [
    { "domain": "company1.com" },
    { "name": "Globex Inc", "website": "globex.com" }
  ]
}
```
Each object in `details` may combine `domain`, `linkedin_url`, `name`, and `website`. A `domains[]` query/array form is also accepted for domain-only lookups, but `details` takes precedence if both are supplied.

---

### Search — People

| Endpoint | Method | Description |
|---|---|---|
| `/mixed_people/search` | POST | (Web/legacy app endpoint.) For API integrations use `/mixed_people/api_search` below. |
| `/mixed_people/api_search` | POST | Search Apollo's database of 270M+ contacts. Filter by title, company, location, industry, seniority, and more. Returns paginated results. **This endpoint is optimized for API usage and does NOT consume credits — it never returns email addresses or phone numbers.** Use the enrichment endpoints (`/people/match`, `/people/bulk_match`) to reveal contact info (which costs credits). |

**`POST /mixed_people/api_search` — Key Parameters**:

| Parameter | Type | Description |
|---|---|---|
| `page` | integer | Page number (1-based) |
| `per_page` | integer | Results per page (100 records per page) |
| `person_titles` | array | Job titles to match (supports similar matches by default) |
| `person_not_titles` | array | Job titles to exclude |
| `person_seniorities` | array | Seniority levels: `owner`, `founder`, `c_suite`, `partner`, `vp`, `head`, `director`, `manager`, `senior`, `entry`, `intern` |
| `q_organization_domains_list` | array | Company domains to filter by (up to 1,000 per request) |
| `organization_ids` | array | Apollo company IDs to filter by |
| `organization_industry_tag_ids` | array | Industry IDs |
| `organization_locations` | array | HQ locations (e.g., `["United States", "California"]`) |
| `organization_num_employees_ranges` | array | Employee count ranges (e.g., `["1,10", "11,50", "51,200"]`) |
| `person_locations` | array | Person's location |
| `contact_email_status` | array | Email status filter: `verified`, `unverified`, `likely to engage`, `unavailable` |
| `q_keywords` | string | Keyword search across profiles |
| `prospected_by_current_team` | array | Filter: `yes` or `no` — already prospected |

**Pagination cap**: This endpoint has a display limit of **50,000 records — 100 records per page, up to 500 pages**. Refine filters to access more data in batches.

---

### Search — Organizations

| Endpoint | Method | Description |
|---|---|---|
| `/mixed_companies/search` | POST | Search Apollo's database of companies. Filter by industry, size, location, revenue, technology, and more. Free (no credits). Same 50,000-record display limit (100 per page, up to 500 pages). |

**`POST /mixed_companies/search` — Key Parameters**:

| Parameter | Type | Description |
|---|---|---|
| `page` | integer | Page number (1-based) |
| `per_page` | integer | Results per page (max 100) |
| `organization_industry_tag_ids` | array | Industry filter |
| `organization_locations` | array | HQ location filter |
| `organization_num_employees_ranges` | array | Employee count ranges |
| `organization_revenue_ranges` | array | Revenue ranges (e.g., `["1000000,10000000"]`) |
| `q_organization_keyword_tags` | array | Technology/keyword tags |
| `q_organization_name` | string | Company name search |
| `organization_domains` | array | Filter by specific domains |

---

### Search — Job Postings & News

| Endpoint | Method | Description |
|---|---|---|
| `/organizations/{id}/job_postings` | GET | List current job postings for an organization. Useful for hiring intent signals. |
| `/news_articles/search` | POST | Search news articles related to companies or people. |

---

### Contacts

Contacts are people saved to your Apollo CRM (as opposed to the broader Apollo database searched via `/mixed_people/search`).

| Endpoint | Method | Description |
|---|---|---|
| `/contacts` | POST | Create a new contact in your Apollo CRM |
| `/contacts/{id}` | GET | Fetch a contact by ID |
| `/contacts/{id}` | PATCH | Update a contact |
| `/contacts/search` | POST | Search contacts in your Apollo CRM (paginated) |
| `/contacts/bulk_create` | POST | Create multiple contacts at once |
| `/contacts/bulk_update` | POST | Update multiple contacts at once |
| `/contacts/bulk_update_stages` | POST | Bulk update contact stages |
| `/contacts/bulk_update_owners` | POST | Bulk reassign contact owners |

**`POST /contacts` — Key Parameters**:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `first_name` | string | Yes | First name |
| `last_name` | string | Yes | Last name |
| `email` | string | Recommended | Email address |
| `organization_name` | string | No | Company name |
| `title` | string | No | Job title |
| `account_id` | string | No | Link to an Apollo account |
| `owner_id` | string | No | Assign to a user |
| `label_names` | array | No | Tags/labels |
| `phone` | string | No | Phone number |
| `linkedin_url` | string | No | LinkedIn profile URL |
| `present_raw_address` | string | No | Street address |
| `city` | string | No | City |
| `state` | string | No | State |
| `country` | string | No | Country |
| `custom_fields` | object | No | Custom field key-value pairs |

**`POST /contacts/search` — Key Parameters**:

| Parameter | Type | Description |
|---|---|---|
| `page` | integer | Page number |
| `per_page` | integer | Results per page |
| `sort_by_field` | string | Field to sort by (e.g., `contact_last_activity_date`, `contact_created_at`) |
| `sort_ascending` | boolean | Sort direction |
| `q_keywords` | string | Keyword search |
| `contact_stage_ids` | array | Filter by stage |
| `owner_ids` | array | Filter by owner |
| `label_ids` | array | Filter by labels/tags |
| `contact_email_status` | array | Filter by email status |

**`POST /contacts/bulk_create` — Body**:
```json
{
  "contacts": [
    { "first_name": "Jane", "last_name": "Doe", "email": "jane@example.com" },
    { "first_name": "John", "last_name": "Smith", "email": "john@example.com" }
  ]
}
```

**`POST /contacts/bulk_update` — Body**:
```json
{
  "contacts": [
    { "id": "contact_id_1", "title": "New Title" },
    { "id": "contact_id_2", "owner_id": "new_owner_id" }
  ]
}
```

**`POST /contacts/bulk_update_stages` — Body**:
```json
{
  "contact_ids": ["id1", "id2"],
  "contact_stage_id": "stage_id"
}
```

**`POST /contacts/bulk_update_owners` — Body**:
```json
{
  "contact_ids": ["id1", "id2"],
  "owner_id": "new_owner_id"
}
```

### Contact Stages

| Endpoint | Method | Description |
|---|---|---|
| `/contact_stages` | GET | List all contact stages configured for your team |

Returns an array of stages with `id`, `name`, `display_name`, `display_order`.

---

### Accounts

Accounts are companies saved to your Apollo CRM.

| Endpoint | Method | Description |
|---|---|---|
| `/accounts` | POST | Create a new account in your Apollo CRM |
| `/accounts/{id}` | GET | Fetch an account by ID |
| `/accounts/{id}` | PATCH | Update an account |
| `/accounts/search` | POST | Search accounts in your Apollo CRM (paginated) |
| `/accounts/bulk_create` | POST | Create multiple accounts at once |
| `/accounts/bulk_update` | POST | Update multiple accounts at once |
| `/accounts/bulk_update_stages` | POST | Bulk update account stages |
| `/accounts/bulk_update_owners` | POST | Bulk reassign account owners |

**`POST /accounts` — Key Parameters**:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Company name |
| `domain` | string | Recommended | Company website domain |
| `owner_id` | string | No | Assign to a user |
| `account_stage_id` | string | No | Set account stage |
| `phone` | string | No | Phone number |
| `industry` | string | No | Industry |
| `raw_address` | string | No | Street address |
| `city` | string | No | City |
| `state` | string | No | State |
| `country` | string | No | Country |
| `label_names` | array | No | Tags/labels |
| `custom_fields` | object | No | Custom field key-value pairs |

**`POST /accounts/search` — Key Parameters**:

| Parameter | Type | Description |
|---|---|---|
| `page` | integer | Page number |
| `per_page` | integer | Results per page |
| `sort_by_field` | string | Field to sort by |
| `sort_ascending` | boolean | Sort direction |
| `q_keywords` | string | Keyword search |
| `account_stage_ids` | array | Filter by stage |
| `owner_ids` | array | Filter by owner |
| `label_ids` | array | Filter by labels/tags |

**`POST /accounts/bulk_create` — Body**:
```json
{
  "accounts": [
    { "name": "Acme Corp", "domain": "acme.com" },
    { "name": "Globex Inc", "domain": "globex.com" }
  ]
}
```

**`POST /accounts/bulk_update` — Body**:
```json
{
  "accounts": [
    { "id": "account_id_1", "industry": "Technology" },
    { "id": "account_id_2", "owner_id": "new_owner_id" }
  ]
}
```

**`POST /accounts/bulk_update_stages` — Body**:
```json
{
  "account_ids": ["id1", "id2"],
  "account_stage_id": "stage_id"
}
```

**`POST /accounts/bulk_update_owners` — Body**:
```json
{
  "account_ids": ["id1", "id2"],
  "owner_id": "new_owner_id"
}
```

### Account Stages

| Endpoint | Method | Description |
|---|---|---|
| `/account_stages` | GET | List all account stages configured for your team |

Returns an array of stages with `id`, `name`, `display_name`, `display_order`.

---

### Deals (Opportunities)

In the API, deals live under the `/opportunities` resource (Apollo's UI label is "Deals"). **The create endpoint requires a master API key** — a regular key returns `403` with `"deals/api/v1/opportunities/create is not accessible with this api_key"`.

| Endpoint | Method | Description |
|---|---|---|
| `/opportunities` | POST | Create a new deal (master API key required) |
| `/opportunities/search` | GET | List/search all deals (paginated) |
| `/opportunities/{opportunity_id}` | GET | Fetch a deal by ID |
| `/opportunities/{opportunity_id}` | PATCH | Update a deal |

**`POST /opportunities` — Key Parameters**:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Deal name |
| `owner_id` | string | No | Assign to a user |
| `opportunity_stage_id` | string | No | Deal stage |
| `amount` | number | No | Deal value (no commas or currency symbols) |
| `closed_date` | string | No | Estimated close date (`YYYY-MM-DD`) |
| `account_id` | string | No | Associated account |
| `contact_ids` | array | No | Associated contacts |
| `custom_fields` | object | No | Custom field key-value pairs |

**`GET /opportunities/search` — Query Parameters**:

| Parameter | Type | Description |
|---|---|---|
| `page` | integer | Page number |
| `per_page` | integer | Results per page |
| `sort_by_field` | string | Field to sort by |
| `sort_ascending` | boolean | Sort direction |

### Deal Stages

| Endpoint | Method | Description |
|---|---|---|
| `/opportunity_stages` | GET | List all deal stages and pipeline configuration |

---

### Sequences (Emailer Campaigns)

Apollo calls sequences "emailer campaigns" in the API.

| Endpoint | Method | Description |
|---|---|---|
| `/emailer_campaigns/search` | POST | Search sequences with filters (name, status, labels, etc.) |
| `/emailer_campaigns/{id}/activate` | POST | Activate a paused or draft sequence |
| `/emailer_campaigns/{id}/deactivate` | POST | Pause/deactivate an active sequence |
| `/emailer_campaigns/{id}/archive` | POST | Archive a sequence |
| `/emailer_campaigns/{sequence_id}/add_contact_ids` | POST | Add one or more contacts to a sequence |
| `/emailer_campaigns/remove_or_stop_contact_ids` | POST | Update a contact's status in a sequence — `mode` = `mark_as_finished` / `remove` / `stop`. **Requires a master API key** (else `403 API_INACCESSIBLE`). |
| `/emailer_messages/{id}/activities` | GET | Get activities/stats for a sent sequence email (opens, clicks, replies) |

**`POST /emailer_campaigns/search` — Key Parameters**:

| Parameter | Type | Description |
|---|---|---|
| `page` | integer | Page number |
| `per_page` | integer | Results per page |
| `q_name` | string | Search by sequence name |
| `label_ids` | array | Filter by labels |
| `status` | string | Filter: `active`, `paused`, `archived`, `draft` |
| `creator_ids` | array | Filter by creator |

**`POST /emailer_campaigns/{sequence_id}/add_contact_ids` — Body**:
```json
{
  "contact_ids": ["contact_id_1", "contact_id_2"],
  "send_email_from_email_account_id": "email_account_id",
  "sequence_active_in_other_campaigns": false,
  "sequence_no_email": false,
  "sequence_finished_in_other_campaigns": false
}
```
(The sequence is identified by the `{sequence_id}` path param.)

**`POST /emailer_campaigns/remove_or_stop_contact_ids` — Body** (master API key required):
```json
{
  "emailer_campaign_id": "sequence_id",
  "contact_ids": ["contact_id_1"],
  "mode": "stop"
}
```

`mode` options: `mark_as_finished` (mark contacts as finished), `remove` (remove from sequence), `stop` (halt progress).

---

### Tasks

| Endpoint | Method | Description |
|---|---|---|
| `/tasks` | POST | Create a task |
| `/tasks/bulk_create` | POST | Create multiple tasks at once |
| `/tasks/search` | POST | Search tasks with filters |

**`POST /tasks` — Key Parameters**:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `type` | string | Yes | Task type: `call`, `email`, `action_item`, `linkedin` |
| `priority` | string | No | Priority: `high`, `medium`, `low` |
| `due_at` | string | No | Due date (ISO 8601) |
| `note` | string | No | Task description/notes |
| `contact_ids` | array | No | Associated contacts |
| `account_ids` | array | No | Associated accounts |
| `owner_id` | string | No | Assign to a user |
| `status` | string | No | Status: `open`, `complete` |

**`POST /tasks/bulk_create` — Body**:
```json
{
  "tasks": [
    { "type": "call", "contact_ids": ["id1"], "due_at": "2024-03-01T10:00:00Z" },
    { "type": "email", "contact_ids": ["id2"], "priority": "high" }
  ]
}
```

**`POST /tasks/search` — Key Parameters**:

| Parameter | Type | Description |
|---|---|---|
| `page` | integer | Page number |
| `per_page` | integer | Results per page |
| `type` | string | Filter by task type |
| `status` | string | Filter: `open`, `complete` |
| `owner_ids` | array | Filter by owner |
| `due_at_range` | object | Filter by due date range (`from`, `to` in ISO 8601) |

---

### Calls

| Endpoint | Method | Description |
|---|---|---|
| `/phone_calls` | POST | Log a call |
| `/phone_calls/search` | GET | Search/list calls with filters |
| `/phone_calls/{id}` | PUT | Update a call record |

**`POST /phone_calls` — Key Parameters**:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `contact_id` | string | Yes | Contact the call is with |
| `user_id` | string | No | User who made the call |
| `note` | string | No | Call notes |
| `disposition` | string | No | Call outcome (e.g., `interested`, `not_interested`, `no_answer`, `left_voicemail`) |
| `duration` | integer | No | Call duration in seconds |
| `direction` | string | No | `inbound` or `outbound` |
| `recording_url` | string | No | URL to call recording |

**`GET /phone_calls/search` — Query Parameters**:

| Parameter | Type | Description |
|---|---|---|
| `page` | integer | Page number |
| `per_page` | integer | Results per page |
| `contact_id` | string | Filter by contact |
| `user_id` | string | Filter by user |
| `sort_by_field` | string | Field to sort by |
| `sort_ascending` | boolean | Sort direction |

---

### Users & Team

| Endpoint | Method | Description |
|---|---|---|
| `/users` | GET | List all users in your Apollo team |

Returns an array of users with `id`, `email`, `first_name`, `last_name`, `team_id`, `role`.

---

### Email Accounts

| Endpoint | Method | Description |
|---|---|---|
| `/email_accounts` | GET | List email accounts (mailboxes) connected for sending |

Returns email accounts with `id`, `email`, `type`, `active`, `daily_limit`, `emails_sent_today`.

---

### Labels (Tags)

| Endpoint | Method | Description |
|---|---|---|
| `/labels` | GET | List all labels/tags configured for your team |

Returns labels with `id`, `name`, `created_at`. Labels can be applied to contacts, accounts, and sequences.

---

### Custom Fields

| Endpoint | Method | Description |
|---|---|---|
| `/typed_custom_fields` | GET | List all custom fields configured for your team |
| `/typed_custom_fields` | POST | Create a new custom field |

**`GET /typed_custom_fields` — Response**:

Returns custom fields with `id`, `name`, `field_type`, `picklist_values`, `entity_type` (`contact`, `account`, `deal`).

**`POST /typed_custom_fields` — Body**:
```json
{
  "name": "Contract Value",
  "field_type": "number",
  "entity_type": "contact",
  "picklist_values": []
}
```

Field types: `text`, `number`, `date`, `datetime`, `boolean`, `picklist`, `multi_picklist`, `url`.

---

### Usage & Rate-Limit Stats

| Endpoint | Method | Description |
|---|---|---|
| `/usage_stats/api_usage_stats` | POST | View per-endpoint API usage and rate limits. **Requires a master API key** (non-master keys return `403`). |

**Response shape** — per endpoint, broken out by `day` / `hour` / `minute`, each window reporting `limit`, `consumed`, and `left_over`:
```json
{
  "/contacts/search": {
    "day":    { "limit": 2000, "consumed": 120, "left_over": 1880 },
    "hour":   { "limit": 500,  "consumed": 40,  "left_over": 460 },
    "minute": { "limit": 200,  "consumed": 5,   "left_over": 195 }
  }
}
```

---

## Common Automation Patterns

**Prospect and enrich**: Search for people via `POST /mixed_people/api_search` (free, returns no contact info), then enrich with `POST /people/match` to get verified emails and phone numbers, then create as contacts via `POST /contacts`.

**Build target account lists**: Search organizations via `POST /mixed_companies/search` with filters (industry, size, tech stack, location), then create accounts via `POST /accounts/bulk_create`.

**Sequence enrollment**: Create contacts, then enroll them in a sequence via `POST /emailer_campaigns/{sequence_id}/add_contact_ids`. Monitor sent-email performance via `GET /emailer_messages/{id}/activities`.

**CRM enrichment**: For existing contacts, use `POST /people/bulk_match` with email addresses to enrich profiles with latest title, company, phone, and social data.

**Hiring intent signals**: Use `GET /organizations/{id}/job_postings` to monitor target accounts' hiring activity as a buying signal.

**Credit-efficient enrichment**: Check `POST /usage_stats/api_usage_stats` (master key) before bulk operations. Use `POST /people/bulk_match` (up to 10 per request) instead of individual `/people/match` calls to reduce rate limit impact.

**Contact stage tracking**: Use `GET /contact_stages` to list stages, then `POST /contacts/bulk_update_stages` to move contacts through your pipeline in bulk.

**Multi-channel outreach**: Create tasks via `POST /tasks/bulk_create` for call and LinkedIn touchpoints alongside email sequences to coordinate multi-channel cadences.

---

## Key Differences from Other Sales APIs

| Feature | Apollo Behavior |
|---|---|
| Search endpoints | Use **POST** with JSON body. For API integrations, the people search path is `/mixed_people/api_search` and company search is `/mixed_companies/search`. |
| Sequences | Called "emailer_campaigns" in the API |
| Deals | Called "opportunities" in the API (`/opportunities`, `/opportunity_stages`); deal create needs a master API key |
| Calls | Called "phone_calls" in the API (`/phone_calls`) |
| Contact vs. Person | "Contact" = saved to your CRM; "Person" = in Apollo's broader database |
| Credits | Enrichment reveals cost credits (email ≈1, phone ≈8); search and CRM operations are free |
| Pagination cap | People/company search limited to 50,000 records (100/page × 500 pages) per query |
| Bulk match limit | `/people/bulk_match` and `/organizations/bulk_enrich` accept up to 10 records per request |
| Async phone reveal | `reveal_phone_number=true` requires a `webhook_url`; numbers arrive asynchronously |
| Custom fields | Use `/typed_custom_fields` endpoint; pass values as `custom_fields` object on contacts/accounts |

---

## Source URLs

(Docs are JS-rendered; append `.md` to any reference URL for the raw OpenAPI/Markdown version. Page index: https://docs.apollo.io/llms.txt)

- API Documentation: https://docs.apollo.io/
- Authentication: https://docs.apollo.io/reference/authentication
- OAuth 2.0 flow: https://docs.apollo.io/docs/use-oauth-20-authorization-flow-to-access-apollo-user-information-partners
- Rate Limits: https://docs.apollo.io/reference/rate-limits
- View API Usage Stats: https://docs.apollo.io/reference/view-api-usage-stats
- People Enrichment: https://docs.apollo.io/reference/people-enrichment
- Bulk People Enrichment: https://docs.apollo.io/reference/bulk-people-enrichment
- Organization Enrichment: https://docs.apollo.io/reference/organization-enrichment
- Bulk Organization Enrichment: https://docs.apollo.io/reference/bulk-organization-enrichment
- People Search: https://docs.apollo.io/reference/people-api-search
- Organization Search: https://docs.apollo.io/reference/organization-search
- Contacts: https://docs.apollo.io/reference/create-a-contact
- Accounts: https://docs.apollo.io/reference/create-an-account
- Deals (Opportunities): https://docs.apollo.io/reference/create-deal
- Sequences: https://docs.apollo.io/reference/search-for-sequences
- Tasks: https://docs.apollo.io/reference/create-a-task
- Calls (Phone Calls): https://docs.apollo.io/reference/create-call-records
