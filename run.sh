#!/bin/bash

set -e

echo "🌱 RootMind - Iniciando Backend y Frontend..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get absolute paths
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# Trap para limpiar procesos al salir
cleanup() {
    echo -e "\n${BLUE}Deteniendo procesos...${NC}"
    jobs -p | xargs -r kill 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# Backend
echo -e "${GREEN}[1/2]${NC} Iniciando Backend (FastAPI)..."

if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "  Creando entorno virtual..."
    python3 -m venv "$BACKEND_DIR/venv"
fi

source "$BACKEND_DIR/venv/bin/activate"

echo "  Instalando dependencias del backend..."
pip install -q -r "$BACKEND_DIR/requirements.txt"

echo -e "  ${GREEN}✓ Backend listo${NC}"
echo "  Ejecutando: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
cd "$ROOT_DIR"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2

# Frontend
echo -e "\n${GREEN}[2/2]${NC} Iniciando Frontend (React + Vite)..."
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo "  Instalando dependencias del frontend..."
    npm install
fi

echo -e "  ${GREEN}✓ Frontend listo${NC}"
echo "  Ejecutando: npm run dev"
export VITE_API_BASE=http://localhost:8000
npm run dev &
FRONTEND_PID=$!

echo -e "\n${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ RootMind está en ejecución${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "  📚 Docs:   http://localhost:8000/docs"
echo ""
echo -e "  Presiona ${BLUE}Ctrl+C${NC} para detener..."
echo ""

wait
