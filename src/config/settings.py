"""
Configuración principal del sistema
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ============================================================================
# CONFIGURACIÓN SIP
# ============================================================================

SIP_CONFIG = {
    'host': os.environ.get("SIP_HOST", "sip.example.com"),
    'username': os.environ.get("SIP_USERNAME", "tu_usuario"),
    'password': os.environ.get("SIP_PASSWORD", "tu_contraseña"),
    'port': 5060,
    'transport': 'udp',  # udp, tcp, tls
    'timeout': 30,  # segundos
    'retry_count': 3,
    'retry_delay': 5,  # segundos
    'max_concurrent_calls': 5,
    'call_timeout': 300,  # segundos (5 minutos)
    'ring_timeout': 30,  # segundos
}

# ============================================================================
# CONFIGURACIÓN DE AUDIO
# ============================================================================

AUDIO_CONFIG = {
    'sample_rate': 16000,
    'channels': 1,  # mono
    'chunk_size': 1024,
    'chunk_duration': 2.0,  # segundos
    'audio_format': 'pcm_s16le',  # 16-bit PCM
    'silence_threshold': 0.01,  # umbral de silencio
    'noise_reduction': True,
    'echo_cancellation': True,
    'buffer_size': 8192,  # bytes
}

# Codecs SIP (prioridad)
SIP_CODECS = [
    'PCMU',    # G.711 u-law
    'PCMA',    # G.711 a-law
    'opus',    # Opus (si está disponible)
    'G722',    # G.722 (si está disponible)
]

# ============================================================================
# CONFIGURACIÓN STT (DEEPGRAM)
# ============================================================================

DEEPGRAM_CONFIG = {
    'api_key': os.environ.get("DEEPGRAM_API_KEY", "tu_clave_deepgram"),
    'url': 'https://api.deepgram.com/v1/listen',
    'language': 'es-ES',  # español
    'model': 'nova-2',  # modelo de transcripción
    'punctuate': True,
    'diarize': False,
    'utterances': True,
    'interim_results': False,
    'endpointing': 800,  # ms de silencio para finalizar
    'vad_turnoff': 1000,  # ms de silencio para VAD
    'timeout': 30,  # segundos
    'retry_attempts': 3,
}

# ============================================================================
# CONFIGURACIÓN TTS (ELEVENLABS)
# ============================================================================

ELEVENLABS_CONFIG = {
    'api_key': os.environ.get("ELEVENLABS_API_KEY", "tu_clave_elevenlabs"),
    'voice_id': os.environ.get("ELEVENLABS_VOICE_ID", "tu_voz_id"),
    'url': 'https://api.elevenlabs.io/v1/text-to-speech',
    'model_id': 'eleven_monolingual_v1',
    'voice_settings': {
        'stability': 0.5,
        'similarity_boost': 0.5,
        'style': 0.0,
        'use_speaker_boost': True,
    },
    'optimization_level': 0,  # 0=standard, 1=enhanced
    'timeout': 30,  # segundos
    'retry_attempts': 3,
}

# ============================================================================
# CONFIGURACIÓN DE IA
# ============================================================================

AI_CONFIG = {
    'model_type': os.environ.get("AI_MODEL_TYPE", "ollama"),  # placeholder, ollama, llama, grok, custom
    'model_name': os.environ.get("AI_MODEL_NAME", "llama2"),
    'ollama_url': os.environ.get("OLLAMA_URL", "http://localhost:11434"),
    'max_response_length': int(os.environ.get("AI_MAX_LENGTH", "200")),  # caracteres
    'response_delay': float(os.environ.get("AI_RESPONSE_DELAY", "0.5")),  # segundos (simulación)
    'context_window': int(os.environ.get("AI_CONTEXT_WINDOW", "1000")),  # caracteres de contexto
    'temperature': float(os.environ.get("AI_TEMPERATURE", "0.7")),  # para modelos generativos
    'top_p': float(os.environ.get("AI_TOP_P", "0.9")),  # para modelos generativos
    'timeout': int(os.environ.get("AI_TIMEOUT", "30")),  # segundos
    'retry_attempts': int(os.environ.get("AI_RETRY_ATTEMPTS", "3")),
    'use_gpu': os.environ.get("AI_USE_GPU", "False").lower() == "true",
    'device': os.environ.get("AI_DEVICE", "cpu"),  # cpu, cuda, mps
}

# Respuestas de placeholder (para pruebas)
PLACEHOLDER_RESPONSES = [
    "Entiendo lo que dices. ¿Puedes contarme más?",
    "Esa es una pregunta interesante. Déjame pensar en eso.",
    "Gracias por compartir eso conmigo. ¿Hay algo más en lo que pueda ayudarte?",
    "He procesado tu información. ¿Necesitas alguna aclaración?",
    "Excelente punto. ¿Te gustaría que profundicemos en ese tema?",
    "Estoy aquí para ayudarte. ¿Qué más te gustaría saber?",
    "Interesante perspectiva. ¿Puedes elaborar un poco más?",
    "Gracias por tu paciencia. Estoy procesando tu solicitud.",
]

# ============================================================================
# CONFIGURACIÓN DE RENDIMIENTO
# ============================================================================

PERFORMANCE_CONFIG = {
    'max_memory_usage': 1024,  # MB
    'cpu_limit': 80,  # porcentaje
    'audio_buffer_size': 8192,  # bytes
    'network_timeout': 30,  # segundos
    'retry_attempts': 3,
    'cache_audio': True,
    'cache_duration': 3600,  # segundos (1 hora)
    'max_concurrent_requests': 10,
    'queue_size': 100,
}

# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================================================

SECURITY_CONFIG = {
    'enable_ssl': True,
    'verify_ssl': True,
    'api_rate_limit': 100,  # requests por minuto
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'allowed_audio_formats': ['.wav', '.mp3', '.flac'],
    'sanitize_input': True,
    'encrypt_credentials': True,
}

# ============================================================================
# CONFIGURACIÓN DE MONITOREO
# ============================================================================

MONITORING_CONFIG = {
    'enable_metrics': True,
    'metrics_interval': 60,  # segundos
    'health_check_interval': 30,  # segundos
    'alert_on_failure': True,
    'log_call_details': True,
    'log_audio_quality': True,
    'enable_tracing': True,
    'tracing_sample_rate': 0.1,  # 10% de las llamadas
}

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

DATABASE_CONFIG = {
    'type': 'sqlite',  # sqlite, postgresql, mysql
    'url': os.environ.get("DATABASE_URL", "sqlite:///sip_system.db"),
    'pool_size': 10,
    'max_overflow': 20,
    'echo': False,  # SQL logging
}

# ============================================================================
# CONFIGURACIÓN DE CACHE
# ============================================================================

CACHE_CONFIG = {
    'type': 'memory',  # memory, redis
    'redis_url': os.environ.get("REDIS_URL", "redis://localhost:6379"),
    'ttl': 3600,  # segundos
    'max_size': 1000,  # items
}

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

LOGGING_CONFIG = {
    'level': os.environ.get("LOG_LEVEL", "INFO"),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/sip_system.log',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'console_output': True,
    'json_format': False,
}

# ============================================================================
# CONFIGURACIÓN DE API REST
# ============================================================================

API_CONFIG = {
    'host': os.environ.get("API_HOST", "0.0.0.0"),
    'port': int(os.environ.get("API_PORT", "8000")),
    'debug': os.environ.get("DEBUG", "False").lower() == "true",
    'cors_origins': ["*"],
    'rate_limit': 100,  # requests por minuto
    'timeout': 30,  # segundos
}

# ============================================================================
# FUNCIONES DE CONFIGURACIÓN
# ============================================================================

def get_sip_uri() -> str:
    """Obtiene la URI SIP completa"""
    return f"sip:{SIP_CONFIG['username']}@{SIP_CONFIG['host']}"

def get_registrar_uri() -> str:
    """Obtiene la URI del registrador SIP"""
    return f"sip:{SIP_CONFIG['host']}"

def validate_config() -> List[str]:
    """Valida la configuración y retorna lista de errores"""
    errors = []
    
    # Verificar credenciales SIP
    if SIP_CONFIG['host'] == "sip.example.com":
        errors.append("SIP_HOST no configurado")
    if SIP_CONFIG['username'] == "tu_usuario":
        errors.append("SIP_USERNAME no configurado")
    if SIP_CONFIG['password'] == "tu_contraseña":
        errors.append("SIP_PASSWORD no configurado")
    
    # Verificar APIs
    if DEEPGRAM_CONFIG['api_key'] == "tu_clave_deepgram":
        errors.append("DEEPGRAM_API_KEY no configurado")
    if ELEVENLABS_CONFIG['api_key'] == "tu_clave_elevenlabs":
        errors.append("ELEVENLABS_API_KEY no configurado")
    if ELEVENLABS_CONFIG['voice_id'] == "tu_voz_id":
        errors.append("ELEVENLABS_VOICE_ID no configurado")
    
    return errors

def get_config_summary() -> Dict[str, Any]:
    """Retorna un resumen de la configuración"""
    return {
        'sip': {
            'host': SIP_CONFIG['host'],
            'username': SIP_CONFIG['username'],
            'port': SIP_CONFIG['port'],
        },
        'audio': {
            'sample_rate': AUDIO_CONFIG['sample_rate'],
            'channels': AUDIO_CONFIG['channels'],
            'chunk_duration': AUDIO_CONFIG['chunk_duration'],
        },
        'stt': {
            'provider': 'Deepgram',
            'model': DEEPGRAM_CONFIG['model'],
            'language': DEEPGRAM_CONFIG['language'],
        },
        'tts': {
            'provider': 'ElevenLabs',
            'voice_id': ELEVENLABS_CONFIG['voice_id'],
        },
        'ai': {
            'model_type': AI_CONFIG['model_type'],
        },
        'api': {
            'host': API_CONFIG['host'],
            'port': API_CONFIG['port'],
        },
    } 