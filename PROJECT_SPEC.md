# PROJECT_SPEC — Local-First AI Job Search & Application Management Platform

> **Status of this document:** synthesized from the phase-by-phase brief. It is the
> source of truth for what the system should become. Refine it as requirements sharpen.

## 1. Vision

A **local-first**, **zero-paid-API** platform that helps a single user (the candidate)
discover, analyze, track, and apply to jobs — with an emphasis on **visa sponsorship /
work-authorization intelligence** for USA and Europe. All AI runs locally via **Ollama +
Qwen3**. No OpenAI/Anthropic/Gemini or any paid API is used anywhere.

### Non-negotiable principles

- **Local-first & free.** The only AI engine is local Qwen3 via Ollama. Embeddings use a
  local model. No paid APIs, ever.
- **The AI never invents facts.** It must never fabricate jobs, employers, degrees,
  certifications, skills, projects, experience, or achievements. It works only from facts
  in the user's profile, resume, and the imported job text.
- **Never guarantee visa outcomes.** Sponsorship analysis is evidence-based and
  probabilistic; it must never claim approval is guaranteed.
- **Human-in-the-loop for anything irreversible.** No application is submitted, no email
  is sent, and no destructive action is taken without explicit user confirmation.
- **Compliance-first automation.** Browser automation must never bypass CAPTCHAs,
  anti-bot systems, rate limits, or security controls.

## 2. Architecture

Monorepo:

```
job-agent/
├── backend/     FastAPI (Python) — API, DB, AI orchestration, services
├── frontend/    Next.js + TypeScript + Tailwind — dashboard & UI
├── workers/     background jobs (email sync, analysis queues) — later phases
├── automation/  Playwright application-assistance framework — later phases
├── ai/          prompt templates & AI assets
├── database/    SQL, seed data, pgvector setup notes
├── scripts/     dev/ops helper scripts
└── docs/        additional documentation
```

### Tech stack

| Layer      | Choice                                                              |
|------------|---------------------------------------------------------------------|
| Backend    | Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2          |
| AI         | Ollama + Qwen3 (`qwen3:8b` default), local embedding model          |
| DB (prod)  | PostgreSQL + pgvector (via Docker Compose)                          |
| DB (dev)   | SQLite (Phase 1 fallback so the app runs before Docker is set up)   |
| Frontend   | Next.js 15 (App Router), TypeScript, Tailwind CSS v4                |
| Automation | Playwright (Phase 11)                                               |
| Export     | openpyxl (Phase 10)                                                 |

> **Database note:** The app reads `DATABASE_URL` from env. Phase 1 defaults to SQLite so
> it runs today; switching to Postgres+pgvector later is just a URL change plus running
> the provided `docker-compose.yml`. Vector columns/search are stubbed until pgvector is
> live.

## 3. Phase plan

The build is strictly incremental. **Do not start a phase until the previous one runs and
its tests pass.**

- **Phase 1 — Foundation (this phase).** Monorepo, FastAPI backend, Next.js frontend,
  DB config + models + migrations, Docker Compose, `.env.example`, README, health check
  endpoint, basic dashboard page, verified frontend↔backend communication, basic tests.
  **Explicitly NOT in Phase 1:** scraping, browser automation, Playwright, Gmail/Outlook,
  auto-applications, credential management, AI analysis.
- **Phase 2 — Local AI layer.** Ollama integration, Qwen3, `AIProvider` abstraction +
  `OllamaProvider`, structured JSON output validated with Pydantic + retry on invalid
  JSON, Ollama health check, a test prompt endpoint.
- **Phase 3 — Resume system.** Upload PDF/DOCX/TXT, parse text, store metadata + parsed
  text, resume versions (Master, Software Engineer, AI Engineer, Cloud Engineer, DevOps
  Engineer), management UI, preview, version history. AI must not invent content.
- **Phase 4 — Job analysis (Qwen3).** Analyze manually imported jobs: USA vs Europe
  classification, sponsorship & work-authorization analysis, relocation, English
  compatibility, skill extraction, experience requirements, salary extraction. Evidence
  required; never guarantee visas. Structured Pydantic output.
- **Phase 5 — Matching engine.** Score Technical/Experience/Sponsorship/Location/Language/
  Relocation with default weights (35/20/25/10/5/5), overall score + recommendation
  (APPLY / REVIEW / LOW_PRIORITY / DO_NOT_APPLY), reasoning, matched/missing skills,
  sponsorship evidence, concerns. Local embeddings for semantic similarity.
- **Phase 6 — Dashboard.** Stats (total/review/approved/applied/interview/offers/
  rejected), USA & Europe breakdowns, sponsorship stats, top matches, pipeline, search &
  filtering, job detail + analysis display. Responsive, modern UI.
- **Phase 7 — Application tracker.** Full status lifecycle, application records, Kanban
  board with drag-and-drop, application detail page, history/audit events.
- **Phase 8 — Resume tailoring & cover letters.** For an approved job: pick best resume
  version, tailor via Qwen3, generate cover letter + draft answers, before/after diff,
  require approval before saving, document generation. Never invent facts.
- **Phase 9 — Email (Gmail OAuth).** OAuth (no passwords), secure token storage, sync,
  local Qwen3 classification (confirmation/recruiter/interview/assessment/rejection/offer/
  follow-up/other) with confidence + NEEDS_REVIEW, match emails to applications, update
  status, email dashboard. Never delete emails.
- **Phase 10 — Excel export.** openpyxl workbook (Applications/Jobs/Interviews/Offers/
  Rejected/Statistics/Credential Inventory). Never export passwords; credential inventory
  holds only references.
- **Phase 11 — Playwright application assistance.** Generic, compliant automation:
  `AUTO_SUBMIT=false` default, detect fields, fill profile, upload resume/cover letter,
  pause on CAPTCHA/security challenge, preview, explicit confirmation before submit.
  No site-specific bypass. Start with a local mock form + tests.

## 4. Domain enums (reference for later phases)

**Application status:** DISCOVERED, REVIEW, APPROVED, APPLICATION_READY, APPLYING,
APPLIED, RESPONSE_RECEIVED, INTERVIEW, OFFER, REJECTED, ON_HOLD, NOT_ELIGIBLE.

**USA sponsorship:** SPONSORSHIP_EXPLICIT, SPONSORSHIP_LIKELY, SPONSORSHIP_UNCLEAR,
SPONSORSHIP_UNLIKELY, NO_SPONSORSHIP, WORK_AUTH_REQUIRED.

**Europe visa:** VISA_SUPPORT_EXPLICIT, VISA_SUPPORT_LIKELY, VISA_SUPPORT_UNCLEAR,
VISA_SUPPORT_UNLIKELY, NO_VISA_SUPPORT, EU_WORK_AUTH_REQUIRED.

**Recommendation:** APPLY, REVIEW, LOW_PRIORITY, DO_NOT_APPLY.

**Email classification:** APPLICATION_CONFIRMATION, RECRUITER_CONTACT, INTERVIEW,
ASSESSMENT, REJECTION, OFFER, FOLLOW_UP, OTHER (+ NEEDS_REVIEW when low confidence).

## 5. Working agreement (see CLAUDE.md)

Before any task: read PROJECT_SPEC.md, TASKS.md, README.md; inspect existing code; don't
rewrite working code; implement only the requested phase; run tests; update TASKS.md and
docs; report what changed.
