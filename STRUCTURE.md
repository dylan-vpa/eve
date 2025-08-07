# 📁 Estructura del Proyecto

```
📁 Sistema de Llamadas SIP con IA
├── 📋 README.md                    # Documentación principal
├── 📋 STRUCTURE.md                 # Este archivo - Estructura del proyecto
├── 📋 requirements.txt             # Dependencias Python
├── 📋 .env                        # Variables de entorno (creado automáticamente)
├── 📁 scripts/                    # Scripts de ejecución
│   ├── 🚀 install.sh              # Instalación completa del sistema
│   ├── 🚀 run.sh                  # Ejecutar sistema completo
│   ├── 🌐 api.sh                  # Ejecutar servidor API
│   ├── 🧪 test.sh                 # Probar sistema
│   └── 🐍 agi_handler.py          # Script AGI para Asterisk
├── 📁 config/                     # Configuraciones
│   ├── 📁 asterisk/               # Configuración de Asterisk
│   │   ├── asterisk.conf          # Configuración principal de Asterisk
│   │   └── extensions.conf        # Dialplan de Asterisk
│   └── env.example                # Plantilla de variables de entorno
├── 📁 data/                       # Datos del sistema
│   └── numbers.txt                # Números de destino
├── 📁 src/                        # Código fuente
│   ├── 📁 core/                   # Núcleo del sistema
│   │   └── config.py              # Configuración centralizada
│   ├── 📁 services/               # Servicios del sistema
│   │   ├── asterisk_service.py    # Servicio Asterisk AMI
│   │   ├── stt_service.py         # Speech-to-Text (Deepgram)
│   │   ├── tts_service.py         # Text-to-Speech (ElevenLabs)
│   │   ├── ai_service.py          # IA (Ollama)
│   │   └── call_manager.py        # Orquestador principal
│   ├── 📁 api/                    # API REST
│   │   └── server.py              # Servidor FastAPI
│   ├── 📁 utils/                  # Utilidades
│   ├── __init__.py                # Inicializador del paquete
│   └── main.py                    # Punto de entrada principal
└── 📁 venv/                       # Entorno virtual Python (creado automáticamente)
```

## 🔧 Descripción de Carpetas

### **📁 scripts/**
Contiene todos los scripts de ejecución y utilidades:
- `install.sh` - Instalación completa del sistema
- `run.sh` - Ejecutar sistema completo
- `api.sh` - Ejecutar servidor API
- `test.sh` - Probar sistema
- `agi_handler.py` - Script AGI para Asterisk

### **📁 config/**
Configuraciones del sistema:
- `asterisk/` - Configuración de Asterisk
- `env.example` - Plantilla de variables de entorno

### **📁 data/**
Datos del sistema:
- `numbers.txt` - Números de destino para llamadas

### **📁 src/**
Código fuente de la aplicación:
- `core/` - Núcleo y configuración
- `services/` - Servicios del sistema
- `api/` - API REST
- `utils/` - Utilidades
- `main.py` - Punto de entrada

## 🚀 Comandos Principales

```bash
# Instalar sistema completo
./scripts/install.sh

# Ejecutar sistema
./scripts/run.sh

# Ejecutar API
./scripts/api.sh

# Probar sistema
./scripts/test.sh
```

## 📋 Archivos de Configuración

### **Asterisk**
- `config/asterisk/asterisk.conf` - Configuración principal
- `config/asterisk/extensions.conf` - Dialplan

### **Variables de Entorno**
- `config/env.example` - Plantilla
- `.env` - Configuración real (creado automáticamente)

### **Datos**
- `data/numbers.txt` - Números de destino

## 🎯 Flujo de Desarrollo

1. **Instalar**: `./scripts/install.sh`
2. **Configurar**: Editar `.env` con credenciales
3. **Probar**: `./scripts/test.sh`
4. **Ejecutar**: `./scripts/run.sh`
5. **API**: `./scripts/api.sh` (opcional)

## 🔍 Mantenimiento

### **Logs**
- Asterisk: `/var/log/asterisk/full`
- Aplicación: Consola
- API: Consola

### **Configuración**
- Asterisk: `config/asterisk/`
- Variables: `.env`
- Números: `data/numbers.txt`

### **Reiniciar Servicios**
```bash
sudo systemctl restart asterisk
sudo systemctl restart ollama
``` 