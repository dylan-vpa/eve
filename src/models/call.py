"""
Modelos para manejo de llamadas SIP
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
import uuid

class CallStatus(Enum):
    """Estados de una llamada SIP"""
    INITIATING = "initiating"
    RINGING = "ringing"
    CONNECTED = "connected"
    IN_PROGRESS = "in_progress"
    ENDED = "ended"
    FAILED = "failed"
    TIMEOUT = "timeout"
    BUSY = "busy"
    NO_ANSWER = "no_answer"

class CallDirection(Enum):
    """Dirección de la llamada"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"

@dataclass
class CallMetrics:
    """Métricas de una llamada"""
    duration: float = 0.0  # segundos
    audio_quality: float = 0.0  # 0-1
    latency: float = 0.0  # ms
    packet_loss: float = 0.0  # porcentaje
    jitter: float = 0.0  # ms
    mos_score: float = 0.0  # Mean Opinion Score
    stt_accuracy: float = 0.0  # porcentaje
    tts_latency: float = 0.0  # ms
    ai_response_time: float = 0.0  # ms

@dataclass
class Call:
    """Modelo de llamada SIP"""
    
    # Identificación
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sip_call_id: Optional[str] = None
    
    # Información básica
    direction: CallDirection = CallDirection.OUTBOUND
    status: CallStatus = CallStatus.INITIATING
    
    # Números
    from_number: str = ""
    to_number: str = ""
    sip_uri: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    connected_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Duración
    duration: float = 0.0  # segundos
    
    # Configuración
    timeout: int = 30  # segundos
    max_duration: int = 300  # segundos
    
    # Métricas
    metrics: CallMetrics = field(default_factory=CallMetrics)
    
    # Estado de procesamiento
    transcription_count: int = 0
    ai_response_count: int = 0
    tts_generation_count: int = 0
    
    # Errores
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if not self.sip_call_id:
            self.sip_call_id = f"call_{self.id[:8]}"
    
    def start(self) -> None:
        """Marca el inicio de la llamada"""
        self.started_at = datetime.now()
        self.status = CallStatus.RINGING
    
    def connect(self) -> None:
        """Marca la conexión de la llamada"""
        self.connected_at = datetime.now()
        self.status = CallStatus.CONNECTED
    
    def end(self, reason: Optional[str] = None) -> None:
        """Marca el fin de la llamada"""
        self.ended_at = datetime.now()
        self.status = CallStatus.ENDED
        
        if self.started_at:
            self.duration = (self.ended_at - self.started_at).total_seconds()
        
        if reason:
            self.error_message = reason
    
    def fail(self, error_code: str, error_message: str) -> None:
        """Marca la falla de la llamada"""
        self.ended_at = datetime.now()
        self.status = CallStatus.FAILED
        self.error_code = error_code
        self.error_message = error_message
    
    def timeout(self) -> None:
        """Marca timeout de la llamada"""
        self.ended_at = datetime.now()
        self.status = CallStatus.TIMEOUT
        self.error_message = "Call timeout"
    
    def is_active(self) -> bool:
        """Verifica si la llamada está activa"""
        return self.status in [CallStatus.CONNECTED, CallStatus.IN_PROGRESS]
    
    def is_ended(self) -> bool:
        """Verifica si la llamada ha terminado"""
        return self.status in [CallStatus.ENDED, CallStatus.FAILED, CallStatus.TIMEOUT, CallStatus.BUSY, CallStatus.NO_ANSWER]
    
    def get_duration(self) -> float:
        """Obtiene la duración actual de la llamada"""
        if self.ended_at and self.started_at:
            return (self.ended_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now() - self.started_at).total_seconds()
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la llamada a diccionario"""
        return {
            'id': self.id,
            'sip_call_id': self.sip_call_id,
            'direction': self.direction.value,
            'status': self.status.value,
            'from_number': self.from_number,
            'to_number': self.to_number,
            'sip_uri': self.sip_uri,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'connected_at': self.connected_at.isoformat() if self.connected_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration': self.get_duration(),
            'timeout': self.timeout,
            'max_duration': self.max_duration,
            'transcription_count': self.transcription_count,
            'ai_response_count': self.ai_response_count,
            'tts_generation_count': self.tts_generation_count,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Call':
        """Crea una llamada desde diccionario"""
        # Convertir timestamps
        for field in ['created_at', 'started_at', 'connected_at', 'ended_at']:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        # Convertir enums
        data['direction'] = CallDirection(data['direction'])
        data['status'] = CallStatus(data['status'])
        
        return cls(**data)

@dataclass
class CallQueue:
    """Cola de llamadas"""
    
    calls: List[Call] = field(default_factory=list)
    max_size: int = 100
    processing: bool = False
    
    def add_call(self, call: Call) -> bool:
        """Agrega una llamada a la cola"""
        if len(self.calls) >= self.max_size:
            return False
        
        self.calls.append(call)
        return True
    
    def get_next_call(self) -> Optional[Call]:
        """Obtiene la siguiente llamada de la cola"""
        if not self.calls:
            return None
        
        return self.calls.pop(0)
    
    def get_active_calls(self) -> List[Call]:
        """Obtiene las llamadas activas"""
        return [call for call in self.calls if call.is_active()]
    
    def get_ended_calls(self) -> List[Call]:
        """Obtiene las llamadas terminadas"""
        return [call for call in self.calls if call.is_ended()]
    
    def clear_ended_calls(self) -> int:
        """Limpia las llamadas terminadas y retorna el número eliminado"""
        initial_count = len(self.calls)
        self.calls = [call for call in self.calls if not call.is_ended()]
        return initial_count - len(self.calls)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la cola"""
        return {
            'total_calls': len(self.calls),
            'active_calls': len(self.get_active_calls()),
            'ended_calls': len(self.get_ended_calls()),
            'processing': self.processing,
            'max_size': self.max_size,
        } 