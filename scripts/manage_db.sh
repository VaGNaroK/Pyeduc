#!/usr/bin/env bash

# ==============================================================================
# Pyeduc - Wrapper Shell para o Gerenciador de Banco de Dados SQLite
# Localização: scripts/manage_db.sh
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT" || exit 1

if [ -d "venv" ]; then
    PYTHON_EXEC="venv/bin/python"
elif [ -d ".venv" ]; then
    PYTHON_EXEC=".venv/bin/python"
else
    PYTHON_EXEC="python3"
fi

exec $PYTHON_EXEC "$SCRIPT_DIR/manage_db.py" "$@"
