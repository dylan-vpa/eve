"""
Modelos para manejo de audio
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List, Union
import numpy as np

class AudioFormat(Enum):
    """Formatos de audio soportados"""
    PCM_16BIT = "pcm_s16le"
    PCM_8BIT = "pcm_s8"
    G711_ULAW = "PCMU"
    G711_ALAW = "PCMA"
    OPUS = "opus"
    MP3 = "mp3"
    WAV = "wav"

class AudioQuality(Enum):
    """Niveles de calidad de audio"""
    EXCELLENT = "excellent"  # MOS 4.5-5.0
    GOOD = "good"           # MOS 4.0-4.5
    FAIR = "fair"           # MOS 3.0-4.0
    POOR = "poor"           # MOS 2.0-3.0
    BAD = "bad"             # MOS 1.0-2.0

@dataclass
class AudioChunk:
    """Chunk de audio"""
    
    # Datos
    data: bytes
    format: AudioFormat = AudioFormat.PCM_16BIT
    sample_rate: int = 16000
    channels: int = 1
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0  # segundos
    size: int = 0  # bytes
    
    # Calidad
    quality_score: float = 0.0  # 0-1
    noise_level: float = 0.0  # 0-1
    volume_level: float = 0.0  # 0-1
    
    # Procesamiento
    processed: bool = False
    transcription_id: Optional[str] = None
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if self.size == 0:
            self.size = len(self.data)
        
        if self.duration == 0.0:
            # Calcular duración basada en el tamaño
            bytes_per_sample = 2 if self.format == AudioFormat.PCM_16BIT else 1
            total_samples = self.size // (bytes_per_sample * self.channels)
            self.duration = total_samples / self.sample_rate
    
    def get_quality_level(self) -> AudioQuality:
        """Obtiene el nivel de calidad basado en el score"""
        if self.quality_score >= 0.9:
            return AudioQuality.EXCELLENT
        elif self.quality_score >= 0.8:
            return AudioQuality.GOOD
        elif self.quality_score >= 0.6:
            return AudioQuality.FAIR
        elif self.quality_score >= 0.4:
            return AudioQuality.POOR
        else:
            return AudioQuality.BAD
    
    def to_numpy(self) -> np.ndarray:
        """Convierte a numpy array"""
        if self.format == AudioFormat.PCM_16BIT:
            return np.frombuffer(self.data, dtype=np.int16)
        elif self.format == AudioFormat.PCM_8BIT:
            return np.frombuffer(self.data, dtype=np.int8)
        else:
            raise ValueError(f"Formato no soportado para conversión a numpy: {self.format}")
    
    def normalize_volume(self, target_level: float = 0.7) -> 'AudioChunk':
        """Normaliza el volumen del audio"""
        if self.volume_level == 0:
            return self
        
        # Calcular factor de normalización
        factor = target_level / self.volume_level
        
        # Aplicar normalización
        audio_array = self.to_numpy()
        normalized_array = np.clip(audio_array * factor, -32768, 32767).astype(np.int16)
        
        # Crear nuevo chunk
        return AudioChunk(
            data=normalized_array.tobytes(),
            format=self.format,
            sample_rate=self.sample_rate,
            channels=self.channels,
            timestamp=self.timestamp,
            duration=self.duration,
            size=len(normalized_array.tobytes()),
            quality_score=self.quality_score,
            noise_level=self.noise_level,
            volume_level=target_level,
            processed=True,
            transcription_id=self.transcription_id
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'format': self.format.value,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration,
            'size': self.size,
            'quality_score': self.quality_score,
            'noise_level': self.noise_level,
            'volume_level': self.volume_level,
            'processed': self.processed,
            'transcription_id': self.transcription_id,
            'quality_level': self.get_quality_level().value,
        }

@dataclass
class AudioBuffer:
    """Buffer de audio para procesamiento en tiempo real"""
    
    chunks: List[AudioChunk] = field(default_factory=list)
    max_size: int = 100  # número máximo de chunks
    max_duration: float = 60.0  # segundos
    
    def add_chunk(self, chunk: AudioChunk) -> bool:
        """Agrega un chunk al buffer"""
        if len(self.chunks) >= self.max_size:
            return False
        
        # Verificar duración total
        total_duration = sum(c.duration for c in self.chunks) + chunk.duration
        if total_duration > self.max_duration:
            return False
        
        self.chunks.append(chunk)
        return True
    
    def get_chunks(self, duration: float) -> List[AudioChunk]:
        """Obtiene chunks que sumen la duración especificada"""
        result = []
        current_duration = 0.0
        
        for chunk in self.chunks:
            if current_duration + chunk.duration <= duration:
                result.append(chunk)
                current_duration += chunk.duration
            else:
                break
        
        return result
    
    def clear_old_chunks(self, max_age: float) -> int:
        """Limpia chunks antiguos y retorna el número eliminado"""
        current_time = datetime.now()
        initial_count = len(self.chunks)
        
        self.chunks = [
            chunk for chunk in self.chunks
            if (current_time - chunk.timestamp).total_seconds() <= max_age
        ]
        
        return initial_count - len(self.chunks)
    
    def get_buffer_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del buffer"""
        if not self.chunks:
            return {
                'total_chunks': 0,
                'total_duration': 0.0,
                'total_size': 0,
                'average_quality': 0.0,
                'average_volume': 0.0,
            }
        
        total_duration = sum(c.duration for c in self.chunks)
        total_size = sum(c.size for c in self.chunks)
        avg_quality = sum(c.quality_score for c in self.chunks) / len(self.chunks)
        avg_volume = sum(c.volume_level for c in self.chunks) / len(self.chunks)
        
        return {
            'total_chunks': len(self.chunks),
            'total_duration': total_duration,
            'total_size': total_size,
            'average_quality': avg_quality,
            'average_volume': avg_volume,
        }

