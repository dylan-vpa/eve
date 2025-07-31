"""
Servicio STT (Speech-to-Text) usando Deepgram
"""

import asyncio
import logging
import aiohttp
import tempfile
import wave
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

from ..config.settings import DEEPGRAM_CONFIG
from ..config.logging_config import get_logger, PerformanceLogger
from ..models.audio import AudioChunk
from ..models.transcription import TranscriptionResult, TranscriptionQueue, TranscriptionStatus

logger = get_logger('stt')

class STTService:
    """Servicio para transcripción de audio usando Deepgram"""
    
    def __init__(self):
        self.api_key = DEEPGRAM_CONFIG['api_key']
        self.base_url = DEEPGRAM_CONFIG['url']
        self.performance_logger = PerformanceLogger()
        self.transcription_queue = TranscriptionQueue()
        
        # Configuración
        self.language = DEEPGRAM_CONFIG['language']
        self.model = DEEPGRAM_CONFIG['model']
        self.punctuate = DEEPGRAM_CONFIG['punctuate']
        self.diarize = DEEPGRAM_CONFIG['diarize']
        self.utterances = DEEPGRAM_CONFIG['utterances']
        self.interim_results = DEEPGRAM_CONFIG['interim_results']
        self.endpointing = DEEPGRAM_CONFIG['endpointing']
        self.vad_turnoff = DEEPGRAM_CONFIG['vad_turnoff']
        
        # Estado
        self.is_processing = False
        self.total_transcriptions = 0
        self.successful_transcriptions = 0
        self.failed_transcriptions = 0
        
        # Métricas
        self.average_processing_time = 0.0
        self.average_confidence = 0.0
        
    async def transcribe_audio(self, audio_chunk: AudioChunk, call_id: Optional[str] = None) -> Optional[TranscriptionResult]:
        """Transcribe un chunk de audio"""
        try:
            start_time = datetime.now()
            
            # Crear resultado de transcripción
            result = TranscriptionResult(
                call_id=call_id,
                audio_chunk_id=str(audio_chunk.timestamp),
                language=self.language,
                model=self.model,
                punctuate=self.punctuate,
                diarize=self.diarize,
                utterances=self.utterances,
                status=TranscriptionStatus.PROCESSING
            )
            
            # Guardar audio temporalmente
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(audio_chunk.channels)
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(audio_chunk.sample_rate)
                    wav_file.writeframes(audio_chunk.data)
                
                # Enviar a Deepgram
                success = await self._send_to_deepgram(temp_file.name, result)
                
                if success:
                    # Calcular tiempo de procesamiento
                    processing_time = (datetime.now() - start_time).total_seconds()
                    result.complete(processing_time)
                    
                    # Actualizar métricas
                    self._update_metrics(result)
                    
                    logger.info(f"Transcripción completada: {result.text[:50]}...")
                    return result
                else:
                    result.fail("API_ERROR", "Error en API de Deepgram")
                    logger.error("Transcripción fallida")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en transcripción: {e}")
            return None
    
    async def _send_to_deepgram(self, audio_file_path: str, result: TranscriptionResult) -> bool:
        """Envía audio a Deepgram API"""
        try:
            headers = {
                'Authorization': f'Token {self.api_key}',
                'Content-Type': 'audio/wav'
            }
            
            # Parámetros de la API
            params = {
                'model': self.model,
                'language': self.language,
                'punctuate': str(self.punctuate).lower(),
                'diarize': str(self.diarize).lower(),
                'utterances': str(self.utterances).lower(),
                'interim_results': str(self.interim_results).lower(),
                'endpointing': str(self.endpointing),
                'vad_turnoff': str(self.vad_turnoff),
            }
            
            async with aiohttp.ClientSession() as session:
                with open(audio_file_path, 'rb') as audio_file:
                    start_time = datetime.now()
                    
                    async with session.post(
                        self.base_url,
                        headers=headers,
                        params=params,
                        data=audio_file,
                        timeout=aiohttp.ClientTimeout(total=DEEPGRAM_CONFIG['timeout'])
                    ) as response:
                        
                        # Calcular latencia
                        latency = (datetime.now() - start_time).total_seconds() * 1000
                        self.performance_logger.log_api_latency('deepgram', latency)
                        
                        if response.status == 200:
                            api_result = await response.json()
                            return self._parse_deepgram_response(api_result, result)
                        else:
                            error_text = await response.text()
                            logger.error(f"Error en Deepgram API: {response.status} - {error_text}")
                            return False
                            
        except asyncio.TimeoutError:
            logger.error("Timeout en API de Deepgram")
            return False
        except Exception as e:
            logger.error(f"Error enviando a Deepgram: {e}")
            return False
    
    def _parse_deepgram_response(self, api_result: Dict[str, Any], result: TranscriptionResult) -> bool:
        """Parsea la respuesta de Deepgram"""
        try:
            if 'results' not in api_result or not api_result['results']:
                logger.warning("Respuesta vacía de Deepgram")
                return False
            
            # Obtener el primer canal
            channel = api_result['results']['channels'][0]
            alternatives = channel.get('alternatives', [])
            
            if not alternatives:
                logger.warning("No hay alternativas en la respuesta")
                return False
            
            # Obtener la mejor alternativa
            best_alternative = alternatives[0]
            
            # Extraer texto
            result.text = best_alternative.get('transcript', '')
            result.confidence = best_alternative.get('confidence', 0.0)
            
            # Extraer palabras si están disponibles
            if 'words' in best_alternative:
                for word_data in best_alternative['words']:
                    from ..models.transcription import TranscriptionWord
                    word = TranscriptionWord(
                        word=word_data['word'],
                        start_time=word_data.get('start', 0.0),
                        end_time=word_data.get('end', 0.0),
                        confidence=word_data.get('confidence', 0.0),
                        speaker=word_data.get('speaker', None)
                    )
                    result.segments.append(word)
            
            # Extraer segmentos si están disponibles
            if 'paragraphs' in best_alternative:
                for paragraph in best_alternative['paragraphs']:
                    from ..models.transcription import TranscriptionSegment
                    segment = TranscriptionSegment(
                        text=paragraph.get('sentences', [{}])[0].get('text', ''),
                        start_time=paragraph.get('start', 0.0),
                        end_time=paragraph.get('end', 0.0),
                        confidence=paragraph.get('confidence', 0.0),
                        speaker=paragraph.get('speaker', None)
                    )
                    result.segments.append(segment)
            
            # Actualizar contadores
            result.word_count = len(result.text.split())
            result.character_count = len(result.text)
            
            return True
            
        except Exception as e:
            logger.error(f"Error parseando respuesta de Deepgram: {e}")
            return False
    
    def _update_metrics(self, result: TranscriptionResult) -> None:
        """Actualiza métricas del servicio"""
        self.total_transcriptions += 1
        
        if result.status == TranscriptionStatus.COMPLETED:
            self.successful_transcriptions += 1
            
            # Actualizar promedio de confianza
            if self.successful_transcriptions == 1:
                self.average_confidence = result.confidence
            else:
                self.average_confidence = (
                    (self.average_confidence * (self.successful_transcriptions - 1) + result.confidence) /
                    self.successful_transcriptions
                )
            
            # Actualizar promedio de tiempo de procesamiento
            if result.get_processing_time():
                if self.successful_transcriptions == 1:
                    self.average_processing_time = result.get_processing_time()
                else:
                    self.average_processing_time = (
                        (self.average_processing_time * (self.successful_transcriptions - 1) + result.get_processing_time()) /
                        self.successful_transcriptions
                    )
        else:
            self.failed_transcriptions += 1
    
    async def transcribe_file(self, file_path: str, call_id: Optional[str] = None) -> Optional[TranscriptionResult]:
        """Transcribe un archivo de audio"""
        try:
            # Cargar audio desde archivo
            from ..services.audio_service import AudioService
            audio_service = AudioService()
            audio_chunk = await audio_service.load_audio_from_file(file_path)
            
            if audio_chunk:
                return await self.transcribe_audio(audio_chunk, call_id)
            else:
                logger.error(f"No se pudo cargar el archivo: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error transcribiendo archivo: {e}")
            return None
    
    async def batch_transcribe(self, audio_chunks: List[AudioChunk], call_id: Optional[str] = None) -> List[TranscriptionResult]:
        """Transcribe múltiples chunks de audio"""
        results = []
        
        for chunk in audio_chunks:
            result = await self.transcribe_audio(chunk, call_id)
            if result:
                results.append(result)
        
        return results
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del servicio"""
        queue_stats = self.transcription_queue.get_queue_stats()
        
        return {
            'total_transcriptions': self.total_transcriptions,
            'successful_transcriptions': self.successful_transcriptions,
            'failed_transcriptions': self.failed_transcriptions,
            'success_rate': self.successful_transcriptions / max(self.total_transcriptions, 1),
            'average_confidence': self.average_confidence,
            'average_processing_time': self.average_processing_time,
            'queue_stats': queue_stats,
            'model': self.model,
            'language': self.language,
            'punctuate': self.punctuate,
            'diarize': self.diarize,
            'utterances': self.utterances,
        }
    
    def test_api_connection(self) -> bool:
        """Prueba la conexión con la API de Deepgram"""
        try:
            # Crear un archivo de audio de prueba (silencioso)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(16000)
                    # 1 segundo de silencio
                    wav_file.writeframes(b'\x00\x00' * 16000)
                
                # Intentar transcribir
                async def test():
                    result = await self.transcribe_audio(
                        AudioChunk(
                            data=b'\x00\x00' * 16000,
                            sample_rate=16000,
                            channels=1,
                            duration=1.0
                        )
                    )
                    return result is not None
                
                return asyncio.run(test())
                
        except Exception as e:
            logger.error(f"Error probando conexión con Deepgram: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Cierra el servicio STT"""
        try:
            # Limpiar cola de transcripciones
            self.transcription_queue.clear_old_results(0)
            
            logger.info("Servicio STT cerrado correctamente")
            
        except Exception as e:
            logger.error(f"Error cerrando servicio STT: {e}") 