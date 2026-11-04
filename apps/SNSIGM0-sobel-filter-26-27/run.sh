#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

LOG_FILE="run.log"
TMP_LOG="$(mktemp)"
trap 'rm -f "$TMP_LOG"' EXIT

MAMBA=".tools/micromamba"
[ -f "$MAMBA.exe" ] && MAMBA="$MAMBA.exe"

if [ ! -f "$MAMBA" ]; then
    echo "Lance d'abord ./setup.sh" >&2
    exit 1
fi

# Affiche la sortie en direct ET la garde dans un fichier temporaire
PYTHONUNBUFFERED=1 "$MAMBA" run -p ./.venv python src/main.py "$@" 2>&1 | tee "$TMP_LOG"
status=${PIPESTATUS[0]}

if [ "$status" -ne 0 ]; then
    {
        echo "=== $(date '+%Y-%m-%d %H:%M:%S') | code de sortie : $status ==="
        cat "$TMP_LOG"
    } > "$LOG_FILE"
    echo "Erreur (code $status), logs ecrits dans $LOG_FILE" >&2
else
    rm -f "$LOG_FILE"
fi

exit "$status"