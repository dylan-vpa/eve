#!/bin/bash

# SIP AI Call System - Installation Script
# Sistema de Llamadas SIP con IA, STT y TTS

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
    echo "🚀 SIP AI Call System - Instalación"
    echo "=================================="
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
    cp env.example .env
    print_warning "📝 Configura las variables en .env antes de ejecutar"
fi

# Create execution scripts
print_info "Creando scripts de ejecución..."

# Create run_system.sh
cat > run_system.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python3 src/main.py
EOF

# Create run_api.sh
cat > run_api.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload
EOF

# Create test.sh
cat > test.sh << 'EOF'
#!/bin/bash
echo "🧪 PROBANDO SISTEMA DE LLAMADAS SIP"
echo "===================================="

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3 disponible"
else
    echo "❌ Python3 no encontrado"
    exit 1
fi

# Check essential files
files=("requirements.txt" "env.example" "numbers.txt" "src/main.py")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file existe"
    else
        echo "❌ $file no existe"
        exit 1
    fi
done

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama está funcionando"
else
    echo "⚠️ Ollama no está funcionando"
fi

# Test Python
if python3 -c "import sys; print('✅ Python funciona')" 2>/dev/null; then
    echo "✅ Python funciona correctamente"
else
    echo "❌ Error con Python"
    exit 1
fi

echo ""
echo "🎉 Sistema listo para usar!"
echo "Ejecuta: ./run_system.sh"
EOF

# Make scripts executable
chmod +x run_system.sh run_api.sh test.sh

print_success "✅ Instalación completada!"

echo ""
echo "🎉 SISTEMA INSTALADO CORRECTAMENTE"
echo "=================================="
echo ""
echo "📋 Próximos pasos:"
echo "1. Configura las variables en .env"
echo "2. Ejecuta: ./test.sh"
echo "3. Ejecuta: ./run_system.sh"
echo ""
echo "🔧 Comandos disponibles:"
echo "  ./run_system.sh  - Ejecutar sistema completo"
echo "  ./run_api.sh     - Ejecutar servidor API"
echo "  ./test.sh        - Probar sistema"
echo ""
print_success "¡Listo para usar! 🚀" 