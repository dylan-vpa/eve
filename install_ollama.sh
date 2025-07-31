#!/bin/bash

# Script para instalar y configurar Ollama
# Ollama es un servidor local para ejecutar modelos de IA

set -e

echo "🤖 INSTALANDO OLLAMA"
echo "====================="
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

# Verificar si Ollama ya está instalado
check_ollama() {
    print_status "Verificando instalación de Ollama..."
    
    if command -v ollama &> /dev/null; then
        local version=$(ollama --version)
        print_success "Ollama ya está instalado: $version"
        return 0
    else
        print_warning "Ollama no encontrado, procediendo con instalación..."
        return 1
    fi
}

# Instalar Ollama
install_ollama() {
    print_status "Instalando Ollama..."
    
    # Descargar e instalar Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if [ $? -eq 0 ]; then
        print_success "Ollama instalado correctamente"
    else
        print_error "Error instalando Ollama"
        exit 1
    fi
}

# Iniciar servicio Ollama
start_ollama() {
    print_status "Iniciando servicio Ollama..."
    
    # Verificar si el servicio está corriendo
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Ollama ya está ejecutándose"
        return 0
    fi
    
    # Iniciar Ollama en background
    ollama serve &
    local pid=$!
    
    # Esperar a que inicie
    print_status "Esperando a que Ollama inicie..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_success "Ollama iniciado correctamente (PID: $pid)"
            return 0
        fi
        sleep 1
    done
    
    print_error "Timeout esperando a que Ollama inicie"
    return 1
}

# Descargar modelo LLaMA
download_model() {
    print_status "Descargando modelo LLaMA 2..."
    
    # Verificar si el modelo ya está descargado
    if ollama list | grep -q "llama2"; then
        print_success "Modelo llama2 ya está descargado"
        return 0
    fi
    
    # Descargar modelo
    ollama pull llama2
    
    if [ $? -eq 0 ]; then
        print_success "Modelo llama2 descargado correctamente"
    else
        print_error "Error descargando modelo llama2"
        return 1
    fi
}

# Probar modelo
test_model() {
    print_status "Probando modelo LLaMA 2..."
    
    # Crear archivo de prueba temporal
    cat > test_ollama.py << 'EOF'
import asyncio
import aiohttp
import json

async def test_ollama():
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "llama2",
                "prompt": "Hola, ¿cómo estás?",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 50
                }
            }
            
            async with session.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    response = result.get('response', '').strip()
                    print(f"✅ Respuesta de prueba: {response}")
                    return True
                else:
                    print(f"❌ Error: {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_ollama())
EOF
    
    # Ejecutar prueba
    if python3 test_ollama.py; then
        print_success "Prueba de Ollama exitosa"
        rm test_ollama.py
        return 0
    else
        print_error "Prueba de Ollama falló"
        rm test_ollama.py
        return 1
    fi
}

# Mostrar información
show_info() {
    echo ""
    echo "🤖 INFORMACIÓN DE OLLAMA"
    echo "========================"
    echo "📡 URL: http://localhost:11434"
    echo "📚 Documentación: https://ollama.ai"
    echo "🎯 Modelo: llama2"
    echo ""
    echo "📋 Comandos útiles:"
    echo "   ollama list                    - Ver modelos instalados"
    echo "   ollama run llama2 'Hola'      - Probar modelo"
    echo "   ollama pull llama2:13b        - Descargar modelo 13B"
    echo "   ollama pull codellama         - Descargar Code Llama"
    echo "   ollama pull mistral           - Descargar Mistral"
    echo ""
    echo "🔧 Configuración en el sistema:"
    echo "   AI_MODEL_TYPE=ollama"
    echo "   AI_MODEL_NAME=llama2"
    echo "   OLLAMA_URL=http://localhost:11434"
    echo ""
}

# Función principal
main() {
    echo ""
    echo "🤖 INICIANDO INSTALACIÓN DE OLLAMA"
    echo "=================================="
    echo ""
    
    # Verificar si ya está instalado
    if check_ollama; then
        print_warning "Ollama ya está instalado"
    else
        # Instalar Ollama
        install_ollama
    fi
    
    # Iniciar servicio
    if ! start_ollama; then
        print_error "No se pudo iniciar Ollama"
        exit 1
    fi
    
    # Descargar modelo
    if ! download_model; then
        print_error "No se pudo descargar el modelo"
        exit 1
    fi
    
    # Probar modelo
    if ! test_model; then
        print_error "No se pudo probar el modelo"
        exit 1
    fi
    
    # Mostrar información
    show_info
    
    echo ""
    print_success "✅ OLLAMA CONFIGURADO CORRECTAMENTE"
    print_success "🚀 Listo para usar con el sistema de llamadas SIP"
    echo ""
}

# Manejar interrupciones
trap 'echo ""; print_warning "Interrumpido por el usuario"; exit 1' INT TERM

# Ejecutar función principal
main "$@" 