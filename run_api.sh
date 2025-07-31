#!/bin/bash

# Script para ejecutar el servidor API del Sistema de Llamadas SIP con IA
# Ejecuta el servidor en el puerto 8000

set -e

echo "🌐 SISTEMA DE LLAMADAS SIP CON IA - SERVIDOR API"
echo "================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar dependencias
check_dependencies() {
    print_status "Verificando dependencias..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 no encontrado"
        exit 1
    fi
    
    # Verificar archivos necesarios
    local required_files=(
        "server.py"
        "src/api/server.py"
        "src/services/call_manager.py"
        "requirements.txt"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Archivo no encontrado: $file"
            exit 1
        fi
    done
    
    print_success "Dependencias verificadas"
}

# Instalar dependencias Python si es necesario
install_python_deps() {
    print_status "Verificando dependencias Python..."
    
    # Verificar si FastAPI está instalado
    if ! python3 -c "import fastapi" 2>/dev/null; then
        print_warning "FastAPI no encontrado, instalando dependencias..."
        pip install -r requirements.txt
        print_success "Dependencias Python instaladas"
    else
        print_success "Dependencias Python ya instaladas"
    fi
}

# Verificar configuración
check_config() {
    print_status "Verificando configuración..."
    
    if [ ! -f ".env" ]; then
        print_warning "Archivo .env no encontrado"
        print_warning "Creando archivo .env desde ejemplo..."
        cp env.example .env
        print_warning "⚠️  IMPORTANTE: Edita .env con tus credenciales reales"
        echo ""
        echo "Credenciales necesarias:"
        echo "  - SIP_HOST: Host de tu troncal SIP"
        echo "  - SIP_USERNAME: Usuario SIP"
        echo "  - SIP_PASSWORD: Contraseña SIP"
        echo "  - DEEPGRAM_API_KEY: Clave de Deepgram"
        echo "  - ELEVENLABS_API_KEY: Clave de ElevenLabs"
        echo "  - ELEVENLABS_VOICE_ID: ID de voz de ElevenLabs"
        echo ""
        echo "Presiona ENTER cuando hayas configurado las credenciales..."
        read -r
    else
        print_success "Archivo .env encontrado"
    fi
}

# Verificar puerto
check_port() {
    print_status "Verificando puerto 8000..."
    
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Puerto 8000 ya está en uso"
        echo "Procesos usando puerto 8000:"
        lsof -i :8000
        echo ""
        read -p "¿Quieres continuar de todas formas? (y/n): " continue_anyway
        if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
            print_error "Puerto ocupado, abortando"
            exit 1
        fi
    else
        print_success "Puerto 8000 disponible"
    fi
}

# Mostrar información del servidor
show_server_info() {
    echo ""
    echo "🌐 INFORMACIÓN DEL SERVIDOR API"
    echo "==============================="
    echo "📡 URL principal: http://localhost:8000"
    echo "📚 Documentación: http://localhost:8000/docs"
    echo "🔍 Estado de salud: http://localhost:8000/health"
    echo "📊 Estado completo: http://localhost:8000/status"
    echo "📞 Gestión de llamadas: http://localhost:8000/calls"
    echo "⚙️  Configuración: http://localhost:8000/config"
    echo "🧪 Pruebas: http://localhost:8000/test"
    echo ""
    echo "📋 Endpoints disponibles:"
    echo "   GET  /                    - Información del sistema"
    echo "   GET  /health              - Estado de salud"
    echo "   GET  /status              - Estado completo"
    echo "   GET  /calls               - Lista de llamadas"
    echo "   POST /calls               - Iniciar llamada"
    echo "   DELETE /calls/{call_id}   - Colgar llamada"
    echo "   GET  /config              - Configuración"
    echo "   POST /test                - Probar APIs"
    echo ""
    echo "📝 Ejemplo de uso:"
    echo "   # Iniciar llamada"
    echo "   curl -X POST http://localhost:8000/calls \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"number\": \"sip:+573001234567@sip.example.com\"}'"
    echo ""
    echo "   # Ver llamadas activas"
    echo "   curl http://localhost:8000/calls"
    echo ""
    echo "   # Ver estado del sistema"
    echo "   curl http://localhost:8000/status"
    echo ""
}

# Ejecutar servidor
run_server() {
    print_status "Iniciando servidor API en puerto 8000..."
    echo ""
    echo "🚀 SERVIDOR API EN EJECUCIÓN"
    echo "============================"
    echo "📡 URL: http://localhost:8000"
    echo "📚 Documentación: http://localhost:8000/docs"
    echo "🔍 Estado: http://localhost:8000/health"
    echo "📞 Llamadas: http://localhost:8000/calls"
    echo ""
    echo "📊 Monitoreo en tiempo real:"
    echo "   - Llamadas activas"
    echo "   - Transcripciones"
    echo "   - Respuestas de IA"
    echo "   - Métricas de calidad"
    echo ""
    echo "🛑 Para detener: Ctrl+C"
    echo ""
    
    # Ejecutar el servidor
    python3 server.py
}

# Función principal
main() {
    echo ""
    echo "🌐 INICIANDO SERVIDOR API"
    echo "========================"
    echo ""
    
    # Verificar dependencias
    check_dependencies
    
    # Instalar dependencias Python
    install_python_deps
    
    # Verificar configuración
    check_config
    
    # Verificar puerto
    check_port
    
    # Mostrar información
    show_server_info
    
    # Ejecutar servidor
    run_server
}

# Manejar interrupciones
trap 'echo ""; print_warning "Interrumpido por el usuario"; exit 1' INT TERM

# Ejecutar función principal
main "$@" 