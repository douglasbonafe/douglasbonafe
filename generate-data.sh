#!/usr/bin/env bash
# =============================================================
# generate-data.sh
# Script local para regenerar os SVGs e o README.md do portfolio.
#
# USO:
#   ./generate-data.sh           → usa dados reais da API do GitHub
#   ./generate-data.sh --demo    → usa dados de demonstração (sem API)
#
# REQUISITOS:
#   - Python 3.9+
#   - pip install -r requirements.txt
#   - GITHUB_TOKEN no ambiente (opcional, mas recomendado para stats precisas)
#     export GITHUB_TOKEN="ghp_..."
#
# FLUXO:
#   1. Lê github-portfolio-data.yml (fonte de verdade)
#   2. Busca stats ao vivo da API do GitHub (ou usa demo)
#   3. Gera assets/generated/*.svg
#   4. Gera README.md
#   5. (Opcional) faz commit e push automaticamente com --push
# =============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DEMO_FLAG=""
PUSH_FLAG=false

for arg in "$@"; do
  case $arg in
    --demo) DEMO_FLAG="--demo" ;;
    --push) PUSH_FLAG=true ;;
  esac
done

# ── Verificação do ambiente ───────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 não encontrado. Instale Python 3.9+."
  exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]; }; then
  echo "❌ Python 3.9+ necessário. Versão atual: $PYTHON_VERSION"
  exit 1
fi

# ── Instalar dependências ─────────────────────────────────────
echo "📦 Verificando dependências..."
pip install -q -r requirements.txt

# ── Token do GitHub ───────────────────────────────────────────
if [ -z "${GITHUB_TOKEN:-}" ] && [ -z "$DEMO_FLAG" ]; then
  echo "⚠️  GITHUB_TOKEN não definido. Stats podem ser limitadas pela API do GitHub."
  echo "   Para melhores resultados: export GITHUB_TOKEN='ghp_...'"
  echo "   Ou rode com --demo para usar dados de demonstração."
  echo ""
fi

# ── Geração ──────────────────────────────────────────────────
echo "🚀 Iniciando geração do portfolio..."
if [ -n "$DEMO_FLAG" ]; then
  echo "   Modo: DEMO (dados hardcoded, sem chamadas à API)"
else
  echo "   Modo: LIVE (dados reais da API do GitHub)"
fi
echo ""

python3 -m generator.main $DEMO_FLAG

echo ""
echo "✅ Portfolio gerado com sucesso!"
echo "   → assets/generated/galaxy-header.svg"
echo "   → assets/generated/stats-card.svg"
echo "   → assets/generated/tech-stack.svg"
echo "   → assets/generated/projects-constellation.svg"
echo "   → README.md"

# ── Push automático (opcional) ────────────────────────────────
if [ "$PUSH_FLAG" = true ]; then
  echo ""
  echo "📤 Fazendo commit e push..."
  git add assets/generated/ README.md
  if ! git diff --staged --quiet; then
    git commit -m "chore: update portfolio SVGs and README [skip ci]"
    git push
    echo "✅ Push realizado com sucesso!"
  else
    echo "ℹ️  Nenhuma alteração detectada. Nada a commitar."
  fi
fi
