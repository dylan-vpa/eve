"""
Configuration management for SIP AI Call System
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration class"""
    
    # SIP Configuration
    SIP_HOST = os.environ.get("SIP_HOST", "sip.example.com")
    SIP_USERNAME = os.environ.get("SIP_USERNAME", "your_username")
    SIP_PASSWORD = os.environ.get("SIP_PASSWORD", "your_password")
    SIP_PORT = int(os.environ.get("SIP_PORT", "5060"))
    
    # Deepgram STT
    DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY", "")
    
    # ElevenLabs TTS
    ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "")
    
    # Ollama AI - Always use localhost for Ollama
    OLLAMA_HOST = "http://localhost:11434"
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2")
    
    # Server Configuration
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "8000"))
    DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate configuration and return errors"""
        errors = []
        
        if not cls.SIP_HOST or cls.SIP_HOST == "sip.example.com":
            errors.append("SIP_HOST not configured")
        
        if not cls.SIP_USERNAME or cls.SIP_USERNAME == "your_username":
            errors.append("SIP_USERNAME not configured")
            
        if not cls.SIP_PASSWORD or cls.SIP_PASSWORD == "your_password":
            errors.append("SIP_PASSWORD not configured")
            
        if not cls.DEEPGRAM_API_KEY:
            errors.append("DEEPGRAM_API_KEY not configured")
            
        if not cls.ELEVENLABS_API_KEY:
            errors.append("ELEVENLABS_API_KEY not configured")
            
        if not cls.ELEVENLABS_VOICE_ID:
            errors.append("ELEVENLABS_VOICE_ID not configured")
        
        return {"errors": errors, "valid": len(errors) == 0}
    
    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "sip": {
                "host": cls.SIP_HOST,
                "username": cls.SIP_USERNAME,
                "port": cls.SIP_PORT
            },
            "ai": {
                "host": cls.OLLAMA_HOST,
                "model": cls.OLLAMA_MODEL
            },
            "server": {
                "host": cls.HOST,
                "port": cls.PORT,
                "debug": cls.DEBUG
            }
        } 