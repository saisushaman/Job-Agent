-- Runs automatically on first Postgres container start (docker-entrypoint-initdb.d).
-- Enables the pgvector extension used for local embedding similarity search (Phase 5).
CREATE EXTENSION IF NOT EXISTS vector;
