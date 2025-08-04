"""
Speech-to-Text service using Deepgram
"""

import asyncio
import logging
import aiohttp
from typing import Optional
from src.core.config import Config

logger = logging.getLogger(__name__)

class STTService:
    """Speech-to-Text service using Deepgram"""
    
    def __init__(self):
        self.api_key = Config.DEEPGRAM_API_KEY
        self.base_url = "https://api.deepgram.com/v1/listen"
        
    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio to text using Deepgram"""
        try:
            if not self.api_key:
                logger.error("❌ Deepgram API key no configurada")
                return None
            
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/wav"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    data=audio_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        transcript = result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
                        
                        if transcript:
                            logger.info(f"🎤 Transcripción: {transcript}")
                            return transcript
                        else:
                            logger.warning("⚠️ No se detectó texto en el audio")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Error en Deepgram API: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Error en transcripción: {e}")
            return None
    
    async def transcribe_file(self, file_path: str) -> Optional[str]:
        """Transcribe audio file to text"""
        try:
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            return await self.transcribe_audio(audio_data)
        except Exception as e:
            logger.error(f"❌ Error leyendo archivo de audio: {e}")
            return None 