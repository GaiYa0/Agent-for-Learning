#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "Created virtual environment at $VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip -q
pip install -e "$PROJECT_ROOT[dev]" -q

if [ ! -f "$PROJECT_ROOT/.env" ]; then
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo "Created .env from .env.example — fill in your API keys"
fi

echo ""
echo "Setup complete. Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run: pytest"
echo "  3. Run: ruff check src/ tests/"
echo "  4. Run: mypy src/"
