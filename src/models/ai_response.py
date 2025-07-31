"""
Modelos para respuestas de IA
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
import uuid

class AIResponseType(Enum):
    """Tipos de respuesta de IA"""
    GREETING = "greeting"
    QUESTION = "question"
    ANSWER = "answer"
    CLARIFICATION = "clarification"
    CONFIRMATION = "confirmation"
    GOODBYE = "goodbye"
    ERROR = "error"
    FALLBACK = "fallback"

class AIResponseStatus(Enum):
    """Estados de respuesta de IA"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class AIResponseQuality(Enum):
    """Niveles de calidad de respuesta de IA"""
    EXCELLENT = "excellent"  # Muy relevante y útil
    GOOD = "good"           # Relevante y útil
    FAIR = "fair"           # Moderadamente relevante
    POOR = "poor"           # Poco relevante
    BAD = "bad"             # No relevante o inútil

@dataclass
class AIResponseContext:
    """Contexto para la respuesta de IA"""
    
    # Información de la llamada
    call_id: str
    user_input: str
    conversation_history: List[str] = field(default_factory=list)
    
    # Configuración
    max_length: int = 200
    temperature: float = 0.7
    top_p: float = 0.9
    
    # Metadata
    language: str = "es-ES"
    intent: Optional[str] = None
    entities: List[str] = field(default_factory=list)
    sentiment: Optional[str] = None
    
    def add_to_history(self, text: str) -> None:
        """Agrega texto al historial de conversación"""
        self.conversation_history.append(text)
        # Mantener solo los últimos 10 mensajes
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_context_summary(self) -> str:
        """Obtiene un resumen del contexto"""
        return f"Call: {self.call_id}, Input: {self.user_input[:50]}..., History: {len(self.conversation_history)} messages"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'call_id': self.call_id,
            'user_input': self.user_input,
            'conversation_history': self.conversation_history,
            'max_length': self.max_length,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'language': self.language,
            'intent': self.intent,
            'entities': self.entities,
            'sentiment': self.sentiment,
        }

