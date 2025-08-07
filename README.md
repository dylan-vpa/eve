# 🚀 Sistema de Llamadas SIP con IA (Asterisk + Python)

**Sistema híbrido completo y funcional** para gestión de llamadas SIP usando **Asterisk** para manejo de llamadas y **Python** para IA, STT y TTS.

## 🎯 Características

- **Asterisk**: Manejo robusto de llamadas SIP con el trunk configurado
- **AMI (Asterisk Manager Interface)**: Conexión Python-Asterisk para control de llamadas
- **AGI (Asterisk Gateway Interface)**: Script Python que procesa llamadas en tiempo real
- **IA Local**: Ollama con modelo llama2 para procesamiento de conversaciones
- **STT**: Deepgram para transcripción de audio a texto
- **TTS**: ElevenLabs para generación de audio desde texto
- **API REST**: FastAPI para control externo del sistema
- **Modular**: Arquitectura limpia y bien organizada

## 🔄 Flujo del Sistema

1. **Asterisk** se conecta al SIP trunk (1998010101.tscpbx.net)
2. **Python** se conecta a Asterisk via AMI (puerto 5038)
3. Cuando se inicia una llamada:
   - Python envía comando de llamada via AMI
   - Asterisk maneja la conexión SIP y audio RTP
   - AGI script procesa la llamada en tiempo real
   - STT transcribe audio del usuario
   - IA genera respuesta contextual
   - TTS convierte respuesta a audio
   - Audio se reproduce en la llamada

## 🚀 Instalación Rápida

### **Instalación Automática (RECOMENDADA)**
```bash
# Dar permisos y ejecutar
chmod +x scripts/install.sh
./scripts/install.sh
```

### **Configuración Manual**
```bash
# 1. Instalar Asterisk
sudo apt install -y asterisk asterisk-modules

# 2. Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh
sudo systemctl start ollama
ollama pull llama2

# 3. Configurar Asterisk
sudo cp asterisk.conf /etc/asterisk/asterisk.conf
sudo cp extensions.conf /etc/asterisk/extensions.conf
sudo systemctl restart asterisk

# 4. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configurar variables
cp env.example .env
# Editar .env con tus credenciales
```

## 📋 Configuración

### **Variables de Entorno (.env)**
```bash
# SIP Trunk (ya configurado)
SIP_HOST=1998010101.tscpbx.net
SIP_USERNAME=paradixe01
SIP_PASSWORD=WiFO8=77wich
SIP_PORT=5060

# Deepgram STT
DEEPGRAM_API_KEY=tu_clave_deepgram

# ElevenLabs TTS
ELEVENLABS_API_KEY=tu_clave_elevenlabs
ELEVENLABS_VOICE_ID=tu_voice_id

# Ollama AI
OLLAMA_MODEL=llama2

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### **Números de Destino (numbers.txt)**
```
sip:+573013304134@1998010101.tscpbx.net
```

## 🏗️ Arquitectura

```
📁 Sistema de Llamadas SIP con IA
├── 📋 README.md                    # Documentación principal
├── 📋 STRUCTURE.md                 # Estructura del proyecto
├── 📋 requirements.txt             # Dependencias Python
├── 📁 scripts/                    # Scripts de ejecución
│   ├── 🚀 install.sh              # Instalación completa
│   ├── 🚀 run.sh                  # Ejecutar sistema
│   ├── 🌐 api.sh                  # Ejecutar API
│   ├── 🧪 test.sh                 # Probar sistema
│   └── 🐍 agi_handler.py          # Script AGI para Asterisk
├── 📁 config/                     # Configuraciones
│   ├── 📁 asterisk/               # Configuración de Asterisk
│   │   ├── asterisk.conf          # Configuración principal
│   │   └── extensions.conf        # Dialplan
│   └── env.example                # Plantilla de variables
├── 📁 data/                       # Datos del sistema
│   └── numbers.txt                # Números de destino
└── 📁 src/                        # Código fuente
    ├── core/
    │   └── config.py              # Configuración centralizada
    ├── services/
    │   ├── asterisk_service.py    # Servicio Asterisk AMI
    │   ├── stt_service.py         # Speech-to-Text (Deepgram)
    │   ├── tts_service.py         # Text-to-Speech (ElevenLabs)
    │   ├── ai_service.py          # IA (Ollama)
    │   └── call_manager.py        # Orquestador principal
    ├── api/
    │   └── server.py              # Servidor FastAPI
    └── main.py                    # Punto de entrada
```

## 🔧 Servicios

### **Asterisk Service**
- Conexión AMI con Asterisk (puerto 5038)
- Control de llamadas salientes
- Manejo de eventos de llamada
- Integración con SIP trunk

### **AGI Handler**
- Script ejecutado por Asterisk durante llamadas
- Grabación de audio del usuario
- Reproducción de respuestas AI
- Manejo de conversaciones en tiempo real

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

## 🧪 Pruebas

### **Probar Sistema Completo**
```bash
./scripts/test.sh
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
./scripts/run.sh
```

### **Servidor API**
```bash
./scripts/api.sh
```

### **Directo**
```bash
source venv/bin/activate
python3 src/main.py
```

## 📊 Monitoreo

### **Logs de Asterisk**
```bash
sudo tail -f /var/log/asterisk/full
```

### **Estado del Sistema**
```bash
curl http://localhost:8000/status
```

### **Verificar Asterisk**
```bash
sudo asterisk -rx "sip show peers"
sudo asterisk -rx "core show channels"
```

## 🔍 Troubleshooting

### **Problemas Comunes**

1. **Asterisk no inicia**
   ```bash
   sudo systemctl status asterisk
   sudo asterisk -rx "core restart now"
   ```

2. **Error en SIP trunk**
   ```bash
   sudo asterisk -rx "sip show peers"
   sudo asterisk -rx "sip show registry"
   ```

3. **AGI no funciona**
   ```bash
   chmod +x agi_handler.py
   sudo asterisk -rx "agi show"
   ```

4. **Ollama no responde**
   ```bash
   sudo systemctl start ollama
   ollama pull llama2
   ```

### **Logs de Debug**
```bash
# Activar debug
export DEBUG=true
./run_system.sh
```

## 🎯 Casos de Uso

### **1. Call Center Automatizado**
- Llamadas salientes automáticas
- Respuestas inteligentes
- Escalabilidad masiva

### **2. Asistente Telefónico**
- Atención al cliente 24/7
- Respuestas contextuales
- Integración con CRM

### **3. Sistema de Encuestas**
- Llamadas programadas
- Recolección de datos
- Análisis automático

## 🎉 **CONCLUSIÓN**

**Este sistema híbrido está completamente funcional y listo para usar:**

1. **Ejecutar** `./scripts/install.sh`
2. **Configurar** tus credenciales en `.env`
3. **Probar** con `./scripts/test.sh`
4. **Ejecutar** con `./scripts/run.sh`

**¡Y listo! 🚀**

---

**Desarrollado con ❤️ para llamadas SIP inteligentes con Asterisk** 