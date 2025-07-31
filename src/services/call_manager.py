"""
Gestor de llamadas que coordina todos los servicios
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

from ..config.logging_config import get_logger, CallLogger
from ..models.call import Call, CallStatus, CallDirection
from ..models.audio import AudioChunk
from ..models.transcription import TranscriptionResult
from ..models.ai_response import AIResponse
from .sip_service import SIPService
from .audio_service import AudioService
from .stt_service import STTService
from .tts_service import TTSService
from .ai_service import AIService

logger = get_logger('call_manager')

class CallManager:
    """Gestor principal de llamadas que coordina todos los servicios"""
    
    def __init__(self):
        # Servicios
        self.sip_service = SIPService()
        self.audio_service = AudioService()
        self.stt_service = STTService()
        self.tts_service = TTSService()
        self.ai_service = AIService()
        
        # Estado
        self.is_initialized = False
        self.active_calls: Dict[str, Call] = {}
        self.call_handlers: Dict[str, asyncio.Task] = {}
        
        # Configuración
        self.auto_answer_incoming = True
        self.max_concurrent_calls = 5
        self.call_timeout = 300  # segundos
        
        # Callbacks
        self.on_call_started_callback: Optional[Callable] = None
        self.on_call_ended_callback: Optional[Callable] = None
        self.on_transcription_callback: Optional[Callable] = None
        self.on_ai_response_callback: Optional[Callable] = None
        
    async def initialize(self) -> bool:
        """Inicializa el gestor de llamadas"""
        try:
            logger.info("Inicializando gestor de llamadas...")
            
            # Inicializar servicios
            sip_ok = await self.sip_service.initialize()
            if not sip_ok:
                logger.error("Error inicializando servicio SIP")
                return False
            
            # Configurar callbacks SIP
            self.sip_service.set_call_connected_callback(self._on_call_connected)
            self.sip_service.set_call_ended_callback(self._on_call_ended)
            self.sip_service.set_incoming_call_callback(self._on_incoming_call)
            
            # Probar servicios
            await self._test_services()
            
            self.is_initialized = True
            logger.info("Gestor de llamadas inicializado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando gestor de llamadas: {e}")
            return False
    
    async def _test_services(self) -> None:
        """Prueba todos los servicios"""
        logger.info("Probando servicios...")
        
        # Probar STT
        stt_ok = self.stt_service.test_api_connection()
        logger.info(f"STT Service: {'✅' if stt_ok else '❌'}")
        
        # Probar TTS
        tts_ok = await self.tts_service.test_api_connection()
        logger.info(f"TTS Service: {'✅' if tts_ok else '❌'}")
        
        # Probar IA
        ai_ok = await self.ai_service.test_model_connection()
        logger.info(f"AI Service: {'✅' if ai_ok else '❌'}")
    
    async def make_outgoing_call(self, destination: str, call_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Realiza una llamada saliente"""
        try:
            if not self.is_initialized:
                logger.error("Gestor de llamadas no inicializado")
                return None
            
            # Crear objeto de llamada
            call = Call(
                direction=CallDirection.OUTBOUND,
                to_number=destination,
                sip_uri=destination,
                timeout=self.call_timeout,
                max_duration=self.call_timeout,
                metadata=call_data or {}
            )
            
            # Realizar llamada SIP
            sip_call_id = await self.sip_service.make_call(destination, call_data)
            
            if sip_call_id:
                call.sip_call_id = sip_call_id
                self.active_calls[sip_call_id] = call
                
                logger.info(f"Llamada saliente iniciada: {destination}")
                return sip_call_id
            else:
                logger.error(f"Error iniciando llamada a: {destination}")
                return None
                
        except Exception as e:
            logger.error(f"Error realizando llamada saliente: {e}")
            return None
    
    async def _on_call_connected(self, sip_call):
        """Callback cuando se conecta una llamada"""
        call_id = sip_call.getId()
        call_logger = CallLogger(call_id)
        
        call_logger.info("Llamada conectada, iniciando procesamiento")
        
        # Actualizar estado de la llamada
        if call_id in self.active_calls:
            call = self.active_calls[call_id]
            call.connect()
        
        # Iniciar handler de llamada
        handler_task = asyncio.create_task(self._handle_call_flow(call_id))
        self.call_handlers[call_id] = handler_task
        
        # Llamar callback
        if self.on_call_started_callback:
            await self.on_call_started_callback(call_id)
    
    async def _on_call_ended(self, sip_call):
        """Callback cuando termina una llamada"""
        call_id = sip_call.getId()
        call_logger = CallLogger(call_id)
        
        call_logger.info("Llamada terminada")
        
        # Actualizar estado de la llamada
        if call_id in self.active_calls:
            call = self.active_calls[call_id]
            call.end()
        
        # Cancelar handler de llamada
        if call_id in self.call_handlers:
            self.call_handlers[call_id].cancel()
            del self.call_handlers[call_id]
        
        # Remover de llamadas activas
        if call_id in self.active_calls:
            del self.active_calls[call_id]
        
        # Llamar callback
        if self.on_call_ended_callback:
            await self.on_call_ended_callback(call_id)
    
    async def _on_incoming_call(self, sip_call):
        """Callback para llamada entrante"""
        call_id = sip_call.getId()
        call_logger = CallLogger(call_id)
        
        call_logger.info("Llamada entrante recibida")
        
        # Crear objeto de llamada
        call = Call(
            direction=CallDirection.INBOUND,
            sip_call_id=call_id,
            timeout=self.call_timeout,
            max_duration=self.call_timeout
        )
        
        self.active_calls[call_id] = call
        
        # Responder automáticamente si está habilitado
        if self.auto_answer_incoming:
            await self.sip_service.answer_call(sip_call)
            call_logger.info("Llamada entrante respondida automáticamente")
    
    async def _handle_call_flow(self, call_id: str) -> None:
        """Maneja el flujo completo de una llamada: STT → IA → TTS"""
        call_logger = CallLogger(call_id)
        
        try:
            call_logger.info("Iniciando flujo de llamada")
            
            while call_id in self.active_calls:
                call = self.active_calls[call_id]
                
                # Verificar si la llamada sigue activa
                if not call.is_active():
                    call_logger.info("Llamada ya no está activa")
                    break
                
                # 1. Grabar audio del usuario
                call_logger.info("Grabando audio del usuario...")
                audio_chunk = await self.audio_service.record_audio(self.audio_service.chunk_duration)
                
                if not audio_chunk:
                    call_logger.warning("No se pudo grabar audio")
                    await asyncio.sleep(1)
                    continue
                
                call_logger.info(f"Audio grabado: {audio_chunk.duration:.2f}s")
                
                # 2. Transcribir audio (STT)
                call_logger.info("Transcribiendo audio...")
                transcription = await self.stt_service.transcribe_audio(audio_chunk, call_id)
                
                if not transcription or not transcription.text.strip():
                    call_logger.warning("No se pudo transcribir audio o está vacío")
                    await asyncio.sleep(1)
                    continue
                
                call.transcription_count += 1
                call_logger.info(f"Transcripción: {transcription.text}")
                
                # Llamar callback de transcripción
                if self.on_transcription_callback:
                    await self.on_transcription_callback(call_id, transcription)
                
                # 3. Procesar con IA
                call_logger.info("Procesando con IA...")
                ai_response = await self.ai_service.process_input(transcription.text, call_id)
                
                if not ai_response or not ai_response.text.strip():
                    call_logger.warning("No se pudo generar respuesta de IA")
                    await asyncio.sleep(1)
                    continue
                
                call.ai_response_count += 1
                call_logger.info(f"Respuesta IA: {ai_response.text}")
                
                # Llamar callback de respuesta de IA
                if self.on_ai_response_callback:
                    await self.on_ai_response_callback(call_id, ai_response)
                
                # 4. Generar audio (TTS)
                call_logger.info("Generando audio...")
                response_audio = await self.tts_service.generate_speech(ai_response.text, call_id)
                
                if not response_audio:
                    call_logger.warning("No se pudo generar audio de respuesta")
                    await asyncio.sleep(1)
                    continue
                
                call.tts_generation_count += 1
                call_logger.info(f"Audio generado: {response_audio.duration:.2f}s")
                
                # 5. Reproducir audio en la llamada
                call_logger.info("Reproduciendo audio en la llamada...")
                # Aquí implementarías la reproducción en la llamada SIP
                # Por ahora, simulamos el tiempo de reproducción
                await asyncio.sleep(response_audio.duration)
                
                call_logger.info("Ciclo de procesamiento completado")
                
        except asyncio.CancelledError:
            call_logger.info("Handler de llamada cancelado")
        except Exception as e:
            call_logger.error(f"Error en flujo de llamada: {e}")
    
    async def hangup_call(self, call_id: str, reason: Optional[str] = None) -> bool:
        """Cuelga una llamada"""
        try:
            # Cancelar handler si existe
            if call_id in self.call_handlers:
                self.call_handlers[call_id].cancel()
                del self.call_handlers[call_id]
            
            # Colgar llamada SIP
            success = await self.sip_service.hangup_call(call_id, reason)
            
            if success and call_id in self.active_calls:
                call = self.active_calls[call_id]
                call.end(reason)
                del self.active_calls[call_id]
            
            return success
            
        except Exception as e:
            logger.error(f"Error colgando llamada: {e}")
            return False
    
    def get_call_info(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de una llamada"""
        if call_id in self.active_calls:
            call = self.active_calls[call_id]
            return call.to_dict()
        return None
    
    def get_active_calls(self) -> List[Dict[str, Any]]:
        """Obtiene todas las llamadas activas"""
        return [call.to_dict() for call in self.active_calls.values()]
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del gestor"""
        return {
            'is_initialized': self.is_initialized,
            'active_calls': len(self.active_calls),
            'active_handlers': len(self.call_handlers),
            'max_concurrent_calls': self.max_concurrent_calls,
            'auto_answer_incoming': self.auto_answer_incoming,
            'call_timeout': self.call_timeout,
            'sip_service_stats': self.sip_service.get_service_status(),
            'audio_service_stats': self.audio_service.get_service_stats(),
            'stt_service_stats': self.stt_service.get_service_stats(),
            'tts_service_stats': self.tts_service.get_service_stats(),
            'ai_service_stats': self.ai_service.get_service_stats(),
        }
    
    # Configuración de callbacks
    def set_call_started_callback(self, callback: Callable) -> None:
        """Establece callback para llamadas iniciadas"""
        self.on_call_started_callback = callback
    
    def set_call_ended_callback(self, callback: Callable) -> None:
        """Establece callback para llamadas terminadas"""
        self.on_call_ended_callback = callback
    
    def set_transcription_callback(self, callback: Callable) -> None:
        """Establece callback para transcripciones"""
        self.on_transcription_callback = callback
    
    def set_ai_response_callback(self, callback: Callable) -> None:
        """Establece callback para respuestas de IA"""
        self.on_ai_response_callback = callback
    
    async def shutdown(self) -> None:
        """Cierra el gestor de llamadas"""
        try:
            logger.info("Cerrando gestor de llamadas...")
            
            # Cancelar todos los handlers
            for task in self.call_handlers.values():
                task.cancel()
            
            # Colgar todas las llamadas activas
            for call_id in list(self.active_calls.keys()):
                await self.hangup_call(call_id, "Shutdown")
            
            # Cerrar servicios
            await self.sip_service.shutdown()
            await self.audio_service.shutdown()
            await self.stt_service.shutdown()
            await self.tts_service.shutdown()
            await self.ai_service.shutdown()
            
            logger.info("Gestor de llamadas cerrado correctamente")
            
        except Exception as e:
            logger.error(f"Error cerrando gestor de llamadas: {e}") 