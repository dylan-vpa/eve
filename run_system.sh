#!/bin/bash

# Script completo para ejecutar el Sistema de Llamadas SIP con IA
# Este script configura todo y ejecuta el sistema automáticamente

set -e

echo "🚀 SISTEMA DE LLAMADAS SIP CON IA - INSTALACIÓN Y EJECUCIÓN AUTOMÁTICA"
echo "=================================================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
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

# Verificar si estamos en Ubuntu/Debian
check_system() {
    print_status "Verificando sistema operativo..."
    
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_error "Este script está diseñado para Ubuntu/Linux"
        exit 1
    fi
    
    print_success "Sistema compatible detectado"
}

# Actualizar sistema
update_system() {
    print_status "Actualizando sistema..."
    sudo apt update -y
    sudo apt upgrade -y
    print_success "Sistema actualizado"
}

# Instalar dependencias del sistema
install_system_dependencies() {
    print_status "Instalando dependencias del sistema..."
    
    sudo apt install -y \
        build-essential \
        libssl-dev \
        python3-dev \
        libasound-dev \
        portaudio19-dev \
        python3-pip \
        git \
        curl \
        wget \
        ffmpeg \
        python3-venv
    
    print_success "Dependencias del sistema instaladas"
}

# Crear entorno virtual
setup_python_environment() {
    print_status "Configurando entorno Python..."
    
    # Crear entorno virtual si no existe
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Entorno virtual creado"
    else
        print_warning "Entorno virtual ya existe"
    fi
    
    # Activar entorno virtual
    source venv/bin/activate
    
    # Actualizar pip
    pip install --upgrade pip
    
    print_success "Entorno Python configurado"
}

# Instalar PJSIP
install_pjsip() {
    print_status "Instalando PJSIP..."
    
    if [ ! -f "install_pjsip.sh" ]; then
        print_error "Script de instalación PJSIP no encontrado"
        exit 1
    fi
    
    chmod +x install_pjsip.sh
    bash install_pjsip.sh
    
    print_success "PJSIP instalado"
}

# Instalar dependencias Python
install_python_dependencies() {
    print_status "Instalando dependencias Python..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "Archivo requirements.txt no encontrado"
        exit 1
    fi
    
    pip install -r requirements.txt
    
    print_success "Dependencias Python instaladas"
}

# Configurar variables de entorno
setup_environment() {
    print_status "Configurando variables de entorno..."
    
    # Crear archivo .env si no existe
    if [ ! -f ".env" ]; then
        cp env.example .env
        print_warning "Archivo .env creado desde ejemplo"
        print_warning "⚠️  IMPORTANTE: Edita .env con tus credenciales antes de continuar"
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
        print_success "Archivo .env ya existe"
    fi
}

# Crear archivo de números de prueba
create_test_numbers() {
    print_status "Creando números de prueba..."
    
    cat > numbers.txt << EOF
sip:+573001234567@sip.example.com
sip:+573001234568@sip.example.com
sip:+573001234569@sip.example.com
EOF
    
    print_success "Números de prueba creados"
    print_warning "⚠️  Edita numbers.txt con números reales antes de usar"
}

# Probar APIs
test_apis() {
    print_status "Probando APIs..."
    
    if [ ! -f "test_apis.py" ]; then
        print_error "Script de pruebas no encontrado"
        return 1
    fi
    
    python3 test_apis.py
    
    if [ $? -eq 0 ]; then
        print_success "APIs funcionando correctamente"
        return 0
    else
        print_error "Error en las APIs"
        return 1
    fi
}

# Verificar configuración
verify_configuration() {
    print_status "Verificando configuración..."
    
    # Verificar que el archivo .env existe
    if [ ! -f ".env" ]; then
        print_error "Archivo .env no encontrado"
        return 1
    fi
    
    # Verificar que numbers.txt existe
    if [ ! -f "numbers.txt" ]; then
        print_error "Archivo numbers.txt no encontrado"
        return 1
    fi
    
    # Verificar que main.py existe
    if [ ! -f "main.py" ]; then
        print_error "Archivo main.py no encontrado"
        return 1
    fi
    
    print_success "Configuración verificada"
    return 0
}

