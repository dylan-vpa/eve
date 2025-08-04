"""
FastAPI server for SIP AI Call System
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from src.core.config import Config
from src.services.call_manager import CallManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SIP AI Call System",
    description="Sistema de llamadas SIP con IA, STT y TTS",
    version="1.0.0"
)

# Global call manager
call_manager = None

class CallRequest(BaseModel):
    number: str
    message: str = "Hola, esta es una llamada de prueba"

class NumbersRequest(BaseModel):
    numbers: List[str]

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global call_manager
    try:
        call_manager = CallManager()
        if await call_manager.initialize():
            logger.info("✅ Servidor inicializado correctamente")
        else:
            logger.warning("⚠️ Servidor inicializado con advertencias")
    except Exception as e:
        logger.error(f"❌ Error inicializando servidor: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown services"""
    global call_manager
    if call_manager:
        await call_manager.shutdown()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SIP AI Call System",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global call_manager
    if call_manager:
        status = call_manager.get_status()
        return {
            "status": "healthy",
            "services": status
        }
    else:
        raise HTTPException(status_code=503, detail="Call manager not initialized")

@app.get("/config")
async def get_config():
    """Get configuration summary"""
    return {
        "config": Config.get_summary(),
        "validation": Config.validate()
    }

@app.post("/call")
async def make_call(request: CallRequest):
    """Make a single call"""
    global call_manager
    if not call_manager:
        raise HTTPException(status_code=503, detail="Call manager not available")
    
    try:
        success = await call_manager.make_call(request.number)
        return {
            "success": success,
            "number": request.number,
            "message": "Llamada iniciada" if success else "Error iniciando llamada"
        }
    except Exception as e:
        logger.error(f"Error en llamada: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/call/batch")
async def make_batch_calls(request: NumbersRequest):
    """Make batch calls"""
    global call_manager
    if not call_manager:
        raise HTTPException(status_code=503, detail="Call manager not available")
    
    try:
        await call_manager.process_numbers(request.numbers)
        return {
            "success": True,
            "numbers_processed": len(request.numbers),
            "message": "Llamadas en lote iniciadas"
        }
    except Exception as e:
        logger.error(f"Error en llamadas en lote: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """Get system status"""
    global call_manager
    if call_manager:
        return call_manager.get_status()
    else:
        return {"error": "Call manager not available"}

@app.post("/test/ai")
async def test_ai():
    """Test AI service"""
    global call_manager
    if not call_manager:
        raise HTTPException(status_code=503, detail="Call manager not available")
    
    try:
        response = await call_manager.ai_service.generate_response("Hola, ¿cómo estás?")
        return {
            "success": bool(response),
            "response": response,
            "message": "Test AI completado"
        }
    except Exception as e:
        logger.error(f"Error en test AI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/tts")
async def test_tts():
    """Test TTS service"""
    global call_manager
    if not call_manager:
        raise HTTPException(status_code=503, detail="Call manager not available")
    
    try:
        audio_data = await call_manager.tts_service.generate_speech("Hola, esta es una prueba de texto a voz.")
        return {
            "success": bool(audio_data),
            "audio_size": len(audio_data) if audio_data else 0,
            "message": "Test TTS completado"
        }
    except Exception as e:
        logger.error(f"Error en test TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 