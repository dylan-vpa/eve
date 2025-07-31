# Sistema de Llamadas SIP con IA y STT/TTS

Este proyecto implementa un **backend robusto y modular** para conectar con una troncal SIP, iniciar llamadas salientes a números específicos, transcribir el audio del usuario (Speech-to-Text con Deepgram), procesar la entrada con un modelo de IA, generar audio de respuesta (Text-to-Speech con ElevenLabs), y enviar el audio al usuario a través de la troncal SIP.

## 🏗️ Arquitectura del Sistema

### Estructura Modular

```
eve/
├── src/                          # Código fuente principal
│   ├── config/                   # Configuración del sistema
│   │   ├── settings.py          # Configuración principal
│   │   └── logging_config.py    # Configuración de logging
│   ├── models/                   # Modelos de datos
│   │   ├── call.py              # Modelos de llamadas SIP
│   │   ├── audio.py             # Modelos de audio
│   │   ├── transcription.py     # Modelos de transcripción
│   │   └── ai_response.py       # Modelos de respuestas IA
│   ├── services/                 # Servicios del sistema
│   │   ├── sip_service.py       # Servicio SIP
│   │   ├── audio_service.py     # Servicio de audio
│   │   ├── stt_service.py       # Servicio STT (Deepgram)
│   │   ├── tts_service.py       # Servicio TTS (ElevenLabs)
│   │   ├── ai_service.py        # Servicio de IA
│   │   └── call_manager.py      # Gestor de llamadas
│   ├── utils/                    # Utilidades
│   ├── api/                      # APIs REST (futuro)
│   ├── handlers/                 # Manejadores de eventos
│   └── main.py                  # Aplicación principal
├── tests/                        # Tests unitarios
├── docs/                         # Documentación
├── scripts/                      # Scripts de utilidad
├── main.py                       # Punto de entrada
├── requirements.txt              # Dependencias Python
├── install_pjsip.sh             # Instalación PJSIP
├── setup.sh                      # Script de configuración
├── test_apis.py                  # Pruebas de APIs
├── numbers.txt                   # Números de destino
├── env.example                   # Variables de entorno
└── README.md                     # Este archivo
```

### Características del Backend

- **🔄 Arquitectura Modular**: Separación clara de responsabilidades
- **📊 Gestión de Estado**: Modelos de datos robustos con validación
- **🔧 Servicios Especializados**: Cada servicio maneja una funcionalidad específica
- **📝 Logging Avanzado**: Sistema de logging jerárquico con métricas
- **⚡ Concurrencia**: Uso de asyncio para operaciones asíncronas
- **🛡️ Manejo de Errores**: Gestión robusta de errores y excepciones
- **📈 Métricas**: Monitoreo de rendimiento y calidad
- **🔌 Callbacks**: Sistema de eventos para integración flexible

## 🚀 Características

### Servicios Principales

- **📞 SIP Service**: Manejo completo de llamadas SIP con PJSIP
- **🎤 Audio Service**: Grabación, procesamiento y análisis de calidad de audio
- **🎯 STT Service**: Transcripción de audio usando Deepgram API
- **🎵 TTS Service**: Generación de audio usando ElevenLabs API
- **🤖 AI Service**: Procesamiento de IA con soporte para múltiples modelos
- **🎛️ Call Manager**: Coordinación de todos los servicios

### Funcionalidades Avanzadas

- **🔄 Flujo Completo**: STT → IA → TTS → SIP
- **📊 Métricas en Tiempo Real**: Calidad de audio, latencia, confianza
- **🎛️ Configuración Flexible**: Variables de entorno y archivos de configuración
- **🛡️ Robustez**: Manejo de errores, reintentos y fallbacks
- **📈 Escalabilidad**: Arquitectura preparada para múltiples llamadas concurrentes

## 📋 Requisitos

### RunPod
- Instancia con Ubuntu 20.04/22.04
- 8+ vCPUs, 16+ GB RAM
- GPU opcional (para modelos de IA pesados)
- Puertos abiertos: 5060 (SIP, UDP), 16384-32767 (RTP), 443 (HTTPS)

