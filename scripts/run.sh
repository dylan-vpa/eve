#!/bin/bash

# SIP AI Call System - Run Script
# Ejecutar sistema completo

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Iniciando Sistema de Llamadas SIP con IA${NC}"
echo "================================================"

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

# Run the main application
echo -e "${GREEN}✅ Iniciando aplicación...${NC}"
python3 src/main.py 