#!/bin/bash

# Script de configuración automática para el sistema de llamadas SIP con IA
# Ejecutar en Ubuntu 20.04/22.04 en RunPod

set -e

echo "🚀 Configurando Sistema de Llamadas SIP con IA y STT/TTS"
echo "=================================================="

# Verificar sistema operativo
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Este script está diseñado para Ubuntu/Linux"
    exit 1
fi

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt update
sudo apt upgrade -y

# Instalar dependencias del sistema
echo "🔧 Instalando dependencias del sistema..."
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
    ffmpeg

# Verificar Python
echo "🐍 Verificando Python..."
python3 --version
pip3 --version

# Instalar PJSIP
echo "📞 Instalando PJSIP..."
chmod +x install_pjsip.sh
bash install_pjsip.sh

# Instalar dependencias Python
echo "📚 Instalando dependencias Python..."
pip3 install -r requirements.txt

# Configurar variables de entorno
echo "⚙️  Configurando variables de entorno..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "📝 Archivo .env creado. Edita las credenciales:"
    echo "   nano .env"
else
    echo "✅ Archivo .env ya existe"
fi

# Crear directorio de logs
echo "📁 Creando directorios..."
mkdir -p logs
mkdir -p audio_cache

# Configurar permisos
echo "🔐 Configurando permisos..."
chmod +x main.py
chmod +x test_apis.py

# Verificar puertos
echo "🔌 Verificando puertos..."
echo "   Puerto 5060 (SIP): $(netstat -tuln | grep :5060 || echo 'No abierto')"
echo "   Puerto 443 (HTTPS): $(netstat -tuln | grep :443 || echo 'No abierto')"

# Probar APIs
echo "🧪 Probando APIs..."
python3 test_apis.py

echo ""
echo "✅ Configuración completada!"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Edita .env con tus credenciales"
echo "   2. Edita numbers.txt con los números de destino"
echo "   3. Ejecuta: python3 test_apis.py"
echo "   4. Si todo está bien: python3 main.py"
echo ""
echo "📚 Documentación: README.md"
echo "🐛 Problemas: Revisa los logs en la consola" 