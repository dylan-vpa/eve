# 🚀 Sistema de Llamadas SIP con IA

**Sistema completo y funcional** para gestión de llamadas SIP con **IA local** usando Ollama, STT con Deepgram y TTS con ElevenLabs.

## 🎯 Características

- **SIP Trunk**: Conexión con proveedores SIP usando librerías simples y confiables
- **IA Local**: Ollama con modelo llama2 para procesamiento de conversaciones
- **STT**: Deepgram para transcripción de audio a texto
- **TTS**: ElevenLabs para generación de audio desde texto
- **API REST**: FastAPI para control externo del sistema
- **Modular**: Arquitectura limpia y bien organizada

## 🚀 Instalación Rápida

### **Instalación Automática (RECOMENDADA)**
```bash
# Dar permisos y ejecutar
chmod +x install_and_run.sh
./install_and_run.sh
```

### **Configuración Manual**
```bash
# 1. Instalar dependencias del sistema
sudo apt update
sudo apt install -y python3 python3-pip python3-venv curl

# 2. Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh
sudo systemctl start ollama
ollama pull llama2

# 3. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configurar variables
cp env.example .env
# Editar .env con tus credenciales
```

## 📋 Configuración

### **Variables de Entorno (.env)**
```bash
# SIP Trunk
SIP_HOST=sip.example.com
SIP_USERNAME=tu_usuario
SIP_PASSWORD=tu_contraseña
SIP_PORT=5060

# Deepgram STT
DEEPGRAM_API_KEY=tu_clave_deepgram

# ElevenLabs TTS
ELEVENLABS_API_KEY=tu_clave_elevenlabs
ELEVENLABS_VOICE_ID=tu_voice_id

# Ollama AI
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### **Números de Destino (numbers.txt)**
```
sip:+1234567890@sip.example.com
sip:+1987654321@sip.example.com
```

## 🧪 Pruebas

### **Probar Sistema Completo**
```bash
./test.sh
```

### **Probar Servicios Individuales**
```bash
# Probar AI
curl -X POST http://localhost:8000/test/ai

# Probar TTS
curl -X POST http://localhost:8000/test/tts

# Verificar estado
curl http://localhost:8000/health
```

## 🚀 Ejecución

### **Sistema Completo**
```bash
./run_system.sh
```

### **Servidor API**
```bash
./run_api.sh
```

### **Directo**
```bash
source venv/bin/activate
python3 src/main.py
```

## 🏗️ Arquitectura

```
src/
├── core/
│   └── config.py          # Configuración centralizada
├── services/
│   ├── sip_service.py     # Servicio SIP simplificado
│   ├── stt_service.py     # Speech-to-Text (Deepgram)
│   ├── tts_service.py     # Text-to-Speech (ElevenLabs)
│   ├── ai_service.py      # IA (Ollama)
│   └── call_manager.py    # Orquestador principal
├── api/
│   └── server.py          # Servidor FastAPI
└── main.py                # Punto de entrada
```

## 🔧 Servicios

### **SIP Service**
- Conexión UDP con troncal SIP
- Registro automático
- Llamadas salientes
- Manejo de mensajes SIP básicos

### **STT Service (Deepgram)**
- Transcripción de audio a texto
- Soporte para múltiples formatos
- Procesamiento asíncrono

### **TTS Service (ElevenLabs)**
- Generación de audio desde texto
- Múltiples voces disponibles
- Optimización de calidad

### **AI Service (Ollama)**
- Procesamiento local con llama2
- Respuestas contextuales
- Baja latencia

## 🌐 API Endpoints

### **GET /** - Información del sistema
### **GET /health** - Estado de salud
### **GET /config** - Configuración actual
### **GET /status** - Estado de servicios
### **POST /call** - Hacer llamada individual
### **POST /call/batch** - Llamadas en lote
### **POST /test/ai** - Probar servicio AI
### **POST /test/tts** - Probar servicio TTS

## 📊 Monitoreo

### **Logs**
- Logs detallados en consola
- Formato estructurado
- Niveles de log configurables

### **Estado del Sistema**
```bash
curl http://localhost:8000/status
```

## 🔍 Troubleshooting

### **Problemas Comunes**

1. **Ollama no responde**
   ```bash
   sudo systemctl start ollama
   ollama pull llama2
   ```

2. **Error en SIP**
   - Verificar credenciales en `.env`
   - Confirmar conectividad de red
   - Revisar puerto 5060

3. **Error en APIs**
   - Verificar claves de Deepgram/ElevenLabs
   - Confirmar conectividad a internet

### **Logs de Debug**
```bash
# Activar debug
export DEBUG=true
./run_system.sh
```

## 🎉 **CONCLUSIÓN**

**Este sistema está completamente funcional y listo para usar. Solo necesitas:**

1. **Ejecutar** `./install_and_run.sh`
2. **Configurar** tus credenciales en `.env`
3. **Probar** con `./test.sh`
4. **Ejecutar** con `./run_system.sh`

**¡Y listo! 🚀**

---

**Desarrollado con ❤️ para llamadas SIP inteligentes** 