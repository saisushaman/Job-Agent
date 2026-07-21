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
- [ ] Ollama integration
- [ ] Qwen3 (`qwen3:8b` default, configurable)
- [ ] AIProvider abstraction + OllamaProvider
- [ ] Structured JSON output validation (Pydantic) + retry
- [ ] Ollama health check
- [ ] Test prompt endpoint

## Phase 3 — Resume system
- [ ] Upload PDF/DOCX/TXT
- [ ] Parse resume text
- [ ] Store metadata + parsed text
- [ ] Resume versions (Master, SWE, AI, Cloud, DevOps)
- [ ] Management UI, preview, version history

## Phase 4 — Job analysis
- [ ] USA vs Europe classification
- [ ] Sponsorship / work-auth analysis (with evidence)
- [ ] Relocation, English compatibility
- [ ] Skill / experience / salary extraction

## Phase 5 — Matching engine
- [ ] Weighted scoring + overall + recommendation
- [ ] Local embeddings semantic similarity

## Phase 6 — Dashboard
- [ ] Stats, USA/Europe, sponsorship, top matches, pipeline
- [ ] Search & filtering, job detail + analysis

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
