# Job-Agent

A **local-first, zero-paid-API** AI Job Search & Application Management platform. All AI
runs locally via **Ollama + Qwen3**; there are no OpenAI/Anthropic/Gemini or other paid
API calls anywhere in the system.

See [`PROJECT_SPEC.md`](PROJECT_SPEC.md) for the full vision and phase plan, and
[`TASKS.md`](TASKS.md) for progress.

> **Current status: Phase 1 (Foundation) complete.** Monorepo, FastAPI backend, Next.js
> frontend, database layer, health check, and a basic dashboard that talks to the backend.
> Scraping, browser automation, email, and AI analysis arrive in later phases.

## Repository layout

```
job-agent/
├── PROJECT_SPEC.md      full product spec & phase plan
├── TASKS.md             phase checklist
├── CLAUDE.md            working agreement / rules
├── docker-compose.yml   Postgres + pgvector (for when you move off SQLite)
├── .env.example
├── backend/             FastAPI app, models, migrations, tests
├── frontend/            Next.js + TypeScript + Tailwind
├── workers/             background workers (later phases)
├── automation/          Playwright framework (later phases)
├── ai/prompts/          prompt templates (later phases)
├── database/            DB init scripts / notes
├── scripts/             dev/ops helpers
└── docs/
```

## Prerequisites

- **Python 3.12** and [`uv`](https://docs.astral.sh/uv/) (backend)
- **Node.js 20+** and npm (frontend)
- Docker Desktop — **optional in Phase 1**, only needed to run Postgres+pgvector later

## Quick start

### 1. Backend (FastAPI)

```bash
cd backend
uv sync                      # creates .venv and installs deps (pins Python 3.12)
cp ../.env.example .env      # or: copy ..\.env.example .env   (Windows)
uv run alembic upgrade head  # create the SQLite schema
uv run uvicorn app.main:app --reload --port 8000
```

- API root: http://localhost:8000/
- Health check: http://localhost:8000/api/health
- Interactive docs: http://localhost:8000/docs

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # sets NEXT_PUBLIC_API_URL
npm run dev
```

- Dashboard: http://localhost:3000
- The dashboard's status badge calls the backend `GET /api/health` to prove the two
  services communicate.

## Running tests

```bash
# backend
cd backend && uv run pytest

# frontend
cd frontend && npm test
```

## Database

Phase 1 uses **SQLite** by default (`DATABASE_URL=sqlite:///./job_agent.db`) so the app
runs with no extra services. To switch to **Postgres + pgvector**:

```bash
docker compose up -d
# then set DATABASE_URL in backend/.env to:
# postgresql+psycopg://job_agent:job_agent@localhost:5432/job_agent
uv run alembic upgrade head
```

Migrations are managed with Alembic (`backend/alembic/`).

## Principles

- Local & free (Ollama + Qwen3 only).
- The AI never invents facts about you.
- Visa/sponsorship analysis is evidence-based — never a guarantee.
- Nothing irreversible happens without your explicit confirmation.
