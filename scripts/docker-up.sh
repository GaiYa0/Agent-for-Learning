#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example — set OPENAI_API_KEY before using the app."
fi

if ! grep -qE '^OPENAI_API_KEY=.+' .env 2>/dev/null; then
    echo "Warning: OPENAI_API_KEY is empty in .env. The API container may fail to start."
fi

docker compose up --build -d

echo ""
echo "Stack started:"
echo "  Frontend: http://localhost:8501"
echo "  API docs: http://localhost:8000/docs"
echo "  Health:   http://localhost:8000/health"
echo ""
echo "Logs:  docker compose logs -f"
echo "Stop:  docker compose down"
