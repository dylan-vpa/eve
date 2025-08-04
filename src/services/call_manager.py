"""
Call Manager - Main orchestrator for SIP calls with AI
"""

import asyncio
import logging
from typing import List, Optional
from src.services.sip_service import SimpleSIPService
from src.services.stt_service import STTService
from src.services.tts_service import TTSService
from src.services.ai_service import AIService
from src.core.config import Config

logger = logging.getLogger(__name__)

class CallManager:
    """Main call manager orchestrating SIP, STT, TTS, and AI"""
    
    def __init__(self):
        self.sip_service = SimpleSIPService()
        self.stt_service = STTService()
        self.tts_service = TTSService()
        self.ai_service = AIService()
        self.is_running = False
        self.current_call = None
        
    async def initialize(self) -> bool:
        """Initialize all services"""
        try:
            logger.info("🚀 Inicializando Call Manager...")
            
            # Test AI service first
            if not await self.ai_service.test_connection():
                logger.error("❌ No se pudo conectar con Ollama")
                return False
            
            # Initialize SIP service
            if not await self.sip_service.connect():
                logger.warning("⚠️ No se pudo conectar con SIP trunk (modo simulación)")
            
            logger.info("✅ Call Manager inicializado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Call Manager: {e}")
            return False
    
    async def process_numbers(self, numbers: List[str]) -> None:
        """Process list of phone numbers"""
        for number in numbers:
            if number.strip():
                logger.info(f"📞 Procesando número: {number}")
                await self.make_call(number)
                await asyncio.sleep(2)  # Wait between calls
    
    async def make_call(self, number: str) -> bool:
        """Make a call and handle the conversation flow"""
        try:
            logger.info(f"📞 Iniciando llamada a: {number}")
            
            # Make SIP call
            if not await self.sip_service.make_call(number):
                logger.error("❌ Error iniciando llamada SIP")
                return False
            
            # Simulate conversation flow
            await self._simulate_conversation()
            
            # Hangup call
            await self.sip_service.hangup_call()
            
            logger.info(f"✅ Llamada completada: {number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en llamada: {e}")
            return False
    
    async def _simulate_conversation(self) -> None:
        """Simulate conversation flow (STT -> AI -> TTS)"""
        try:
            logger.info("🎤 Simulando conversación...")
            
            # Simulate user input
            user_text = "Hola, necesito ayuda con mi cuenta"
            logger.info(f"👤 Usuario dice: {user_text}")
            
            # Generate AI response
            ai_response = await self.ai_service.generate_response(user_text)
            if ai_response:
                logger.info(f"🤖 AI responde: {ai_response}")
                
                # Generate speech
                audio_data = await self.tts_service.generate_speech(ai_response)
                if audio_data:
                    logger.info(f"🔊 Audio generado: {len(audio_data)} bytes")
                    # In real implementation, this would be sent via SIP
                else:
                    logger.warning("⚠️ No se pudo generar audio")
            else:
                logger.warning("⚠️ No se pudo generar respuesta AI")
                
        except Exception as e:
            logger.error(f"❌ Error en conversación: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown all services"""
        try:
            logger.info("🛑 Cerrando Call Manager...")
            await self.sip_service.disconnect()
            self.is_running = False
            logger.info("✅ Call Manager cerrado")
        except Exception as e:
            logger.error(f"❌ Error cerrando Call Manager: {e}")
    
    def get_status(self) -> dict:
        """Get system status"""
        return {
            "sip_connected": self.sip_service.is_connected,
            "ai_available": True,  # Will be updated with actual check
            "stt_configured": bool(Config.DEEPGRAM_API_KEY),
            "tts_configured": bool(Config.ELEVENLABS_API_KEY),
            "running": self.is_running
        } 