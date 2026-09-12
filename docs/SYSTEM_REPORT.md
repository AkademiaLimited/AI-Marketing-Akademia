# AI Marketing Akademia — System Report

## 1. Overview

AI Marketing Akademia is a full-stack B2B marketing automation platform with two sides:

- **Public marketing website** — Next.js 16 server-rendered pages showcasing 4 AI products (AI Pod, AI Recruiter, AI Dojo, AI World), a contact form, and company content.
- **Authenticated admin workspace** — A password-protected dashboard for managing products, leads, campaigns, email drafts, content, automations, and AI workflows.

The system uses **FastAPI** (Python) for the backend, **Next.js 16** (TypeScript/React) for the frontend, **PostgreSQL** for data, **Redis + Celery** for background tasks, and **Groq** (LLM) for AI content generation and lead qualification. **LangGraph** orchestrates the lead research workflow.

---

## 2. Folder Map

AI-Marketing-Akademia/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── main.py                   # FastAPI app entry, CORS, router registration
│   │   ├── api/
│   │   │   └── routers/              # 10 REST routers (auth, products, leads, etc.)
│   │   ├── core/
│   │   │   ├── config.py             # Environment settings (pydantic-settings)
│   │   │   ├── database.py           # Async SQLAlchemy engine + session
│   │   │   ├── auth.py               # JWT, bcrypt, password policy, rate limiting
│   │   │   ├── celery_app.py         # Celery app configuration
│   │   │   ├── init_db.py            # Startup DB init with retries
│   │   │   └── seed.py               # Demo data + admin account
│   │   ├── models/                   # 11 SQLAlchemy ORM models
│   │   ├── schemas/                  # 10 Pydantic schema files
│   │   ├── ai/
│   │   │   └── groq_client.py        # Async Groq LLM client wrapper
│   │   ├── services/
│   │   │   ├── research.py           # LangGraph workflow (lead research)
│   │   │   └── tracking.py           # Workflow run + activity audit helpers
│   │   └── tasks/
│   │       ├── automation.py         # Celery: AI lead discovery
│   │       └── content.py            # Celery: content generation + publishing
│   ├── tests/                        # 44 pytest tests (API, auth, security, workflows)
│   ├── .env.example                  # Template env file (placeholders only)
│   ├── Dockerfile                    # Multi-stage Python build
│   ├── requirements.txt              # Python dependencies
│   └── pyproject.toml                # pytest config
├── frontend/                         # Next.js 16 application
│   ├── src/
│   │   ├── app/
│   │   │   ├── (marketing)/          # Public pages (home, products, about, contact)
│   │   │   └── admin/                # Protected admin workspace
│   │   │       ├── _components/      # AuthProvider, RequireAuth, Sidebar, icons
│   │   │       ├── login/page.tsx    # Admin login
│   │   │       ├── dashboard/page.tsx # Marketing overview
│   │   │       ├── leads/            # Lead list + detail + status form
│   │   │       ├── campaigns/page.tsx # Campaign list + create
│   │   │       ├── emails/page.tsx    # Email drafts + approve/reject
│   │   │       ├── automation/page.tsx # Automations + activity feed
│   │   │       ├── products/page.tsx  # Product list + publish button
│   │   │       ├── content/page.tsx   # Content list + create
│   │   │       └── settings/page.tsx  # Static settings panel
│   │   ├── lib/api.ts                # Fetch wrapper (with/without auth)
│   │   └── types/index.ts            # TypeScript API models
│   ├── package.json                  # Next.js 16, React 19, Tailwind CSS 4
│   └── next.config.ts
├── docker-compose.yml                # 5 services: db, redis, backend, worker, frontend
├── docs/
│   ├── ARCHITECTURE.md               # Architecture and maintenance guide
│   └── SYSTEM_REPORT.md              # This document
└── .gitignore                        # Ignores .env, node_modules, __pycache__, etc.

## 3. Architecture

```
┌─────────────┐     HTTP + JWT      ┌──────────────┐
│   Browser    │ ──────────────────▶ │   FastAPI    │
│  (Next.js)   │ ◀───────────────── │   Backend    │
└──────┬──────┘                     └──────┬───────┘
       │                                  │
       │                          ┌───────┴───────┐
       │                          │               │
       │                    ┌─────▼─────┐   ┌─────▼──────┐
       │                    │ PostgreSQL │   │    Redis   │
       │                    └───────────┘   └─────┬──────┘
       │                                          │
       │                                   ┌──────▼───────┐
       │                                   │   Celery     │
       │                                   │   Worker     │
       │                                   └──────┬───────┘
       │                                          │
       │                                   ┌──────▼───────┐
       │                                   │    Groq      │
       │                                   │  (LLM API)   │
       │                                   └──────────────┘
```

