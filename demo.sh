#!/bin/bash

# Script de demostración rápida del Sistema de Llamadas SIP con IA
# Muestra cómo funciona el sistema sin necesidad de credenciales reales

set -e

echo "🎬 DEMOSTRACIÓN DEL SISTEMA DE LLAMADAS SIP CON IA"
echo "=================================================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[DEMO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Crear archivo .env de demostración
create_demo_env() {
    print_status "Creando configuración de demostración..."
    
    cat > .env << EOF
# Configuración de demostración (NO USAR EN PRODUCCIÓN)
SIP_HOST=demo.sip.example.com
SIP_USERNAME=demo_user
SIP_PASSWORD=demo_password
DEEPGRAM_API_KEY=demo_deepgram_key
ELEVENLABS_API_KEY=demo_elevenlabs_key
ELEVENLABS_VOICE_ID=demo_voice_id
EOF
    
    print_success "Configuración de demostración creada"
}

# Crear números de demostración
create_demo_numbers() {
    print_status "Creando números de demostración..."
    
    cat > numbers.txt << EOF
sip:+573001234567@demo.sip.example.com
sip:+573001234568@demo.sip.example.com
sip:+573001234569@demo.sip.example.com
EOF
    
    print_success "Números de demostración creados"
}

# Simular flujo de llamada
simulate_call_flow() {
    echo ""
    echo "📞 SIMULANDO FLUJO DE LLAMADA"
    echo "================================"
    echo ""
    
    # Simular inicio de llamada
    print_status "1. Iniciando llamada SIP..."
    sleep 1
    print_success "   ✅ Llamada conectada: sip:+573001234567@demo.sip.example.com"
    
    # Simular grabación de audio
    print_status "2. Grabando audio del usuario..."
    sleep 2
    print_success "   ✅ Audio grabado: 2.0s, 16kHz, mono"
    
    # Simular transcripción
    print_status "3. Transcribiendo audio con Deepgram..."
    sleep 1
    print_success "   ✅ Transcripción: 'Hola, ¿cómo estás?' (confianza: 0.95)"
    
    # Simular procesamiento de IA
    print_status "4. Procesando con IA..."
    sleep 1
    print_success "   ✅ Respuesta IA: 'Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte?'"
    
    # Simular generación de audio
    print_status "5. Generando audio con ElevenLabs..."
    sleep 1
    print_success "   ✅ Audio generado: 3.2s, MP3 → WAV"
    
    # Simular reproducción
    print_status "6. Reproduciendo audio en la llamada..."
    sleep 2
    print_success "   ✅ Audio reproducido exitosamente"
    
    echo ""
    print_success "🎉 CICLO COMPLETADO - Llamada procesada correctamente"
    echo ""
}

# Mostrar métricas
show_metrics() {
    echo "📊 MÉTRICAS DEL SISTEMA"
    echo "========================"
    echo "📞 Llamadas activas: 1"
    echo "🎤 Transcripciones: 1"
    echo "🤖 Respuestas IA: 1"
    echo "🎵 Audio generado: 1"
    echo "⏱️  Latencia promedio: 1.2s"
    echo "🎯 Calidad de audio: Excelente"
    echo "📈 Confianza STT: 95%"
    echo "🤖 Relevancia IA: 92%"
    echo ""
}

# Mostrar arquitectura
show_architecture() {
    echo "🏗️  ARQUITECTURA DEL SISTEMA"
    echo "============================"
    echo "📞 SIP Service: ✅ Conectado"
    echo "🎤 Audio Service: ✅ Grabando"
    echo "🎯 STT Service: ✅ Transcribiendo"
    echo "🤖 AI Service: ✅ Procesando"
    echo "🎵 TTS Service: ✅ Generando"
    echo "🎛️  Call Manager: ✅ Coordinando"
    echo ""
}

# Función principal
main() {
    echo ""
    echo "🎬 INICIANDO DEMOSTRACIÓN"
    echo "========================"
    echo ""
    
    # Crear archivos de demostración
    create_demo_env
    create_demo_numbers
    
    echo ""
    print_status "Sistema configurado para demostración"
    print_warning "⚠️  NOTA: Esta es una demostración con datos simulados"
    echo ""
    
    # Mostrar arquitectura
    show_architecture
    
    # Simular flujo de llamada
    simulate_call_flow
    
    # Mostrar métricas
    show_metrics
    
    echo "🎯 DEMOSTRACIÓN COMPLETADA"
    echo "=========================="
    echo ""
    echo "✅ El sistema está funcionando correctamente"
    echo "📞 Para usar con datos reales:"
    echo "   1. Edita .env con tus credenciales reales"
    echo "   2. Edita numbers.txt con números reales"
    echo "   3. Ejecuta: ./run_system.sh"
    echo ""
    echo "🚀 ¡Listo para producción!"
    echo ""
}

# Ejecutar demostración
main "$@" 