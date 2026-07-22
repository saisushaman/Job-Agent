# Project Progress

## Phase 1 — Foundation
- [x] Monorepo structure
- [x] Backend (FastAPI)
- [x] Frontend (Next.js + TS + Tailwind)
- [x] Database config (SQLite dev; Postgres+pgvector via Docker for later)
- [x] SQLAlchemy models + Alembic migration
- [x] Docker Compose (Postgres + pgvector)
- [x] .env.example
- [x] README with setup instructions
- [x] Health check endpoint
- [x] Basic dashboard page
- [x] Frontend ↔ backend communication verified
- [x] Basic tests (backend pytest, frontend vitest)

## Phase 2 — Local AI layer
- [x] Ollama integration
- [x] Qwen3 (`qwen3:8b` default, configurable via .env)
- [x] AIProvider abstraction + OllamaProvider
- [x] Structured JSON output validation (Pydantic) + retry
- [x] Ollama health check (`GET /api/ai/health`)
- [x] Test prompt endpoint (`POST /api/ai/test`, `POST /api/ai/test-structured`)

## Phase 3 — Resume system
- [x] Upload PDF/DOCX/TXT
- [x] Parse resume text (pypdf / python-docx / txt)
- [x] Store metadata + parsed text (+ original file on disk)
- [x] Resume versions (Master, SWE, AI, Cloud, DevOps — seeded)
- [x] Management UI, preview, version history, download

## Phase 4 — Job analysis
- [x] USA vs Europe classification
- [x] Sponsorship / work-auth analysis (with evidence)
- [x] Relocation, English compatibility
- [x] Skill / experience / salary extraction
- [x] Citizenship / security-clearance detection → deterministic NOT_ELIGIBLE (never apply)
- [x] Job import CRUD + POST /api/jobs/{id}/analyze (local Qwen3, structured output)

## Phase 5 — Matching engine
- [x] Weighted scoring (technical/experience/sponsorship/location/language/relocation)
- [x] Overall score + recommendation (APPLY/REVIEW/LOW_PRIORITY/DO_NOT_APPLY)
- [x] NOT_ELIGIBLE (citizenship/no-sponsorship) hard-maps to DO_NOT_APPLY
- [x] Local embeddings (nomic-embed-text) semantic similarity for technical match
- [x] Candidate profile GET/PUT; matched/missing skills; Qwen3 reasoning
- [x] POST/GET /api/jobs/{id}/match

## Phase 6 — Dashboard
- [x] Stats (totals, pipeline, USA/Europe, sponsorship, recommendations, eligibility)
- [x] Top matching jobs (excludes DO_NOT_APPLY)
- [x] Job search & filtering (q, region, country, company, eligibility, recommendation,
      min score, remote)
- [x] Job detail page with analysis + match display
- [x] Candidate profile editor UI; shared nav across pages

## Phase 7 — Application tracker
- [ ] Status lifecycle, records, Kanban + drag/drop, detail, audit

## Phase 8 — Resume tailoring & cover letters
- [ ] Tailor resume, cover letter, draft answers, before/after, approval

## Phase 9 — Email (Gmail OAuth)
- [ ] OAuth, token storage, sync, classification, match, dashboard

## Phase 10 — Excel export
- [ ] openpyxl workbook + sheets (no passwords)

## Phase 11 — Playwright assistance
- [ ] Compliant automation, mock form, preview + explicit confirm