### Runtime Services

| Service | URL | Responsibility |
|---------|-----|---------------|
| Frontend | `http://localhost:3003` | Next.js public site + admin UI |
| Backend | `http://localhost:8000` | FastAPI REST API |
| API Docs | `http://localhost:8000/docs` | Swagger/OpenAPI docs |
| PostgreSQL | `db:5432` (Docker) | Persistent data |
| Redis | `redis:6379` (Docker) | Celery broker + results |
| Celery Worker | internal | Background AI/content tasks |

---

## 4. Security Controls

| Control | Implementation |
|---------|---------------|
| **JWT Signing** | HS256 algorithm with auto-generated 32+ char SECRET_KEY (never a default value) |
| **Token Expiry** | 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`) |
| **Password Hashing** | bcrypt via passlib |
| **Password Policy** | Min 8 chars, requires uppercase, lowercase, and digit |
| **Login Rate Limiting** | 5 attempts per 300 seconds per IP address |
| **CORS** | Restricted to configured origins |
| **Secrets Management** | `.env` files gitignored; `.env.example` contains placeholders only |
| **Token Storage** | `sessionStorage` in frontend (not `localStorage`) |
| **Auth Flow** | JWT Bearer token validated via `get_current_user` → `get_current_admin` checks `is_active` + `is_superuser` |

---

## 5. API Keys Required

### For Developers

| Secret | Required? | Where to Set | Purpose |
|--------|-----------|-------------|---------|
| `GROQ_API_KEY` | **YES** | `backend/.env` | All AI features: lead qualification, content generation, channel selection. Get one free at [groq.com](https://groq.com). |
| `DB_PASSWORD` | **YES** | `backend/.env` | PostgreSQL password. Default is `changeme` — change for production. |
| `SECRET_KEY` | No (auto) | `backend/.env` (optional) | JWT signing key. Auto-generated if empty. Override for production. |
| `NEXT_PUBLIC_API_URL` | No | `frontend/.env.local` (optional) | Frontend API URL. Defaults to `http://localhost:8000/api`. |

### Why Groq API Key Is Required

Every AI feature depends on Groq:
- **Lead Research** — LangGraph calls Groq to qualify leads and draft emails
- **Lead Discovery** — Celery task calls Groq to generate synthetic B2B candidates
- **Content Generation** — Celery chain calls Groq for platform-specific copy
- **Channel Selection** — Groq estimates best channels per product category

Without `GROQ_API_KEY`, all AI features return errors. The app will still function for CRUD operations and manual data entry.

### Why Other Keys Are NOT Currently Needed

| Provider | Status | Future Use |
|----------|--------|------------|
| Email (SMTP/Resend/SendGrid) | Not connected | Real email delivery |
| LinkedIn | Not connected | Official API publishing |
| Instagram/Meta | Not connected | Graph API publishing |
| Twilio | Not connected | Phone call automation |
| Search API | Not connected | Real lead research via web search |

## 6. Admin Features

### 6.1 Dashboard (`/admin/dashboard`)
**File:** `frontend/src/app/admin/dashboard/page.tsx`
**API:** `GET /api/dashboard/summary`, `GET /api/leads`, `GET /api/campaigns`

**What it shows:**
- 5 stat cards: New leads, Contacted, Responded, Meetings, Customers
- Visual lead pipeline funnel (5-stage with dotted connectors)
- "Needs your attention" list — leads with status `new` or `needs-followup`
- Campaign status chips (running/paused/completed)

**How it works:**
1. On page load, parallel `apiFetchWithAuth` calls fetch dashboard summary, all leads, and all campaigns
2. `needsAttention` = leads where status is `new` or `needs-followup`
3. Dashboard summary comes from a single SQL `GROUP BY Lead.status` count query

### 6.2 Leads (`/admin/leads`)
**Files:** `frontend/src/app/admin/leads/page.tsx`, `frontend/src/app/admin/leads/[id]/page.tsx`, `frontend/src/app/admin/leads/[id]/lead-status-form.tsx`
**API:** `GET /api/leads`, `GET /api/leads/{id}`, `POST /api/leads`, `PATCH /api/leads/{id}/status`, `POST /api/leads/{id}/research-email`

