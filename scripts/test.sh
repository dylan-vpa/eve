#!/bin/bash

# SIP AI Call System - Test Script
# Probar sistema completo

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🧪 PROBANDO SISTEMA DE LLAMADAS SIP CON ASTERISK${NC}"
echo "=================================================="

# Check Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python3 disponible${NC}"
else
    echo -e "${RED}❌ Python3 no encontrado${NC}"
    exit 1
fi

# Check Asterisk
if systemctl is-active --quiet asterisk; then
    echo -e "${GREEN}✅ Asterisk está funcionando${NC}"
else
    echo -e "${RED}❌ Asterisk no está funcionando${NC}"
    exit 1
fi

# Check essential files
files=("requirements.txt" "config/env.example" "data/numbers.txt" "src/main.py" "scripts/agi_handler.py")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file existe${NC}"
    else
        echo -e "${RED}❌ $file no existe${NC}"
        exit 1
    fi
done

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${GREEN}✅ Ollama está funcionando${NC}"
else
    echo -e "${YELLOW}⚠️ Ollama no está funcionando${NC}"
fi

# Test Python
if python3 -c "import sys; print('✅ Python funciona')" 2>/dev/null; then
    echo -e "${GREEN}✅ Python funciona correctamente${NC}"
else
    echo -e "${RED}❌ Error con Python${NC}"
    exit 1
fi

# Check virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Entorno virtual existe${NC}"
else
    echo -e "${YELLOW}⚠️ Entorno virtual no existe${NC}"
fi

# Check .env file
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Archivo .env existe${NC}"
else
    echo -e "${YELLOW}⚠️ Archivo .env no existe${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Sistema listo para usar!${NC}"
echo "Ejecuta: ./scripts/run.sh" 