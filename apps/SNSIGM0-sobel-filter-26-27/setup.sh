#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

TOOLS_DIR=".tools"
ENV_DIR=".venv"
INPUT_DIR="image-input"
OUTPUT_DIR="image-output"

# 1. Detecter la plateforme
EXE=""
ARCHIVE_PATH="bin/micromamba"
STRIP=1

case "$(uname -s)-$(uname -m)" in
    Linux-x86_64)                PLATFORM="linux-64" ;;
    Linux-aarch64|Linux-arm64)   PLATFORM="linux-aarch64" ;;
    Darwin-x86_64)               PLATFORM="osx-64" ;;
    Darwin-arm64)                PLATFORM="osx-arm64" ;;
    MINGW*-x86_64|MSYS*-x86_64|CYGWIN*-x86_64)
        PLATFORM="win-64"
        EXE=".exe"
        ARCHIVE_PATH="Library/bin/micromamba.exe"
        STRIP=2
        ;;
    *) echo "Plateforme non supportee : $(uname -s) $(uname -m)" >&2; read -p "Appuyez sur ENTREE pour fermer..."; exit 1 ;;
esac

MAMBA="$TOOLS_DIR/micromamba${EXE}"

# 2. Telecharger micromamba localement (rien n'est installe sur le systeme)
if [ ! -f "$MAMBA" ]; then
    echo "==> Telechargement de micromamba..."
    mkdir -p "$TOOLS_DIR"
    curl -fsSL "https://micro.mamba.pm/api/micromamba/${PLATFORM}/latest" \
        | tar -xj -C "$TOOLS_DIR" --strip-components="$STRIP" "$ARCHIVE_PATH"
fi

# 3. Creer ou mettre a jour l'environnement depuis environment.yml
if [ ! -d "$ENV_DIR" ]; then
    echo "==> Creation de l'environnement..."
    "$MAMBA" create -y -p ./"$ENV_DIR" -f environment.yml
else
    echo "==> Mise a jour de l'environnement..."
    "$MAMBA" install -y -p ./"$ENV_DIR" -f environment.yml
fi

mkdir -p "$INPUT_DIR"
mkdir -p "$OUTPUT_DIR"
echo "Setup termine. Lance ./run.sh"
read -p "Appuyez sur ENTREE pour fermer..."