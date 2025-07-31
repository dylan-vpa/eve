"""
Modelos para transcripción de audio (STT)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
import uuid

class TranscriptionStatus(Enum):
    """Estados de transcripción"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class TranscriptionConfidence(Enum):
    """Niveles de confianza de transcripción"""
    HIGH = "high"      # 0.9-1.0
    MEDIUM = "medium"  # 0.7-0.9
    LOW = "low"        # 0.5-0.7
    VERY_LOW = "very_low"  # 0.0-0.5

@dataclass
class TranscriptionWord:
    """Palabra individual en una transcripción"""
    
    word: str
    start_time: float = 0.0  # segundos
    end_time: float = 0.0    # segundos
    confidence: float = 0.0   # 0-1
    speaker: Optional[str] = None
    
    def get_confidence_level(self) -> TranscriptionConfidence:
        """Obtiene el nivel de confianza"""
        if self.confidence >= 0.9:
            return TranscriptionConfidence.HIGH
        elif self.confidence >= 0.7:
            return TranscriptionConfidence.MEDIUM
        elif self.confidence >= 0.5:
            return TranscriptionConfidence.LOW
        else:
            return TranscriptionConfidence.VERY_LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'word': self.word,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'confidence': self.confidence,
            'speaker': self.speaker,
            'confidence_level': self.get_confidence_level().value,
        }

@dataclass
class TranscriptionSegment:
    """Segmento de transcripción"""
    
    text: str
    start_time: float = 0.0  # segundos
    end_time: float = 0.0    # segundos
    confidence: float = 0.0   # 0-1
    words: List[TranscriptionWord] = field(default_factory=list)
    speaker: Optional[str] = None
    
    def get_duration(self) -> float:
        """Obtiene la duración del segmento"""
        return self.end_time - self.start_time
    
    def get_confidence_level(self) -> TranscriptionConfidence:
        """Obtiene el nivel de confianza del segmento"""
        if self.confidence >= 0.9:
            return TranscriptionConfidence.HIGH
        elif self.confidence >= 0.7:
            return TranscriptionConfidence.MEDIUM
        elif self.confidence >= 0.5:
            return TranscriptionConfidence.LOW
        else:
            return TranscriptionConfidence.VERY_LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'text': self.text,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'confidence': self.confidence,
            'duration': self.get_duration(),
            'words': [word.to_dict() for word in self.words],
            'speaker': self.speaker,
            'confidence_level': self.get_confidence_level().value,
        }

