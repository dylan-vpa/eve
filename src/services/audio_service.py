"""
Servicio de audio para grabación, procesamiento y análisis de calidad
"""

import asyncio
import logging
import numpy as np
import pyaudio
import wave
import tempfile
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

from ..config.settings import AUDIO_CONFIG
from ..config.logging_config import get_logger, PerformanceLogger
from ..models.audio import AudioChunk, AudioBuffer, AudioQualityMetrics, AudioFormat, AudioQuality

logger = get_logger('audio')

class AudioService:
    """Servicio para manejo de audio"""
    
    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.audio_buffer = AudioBuffer()
        self.performance_logger = PerformanceLogger()
        
        # Configuración
        self.sample_rate = AUDIO_CONFIG['sample_rate']
        self.channels = AUDIO_CONFIG['channels']
        self.chunk_size = AUDIO_CONFIG['chunk_size']
        self.chunk_duration = AUDIO_CONFIG['chunk_duration']
        self.audio_format = pyaudio.paInt16
        
        # Estado
        self.is_recording = False
        self.recording_stream = None
        self.recording_callback: Optional[Callable] = None
        
        # Métricas
        self.total_chunks_processed = 0
        self.total_audio_duration = 0.0
        self.average_quality_score = 0.0
        
    async def start_recording(self, callback: Optional[Callable] = None) -> bool:
        """Inicia la grabación de audio"""
        try:
            if self.is_recording:
                logger.warning("Ya está grabando audio")
                return False
            
            self.recording_callback = callback
            self.is_recording = True
            
            # Crear stream de grabación
            self.recording_stream = self.pyaudio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.recording_stream.start_stream()
            logger.info("Grabación de audio iniciada")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando grabación: {e}")
            return False
    
    async def stop_recording(self) -> bool:
        """Detiene la grabación de audio"""
        try:
            if not self.is_recording:
                logger.warning("No está grabando audio")
                return False
            
            self.is_recording = False
            
            if self.recording_stream:
                self.recording_stream.stop_stream()
                self.recording_stream.close()
                self.recording_stream = None
            
            logger.info("Grabación de audio detenida")
            return True
            
        except Exception as e:
            logger.error(f"Error deteniendo grabación: {e}")
            return False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback para procesamiento de audio en tiempo real"""
        try:
            # Crear chunk de audio
            chunk = AudioChunk(
                data=in_data,
                format=AudioFormat.PCM_16BIT,
                sample_rate=self.sample_rate,
                channels=self.channels,
                timestamp=datetime.now(),
                duration=len(in_data) / (self.sample_rate * 2),  # 16-bit = 2 bytes
                size=len(in_data)
            )
            
            # Analizar calidad del audio
            self._analyze_audio_quality(chunk)
            
            # Agregar al buffer
            self.audio_buffer.add_chunk(chunk)
            
            # Actualizar métricas
            self.total_chunks_processed += 1
            self.total_audio_duration += chunk.duration
            
            # Llamar callback si existe
            if self.recording_callback:
                asyncio.create_task(self.recording_callback(chunk))
            
            return (None, pyaudio.paContinue)
            
        except Exception as e:
            logger.error(f"Error en callback de audio: {e}")
            return (None, pyaudio.paAbort)
    
    def _analyze_audio_quality(self, chunk: AudioChunk) -> None:
        """Analiza la calidad del audio"""
        try:
            # Convertir a numpy array
            audio_array = chunk.to_numpy()
            
            # Calcular métricas básicas
            rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
            peak = np.max(np.abs(audio_array))
            
            # Normalizar valores
            chunk.volume_level = min(rms / 32768.0, 1.0)
            
            # Calcular SNR (Signal-to-Noise Ratio) aproximado
            signal_power = np.mean(audio_array.astype(np.float32) ** 2)
            noise_floor = np.percentile(audio_array.astype(np.float32) ** 2, 10)
            snr = 10 * np.log10(signal_power / (noise_floor + 1e-10))
            
            # Calcular score de calidad (0-1)
            quality_score = min(max(snr / 30.0, 0.0), 1.0)
            chunk.quality_score = quality_score
            
            # Calcular nivel de ruido
            chunk.noise_level = 1.0 - quality_score
            
            # Log de métricas
            self.performance_logger.log_audio_quality(
                chunk_id=chunk.timestamp.isoformat(),
                quality_metrics={
                    'rms': rms,
                    'peak': peak,
                    'snr': snr,
                    'quality_score': quality_score,
                    'volume_level': chunk.volume_level,
                    'noise_level': chunk.noise_level,
                }
            )
            
        except Exception as e:
            logger.error(f"Error analizando calidad de audio: {e}")
    
    async def record_audio(self, duration: float) -> Optional[AudioChunk]:
        """Graba audio por una duración específica"""
        try:
            if self.is_recording:
                logger.warning("Ya está grabando audio")
                return None
            
            # Iniciar grabación
            await self.start_recording()
            
            # Esperar la duración especificada
            await asyncio.sleep(duration)
            
            # Detener grabación
            await self.stop_recording()
            
            # Obtener el último chunk del buffer
            chunks = self.audio_buffer.get_chunks(duration)
            if chunks:
                # Combinar chunks si hay múltiples
                combined_data = b''.join(chunk.data for chunk in chunks)
                total_duration = sum(chunk.duration for chunk in chunks)
                
                # Crear chunk combinado
                combined_chunk = AudioChunk(
                    data=combined_data,
                    format=AudioFormat.PCM_16BIT,
                    sample_rate=self.sample_rate,
                    channels=self.channels,
                    timestamp=datetime.now(),
                    duration=total_duration,
                    size=len(combined_data)
                )
                
                # Analizar calidad
                self._analyze_audio_quality(combined_chunk)
                
                return combined_chunk
            
            return None
            
        except Exception as e:
            logger.error(f"Error grabando audio: {e}")
            return None
    
    async def save_audio_to_file(self, chunk: AudioChunk, filename: str) -> bool:
        """Guarda audio en archivo WAV"""
        try:
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(chunk.data)
            
            logger.info(f"Audio guardado en: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando audio: {e}")
            return False
    
    async def load_audio_from_file(self, filename: str) -> Optional[AudioChunk]:
        """Carga audio desde archivo WAV"""
        try:
            with wave.open(filename, 'rb') as wav_file:
                # Leer datos
                frames = wav_file.readframes(wav_file.getnframes())
                
                # Crear chunk
                chunk = AudioChunk(
                    data=frames,
                    format=AudioFormat.PCM_16BIT,
                    sample_rate=wav_file.getframerate(),
                    channels=wav_file.getnchannels(),
                    timestamp=datetime.now(),
                    duration=wav_file.getnframes() / wav_file.getframerate(),
                    size=len(frames)
                )
                
                # Analizar calidad
                self._analyze_audio_quality(chunk)
                
                return chunk
                
        except Exception as e:
            logger.error(f"Error cargando audio: {e}")
            return None
    
    def get_audio_quality_metrics(self, chunk: AudioChunk) -> AudioQualityMetrics:
        """Obtiene métricas detalladas de calidad de audio"""
        try:
            audio_array = chunk.to_numpy()
            
            # Métricas básicas
            rms_amplitude = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
            peak_amplitude = np.max(np.abs(audio_array))
            dynamic_range = 20 * np.log10(peak_amplitude / (rms_amplitude + 1e-10))
            
            # SNR
            signal_power = np.mean(audio_array.astype(np.float32) ** 2)
            noise_floor = np.percentile(audio_array.astype(np.float32) ** 2, 10)
            signal_to_noise_ratio = 10 * np.log10(signal_power / (noise_floor + 1e-10))
            
            # THD aproximado
            fft = np.fft.fft(audio_array)
            fundamental = np.max(np.abs(fft[:len(fft)//2]))
            harmonics = np.sum(np.abs(fft[:len(fft)//2])) - fundamental
            total_harmonic_distortion = (harmonics / fundamental) * 100 if fundamental > 0 else 0
            
            # MOS score aproximado basado en SNR
            mos_score = min(5.0, 1.0 + (signal_to_noise_ratio / 10.0))
            
            return AudioQualityMetrics(
                signal_to_noise_ratio=signal_to_noise_ratio,
                total_harmonic_distortion=total_harmonic_distortion,
                peak_amplitude=peak_amplitude,
                rms_amplitude=rms_amplitude,
                dynamic_range=dynamic_range,
                mos_score=mos_score,
                pesq_score=mos_score,  # Aproximación
                polqa_score=mos_score,  # Aproximación
            )
            
        except Exception as e:
            logger.error(f"Error calculando métricas de calidad: {e}")
            return AudioQualityMetrics()
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del servicio"""
        buffer_stats = self.audio_buffer.get_buffer_stats()
        
        return {
            'is_recording': self.is_recording,
            'total_chunks_processed': self.total_chunks_processed,
            'total_audio_duration': self.total_audio_duration,
            'average_quality_score': self.average_quality_score,
            'buffer_stats': buffer_stats,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'chunk_size': self.chunk_size,
            'chunk_duration': self.chunk_duration,
        }
    
    def get_available_devices(self) -> List[Dict[str, Any]]:
        """Obtiene dispositivos de audio disponibles"""
        devices = []
        
        try:
            for i in range(self.pyaudio.get_device_count()):
                device_info = self.pyaudio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:  # Solo dispositivos de entrada
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'max_input_channels': device_info['maxInputChannels'],
                        'default_sample_rate': device_info['defaultSampleRate'],
                    })
        except Exception as e:
            logger.error(f"Error obteniendo dispositivos: {e}")
        
        return devices
    
    async def shutdown(self) -> None:
        """Cierra el servicio de audio"""
        try:
            if self.is_recording:
                await self.stop_recording()
            
            if self.pyaudio:
                self.pyaudio.terminate()
            
            logger.info("Servicio de audio cerrado correctamente")
            
        except Exception as e:
            logger.error(f"Error cerrando servicio de audio: {e}") 