**What it does:**
- List all leads in a table with status badges
- Inline "Add lead" form (creates lead with client-generated UUID, status `new`)
- Per-lead detail page with contact info, product, problem, reasoning
- Status change form (dropdown of 7 statuses: new, contacted, responded, needs-followup, meeting, customer, lost)
- **AI Research button** — triggers LangGraph workflow to research the lead's website and draft an outreach email

**How AI Research works:**
1. Admin clicks research on a lead
2. Backend calls `POST /api/leads/{id}/research-email`
3. LangGraph workflow runs (see Section 8)
4. Lead status may change to `qualified`, reasoning is stored, an email draft is created
5. Admin sees the draft in the Emails section

### 6.3 Campaigns (`/admin/campaigns`)
**File:** `frontend/src/app/admin/campaigns/page.tsx`
**API:** `GET /api/campaigns`, `POST /api/campaigns`

**What it does:**
- List campaigns with funnel visualization (6 stages: found → contacted → responded → interested → meetings → customers)
- Inline create form with zeroed funnel counts
- Each row shows a proportional bar chart of the funnel

**Data model:** Campaigns track marketing funnel metrics. They are currently manual records — no automated campaign execution exists yet.

### 6.4 Emails (`/admin/emails`)
**File:** `frontend/src/app/admin/emails/page.tsx`
**API:** `GET /api/emails`, `POST /api/emails`, `POST /api/emails/{id}/approve`, `POST /api/emails/{id}/reject`

**What it does:**
- Email draft inbox with approve/reject workflow
- Create manual drafts
- Approve/reject transitions (state machine: only `draft` can be reviewed)
- Status badges: draft, pending, approved, rejected, sent, responded, failed

**Important:** Approval does NOT send an email. A real email provider must be integrated before `approved` can become `sent`.

### 6.5 Automation (`/admin/automation`)
**File:** `frontend/src/app/admin/automation/page.tsx`
**API:** `GET /api/automations`, `GET /api/workflows/activities`

**What it shows:**
- Automation metadata records (name, status, last_run, result)
- **Recent activity feed** — audit trail from the LangGraph workflow tracking system
- Each activity shows: type, details, source URL, status, error (if failed)

**How it works:**
1. Fetch automations list and workflow activities in parallel
2. Activities come from the `marketing_activities` table (append-only audit log)
3. Status pills: red for `failed`, green for `completed`, etc.

### 6.6 Products (`/admin/products`)
**Files:** `frontend/src/app/admin/products/page.tsx`, `frontend/src/app/admin/products/product-toggle.tsx`, `frontend/src/app/admin/products/publish-button.tsx`
**API:** `GET /api/products`, `GET /api/products/{slug}`, `POST /api/products`, `PATCH /api/products/{slug}`, `POST /api/products/{slug}/publish`

**What it does:**
- List products with publish/unpublish toggle
- **Publish to Marketing button** — triggers the full AI content pipeline (see Section 9)
- Create new products with full details (problem, target, description, features, benefits, capabilities, category, price)

**Publish button states:**
- `pending` → shows "Publish to Marketing" button
- `queued`/`running` → shows spinning "Running…" indicator
- `completed` → shows green "Marketing complete" pill

### 6.7 Content (`/admin/content`)
**File:** `frontend/src/app/admin/content/page.tsx`
**API:** `GET /api/content`, `POST /api/content`

**What it does:**
- List published content (blog posts, news, daily quotes)
- Inline create form
- Status badges: published, draft, scheduled

**Note:** This is manual editorial content. AI-generated content goes to a separate `generated_content` table.

### 6.8 Settings (`/admin/settings`)
**File:** `frontend/src/app/admin/settings/page.tsx`
**API:** None (static UI)

**What it does:**
- Follow-up period dropdown
- Default sender name input
- Notify-me dropdown
- **Note:** Purely presentational — settings are not persisted

### 6.9 Login (`/admin/login`)
**File:** `frontend/src/app/admin/login/page.tsx`
**API:** `POST /api/auth/login`, `GET /api/auth/me`

**Auth flow:**
1. Admin enters email + password
2. Frontend sends form-encoded POST to `/api/auth/login`
3. Backend validates credentials (bcrypt check + rate limit check)
4. Backend returns JWT (30-min expiry)
5. Frontend stores token in `sessionStorage`
6. Frontend calls `GET /api/auth/me` to verify user and `is_superuser` flag
7. On success → redirect to `/admin/dashboard`
8. On failure → show inline error

