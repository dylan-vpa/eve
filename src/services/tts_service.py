"""
Servicio TTS (Text-to-Speech) usando ElevenLabs
"""

import asyncio
import logging
import aiohttp
import tempfile
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

from ..config.settings import ELEVENLABS_CONFIG
from ..config.logging_config import get_logger, PerformanceLogger
from ..models.audio import AudioChunk, AudioFormat

logger = get_logger('tts')

class TTSService:
    """Servicio para generación de audio usando ElevenLabs"""
    
    def __init__(self):
        self.api_key = ELEVENLABS_CONFIG['api_key']
        self.voice_id = ELEVENLABS_CONFIG['voice_id']
        self.base_url = ELEVENLABS_CONFIG['url']
        self.performance_logger = PerformanceLogger()
        
        # Configuración
        self.model_id = ELEVENLABS_CONFIG['model_id']
        self.voice_settings = ELEVENLABS_CONFIG['voice_settings']
        self.optimization_level = ELEVENLABS_CONFIG['optimization_level']
        
        # Estado
        self.is_processing = False
        self.total_generations = 0
        self.successful_generations = 0
        self.failed_generations = 0
        
        # Métricas
        self.average_processing_time = 0.0
        self.average_audio_duration = 0.0
        
    async def generate_speech(self, text: str, call_id: Optional[str] = None) -> Optional[AudioChunk]:
        """Genera audio a partir de texto"""
        try:
            if not text.strip():
                logger.warning("Texto vacío para TTS")
                return None
            
            start_time = datetime.now()
            
            # Generar audio usando ElevenLabs
            audio_data = await self._generate_with_elevenlabs(text)
            
            if audio_data:
                # Convertir MP3 a WAV PCM
                wav_data = await self._convert_mp3_to_wav(audio_data)
                
                if wav_data:
                    # Crear chunk de audio
                    chunk = AudioChunk(
                        data=wav_data,
                        format=AudioFormat.PCM_16BIT,
                        sample_rate=16000,
                        channels=1,
                        timestamp=datetime.now(),
                        duration=len(wav_data) / (16000 * 2),  # 16-bit = 2 bytes
                        size=len(wav_data)
                    )
                    
                    # Calcular tiempo de procesamiento
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    # Actualizar métricas
                    self._update_metrics(processing_time, chunk.duration)
                    
                    logger.info(f"Audio generado: {len(text)} caracteres -> {chunk.duration:.2f}s")
                    return chunk
                else:
                    logger.error("Error convirtiendo MP3 a WAV")
                    return None
            else:
                logger.error("Error generando audio con ElevenLabs")
                return None
                
        except Exception as e:
            logger.error(f"Error generando speech: {e}")
            return None
    
    async def _generate_with_elevenlabs(self, text: str) -> Optional[bytes]:
        """Genera audio usando ElevenLabs API"""
        try:
            url = f"{self.base_url}/{self.voice_id}"
            
            headers = {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': self.api_key
            }
            
            data = {
                'text': text,
                'model_id': self.model_id,
                'voice_settings': self.voice_settings,
                'optimization_level': self.optimization_level
            }
            
            async with aiohttp.ClientSession() as session:
                start_time = datetime.now()
                
                async with session.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=ELEVENLABS_CONFIG['timeout'])
                ) as response:
                    
                    # Calcular latencia
                    latency = (datetime.now() - start_time).total_seconds() * 1000
                    self.performance_logger.log_api_latency('elevenlabs', latency)
                    
                    if response.status == 200:
                        audio_data = await response.read()
                        logger.info(f"Audio generado: {len(audio_data)} bytes")
                        return audio_data
                    else:
                        error_text = await response.text()
                        logger.error(f"Error en ElevenLabs API: {response.status} - {error_text}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("Timeout en API de ElevenLabs")
            return None
        except Exception as e:
            logger.error(f"Error enviando a ElevenLabs: {e}")
            return None
    
    async def _convert_mp3_to_wav(self, mp3_data: bytes) -> Optional[bytes]:
        """Convierte MP3 a WAV PCM 16-bit, 16kHz"""
        try:
            from pydub import AudioSegment
            import io
            
            # Cargar MP3 desde bytes
            audio = AudioSegment.from_mp3(io.BytesIO(mp3_data))
            
            # Convertir a formato requerido
            audio = audio.set_frame_rate(16000).set_channels(1)
            
            # Exportar como WAV
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                audio.export(temp_wav.name, format='wav')
                
                # Leer datos WAV
                with open(temp_wav.name, 'rb') as wav_file:
                    wav_data = wav_file.read()
                
                return wav_data
                
        except Exception as e:
            logger.error(f"Error convirtiendo MP3 a WAV: {e}")
            return None
    
    def _update_metrics(self, processing_time: float, audio_duration: float) -> None:
        """Actualiza métricas del servicio"""
        self.total_generations += 1
        self.successful_generations += 1
        
        # Actualizar promedio de tiempo de procesamiento
        if self.successful_generations == 1:
            self.average_processing_time = processing_time
            self.average_audio_duration = audio_duration
        else:
            self.average_processing_time = (
                (self.average_processing_time * (self.successful_generations - 1) + processing_time) /
                self.successful_generations
            )
            self.average_audio_duration = (
                (self.average_audio_duration * (self.successful_generations - 1) + audio_duration) /
                self.successful_generations
            )
    
    async def batch_generate_speech(self, texts: List[str], call_id: Optional[str] = None) -> List[AudioChunk]:
        """Genera audio para múltiples textos"""
        chunks = []
        
        for text in texts:
            chunk = await self.generate_speech(text, call_id)
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    async def generate_speech_with_voice_settings(self, text: str, voice_settings: Dict[str, Any]) -> Optional[AudioChunk]:
        """Genera audio con configuraciones de voz específicas"""
        try:
            # Guardar configuración original
            original_settings = self.voice_settings.copy()
            
            # Aplicar configuración temporal
            self.voice_settings.update(voice_settings)
            
            # Generar audio
            chunk = await self.generate_speech(text)
            
            # Restaurar configuración original
            self.voice_settings = original_settings
            
            return chunk
            
        except Exception as e:
            logger.error(f"Error generando speech con configuración personalizada: {e}")
            return None
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Obtiene voces disponibles de ElevenLabs"""
        try:
            url = "https://api.elevenlabs.io/v1/voices"
            
            headers = {
                'xi-api-key': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        voices_data = await response.json()
                        return voices_data.get('voices', [])
                    else:
                        logger.error(f"Error obteniendo voces: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error obteniendo voces: {e}")
            return []
    
    async def get_voice_info(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de una voz específica"""
        try:
            url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
            
            headers = {
                'xi-api-key': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Error obteniendo información de voz: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error obteniendo información de voz: {e}")
            return None
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del servicio"""
        return {
            'total_generations': self.total_generations,
            'successful_generations': self.successful_generations,
            'failed_generations': self.failed_generations,
            'success_rate': self.successful_generations / max(self.total_generations, 1),
            'average_processing_time': self.average_processing_time,
            'average_audio_duration': self.average_audio_duration,
            'voice_id': self.voice_id,
            'model_id': self.model_id,
            'voice_settings': self.voice_settings,
            'optimization_level': self.optimization_level,
        }
    
    async def test_api_connection(self) -> bool:
        """Prueba la conexión con la API de ElevenLabs"""
        try:
            # Intentar obtener información de la voz actual
            voice_info = await self.get_voice_info(self.voice_id)
            
            if voice_info:
                logger.info(f"API de ElevenLabs conectada. Voz: {voice_info.get('name', 'Unknown')}")
                return True
            else:
                logger.error("No se pudo obtener información de la voz")
                return False
                
        except Exception as e:
            logger.error(f"Error probando conexión con ElevenLabs: {e}")
            return False
    
    async def generate_test_audio(self) -> Optional[AudioChunk]:
        """Genera audio de prueba"""
        test_text = "Hola, esta es una prueba del sistema de llamadas SIP con IA."
        return await self.generate_speech(test_text)
    
    async def shutdown(self) -> None:
        """Cierra el servicio TTS"""
        try:
            logger.info("Servicio TTS cerrado correctamente")
            
        except Exception as e:
            logger.error(f"Error cerrando servicio TTS: {e}") 