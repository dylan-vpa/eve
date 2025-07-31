#!/usr/bin/env python3
"""
Servidor API REST para el Sistema de Llamadas SIP con IA
Ejecuta en el puerto 8000 y expone endpoints para gestionar llamadas
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import asdict

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic.json import pydantic_encoder

from src.config.settings import get_config_summary
from src.services.call_manager import CallManager
from src.models.call import Call, CallStatus, CallDirection
from src.models.audio import AudioChunk
from src.models.transcription import TranscriptionResult
from src.models.ai_response import AIResponse

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Llamadas SIP con IA",
    description="API REST para gestionar llamadas SIP con IA, STT y TTS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para la API
class CallRequest(BaseModel):
    """Modelo para solicitar una llamada"""
    number: str = Field(..., description="Número de destino en formato SIP")
    message: Optional[str] = Field(None, description="Mensaje inicial opcional")
    timeout: Optional[int] = Field(30, description="Timeout de la llamada en segundos")

class CallResponse(BaseModel):
    """Modelo para respuesta de llamada"""
    call_id: str
    status: str
    number: str
    created_at: datetime
    message: Optional[str] = None

class SystemStatus(BaseModel):
    """Modelo para estado del sistema"""
    status: str
    active_calls: int
    total_calls: int
    uptime: str
    version: str
    services: Dict[str, str]

class CallInfo(BaseModel):
    """Modelo para información de llamada"""
    call_id: str
    number: str
    status: str
    direction: str
    created_at: datetime
    duration: Optional[float] = None
    transcription: Optional[str] = None
    ai_response: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

# Variables globales
call_manager: Optional[CallManager] = None
system_start_time: Optional[datetime] = None
active_calls: Dict[str, Call] = {}

@app.on_event("startup")
async def startup_event():
    """Inicializar el sistema al arrancar"""
    global call_manager, system_start_time
    
    logger.info("🚀 Iniciando Sistema de Llamadas SIP con IA en puerto 8000")
    
    try:
        # Inicializar Call Manager
        call_manager = CallManager()
        await call_manager.initialize()
        
        # Configurar callbacks
        call_manager.set_call_connected_callback(on_call_connected)
        call_manager.set_call_ended_callback(on_call_ended)
        call_manager.set_transcription_callback(on_transcription)
        call_manager.set_ai_response_callback(on_ai_response)
        
        system_start_time = datetime.now()
        
        logger.info("✅ Sistema inicializado correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error inicializando sistema: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar"""
    global call_manager
    
    logger.info("🛑 Cerrando sistema...")
    
    if call_manager:
        await call_manager.shutdown()
    
    logger.info("✅ Sistema cerrado correctamente")

# Callbacks del Call Manager
def on_call_connected(call: Call):
    """Callback cuando se conecta una llamada"""
    global active_calls
    active_calls[call.call_id] = call
    logger.info(f"📞 Llamada conectada: {call.number} (ID: {call.call_id})")

def on_call_ended(call: Call):
    """Callback cuando termina una llamada"""
    global active_calls
    if call.call_id in active_calls:
        del active_calls[call.call_id]
    logger.info(f"📞 Llamada terminada: {call.number} (ID: {call.call_id})")

def on_transcription(call_id: str, transcription: TranscriptionResult):
    """Callback cuando se recibe una transcripción"""
    logger.info(f"🎯 Transcripción recibida para {call_id}: {transcription.text}")

def on_ai_response(call_id: str, response: AIResponse):
    """Callback cuando se genera una respuesta de IA"""
    logger.info(f"🤖 Respuesta IA generada para {call_id}: {response.text[:50]}...")

# Endpoints de la API

