#!/usr/bin/env python3
"""
AGI Handler for Asterisk - AI Call Processing
"""

import sys
import os
import asyncio
import logging
import json
import tempfile
from typing import Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.stt_service import STTService
from src.services.tts_service import TTSService
from src.services.ai_service import AIService
from src.core.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AGIHandler:
    def __init__(self):
        self.stt_service = STTService()
        self.tts_service = TTSService()
        self.ai_service = AIService()
        self.agi_vars = {}
        
    def read_agi_vars(self):
        """Read AGI variables from stdin"""
        while True:
            line = sys.stdin.readline().strip()
            if line == "":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                self.agi_vars[key.strip()] = value.strip()
    
    def send_agi_command(self, command):
        """Send command to Asterisk"""
        print(command)
        sys.stdout.flush()
    
    def get_agi_response(self):
        """Get response from Asterisk"""
        response = sys.stdin.readline().strip()
        return response
    
    async def process_call(self):
        """Main call processing logic"""
        try:
            logger.info("🎤 Iniciando procesamiento de llamada AGI")
            
            # Get call information
            caller_id = self.agi_vars.get('agi_callerid', 'Unknown')
            channel = self.agi_vars.get('agi_channel', 'Unknown')
            
            logger.info(f"📞 Llamada de: {caller_id} en canal: {channel}")
            
            # Answer the call
            self.send_agi_command("ANSWER")
            response = self.get_agi_response()
            logger.info(f"Respuesta ANSWER: {response}")
            
            # Play welcome message
            welcome_text = "Hola, soy tu asistente virtual. ¿En qué puedo ayudarte?"
            await self.play_ai_response(welcome_text)
            
            # Main conversation loop
            conversation_rounds = 0
            max_rounds = 5
            
            while conversation_rounds < max_rounds:
                # Record user input
                user_audio = await self.record_user_input()
                if not user_audio:
                    logger.warning("⚠️ No se pudo grabar audio del usuario")
                    break
                
                # Transcribe audio
                transcript = await self.stt_service.transcribe_audio(user_audio)
                if not transcript:
                    logger.warning("⚠️ No se pudo transcribir audio")
                    break
                
                logger.info(f"👤 Usuario dice: {transcript}")
                
                # Generate AI response
                ai_response = await self.ai_service.generate_response(transcript)
                if not ai_response:
                    logger.warning("⚠️ No se pudo generar respuesta AI")
                    break
                
                logger.info(f"🤖 AI responde: {ai_response}")
                
                # Play AI response
                await self.play_ai_response(ai_response)
                
                conversation_rounds += 1
            
            # End call
            self.send_agi_command("HANGUP")
            logger.info("✅ Llamada finalizada")
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento AGI: {e}")
            self.send_agi_command("HANGUP")
    
    async def record_user_input(self) -> Optional[bytes]:
        """Record audio from user"""
        try:
            # Create temporary file for recording
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Record audio using Asterisk
            self.send_agi_command(f"RECORD FILE {temp_path} 0 10 3")
            response = self.get_agi_response()
            
            if "200" in response:
                # Read the recorded file
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                
                # Clean up
                os.unlink(temp_path)
                
                logger.info(f"🎤 Audio grabado: {len(audio_data)} bytes")
                return audio_data
            else:
                logger.error(f"❌ Error grabando audio: {response}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error en grabación: {e}")
            return None
    
    async def play_ai_response(self, text: str):
        """Generate and play AI response"""
        try:
            # Generate speech
            audio_data = await self.tts_service.generate_speech(text)
            if not audio_data:
                logger.error("❌ No se pudo generar audio")
                return
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio_data)
            
            # Play audio via Asterisk
            self.send_agi_command(f"STREAM FILE {temp_path}")
            response = self.get_agi_response()
            
            # Clean up
            os.unlink(temp_path)
            
            if "200" in response:
                logger.info("🔊 Audio reproducido correctamente")
            else:
                logger.error(f"❌ Error reproduciendo audio: {response}")
                
        except Exception as e:
            logger.error(f"❌ Error reproduciendo audio: {e}")

def main():
    """Main AGI entry point"""
    handler = AGIHandler()
    handler.read_agi_vars()
    
    # Run async function
    asyncio.run(handler.process_call())

if __name__ == "__main__":
    main() 