## 7. How AI Works

### 7.1 Groq LLM Client
**File:** `backend/app/ai/groq_client.py`

The system uses **Groq** as the LLM provider with model `openai/gpt-oss-120b`. Two functions:

- **`call_groq(prompt, system_prompt, model, temperature, max_tokens)`** — Returns raw text completion
- **`call_groq_json(prompt, system_prompt, model, temperature, max_tokens)`** — Returns parsed JSON (uses `response_format={"type": "json_object"}`)

The client is a singleton — `get_client()` lazily creates one `AsyncGroq` instance.

### 7.2 AI Lead Discovery (Celery Task)
**File:** `backend/app/tasks/automation.py`

**Trigger:** Manually invoked or scheduled (not yet wired to UI button)

**Flow:**
1. Load product by slug
2. Call Groq with `SYSTEM_PROMPT_DISCOVER` → returns JSON array of 3 synthetic B2B leads
3. For each lead, call Groq again with `SYSTEM_PROMPT` → generates 2-3 sentence fit reasoning
4. Create `Lead` rows in database with `status="new"`
5. Update `Automation` row `A1` with `last_run` timestamp and result summary

**External calls:** 2 Groq API calls per lead (6 total for 3 leads)

### 7.3 AI Content Generation (Celery Chain)
**File:** `backend/app/tasks/content.py`

**Trigger:** Admin clicks "Publish to Marketing" on a product

**3-stage Celery chain:**

**Stage 1: `generate_content`**
- Load product by ID
- Call Groq with `SYSTEM_PROMPT_CONTENT` → returns JSON with platform-specific copy for Instagram, LinkedIn, Twitter, Email
- For each platform, create a `GeneratedContent` row (`status="generated"`)
- Returns `{product_id, product_name, platforms, content_ids}`

**Stage 2: `select_channels`**
- Apply category-based routing rules:
  - `business` → `["linkedin", "email"]`
  - `fashion` → `["instagram", "pinterest"]`
  - `general` → `["twitter", "tiktok"]`
- If category not in rules, call Groq with `SYSTEM_PROMPT_CHANNEL` to estimate best channels (0-1 score per channel, keep >0.5)
- Returns `{product_id, product_name, channels, content_ids}`

**Stage 3: `publish_content`**
- For each selected channel, create a `PublishLog` row
- **Simulated publishing** — fabricates `post_url = f"https://{platform}.com/p/{uuid}"` and sets `status="published"`
- Update product `marketing_status="completed"` and `marketing_result` summary
- Returns publish results per channel

**Important:** Publishing is SIMULATED. No real API calls to social platforms. URLs are fabricated.

### 7.4 AI Lead Research (LangGraph)
**File:** `backend/app/services/research.py`

**Trigger:** Admin clicks "Research" on a lead → `POST /api/leads/{id}/research-email`

**4-node LangGraph workflow:**

1. **`load_context`** — Load lead + parent product from database
2. **`research_website`** — Fetch lead's website with httpx, parse HTML, extract readable text (12,000 char limit)
3. **`qualify_and_draft`** — Call Groq with `RESEARCH_SYSTEM_PROMPT` → returns JSON with `qualification_score` (0-1), `qualification_reason`, `subject`, `body`
4. **`persist_draft`** — Store reasoning on lead, create `Email` draft row if score ≥ 0.7

**Output:** `{lead_id, company, website, qualification_score, qualification_reason, email_id, email_status, subject, body, workflow_run_id}`

### 7.5 How LangGraph vs LangChain

**LangChain** is the framework for building LLM applications with chains of calls.
**LangGraph** extends LangChain by allowing you to define a **state graph** where each node is a step that can read/update state, and edges control flow.

In this project:
- We use **LangGraph** (`StateGraph`) to orchestrate the lead research workflow
- Each node (`load_context`, `research_website`, `qualify_and_draft`, `persist_draft`) is a function that takes state, does work, and returns state updates
- The graph runs sequentially through these nodes
- Each node records a `MarketingActivity` row for audit trail
- If any node fails, a failed activity is recorded and the workflow is marked as failed

**Why use LangGraph instead of a simple chain?**
- Each step can have conditional logic (e.g., skip website fetch if `website_text` already provided)
- Failed nodes are isolated — we record the failure and continue to cleanup
- The state is typed and validated between steps
- Full audit trail per node (not just per workflow)

## 8. How Celery Works

### 8.1 Celery Application
**File:** `backend/app/core/celery_app.py`