@app.get("/", tags=["Info"])
async def root():
    """Endpoint raíz con información del sistema"""
    return {
        "message": "Sistema de Llamadas SIP con IA",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "calls": "/calls",
            "make_call": "/calls",
            "hangup": "/calls/{call_id}/hangup"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Verificar estado de salud del sistema"""
    global call_manager, system_start_time
    
    if not call_manager:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "uptime": str(datetime.now() - system_start_time) if system_start_time else "unknown",
        "services": {
            "sip": "connected" if call_manager.sip_service else "disconnected",
            "audio": "ready" if call_manager.audio_service else "not_ready",
            "stt": "ready" if call_manager.stt_service else "not_ready",
            "tts": "ready" if call_manager.tts_service else "not_ready",
            "ai": "ready" if call_manager.ai_service else "not_ready"
        }
    }

@app.get("/status", tags=["Status"])
async def get_system_status():
    """Obtener estado completo del sistema"""
    global call_manager, active_calls, system_start_time
    
    uptime = str(datetime.now() - system_start_time) if system_start_time else "unknown"
    
    return SystemStatus(
        status="running",
        active_calls=len(active_calls),
        total_calls=len(call_manager.call_queue.calls) if call_manager else 0,
        uptime=uptime,
        version="1.0.0",
        services={
            "sip": "connected" if call_manager and call_manager.sip_service else "disconnected",
            "audio": "ready" if call_manager and call_manager.audio_service else "not_ready",
            "stt": "ready" if call_manager and call_manager.stt_service else "not_ready",
            "tts": "ready" if call_manager and call_manager.tts_service else "not_ready",
            "ai": "ready" if call_manager and call_manager.ai_service else "not_ready"
        }
    )

@app.get("/calls", tags=["Calls"])
async def get_calls():
    """Obtener lista de llamadas activas"""
    global active_calls, call_manager
    
    calls = []
    
    # Llamadas activas
    for call in active_calls.values():
        calls.append(CallInfo(
            call_id=call.call_id,
            number=call.number,
            status=call.status.value,
            direction=call.direction.value,
            created_at=call.created_at,
            duration=call.get_duration(),
            transcription=call.last_transcription,
            ai_response=call.last_ai_response,
            metrics=call.metrics.__dict__ if call.metrics else None
        ))
    
    # Llamadas en cola
    if call_manager and call_manager.call_queue:
        for call in call_manager.call_queue.calls:
            if call.call_id not in active_calls:
                calls.append(CallInfo(
                    call_id=call.call_id,
                    number=call.number,
                    status=call.status.value,
                    direction=call.direction.value,
                    created_at=call.created_at,
                    duration=call.get_duration(),
                    transcription=call.last_transcription,
                    ai_response=call.last_ai_response,
                    metrics=call.metrics.__dict__ if call.metrics else None
                ))
    
    return {"calls": calls, "total": len(calls)}

@app.post("/calls", tags=["Calls"])
async def make_call(call_request: CallRequest, background_tasks: BackgroundTasks):
    """Iniciar una nueva llamada"""
    global call_manager
    
    if not call_manager:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    try:
        # Validar formato del número
        if not call_request.number.startswith("sip:"):
            call_request.number = f"sip:{call_request.number}"
        
        # Crear llamada
        call = Call(
            number=call_request.number,
            direction=CallDirection.OUTGOING,
            message=call_request.message
        )
        
        # Agregar a la cola
        call_manager.call_queue.add_call(call)
        
        # Iniciar llamada en background
        background_tasks.add_task(call_manager.make_outgoing_call, call)
        
        logger.info(f"📞 Llamada programada: {call_request.number}")
        
        return CallResponse(
            call_id=call.call_id,
            status="initiated",
            number=call_request.number,
            created_at=call.created_at,
            message=call_request.message
        )
        
    except Exception as e:
        logger.error(f"❌ Error iniciando llamada: {e}")
        raise HTTPException(status_code=500, detail=f"Error iniciando llamada: {str(e)}")

@app.delete("/calls/{call_id}/hangup", tags=["Calls"])
async def hangup_call(call_id: str):
    """Colgar una llamada específica"""
    global call_manager, active_calls
    
    if not call_manager:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    # Buscar llamada
    call = None
    if call_id in active_calls:
        call = active_calls[call_id]
    elif call_manager.call_queue:
        for c in call_manager.call_queue.calls:
            if c.call_id == call_id:
                call = c
                break
    
    if not call:
        raise HTTPException(status_code=404, detail="Llamada no encontrada")
    
    try:
        await call_manager.hangup_call(call)
        logger.info(f"📞 Llamada colgada: {call_id}")
        
        return {"message": "Llamada colgada correctamente", "call_id": call_id}
        
    except Exception as e:
        logger.error(f"❌ Error colgando llamada: {e}")
        raise HTTPException(status_code=500, detail=f"Error colgando llamada: {str(e)}")

@app.get("/config", tags=["Config"])
async def get_config():
    """Obtener configuración del sistema"""
    try:
        config_summary = get_config_summary()
        return {"config": config_summary}
    except Exception as e:
        logger.error(f"❌ Error obteniendo configuración: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo configuración: {str(e)}")

@app.post("/test", tags=["Test"])
async def test_apis():
    """Probar APIs de STT y TTS"""
    global call_manager
    
    if not call_manager:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")
    
    try:
        results = {}
        
        # Probar STT
        if call_manager.stt_service:
            stt_result = await call_manager.stt_service.test_api_connection()
            results["stt"] = stt_result
        
        # Probar TTS
        if call_manager.tts_service:
            tts_result = await call_manager.tts_service.test_api_connection()
            results["tts"] = tts_result
        
        return {"test_results": results}
        
    except Exception as e:
        logger.error(f"❌ Error en pruebas: {e}")
        raise HTTPException(status_code=500, detail=f"Error en pruebas: {str(e)}")

# Función para ejecutar el servidor
def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Ejecutar el servidor API"""
    logger.info(f"🚀 Iniciando servidor en {host}:{port}")
    
    uvicorn.run(
        "src.api.server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    run_server() 