@dataclass
class AudioQualityMetrics:
    """Métricas de calidad de audio"""
    
    # Métricas básicas
    signal_to_noise_ratio: float = 0.0  # dB
    total_harmonic_distortion: float = 0.0  # %
    frequency_response: Dict[str, float] = field(default_factory=dict)
    
    # Métricas de red
    packet_loss: float = 0.0  # %
    jitter: float = 0.0  # ms
    latency: float = 0.0  # ms
    
    # Métricas perceptuales
    mos_score: float = 0.0  # Mean Opinion Score 1-5
    pesq_score: float = 0.0  # PESQ score
    polqa_score: float = 0.0  # POLQA score
    
    # Métricas de volumen
    peak_amplitude: float = 0.0  # dB
    rms_amplitude: float = 0.0  # dB
    dynamic_range: float = 0.0  # dB
    
    def get_overall_quality(self) -> AudioQuality:
        """Calcula la calidad general basada en todas las métricas"""
        # Ponderación de métricas
        mos_weight = 0.4
        snr_weight = 0.2
        packet_loss_weight = 0.2
        jitter_weight = 0.1
        thd_weight = 0.1
        
        # Normalizar métricas
        mos_normalized = min(self.mos_score / 5.0, 1.0)
        snr_normalized = min(self.signal_to_noise_ratio / 30.0, 1.0)
        packet_loss_normalized = max(1.0 - self.packet_loss / 100.0, 0.0)
        jitter_normalized = max(1.0 - self.jitter / 100.0, 0.0)
        thd_normalized = max(1.0 - self.total_harmonic_distortion / 10.0, 0.0)
        
        # Calcular score ponderado
        overall_score = (
            mos_normalized * mos_weight +
            snr_normalized * snr_weight +
            packet_loss_normalized * packet_loss_weight +
            jitter_normalized * jitter_weight +
            thd_normalized * thd_weight
        )
        
        # Mapear a nivel de calidad
        if overall_score >= 0.9:
            return AudioQuality.EXCELLENT
        elif overall_score >= 0.8:
            return AudioQuality.GOOD
        elif overall_score >= 0.6:
            return AudioQuality.FAIR
        elif overall_score >= 0.4:
            return AudioQuality.POOR
        else:
            return AudioQuality.BAD
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'signal_to_noise_ratio': self.signal_to_noise_ratio,
            'total_harmonic_distortion': self.total_harmonic_distortion,
            'frequency_response': self.frequency_response,
            'packet_loss': self.packet_loss,
            'jitter': self.jitter,
            'latency': self.latency,
            'mos_score': self.mos_score,
            'pesq_score': self.pesq_score,
            'polqa_score': self.polqa_score,
            'peak_amplitude': self.peak_amplitude,
            'rms_amplitude': self.rms_amplitude,
            'dynamic_range': self.dynamic_range,
            'overall_quality': self.get_overall_quality().value,
        } 