"""
Servicio de IA para procesamiento de entrada y generación de respuestas
"""

import asyncio
import logging
import random
import aiohttp
import json
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

from ..config.settings import AI_CONFIG, PLACEHOLDER_RESPONSES
from ..config.logging_config import get_logger, PerformanceLogger
from ..models.ai_response import AIResponse, AIResponseContext, AIResponseType, AIResponseStatus

logger = get_logger('ai')

class AIService:
    """Servicio para procesamiento de IA"""
    
    def __init__(self):
        self.performance_logger = PerformanceLogger()
        
        # Configuración
        self.model_type = AI_CONFIG['model_type']
        self.model_name = AI_CONFIG['model_name']
        self.ollama_url = AI_CONFIG['ollama_url']
        self.max_response_length = AI_CONFIG['max_response_length']
        self.response_delay = AI_CONFIG['response_delay']
        self.context_window = AI_CONFIG['context_window']
        self.temperature = AI_CONFIG['temperature']
        self.top_p = AI_CONFIG['top_p']
        
        # Estado
        self.is_processing = False
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Métricas
        self.average_processing_time = 0.0
        self.average_confidence = 0.0
        self.average_relevance = 0.0
        
        # Historial de conversaciones
        self.conversation_histories: Dict[str, List[str]] = {}
        
    async def process_input(self, text: str, call_id: str, context: Optional[Dict[str, Any]] = None) -> Optional[AIResponse]:
        """Procesa entrada del usuario y genera respuesta"""
        try:
            if not text.strip():
                logger.warning("Texto vacío para procesamiento de IA")
                return None
            
            start_time = datetime.now()
            
            # Crear contexto de respuesta
            ai_context = AIResponseContext(
                call_id=call_id,
                user_input=text,
                conversation_history=self.conversation_histories.get(call_id, []),
                max_length=self.max_response_length,
                temperature=self.temperature,
                top_p=self.top_p
            )
            
            # Agregar entrada actual al historial
            ai_context.add_to_history(text)
            
            # Crear respuesta de IA
            response = AIResponse(
                call_id=call_id,
                text="",
                response_type=AIResponseType.ANSWER,
                context=ai_context,
                status=AIResponseStatus.PROCESSING,
                model=self.model_type,
                temperature=self.temperature,
                max_length=self.max_response_length
            )
            
            # Procesar según el tipo de modelo
            if self.model_type == 'placeholder':
                success = await self._process_with_placeholder(response)
            elif self.model_type == 'ollama':
                success = await self._process_with_ollama(response)
            elif self.model_type == 'llama':
                success = await self._process_with_llama(response)
            elif self.model_type == 'grok':
                success = await self._process_with_grok(response)
            else:
                success = await self._process_with_custom_model(response)
            
            if success:
                # Calcular tiempo de procesamiento
                processing_time = (datetime.now() - start_time).total_seconds()
                response.complete(processing_time)
                
                # Actualizar métricas
                self._update_metrics(response)
                
                # Actualizar historial de conversación
                self.conversation_histories[call_id] = ai_context.conversation_history
                
                logger.info(f"Respuesta de IA generada: {response.text[:50]}...")
                return response
            else:
                response.fail("PROCESSING_ERROR", "Error procesando entrada")
                logger.error("Error procesando entrada de IA")
                return None
                
        except Exception as e:
            logger.error(f"Error procesando entrada de IA: {e}")
            return None
    
    async def _process_with_placeholder(self, response: AIResponse) -> bool:
        """Procesa con modelo placeholder (para pruebas)"""
        try:
            # Simular tiempo de procesamiento
            await asyncio.sleep(self.response_delay)
            
            # Seleccionar respuesta aleatoria
            selected_response = random.choice(PLACEHOLDER_RESPONSES)
            
            # Ajustar longitud si es necesario
            if len(selected_response) > self.max_response_length:
                selected_response = selected_response[:self.max_response_length-3] + "..."
            
            # Asignar respuesta
            response.text = selected_response
            response.confidence = 0.8
            response.relevance_score = 0.7
            
            # Determinar tipo de respuesta
            if "hola" in response.context.user_input.lower():
                response.response_type = AIResponseType.GREETING
            elif "?" in response.context.user_input:
                response.response_type = AIResponseType.ANSWER
            elif "gracias" in response.context.user_input.lower():
                response.response_type = AIResponseType.CONFIRMATION
            else:
                response.response_type = AIResponseType.ANSWER
            
            return True
            
        except Exception as e:
            logger.error(f"Error en procesamiento placeholder: {e}")
            return False
    
    async def _process_with_ollama(self, response: AIResponse) -> bool:
        """Procesa con modelo Ollama"""
        try:
            # Construir prompt con contexto
            context = response.context
            conversation_history = context.conversation_history[-5:]  # Últimos 5 mensajes
            prompt = self._build_prompt(context.user_input, conversation_history)
            
            # Llamar a Ollama API
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "num_predict": self.max_response_length
                    }
                }
                
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        response.text = result.get('response', '').strip()
                        response.status = AIResponseStatus.COMPLETED
                        response.confidence = 0.9  # Ollama no proporciona confianza
                        response.relevance_score = 0.85
                        
                        logger.info(f"Respuesta de Ollama generada: {response.text[:50]}...")
                        return True
                    else:
                        logger.error(f"Error en API de Ollama: {resp.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error en procesamiento Ollama: {e}")
            return False
    
    def _build_prompt(self, user_input: str, conversation_history: List[str]) -> str:
        """Construye el prompt para Ollama"""
        prompt = "Eres un asistente de voz amigable y útil. Responde de manera natural y conversacional.\n\n"
        
        # Agregar historial de conversación
        if conversation_history:
            prompt += "Historial de la conversación:\n"
            for i, msg in enumerate(conversation_history, 1):
                prompt += f"{i}. {msg}\n"
            prompt += "\n"
        
        prompt += f"Usuario: {user_input}\n"
        prompt += "Asistente:"
        
        return prompt
    
    async def _process_with_llama(self, response: AIResponse) -> bool:
        """Procesa con modelo LLaMA"""
        try:
            # Aquí implementarías la integración con LLaMA
            # Por ahora, usar placeholder
            logger.info("Procesando con LLaMA (no implementado)")
            return await self._process_with_placeholder(response)
            
        except Exception as e:
            logger.error(f"Error en procesamiento LLaMA: {e}")
            return False
    
    async def _process_with_grok(self, response: AIResponse) -> bool:
        """Procesa con modelo Grok"""
        try:
            # Aquí implementarías la integración con Grok
            # Por ahora, usar placeholder
            logger.info("Procesando con Grok (no implementado)")
            return await self._process_with_placeholder(response)
            
        except Exception as e:
            logger.error(f"Error en procesamiento Grok: {e}")
            return False
    
    async def _process_with_custom_model(self, response: AIResponse) -> bool:
        """Procesa con modelo personalizado"""
        try:
            # Aquí implementarías tu modelo personalizado
            # Por ahora, usar placeholder
            logger.info("Procesando con modelo personalizado (no implementado)")
            return await self._process_with_placeholder(response)
            
        except Exception as e:
            logger.error(f"Error en procesamiento modelo personalizado: {e}")
            return False
    
    def _update_metrics(self, response: AIResponse) -> None:
        """Actualiza métricas del servicio"""
        self.total_requests += 1
        
        if response.status == AIResponseStatus.COMPLETED:
            self.successful_requests += 1
            
            # Actualizar promedio de confianza
            if self.successful_requests == 1:
                self.average_confidence = response.confidence
                self.average_relevance = response.relevance_score
            else:
                self.average_confidence = (
                    (self.average_confidence * (self.successful_requests - 1) + response.confidence) /
                    self.successful_requests
                )
                self.average_relevance = (
                    (self.average_relevance * (self.successful_requests - 1) + response.relevance_score) /
                    self.successful_requests
                )
            
            # Actualizar promedio de tiempo de procesamiento
            if response.get_processing_time():
                if self.successful_requests == 1:
                    self.average_processing_time = response.get_processing_time()
                else:
                    self.average_processing_time = (
                        (self.average_processing_time * (self.successful_requests - 1) + response.get_processing_time()) /
                        self.successful_requests
                    )
        else:
            self.failed_requests += 1
    
    async def batch_process(self, inputs: List[str], call_id: str) -> List[AIResponse]:
        """Procesa múltiples entradas"""
        responses = []
        
        for text in inputs:
            response = await self.process_input(text, call_id)
            if response:
                responses.append(response)
        
        return responses
    
    async def process_with_context(self, text: str, call_id: str, context: Dict[str, Any]) -> Optional[AIResponse]:
        """Procesa entrada con contexto adicional"""
        try:
            # Crear contexto extendido
            extended_context = {
                'user_input': text,
                'call_id': call_id,
                'intent': context.get('intent'),
                'entities': context.get('entities', []),
                'sentiment': context.get('sentiment'),
                'previous_responses': context.get('previous_responses', []),
                'user_preferences': context.get('user_preferences', {}),
            }
            
            return await self.process_input(text, call_id, extended_context)
            
        except Exception as e:
            logger.error(f"Error procesando con contexto: {e}")
            return None
    
    def get_conversation_history(self, call_id: str) -> List[str]:
        """Obtiene el historial de conversación para una llamada"""
        return self.conversation_histories.get(call_id, [])
    
    def clear_conversation_history(self, call_id: str) -> None:
        """Limpia el historial de conversación para una llamada"""
        if call_id in self.conversation_histories:
            del self.conversation_histories[call_id]
            logger.info(f"Historial de conversación limpiado para llamada: {call_id}")
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del servicio"""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.successful_requests / max(self.total_requests, 1),
            'average_confidence': self.average_confidence,
            'average_relevance': self.average_relevance,
            'average_processing_time': self.average_processing_time,
            'model_type': self.model_type,
            'max_response_length': self.max_response_length,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'active_conversations': len(self.conversation_histories),
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtiene información del modelo de IA"""
        return {
            'type': self.model_type,
            'max_response_length': self.max_response_length,
            'context_window': self.context_window,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'response_delay': self.response_delay,
        }
    
    async def test_model_connection(self) -> bool:
        """Prueba la conexión con el modelo de IA"""
        try:
            # Procesar entrada de prueba
            test_response = await self.process_input(
                "Hola, ¿cómo estás?",
                "test_call_id"
            )
            
            if test_response and test_response.status == AIResponseStatus.COMPLETED:
                logger.info("Modelo de IA funcionando correctamente")
                return True
            else:
                logger.error("Error en modelo de IA")
                return False
                
        except Exception as e:
            logger.error(f"Error probando modelo de IA: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Cierra el servicio de IA"""
        try:
            # Limpiar historiales de conversación
            self.conversation_histories.clear()
            
            logger.info("Servicio de IA cerrado correctamente")
            
        except Exception as e:
            logger.error(f"Error cerrando servicio de IA: {e}") 