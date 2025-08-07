"""
Call Manager - Main orchestrator for SIP calls with AI
"""

import asyncio
import logging
from typing import List, Optional
from src.services.asterisk_service import AsteriskService
from src.services.stt_service import STTService
from src.services.tts_service import TTSService
from src.services.ai_service import AIService
from src.core.config import Config

logger = logging.getLogger(__name__)

class CallManager:
    """Main call manager orchestrating Asterisk, STT, TTS, and AI"""
    
    def __init__(self):
        self.asterisk_service = AsteriskService()
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
            
            # Initialize Asterisk service
            if not await self.asterisk_service.connect():
                logger.warning("⚠️ No se pudo conectar con Asterisk AMI")
            
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
        """Make a call via Asterisk"""
        try:
            logger.info(f"📞 Iniciando llamada a: {number}")
            
            # Make call via Asterisk
            if not await self.asterisk_service.make_call(number):
                logger.error("❌ Error iniciando llamada Asterisk")
                return False
            
            # Wait for call to be processed by AGI
            await asyncio.sleep(30)  # Give time for AGI to process
            
            logger.info(f"✅ Llamada completada: {number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en llamada: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown all services"""
        try:
            logger.info("🛑 Cerrando Call Manager...")
            await self.asterisk_service.disconnect()
            self.is_running = False
            logger.info("✅ Call Manager cerrado")
        except Exception as e:
            logger.error(f"❌ Error cerrando Call Manager: {e}")
    
    def get_status(self) -> dict:
        """Get system status"""
        return {
            "asterisk_connected": self.asterisk_service.is_connected,
            "ai_available": True,  # Will be updated with actual check
            "stt_configured": bool(Config.DEEPGRAM_API_KEY),
            "tts_configured": bool(Config.ELEVENLABS_API_KEY),
            "running": self.is_running
        } 