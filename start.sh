#!/bin/bash
# ─────────────────────────────────────────────────────────────────
#  OrgoLife — One-shot startup script
#  Run from inside the orgolife/ directory:
#    cd orgolife && bash start.sh
# ─────────────────────────────────────────────────────────────────
set -e

echo ""
echo "  🫀  OrgoLife — Organ Donation Platform"
echo "  ─────────────────────────────────────"
echo ""

# ── 1. Python check ───────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "  ❌  Python 3.9+ is required. Install from https://python.org"
  exit 1
fi
PY_VERSION=$(python3 -c "import sys; print(sys.version_info[:2] >= (3,9))")
if [ "$PY_VERSION" != "True" ]; then
  echo "  ❌  Python 3.9 or higher is required."
  exit 1
fi

# ── 2. MongoDB check ──────────────────────────────────────────────
echo "  🔍  Checking MongoDB..."
if pgrep -x mongod &>/dev/null; then
  echo "  ✅  MongoDB is running (local)."
else
  echo "  ⚠️   Local mongod is not running."
  echo "      If using MongoDB Atlas, make sure MONGODB_URL is set in .env"
  echo "      For local install: https://www.mongodb.com/docs/manual/installation/"
  echo ""
fi

# ── 3. .env setup ────────────────────────────────────────────────
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo "  ✅  Created .env from .env.example"
  fi
  echo "  ⚠️   .env not found — using built-in defaults."
  echo "      Edit .env to set your MONGODB_URL and JWT_SECRET_KEY."
  echo ""
fi

# ── 4. Virtual environment ────────────────────────────────────────
if [ ! -d "venv" ]; then
  echo "  📦  Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || . venv/bin/activate

# ── 5. Dependencies ───────────────────────────────────────────────
echo "  📥  Installing / verifying dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "  ✅  Dependencies ready."

# ── 6. Upload directory ───────────────────────────────────────────
mkdir -p uploads

# ── 7. Start ──────────────────────────────────────────────────────
echo ""
echo "  🚀  Starting OrgoLife on http://localhost:8000"
echo ""
echo "  ┌─────────────────────────────────────────┐"
echo "  │  Frontend :  http://localhost:8000/      │"
echo "  │  API Docs :  http://localhost:8000/api/docs │"
echo "  │  Health   :  http://localhost:8000/health   │"
echo "  └─────────────────────────────────────────┘"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
