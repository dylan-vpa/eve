#!/bin/bash

# SIP AI Call System with Asterisk - Installation Script
# Sistema de Llamadas SIP con IA usando Asterisk

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "🚀 SIP AI Call System con Asterisk - Instalación"
    echo "================================================"
    echo -e "${NC}"
}

# Check if running as root (for Docker compatibility)
if [ "$EUID" -eq 0 ]; then
    print_warning "Ejecutando como root (modo Docker)"
    SUDO=""
else
    SUDO="sudo"
fi

print_header

# Update system packages
print_info "Actualizando paquetes del sistema..."
$SUDO apt update
$SUDO apt install -y python3 python3-pip python3-venv curl wget

# Install system dependencies for audio
print_info "Instalando dependencias de audio..."
$SUDO apt install -y portaudio19-dev python3-dev build-essential

# Install Asterisk
print_info "Instalando Asterisk..."
$SUDO apt install -y asterisk asterisk-modules

# Install Ollama
print_info "Instalando Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
print_info "Iniciando servicio Ollama..."
$SUDO systemctl enable ollama
$SUDO systemctl start ollama

# Wait for Ollama to start
print_info "Esperando que Ollama inicie..."
sleep 5

# Pull llama2 model
print_info "Descargando modelo llama2..."
ollama pull llama2

# Configure Asterisk
print_info "Configurando Asterisk..."

# Copy configuration files
$SUDO cp config/asterisk/asterisk.conf /etc/asterisk/asterisk.conf
$SUDO cp config/asterisk/extensions.conf /etc/asterisk/extensions.conf

# Set permissions
$SUDO chown asterisk:asterisk /etc/asterisk/asterisk.conf
$SUDO chown asterisk:asterisk /etc/asterisk/extensions.conf

# Restart Asterisk
print_info "Reiniciando Asterisk..."
$SUDO systemctl restart asterisk
$SUDO systemctl enable asterisk

# Create Python virtual environment
print_info "Creando entorno virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_info "Actualizando pip..."
pip install --upgrade pip

# Install Python dependencies
print_info "Instalando dependencias Python..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_info "Creando archivo .env..."
    cp config/env.example .env
    print_warning "📝 Configura las variables en .env antes de ejecutar"
fi

# Make AGI handler executable
print_info "Configurando AGI handler..."
chmod +x scripts/agi_handler.py

print_success "✅ Instalación completada!"

echo ""
echo "🎉 SISTEMA CON ASTERISK INSTALADO CORRECTAMENTE"
echo "================================================"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configura las variables en .env"
echo "2. Ejecuta: ./scripts/test.sh"
echo "3. Ejecuta: ./scripts/run.sh"
echo ""
echo "🔧 Comandos disponibles:"
echo "  ./scripts/run.sh      - Ejecutar sistema completo"
echo "  ./scripts/api.sh       - Ejecutar servidor API"
echo "  ./scripts/test.sh      - Probar sistema"
echo ""
echo "📞 Asterisk configurado para:"
echo "  - SIP Trunk: 1998010101.tscpbx.net"
echo "  - Usuario: paradixe01"
echo "  - Número destino: +573013304134"
echo ""
print_success "¡Listo para usar! 🚀" 