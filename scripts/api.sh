#!/bin/bash

# SIP AI Call System - API Server Script
# Ejecutar servidor API

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🌐 Iniciando Servidor API${NC}"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Entorno virtual no encontrado. Ejecuta ./scripts/install.sh primero"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Archivo .env no encontrado. Ejecuta ./scripts/install.sh primero"
    exit 1
fi

# Run the API server
echo -e "${GREEN}✅ Iniciando servidor API en puerto 8000...${NC}"
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload 