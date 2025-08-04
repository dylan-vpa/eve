"""
AI service using Ollama
"""

import asyncio
import logging
import aiohttp
import json
from typing import Optional
from src.core.config import Config

logger = logging.getLogger(__name__)

class AIService:
    """AI service using Ollama"""
    
    def __init__(self):
        self.host = Config.OLLAMA_HOST
        self.model = Config.OLLAMA_MODEL
        
    async def check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.host}/api/tags", timeout=5) as response:
                    if response.status == 200:
                        logger.info("✅ Ollama está funcionando")
                        return True
                    else:
                        logger.error("❌ Ollama no responde correctamente")
                        return False
        except Exception as e:
            logger.error(f"❌ Error conectando con Ollama: {e}")
            return False
    
    async def generate_response(self, text: str) -> Optional[str]:
        """Generate AI response using Ollama"""
        try:
            if not await self.check_ollama():
                return None
            
            url = f"{self.host}/api/generate"
            
            data = {
                "model": self.model,
                "prompt": f"Eres un asistente telefónico amigable. Responde de manera natural y útil a: {text}",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 150
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response", "").strip()
                        
                        if response_text:
                            logger.info(f"🤖 Respuesta AI: {response_text}")
                            return response_text
                        else:
                            logger.warning("⚠️ No se generó respuesta de AI")
                            return "Lo siento, no pude procesar tu solicitud."
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Error en Ollama API: {response.status} - {error_text}")
                        return "Lo siento, hay un problema técnico."
                        
        except Exception as e:
            logger.error(f"❌ Error generando respuesta AI: {e}")
            return "Lo siento, hay un problema técnico."
    
    async def test_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            return await self.check_ollama()
        except Exception as e:
            logger.error(f"❌ Error en test de conexión: {e}")
            return False 