@dataclass
class AIResponse:
    """Respuesta generada por IA"""
    
    # Identificación
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    call_id: Optional[str] = None
    transcription_id: Optional[str] = None
    
    # Contenido
    text: str = ""
    response_type: AIResponseType = AIResponseType.ANSWER
    
    # Contexto
    context: Optional[AIResponseContext] = None
    
    # Metadata
    status: AIResponseStatus = AIResponseStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    # Métricas
    confidence: float = 0.0  # 0-1
    relevance_score: float = 0.0  # 0-1
    processing_time: float = 0.0  # segundos
    token_count: int = 0
    character_count: int = 0
    
    # Configuración
    model: str = "placeholder"
    temperature: float = 0.7
    max_length: int = 200
    
    # Errores
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if self.text and not self.character_count:
            self.character_count = len(self.text)
        if self.text and not self.token_count:
            # Estimación simple de tokens (1 token ≈ 4 caracteres)
            self.token_count = len(self.text) // 4
    
    def complete(self, processing_time: Optional[float] = None) -> None:
        """Marca la respuesta como completada"""
        self.status = AIResponseStatus.COMPLETED
        self.processed_at = datetime.now()
        
        if processing_time:
            self.processing_time = processing_time
    
    def fail(self, error_code: str, error_message: str) -> None:
        """Marca la respuesta como fallida"""
        self.status = AIResponseStatus.FAILED
        self.error_code = error_code
        self.error_message = error_message
        self.processed_at = datetime.now()
    
    def get_quality_level(self) -> AIResponseQuality:
        """Obtiene el nivel de calidad basado en relevancia y confianza"""
        # Combinar relevancia y confianza
        quality_score = (self.relevance_score + self.confidence) / 2
        
        if quality_score >= 0.9:
            return AIResponseQuality.EXCELLENT
        elif quality_score >= 0.8:
            return AIResponseQuality.GOOD
        elif quality_score >= 0.6:
            return AIResponseQuality.FAIR
        elif quality_score >= 0.4:
            return AIResponseQuality.POOR
        else:
            return AIResponseQuality.BAD
    
    def is_high_quality(self) -> bool:
        """Verifica si la respuesta es de alta calidad"""
        return (
            self.relevance_score >= 0.8 and
            self.confidence >= 0.8 and
            len(self.text.strip()) > 0 and
            self.status == AIResponseStatus.COMPLETED
        )
    
    def is_appropriate_length(self) -> bool:
        """Verifica si la longitud es apropiada"""
        return 10 <= self.character_count <= self.max_length
    
    def get_response_category(self) -> str:
        """Obtiene la categoría de la respuesta"""
        if self.response_type == AIResponseType.GREETING:
            return "saludo"
        elif self.response_type == AIResponseType.QUESTION:
            return "pregunta"
        elif self.response_type == AIResponseType.ANSWER:
            return "respuesta"
        elif self.response_type == AIResponseType.CLARIFICATION:
            return "aclaración"
        elif self.response_type == AIResponseType.CONFIRMATION:
            return "confirmación"
        elif self.response_type == AIResponseType.GOODBYE:
            return "despedida"
        elif self.response_type == AIResponseType.ERROR:
            return "error"
        else:
            return "fallback"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'call_id': self.call_id,
            'transcription_id': self.transcription_id,
            'text': self.text,
            'response_type': self.response_type.value,
            'context': self.context.to_dict() if self.context else None,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'confidence': self.confidence,
            'relevance_score': self.relevance_score,
            'processing_time': self.processing_time,
            'token_count': self.token_count,
            'character_count': self.character_count,
            'model': self.model,
            'temperature': self.temperature,
            'max_length': self.max_length,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'quality_level': self.get_quality_level().value,
            'is_high_quality': self.is_high_quality(),
            'is_appropriate_length': self.is_appropriate_length(),
            'response_category': self.get_response_category(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIResponse':
        """Crea una respuesta desde diccionario"""
        # Convertir timestamps
        for field in ['created_at', 'processed_at']:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        # Convertir enums
        data['response_type'] = AIResponseType(data['response_type'])
        data['status'] = AIResponseStatus(data['status'])
        
        # Convertir contexto
        if data.get('context'):
            data['context'] = AIResponseContext(**data['context'])
        
        return cls(**data)

@dataclass
class AIResponseQueue:
    """Cola de respuestas de IA pendientes"""
    
    responses: List[AIResponse] = field(default_factory=list)
    max_size: int = 100
    processing: bool = False
    
    def add_response(self, response: AIResponse) -> bool:
        """Agrega una respuesta a la cola"""
        if len(self.responses) >= self.max_size:
            return False
        
        self.responses.append(response)
        return True
    
    def get_next_response(self) -> Optional[AIResponse]:
        """Obtiene la siguiente respuesta de la cola"""
        if not self.responses:
            return None
        
        return self.responses.pop(0)
    
    def get_pending_responses(self) -> List[AIResponse]:
        """Obtiene las respuestas pendientes"""
        return [response for response in self.responses if response.status == AIResponseStatus.PENDING]
    
    def get_completed_responses(self) -> List[AIResponse]:
        """Obtiene las respuestas completadas"""
        return [response for response in self.responses if response.status == AIResponseStatus.COMPLETED]
    
    def get_failed_responses(self) -> List[AIResponse]:
        """Obtiene las respuestas fallidas"""
        return [response for response in self.responses if response.status == AIResponseStatus.FAILED]
    
    def get_high_quality_responses(self) -> List[AIResponse]:
        """Obtiene las respuestas de alta calidad"""
        return [response for response in self.responses if response.is_high_quality()]
    
    def clear_old_responses(self, max_age: float) -> int:
        """Limpia respuestas antiguas y retorna el número eliminado"""
        current_time = datetime.now()
        initial_count = len(self.responses)
        
        self.responses = [
            response for response in self.responses
            if (current_time - response.created_at).total_seconds() <= max_age
        ]
        
        return initial_count - len(self.responses)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la cola"""
        return {
            'total_responses': len(self.responses),
            'pending_responses': len(self.get_pending_responses()),
            'completed_responses': len(self.get_completed_responses()),
            'failed_responses': len(self.get_failed_responses()),
            'high_quality_responses': len(self.get_high_quality_responses()),
            'processing': self.processing,
            'max_size': self.max_size,
        } 