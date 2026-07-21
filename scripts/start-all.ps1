# start-all.ps1 — start the Job-Agent backend + frontend locally (production mode).
# Ollama/Qwen runs as its own background service and is NOT started here.
#
# Run manually:   powershell -ExecutionPolicy Bypass -File scripts\start-all.ps1
# Or register it to auto-start at logon (see scripts/README or the project docs).

$ErrorActionPreference = "Stop"
$root     = Split-Path -Parent $PSScriptRoot     # repo root (this script lives in scripts/)
$backend  = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

Write-Host "Starting Job-Agent from $root ..."

# --- Backend: apply migrations, then serve without --reload (stable for always-on) ---
Start-Process powershell -WorkingDirectory $backend -WindowStyle Minimized -ArgumentList @(
  "-NoExit", "-Command",
  "uv run alembic upgrade head; uv run uvicorn app.main:app --host 127.0.0.1 --port 8000"
)

# --- Frontend: build once if needed, then serve the production build ---
Start-Process powershell -WorkingDirectory $frontend -WindowStyle Minimized -ArgumentList @(
  "-NoExit", "-Command",
  "if (-not (Test-Path .next)) { npm run build }; npm run start"
)

Write-Host "Backend:  http://localhost:8000/api/health"
Write-Host "Frontend: http://localhost:3000"
