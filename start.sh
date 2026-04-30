#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
UI_DIR="$ROOT/cropsense-ui"

BOLD="\033[1m"
GREEN="\033[32m"
BLUE="\033[34m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

log()  { echo -e "${BOLD}${GREEN}[CropSense]${RESET} $*"; }
info() { echo -e "${BOLD}${BLUE}[INFO]${RESET} $*"; }
warn() { echo -e "${BOLD}${YELLOW}[WARN]${RESET} $*"; }
err()  { echo -e "${BOLD}${RED}[ERROR]${RESET} $*"; }

cleanup() {
  echo ""
  log "Shutting down..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  log "Done."
}
trap cleanup SIGINT SIGTERM EXIT

# ── 1. Python virtual environment ─────────────────────────────────────────────
if [ ! -d "$ROOT/.venv" ]; then
  info "Creating Python virtual environment..."
  python3 -m venv "$ROOT/.venv"
fi

source "$ROOT/.venv/bin/activate"

info "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r "$ROOT/requirements.txt"
log "Python dependencies ready."

# ── 2. Node / npm ─────────────────────────────────────────────────────────────
if ! command -v node &>/dev/null; then
  err "Node.js not found. Install it from https://nodejs.org and re-run."
  exit 1
fi

info "Installing Node dependencies..."
npm install --prefix "$UI_DIR" --silent
log "Node dependencies ready."

# ── 3. Start FastAPI backend ───────────────────────────────────────────────────
info "Starting FastAPI backend on http://localhost:8000 ..."
cd "$ROOT"
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait until backend is ready
for i in $(seq 1 20); do
  if curl -sf http://localhost:8000/health &>/dev/null || \
     curl -sf http://localhost:8000/docs  &>/dev/null; then
    break
  fi
  sleep 1
done
log "Backend running (PID $BACKEND_PID)."

# ── 4. Start Vite frontend ─────────────────────────────────────────────────────
info "Starting React frontend on http://localhost:5173 ..."
npm run dev --prefix "$UI_DIR" &
FRONTEND_PID=$!
log "Frontend running (PID $FRONTEND_PID)."

# ── 5. Summary ────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "  ${GREEN}${BOLD}CropSense is running!${RESET}"
echo -e "  ${BLUE}Frontend :${RESET} http://localhost:5173"
echo -e "  ${BLUE}Backend  :${RESET} http://localhost:8000"
echo -e "  ${BLUE}API Docs :${RESET} http://localhost:8000/docs"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "  Press ${BOLD}Ctrl+C${RESET} to stop everything."
echo ""

wait