**Configuration:**
- App name: `akademia_automator`
- Broker: `redis://host:port/0` (Redis)
- Backend: `redis://host:port/0` (Redis)
- Tasks auto-discovered from: `app.tasks.automation`, `app.tasks.content`
- `result_extended=True` — full result metadata
- `task_track_started=True` — emits STARTED state
- `enable_utc=True`, `timezone="UTC"`

### 8.2 Worker Process
**Command:** `celery -A app.core.celery_app.celery_app worker --loglevel=info -n akademia_worker@%h`

The worker runs in a separate Docker container (`docker-compose.yml` → `worker` service).

### 8.3 Task Chain (Content Publishing)
**Trigger:** `POST /api/products/{slug}/publish`

```python
chain(
  generate_content,      # Stage 1: Generate AI copy
  select_channels,        # Stage 2: Select best channels
  publish_content,        # Stage 3: Publish (simulated)
).apply_async()
```

Each stage receives the previous stage's result as input. The chain runs sequentially in the worker.

### 8.4 Task States
- `STARTED` — task began
- `SUCCESS` — task completed with result
- `FAILURE` — task raised an exception

### 8.5 Why Celery?
- **Non-blocking** — the API returns immediately while AI work runs in background
- **Retry** — failed tasks can be retried (not yet configured but available)
- **Scheduling** — Celery Beat can run periodic tasks (not yet configured)
- **Scalability** — multiple workers can run concurrently

### 8.6 Async Pattern in Celery Tasks
Each Celery task wraps an async core function:
```python
@celery_app.task(bind=True)
def run_lead_discovery(self, product_slug):
    self.update_state(state="STARTED")
    result = asyncio.run(discover_leads_for_product(product_slug))
    self.update_state(state="SUCCESS", meta=result)
    return result
```

Celery tasks can't be natively async, so each one uses `asyncio.run()` to execute the async core function.

## 9. How Scraping Works

### 9.1 Website Research
**File:** `backend/app/services/research.py` (node: `research_website`)

**What it does:** Fetches a lead's public website and extracts readable text for AI analysis.

**Flow:**
1. Validate URL (rejects `localhost`, `127.0.0.1`, non-http schemes)
2. `httpx.AsyncClient` GET request with:
   - 10-second timeout
   - Follows redirects
   - User-Agent: `AI-Marketer-Research/1.0`
3. Parse HTML with custom `WebsiteTextParser` (extends `html.parser.HTMLParser`)
   - Skips `<script>`, `<style>`, `<noscript>`, `<svg>` blocks
   - Extracts text from remaining elements
4. Truncate to 12,000 characters
5. Trim whitespace
6. Record `website_researched` activity with source URL and char count

### 9.2 URL Safety
**Validation rules:**
- Must be `http://` or `https://`
- Must have a netloc (hostname)
- Rejects: `localhost`, `127.0.0.1`, `0.0.0.0`, `::1`
- **Note:** Production SSRF protection should also validate private IP ranges after DNS resolution

### 9.3 What Is NOT Implemented
- **No web crawling** — only one URL is fetched per lead
- **No search engine** — no Google/Bing API for lead discovery
- **No scheduled scraping** — research is triggered manually per lead
- **No real social media scraping** — LinkedIn/Instagram content is AI-generated, not scraped

### 9.4 Future Scraping Roadmap
1. Add compliant search API (Google Custom Search, Bing API) for real lead discovery
2. Add multi-page crawling for comprehensive website research
3. Add RSS feed monitoring for content updates
4. Add rate-limited respectful scraping with robots.txt compliance

## 10. Database Schema

### 10.1 Tables

