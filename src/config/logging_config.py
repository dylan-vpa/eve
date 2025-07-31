"""
Configuración de logging del sistema
"""

import logging
import logging.handlers
import os
from typing import Dict, Any
from .settings import LOGGING_CONFIG

def setup_logging() -> None:
    """Configura el sistema de logging"""
    
    # Crear directorio de logs si no existe
    log_dir = os.path.dirname(LOGGING_CONFIG['file'])
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar formato
    formatter = logging.Formatter(LOGGING_CONFIG['format'])
    
    # Configurar nivel
    level = getattr(logging, LOGGING_CONFIG['level'].upper())
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Handler para consola
    if LOGGING_CONFIG['console_output']:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Handler para archivo con rotación
    if LOGGING_CONFIG['file']:
        file_handler = logging.handlers.RotatingFileHandler(
            LOGGING_CONFIG['file'],
            maxBytes=LOGGING_CONFIG['max_size'],
            backupCount=LOGGING_CONFIG['backup_count']
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Configurar loggers específicos
    setup_module_loggers()

def setup_module_loggers() -> None:
    """Configura loggers específicos para módulos"""
    
    # Logger para SIP
    sip_logger = logging.getLogger('sip')
    sip_logger.setLevel(logging.INFO)
    
    # Logger para audio
    audio_logger = logging.getLogger('audio')
    audio_logger.setLevel(logging.INFO)
    
    # Logger para STT
    stt_logger = logging.getLogger('stt')
    stt_logger.setLevel(logging.INFO)
    
    # Logger para TTS
    tts_logger = logging.getLogger('tts')
    tts_logger.setLevel(logging.INFO)
    
    # Logger para IA
    ai_logger = logging.getLogger('ai')
    ai_logger.setLevel(logging.INFO)
    
    # Logger para API
    api_logger = logging.getLogger('api')
    api_logger.setLevel(logging.INFO)
    
    # Logger para base de datos
    db_logger = logging.getLogger('database')
    db_logger.setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger configurado"""
    return logging.getLogger(name)

class CallLogger:
    """Logger especializado para llamadas SIP"""
    
    def __init__(self, call_id: str):
        self.call_id = call_id
        self.logger = logging.getLogger(f'call.{call_id}')
    
    def info(self, message: str) -> None:
        """Log de información de llamada"""
        self.logger.info(f"[Call {self.call_id}] {message}")
    
    def error(self, message: str) -> None:
        """Log de error de llamada"""
        self.logger.error(f"[Call {self.call_id}] {message}")
    
    def warning(self, message: str) -> None:
        """Log de advertencia de llamada"""
        self.logger.warning(f"[Call {self.call_id}] {message}")
    
    def debug(self, message: str) -> None:
        """Log de debug de llamada"""
        self.logger.debug(f"[Call {self.call_id}] {message}")

class PerformanceLogger:
    """Logger para métricas de rendimiento"""
    
    def __init__(self):
        self.logger = logging.getLogger('performance')
    
    def log_call_metrics(self, call_id: str, metrics: Dict[str, Any]) -> None:
        """Log de métricas de llamada"""
        self.logger.info(f"Call {call_id} metrics: {metrics}")
    
    def log_api_latency(self, service: str, latency: float) -> None:
        """Log de latencia de API"""
        self.logger.info(f"API {service} latency: {latency:.2f}ms")
    
    def log_audio_quality(self, call_id: str, quality_metrics: Dict[str, Any]) -> None:
        """Log de calidad de audio"""
        self.logger.info(f"Call {call_id} audio quality: {quality_metrics}")

class SecurityLogger:
    """Logger para eventos de seguridad"""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
    
    def log_auth_attempt(self, username: str, success: bool, ip: str) -> None:
        """Log de intento de autenticación"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.warning(f"Auth attempt {status} for user {username} from {ip}")
    
    def log_api_access(self, endpoint: str, method: str, ip: str) -> None:
        """Log de acceso a API"""
        self.logger.info(f"API access: {method} {endpoint} from {ip}")
    
    def log_suspicious_activity(self, activity: str, details: Dict[str, Any]) -> None:
        """Log de actividad sospechosa"""
        self.logger.error(f"Suspicious activity: {activity} - {details}")

# Inicializar logging al importar el módulo
setup_logging() 