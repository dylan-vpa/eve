"""
Text-to-Speech service using ElevenLabs
"""

import asyncio
import logging
import aiohttp
import tempfile
import os
from typing import Optional
from src.core.config import Config

logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service using ElevenLabs"""
    
    def __init__(self):
        self.api_key = Config.ELEVENLABS_API_KEY
        self.voice_id = Config.ELEVENLABS_VOICE_ID
        self.base_url = "https://api.elevenlabs.io/v1"
        
    async def generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech from text using ElevenLabs"""
        try:
            if not self.api_key:
                logger.error("❌ ElevenLabs API key no configurada")
                return None
                
            if not self.voice_id:
                logger.error("❌ ElevenLabs Voice ID no configurado")
                return None
            
            url = f"{self.base_url}/text-to-speech/{self.voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        audio_data = await response.read()
                        logger.info(f"🔊 Audio generado: {len(audio_data)} bytes")
                        return audio_data
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Error en ElevenLabs API: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Error generando audio: {e}")
            return None
    
    async def generate_speech_file(self, text: str, output_path: str) -> bool:
        """Generate speech file from text"""
        try:
            audio_data = await self.generate_speech(text)
            if audio_data:
                with open(output_path, 'wb') as f:
                    f.write(audio_data)
                logger.info(f"✅ Audio guardado en: {output_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error guardando audio: {e}")
            return False
    
    async def generate_temp_speech(self, text: str) -> Optional[str]:
        """Generate speech and return temporary file path"""
        try:
            audio_data = await self.generate_speech(text)
            if audio_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                    f.write(audio_data)
                    temp_path = f.name
                
                logger.info(f"✅ Audio temporal creado: {temp_path}")
                return temp_path
            return None
        except Exception as e:
            logger.error(f"❌ Error creando audio temporal: {e}")
            return None 