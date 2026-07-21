# CLAUDE.md — Working agreement for this repo

This is an incremental, phase-based build. Follow these rules on **every** task.

## Before starting any task
1. Read `PROJECT_SPEC.md`.
2. Read `TASKS.md`.
3. Read `README.md`.
4. Inspect the existing code.
5. Do **not** rewrite working code unnecessarily.
6. Implement **only** the requested phase.
7. Run tests.
8. Update `TASKS.md`.
9. Update documentation.
10. Report what changed.

## Hard product rules (never violate)
- **Local & free only.** AI = local Qwen3 via Ollama; embeddings = local model. No paid
  APIs (OpenAI/Anthropic/Gemini/etc.).
- **The AI never invents facts** — no fabricated jobs, employers, degrees, certifications,
  skills, projects, experience, or achievements. Only use facts from the user's profile,
  resume, and imported job text.
- **Never guarantee a visa outcome.** Sponsorship analysis is evidence-based.
- **Human-in-the-loop.** No application submitted, email sent, or destructive action
  without explicit user confirmation. `AUTO_SUBMIT=false` by default.
- **Compliant automation only.** Never bypass CAPTCHA, anti-bot, rate limits, or security
  controls.

## Conventions
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, `uv` for deps.
- Frontend: Next.js App Router, TypeScript, Tailwind v4.
- Config comes from env (`.env`); never commit secrets. Keep `.env.example` current.
- Database URL is configurable; SQLite for dev, Postgres+pgvector for prod.
- Add/keep tests green before declaring a phase done. Smoke-test real wiring, not just
  unit mocks.
