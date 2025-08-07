#!/bin/bash

# SIP AI Call System - Cleanup Script
# Limpiar y organizar el proyecto

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🧹 Limpiando y organizando proyecto${NC}"
echo "======================================"

# Remove Python cache files
echo -e "${YELLOW}🗑️  Eliminando archivos cache de Python...${NC}"
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Remove temporary files
echo -e "${YELLOW}🗑️  Eliminando archivos temporales...${NC}"
find . -type f -name "*.tmp" -delete
find . -type f -name "*.log" -delete

# Remove old files
echo -e "${YELLOW}🗑️  Eliminando archivos antiguos...${NC}"
rm -f agi_handler.py asterisk.conf extensions.conf install_and_run.sh install_asterisk.sh numbers.txt test_ollama.py 2>/dev/null || true

# Check structure
echo -e "${BLUE}📋 Verificando estructura del proyecto...${NC}"

# Check essential directories
directories=("scripts" "config" "config/asterisk" "data" "src" "src/core" "src/services" "src/api")
for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅ $dir existe${NC}"
    else
        echo -e "${YELLOW}⚠️  $dir no existe${NC}"
    fi
done

# Check essential files
files=("scripts/install.sh" "scripts/run.sh" "scripts/api.sh" "scripts/test.sh" "scripts/agi_handler.py" "config/asterisk/asterisk.conf" "config/asterisk/extensions.conf" "config/env.example" "data/numbers.txt" "src/main.py" "requirements.txt" "README.md" "STRUCTURE.md")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file existe${NC}"
    else
        echo -e "${YELLOW}⚠️  $file no existe${NC}"
    fi
done

# Make scripts executable
echo -e "${BLUE}🔧 Haciendo scripts ejecutables...${NC}"
chmod +x scripts/*.sh
chmod +x scripts/agi_handler.py

echo ""
echo -e "${GREEN}🎉 Limpieza completada!${NC}"
echo ""
echo "📋 Estructura final:"
echo "  📁 scripts/     - Scripts de ejecución"
echo "  📁 config/      - Configuraciones"
echo "  📁 data/        - Datos del sistema"
echo "  📁 src/         - Código fuente"
echo ""
echo "🚀 Comandos disponibles:"
echo "  ./scripts/install.sh  - Instalar sistema"
echo "  ./scripts/run.sh      - Ejecutar sistema"
echo "  ./scripts/api.sh      - Ejecutar API"
echo "  ./scripts/test.sh     - Probar sistema" 