### Credenciales
- **SIP**: Usuario, contraseña y host de la troncal SIP
- **Deepgram API Key**: Para transcripción ([deepgram.com](https://deepgram.com))
- **ElevenLabs API Key**: Para TTS ([elevenlabs.io](https://elevenlabs.io))

## 🛠️ Instalación

### 1. Configuración Automática

```bash
# Clonar repositorio
git clone <URL_DEL_REPOSITORIO>
cd eve

# Configuración automática
chmod +x setup.sh
./setup.sh
```

### 2. Configuración Manual

```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install -y build-essential libssl-dev python3-dev libasound-dev portaudio19-dev

# Instalar PJSIP
chmod +x install_pjsip.sh
bash install_pjsip.sh

# Instalar dependencias Python
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar configuración
nano .env
```

O usar variables de entorno:

```bash
export SIP_HOST="tu_host_sip"
export SIP_USERNAME="tu_usuario"
export SIP_PASSWORD="tu_contraseña"
export DEEPGRAM_API_KEY="tu_clave_deepgram"
export ELEVENLABS_API_KEY="tu_clave_elevenlabs"
export ELEVENLABS_VOICE_ID="tu_voz_id"
```

## 🚀 Uso

### Ejecutar el Sistema

```bash
python3 main.py
```

### Probar APIs Individualmente

```bash
python3 test_apis.py
```

### Verificar Configuración

```bash
python3 -c "from src.config.settings import print_config_summary; print_config_summary()"
```

## 📊 Monitoreo y Métricas

### Logs del Sistema

- **SIP**: Registro de llamadas y eventos SIP
- **Audio**: Calidad y procesamiento de audio
- **STT**: Transcripciones y confianza
- **TTS**: Generación de audio
- **AI**: Procesamiento de respuestas
- **Performance**: Métricas de rendimiento

### Métricas Disponibles

- **Llamadas**: Duración, estado, calidad de audio
- **STT**: Confianza, precisión, tiempo de procesamiento
- **TTS**: Latencia, calidad de audio generado
- **IA**: Relevancia, confianza, tiempo de respuesta
- **Sistema**: Uso de recursos, errores, disponibilidad

## 🔧 Configuración Avanzada

### Configuración de Audio

```python
# src/config/settings.py
AUDIO_CONFIG = {
    'sample_rate': 16000,
    'channels': 1,
    'chunk_duration': 2.0,
    'noise_reduction': True,
    'echo_cancellation': True,
}
```

### Configuración de IA

```python
# src/config/settings.py
AI_CONFIG = {
    'model_type': 'placeholder',  # placeholder, llama, grok, custom
    'max_response_length': 200,
    'temperature': 0.7,
    'top_p': 0.9,
}
```

### Configuración de Logging

```python
# src/config/settings.py
LOGGING_CONFIG = {
    'level': 'INFO',
    'file': 'logs/sip_system.log',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
}
```

## 🧪 Testing

### Pruebas Unitarias

```bash
# Ejecutar tests
python -m pytest tests/

# Tests específicos
python -m pytest tests/test_sip_service.py
python -m pytest tests/test_audio_service.py
```

### Pruebas de Integración

```bash
# Probar flujo completo
python3 test_integration.py

# Probar APIs externas
python3 test_apis.py
```

## 🔍 Depuración

### Logs Detallados

```bash
# Activar logs de debug
export LOG_LEVEL=DEBUG
python3 main.py
```

### Métricas en Tiempo Real

```bash
# Ver estadísticas del sistema
python3 -c "
from src.services.call_manager import CallManager
import asyncio

async def show_stats():
    manager = CallManager()
    await manager.initialize()
    stats = manager.get_manager_stats()
    print('Estadísticas:', stats)

asyncio.run(show_stats())
"
```

## 🚀 Escalabilidad

### Múltiples Llamadas Concurrentes

```python
# Configurar máximo de llamadas concurrentes
CALL_CONFIG = {
    'max_concurrent_calls': 10,
    'call_timeout': 300,
    'ring_timeout': 30,
}
```

### Optimización de Rendimiento

```python
# Configuración de rendimiento
PERFORMANCE_CONFIG = {
    'max_memory_usage': 2048,  # MB
    'cpu_limit': 80,  # porcentaje
    'audio_buffer_size': 16384,  # bytes
    'max_concurrent_requests': 20,
}
```

## 🔮 Próximas Características

- **🌐 API REST**: Endpoints para control remoto
- **📊 Dashboard Web**: Interfaz de monitoreo
- **🔌 Webhooks**: Notificaciones en tiempo real
- **📱 SDK**: Librerías para integración
- **🔄 Load Balancer**: Distribución de carga
- **💾 Base de Datos**: Persistencia de datos
- **🔐 Autenticación**: Sistema de seguridad

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

MIT License. Usa y modifica libremente, pero verifica los términos de Deepgram, ElevenLabs, y tu proveedor SIP.

## 🆘 Soporte

- **📖 Documentación**: Revisa los archivos en `docs/`
- **🐛 Issues**: Reporta problemas en GitHub
- **💬 Comunidad**: Únete a nuestro Discord
- **📧 Email**: soporte@tuempresa.com

---

**¡Construido con ❤️ para el futuro de las comunicaciones con IA!** 