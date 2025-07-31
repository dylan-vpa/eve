#!/bin/bash

# Script de prueba rápida del Sistema de Llamadas SIP con IA
# Verifica que todo esté funcionando correctamente

set -e

echo "🧪 PRUEBA RÁPIDA DEL SISTEMA"
echo "============================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Verificar archivos necesarios
check_files() {
    print_status "Verificando archivos del sistema..."
    
    local files=(
        "main.py"
        "requirements.txt"
        "install_pjsip.sh"
        "src/main.py"
        "src/config/settings.py"
        "src/services/call_manager.py"
        "src/models/call.py"
        "numbers.txt"
        "env.example"
    )
    
    local missing_files=()
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            print_success "   ✅ $file"
        else
            print_error "   ❌ $file"
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        print_success "Todos los archivos necesarios están presentes"
        return 0
    else
        print_error "Faltan archivos: ${missing_files[*]}"
        return 1
    fi
}

# Verificar Python
check_python() {
    print_status "Verificando Python..."
    
    if command -v python3 &> /dev/null; then
        local version=$(python3 --version 2>&1)
        print_success "Python encontrado: $version"
        return 0
    else
        print_error "Python3 no encontrado"
        return 1
    fi
}

# Verificar dependencias Python
check_python_deps() {
    print_status "Verificando dependencias Python..."
    
    local deps=(
        "asyncio"
        "aiohttp"
        "numpy"
        "pydub"
        "python-dotenv"
    )
    
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if python3 -c "import $dep" 2>/dev/null; then
            print_success "   ✅ $dep"
        else
            print_error "   ❌ $dep"
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -eq 0 ]; then
        print_success "Todas las dependencias Python están instaladas"
        return 0
    else
        print_warning "Faltan dependencias: ${missing_deps[*]}"
        print_warning "Ejecuta: pip install -r requirements.txt"
        return 1
    fi
}

# Verificar configuración
check_config() {
    print_status "Verificando configuración..."
    
    if [ -f ".env" ]; then
        print_success "Archivo .env encontrado"
        
        # Verificar variables críticas
        local critical_vars=(
            "SIP_HOST"
            "SIP_USERNAME"
            "SIP_PASSWORD"
            "DEEPGRAM_API_KEY"
            "ELEVENLABS_API_KEY"
            "ELEVENLABS_VOICE_ID"
        )
        
        local missing_vars=()
        
        for var in "${critical_vars[@]}"; do
            if grep -q "^$var=" .env; then
                print_success "   ✅ $var configurado"
            else
                print_error "   ❌ $var no configurado"
                missing_vars+=("$var")
            fi
        done
        
        if [ ${#missing_vars[@]} -eq 0 ]; then
            print_success "Todas las variables críticas están configuradas"
            return 0
        else
            print_warning "Faltan variables: ${missing_vars[*]}"
            return 1
        fi
    else
        print_warning "Archivo .env no encontrado"
        print_warning "Ejecuta: cp env.example .env"
        return 1
    fi
}

# Verificar números
check_numbers() {
    print_status "Verificando números de destino..."
    
    if [ -f "numbers.txt" ]; then
        local count=$(wc -l < numbers.txt)
        print_success "Archivo numbers.txt encontrado con $count números"
        
        # Mostrar primeros 3 números
        echo "   Números configurados:"
        head -3 numbers.txt | while read -r line; do
            echo "   📞 $line"
        done
        return 0
    else
        print_error "Archivo numbers.txt no encontrado"
        return 1
    fi
}

# Probar importación del sistema
test_imports() {
    print_status "Probando importaciones del sistema..."
    
    local test_script="
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.config.settings import validate_config
    from src.models.call import Call
    from src.services.call_manager import CallManager
    print('✅ Importaciones exitosas')
    exit(0)
except Exception as e:
    print(f'❌ Error en importaciones: {e}')
    exit(1)
"
    
    if python3 -c "$test_script"; then
        print_success "Sistema importado correctamente"
        return 0
    else
        print_error "Error importando el sistema"
        return 1
    fi
}

# Función principal
main() {
    echo ""
    echo "🧪 INICIANDO PRUEBA RÁPIDA"
    echo "=========================="
    echo ""
    
    local tests_passed=0
    local tests_total=5
    
    # Test 1: Verificar archivos
    if check_files; then
        ((tests_passed++))
    fi
    echo ""
    
    # Test 2: Verificar Python
    if check_python; then
        ((tests_passed++))
    fi
    echo ""
    
    # Test 3: Verificar dependencias
    if check_python_deps; then
        ((tests_passed++))
    fi
    echo ""
    
    # Test 4: Verificar configuración
    if check_config; then
        ((tests_passed++))
    fi
    echo ""
    
    # Test 5: Verificar números
    if check_numbers; then
        ((tests_passed++))
    fi
    echo ""
    
    # Test 6: Probar importaciones
    if test_imports; then
        ((tests_passed++))
        ((tests_total++))
    fi
    echo ""
    
    # Resumen
    echo "📊 RESUMEN DE PRUEBAS"
    echo "====================="
    echo "✅ Tests pasados: $tests_passed/$tests_total"
    
    if [ $tests_passed -eq $tests_total ]; then
        echo ""
        print_success "🎉 ¡TODAS LAS PRUEBAS PASARON!"
        print_success "🚀 El sistema está listo para ejecutar"
        echo ""
        echo "Para ejecutar el sistema:"
        echo "  ./run_system.sh    # Instalación completa y ejecución"
        echo "  ./demo.sh          # Demostración rápida"
        echo "  python3 main.py    # Ejecución directa"
    else
        echo ""
        print_error "❌ ALGUNAS PRUEBAS FALLARON"
        print_warning "Revisa los errores antes de ejecutar el sistema"
    fi
    
    echo ""
}

# Ejecutar pruebas
main "$@" 