# Ejecutar sistema
run_system() {
    print_status "Iniciando sistema de llamadas SIP con IA..."
    echo ""
    echo "🎯 SISTEMA EN EJECUCIÓN"
    echo "========================"
    echo "📞 SIP Service: Conectando con troncal"
    echo "🎤 Audio Service: Grabando y procesando audio"
    echo "🎯 STT Service: Transcribiendo con Deepgram"
    echo "🤖 AI Service: Procesando con IA"
    echo "🎵 TTS Service: Generando audio con ElevenLabs"
    echo ""
    echo "📊 Monitoreo en tiempo real:"
    echo "   - Llamadas activas"
    echo "   - Transcripciones"
    echo "   - Respuestas de IA"
    echo "   - Métricas de calidad"
    echo ""
    echo "🛑 Para detener: Ctrl+C"
    echo ""
    
    # Ejecutar el sistema
    python3 main.py
}

# Ejecutar servidor API
run_api_server() {
    print_status "Iniciando servidor API en puerto 8000..."
    echo ""
    echo "🌐 SERVIDOR API EN EJECUCIÓN"
    echo "============================"
    echo "📡 URL: http://localhost:8000"
    echo "📚 Documentación: http://localhost:8000/docs"
    echo "🔍 Estado: http://localhost:8000/health"
    echo "📞 Llamadas: http://localhost:8000/calls"
    echo ""
    echo "📋 Endpoints disponibles:"
    echo "   GET  /              - Información del sistema"
    echo "   GET  /health        - Estado de salud"
    echo "   GET  /status        - Estado completo"
    echo "   GET  /calls         - Lista de llamadas"
    echo "   POST /calls         - Iniciar llamada"
    echo "   DELETE /calls/{id}  - Colgar llamada"
    echo "   GET  /config        - Configuración"
    echo "   POST /test          - Probar APIs"
    echo ""
    echo "🛑 Para detener: Ctrl+C"
    echo ""
    
    # Ejecutar el servidor API
    python3 server.py
}

# Función principal
main() {
    echo ""
    echo "🚀 INICIANDO INSTALACIÓN Y CONFIGURACIÓN AUTOMÁTICA"
    echo "=================================================="
    echo ""
    
    # Paso 1: Verificar sistema
    check_system
    
    # Paso 2: Actualizar sistema
    update_system
    
    # Paso 3: Instalar dependencias del sistema
    install_system_dependencies
    
    # Paso 4: Configurar entorno Python
    setup_python_environment
    
    # Paso 5: Instalar PJSIP
    install_pjsip
    
    # Paso 6: Instalar dependencias Python
    install_python_dependencies
    
    # Paso 7: Instalar Ollama (si es necesario)
    if [ -f "install_ollama.sh" ]; then
        echo ""
        print_status "¿Quieres instalar Ollama para IA local? (y/n)"
        read -r install_ollama_response
        if [[ $install_ollama_response =~ ^[Yy]$ ]]; then
            chmod +x install_ollama.sh
            bash install_ollama.sh
        fi
    fi
    
    # Paso 8: Configurar variables de entorno
    setup_environment
    
    # Paso 9: Crear números de prueba
    create_test_numbers
    
    # Paso 10: Verificar configuración
    if ! verify_configuration; then
        print_error "Error en la configuración. Revisa los archivos necesarios."
        exit 1
    fi
    
    # Paso 11: Probar APIs (opcional)
    echo ""
    print_status "¿Quieres probar las APIs antes de ejecutar? (y/n)"
    read -r test_response
    if [[ $test_response =~ ^[Yy]$ ]]; then
        if test_apis; then
            print_success "APIs funcionando correctamente"
        else
            print_warning "APIs con problemas, pero continuando..."
        fi
    fi
    
    # Paso 12: Preguntar modo de ejecución
    echo ""
    print_success "✅ TODO CONFIGURADO CORRECTAMENTE"
    echo ""
    echo "🎯 ¿Cómo quieres ejecutar el sistema?"
    echo "1) Modo consola (ejecución directa)"
    echo "2) Servidor API (puerto 8000)"
    echo ""
    read -p "Selecciona una opción (1 o 2): " execution_mode
    
    case $execution_mode in
        1)
            print_success "🚀 INICIANDO SISTEMA EN MODO CONSOLA..."
            echo ""
            run_system
            ;;
        2)
            print_success "🚀 INICIANDO SERVIDOR API EN PUERTO 8000..."
            echo ""
            run_api_server
            ;;
        *)
            print_warning "Opción inválida, iniciando en modo consola..."
            echo ""
            run_system
            ;;
    esac
}

# Manejar interrupciones
trap 'echo ""; print_warning "Interrumpido por el usuario"; exit 1' INT TERM

# Ejecutar función principal
main "$@" 