| Table | File | Key Fields | Purpose |
|-------|------|-----------|---------|
| `users` | `models/user.py` | `id` (PK=email), `email` (unique), `name`, `hashed_password`, `is_active`, `is_superuser` | Admin authentication |
| `products` | `models/product.py` | `id`, `name`, `slug` (unique), `published`, `problem`, `target`, `description`, `features`, `benefits`, `capabilities`, `category`, `price`, `marketing_status`, `marketing_result` | AI products catalog |
| `leads` | `models/lead.py` | `id` (uuid4), `company`, `website`, `industry`, `location`, `contact`, `email`, `product_id` (FK), `status`, `problem`, `reasoning`, `last_contact` | B2B leads pipeline |
| `campaigns` | `models/campaign.py` | `id`, `name`, `product_id` (FK), `target`, `status`, `found`, `contacted`, `responded`, `interested`, `meetings`, `customers` | Campaign funnel metrics |
| `emails` | `models/email.py` | `id`, `lead_name`, `product_name`, `status`, `subject`, `body` | Email draft lifecycle |
| `content` | `models/content.py` | `id`, `type`, `title`, `status`, `date`, `excerpt`, `image_url`, `tag` | Manual editorial content |
| `generated_content` | `models/generated_content.py` | `id` (uuid4), `product_id`, `platform`, `caption`, `hashtags`, `call_to_action`, `status` | AI-generated social copy |
| `publish_logs` | `models/publish_log.py` | `id` (uuid4), `product_id`, `platform`, `status`, `post_url`, `error`, `created_at` | Simulated publish audit |
| `automations` | `models/automation.py` | `id`, `name`, `status`, `last_run`, `result` | Automation metadata |
| `workflow_runs` | `models/workflow.py` | `id` (uuid4), `workflow_type`, `status`, `lead_id`, `error`, `started_at`, `finished_at` | LangGraph execution audit |
| `marketing_activities` | `models/workflow.py` | `id` (uuid4), `workflow_run_id`, `lead_id`, `email_id`, `activity_type`, `channel`, `source_url`, `status`, `provider_message_id`, `details`, `error`, `created_at` | Per-step audit trail |

### 10.2 Lead Status Flow
```
new → contacted → responded → meeting → customer
  ↓         ↓          ↓
lost       needs-followup
```

### 10.3 Email Status Flow
```
draft → approved → (future: sent → responded)
  ↓
rejected
```

### 10.4 Product Category → Channel Routing
| Category | Channels |
|----------|----------|
| `business` | LinkedIn, Email |
| `fashion` | Instagram, Pinterest |
| `general` | Twitter, Tiktok |

### 10.5 Database Initialization
**File:** `backend/app/core/init_db.py`

**Flow:**
1. `Base.metadata.create_all()` — creates missing tables (never drops)
2. If `DEMO_DATA=true` — runs all seed functions
3. Always runs `seed_users()` — creates admin account
4. Retries 12 times with 2-second delay (waits for PostgreSQL in Docker)

**Seed data (when DEMO_DATA=true):**
- 4 products (AI Pod, AI Recruiter, AI Dojo, AI World)
- 3 leads (Kampala FreshFoods, Nile Logistics, Highland People)
- 2 campaigns
- 3 emails
- 3 automations
- 3 content items
- 1 admin user (`admin@akademia.local` / `Admin@1234`)

## 11. Testing

### 11.1 Backend Tests (44 tests)
**Command:** `cd backend && .venv/bin/python -m pytest -q`

**Test files:**
| File | Tests | What it covers |
|------|-------|---------------|
| `test_api.py` | 11 | CRUD for products, leads, campaigns, emails, automations, content, dashboard, contact, auth |
| `test_security.py` | 18 | Password policy, rate limiting, secret key strength, token expiry, password hashing |
| `test_auth_schema.py` | 1 | Pydantic schema validation |
| `test_automation.py` | 3 | AI lead discovery task |
| `test_content_pipeline.py` | 4 | Content generation, channel selection, publishing |
| `test_email_review.py` | 1 | Email approve/reject state machine |
| `test_research.py` | 2 | LangGraph research workflow |
| `test_tracking.py` | 3 | Workflow tracking and audit |

**Test patterns:**
- Async tests with `@pytest.mark.anyio`
- In-memory SQLite database for tests
- FastAPI dependency overrides for DB and auth
- Mocked Groq calls for AI features

### 11.2 Frontend Tests
**Command:** `cd frontend && npm test -- --runInBand`

**Coverage:** Public pages, admin pages, login, products, emails, leads, campaigns, automations, dashboard, content, API helpers, contact flows.

## 12. Operations

### 12.1 Docker Compose Services
```yaml
services:
  db:        postgres:16-alpine     # Database
  redis:     redis:7-alpine        # Celery broker
  backend:   builds from ./backend  # FastAPI API
  worker:    builds from ./backend  # Celery worker
  frontend:  builds from ./frontend # Next.js app
```

### 12.2 Startup Commands
```bash
# Full stack
docker compose up --build

# Backend only (with logs)
docker compose up -d db redis
docker compose up --build --force-recreate backend

# Stop
docker compose down

# Reset (destructive — deletes data)
docker compose down -v
```

### 12.3 Health Check
```bash
curl http://localhost:8000/health
# → {"status":"ok"}
```

### 12.4 API Documentation
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