@dataclass
class TranscriptionResult:
    """Resultado completo de transcripción"""
    
    # Identificación
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    call_id: Optional[str] = None
    audio_chunk_id: Optional[str] = None
    
    # Contenido
    text: str = ""
    language: str = "es-ES"
    segments: List[TranscriptionSegment] = field(default_factory=list)
    
    # Metadata
    status: TranscriptionStatus = TranscriptionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    # Métricas
    confidence: float = 0.0  # 0-1
    duration: float = 0.0    # segundos
    word_count: int = 0
    character_count: int = 0
    
    # Configuración
    model: str = "nova-2"
    punctuate: bool = True
    diarize: bool = False
    utterances: bool = True
    
    # Errores
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if self.text and not self.word_count:
            self.word_count = len(self.text.split())
        if self.text and not self.character_count:
            self.character_count = len(self.text)
    
    def complete(self, processing_time: Optional[float] = None) -> None:
        """Marca la transcripción como completada"""
        self.status = TranscriptionStatus.COMPLETED
        self.processed_at = datetime.now()
        
        if processing_time:
            self.duration = processing_time
    
    def fail(self, error_code: str, error_message: str) -> None:
        """Marca la transcripción como fallida"""
        self.status = TranscriptionStatus.FAILED
        self.error_code = error_code
        self.error_message = error_message
        self.processed_at = datetime.now()
    
    def get_confidence_level(self) -> TranscriptionConfidence:
        """Obtiene el nivel de confianza general"""
        if self.confidence >= 0.9:
            return TranscriptionConfidence.HIGH
        elif self.confidence >= 0.7:
            return TranscriptionConfidence.MEDIUM
        elif self.confidence >= 0.5:
            return TranscriptionConfidence.LOW
        else:
            return TranscriptionConfidence.VERY_LOW
    
    def get_processing_time(self) -> Optional[float]:
        """Obtiene el tiempo de procesamiento"""
        if self.processed_at and self.created_at:
            return (self.processed_at - self.created_at).total_seconds()
        return None
    
    def is_high_quality(self) -> bool:
        """Verifica si la transcripción es de alta calidad"""
        return (
            self.confidence >= 0.8 and
            self.word_count > 0 and
            len(self.text.strip()) > 0
        )
    
    def get_speakers(self) -> List[str]:
        """Obtiene la lista de hablantes identificados"""
        speakers = set()
        for segment in self.segments:
            if segment.speaker:
                speakers.add(segment.speaker)
        return list(speakers)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'call_id': self.call_id,
            'audio_chunk_id': self.audio_chunk_id,
            'text': self.text,
            'language': self.language,
            'segments': [segment.to_dict() for segment in self.segments],
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'confidence': self.confidence,
            'duration': self.duration,
            'word_count': self.word_count,
            'character_count': self.character_count,
            'model': self.model,
            'punctuate': self.punctuate,
            'diarize': self.diarize,
            'utterances': self.utterances,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'confidence_level': self.get_confidence_level().value,
            'processing_time': self.get_processing_time(),
            'is_high_quality': self.is_high_quality(),
            'speakers': self.get_speakers(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranscriptionResult':
        """Crea una transcripción desde diccionario"""
        # Convertir timestamps
        for field in ['created_at', 'processed_at']:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        # Convertir enum
        data['status'] = TranscriptionStatus(data['status'])
        
        # Convertir segmentos
        if 'segments' in data:
            segments = []
            for segment_data in data['segments']:
                words = []
                for word_data in segment_data.get('words', []):
                    words.append(TranscriptionWord(**word_data))
                segment_data['words'] = words
                segments.append(TranscriptionSegment(**segment_data))
            data['segments'] = segments
        
        return cls(**data)

@dataclass
class TranscriptionQueue:
    """Cola de transcripciones pendientes"""
    
    results: List[TranscriptionResult] = field(default_factory=list)
    max_size: int = 100
    processing: bool = False
    
    def add_result(self, result: TranscriptionResult) -> bool:
        """Agrega un resultado a la cola"""
        if len(self.results) >= self.max_size:
            return False
        
        self.results.append(result)
        return True
    
    def get_next_result(self) -> Optional[TranscriptionResult]:
        """Obtiene el siguiente resultado de la cola"""
        if not self.results:
            return None
        
        return self.results.pop(0)
    
    def get_pending_results(self) -> List[TranscriptionResult]:
        """Obtiene los resultados pendientes"""
        return [result for result in self.results if result.status == TranscriptionStatus.PENDING]
    
    def get_completed_results(self) -> List[TranscriptionResult]:
        """Obtiene los resultados completados"""
        return [result for result in self.results if result.status == TranscriptionStatus.COMPLETED]
    
    def get_failed_results(self) -> List[TranscriptionResult]:
        """Obtiene los resultados fallidos"""
        return [result for result in self.results if result.status == TranscriptionStatus.FAILED]
    
    def clear_old_results(self, max_age: float) -> int:
        """Limpia resultados antiguos y retorna el número eliminado"""
        current_time = datetime.now()
        initial_count = len(self.results)
        
        self.results = [
            result for result in self.results
            if (current_time - result.created_at).total_seconds() <= max_age
        ]
        
        return initial_count - len(self.results)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la cola"""
        return {
            'total_results': len(self.results),
            'pending_results': len(self.get_pending_results()),
            'completed_results': len(self.get_completed_results()),
            'failed_results': len(self.get_failed_results()),
            'processing': self.processing,
            'max_size': self.max_size,
        } 