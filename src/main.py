"""
Aplicación principal del sistema de llamadas SIP con IA
"""

import asyncio
import logging
import signal
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime

from .config.settings import validate_config, get_config_summary
from .config.logging_config import get_logger
from .services.call_manager import CallManager

logger = get_logger('main')

class SIPAIApplication:
    """Aplicación principal del sistema"""
    
    def __init__(self):
        self.call_manager = CallManager()
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Maneja señales de terminación"""
        logger.info(f"Señal recibida: {signum}")
        self.shutdown_event.set()
    
    async def initialize(self) -> bool:
        """Inicializa la aplicación"""
        try:
            logger.info("🚀 Iniciando Sistema de Llamadas SIP con IA")
            logger.info("=" * 60)
            
            # Validar configuración
            errors = validate_config()
            if errors:
                logger.error("❌ Errores de configuración:")
                for error in errors:
                    logger.error(f"   - {error}")
                return False
            
            # Mostrar resumen de configuración
            config_summary = get_config_summary()
            logger.info("📋 Configuración del sistema:")
            for section, config in config_summary.items():
                logger.info(f"   {section}: {config}")
            
            # Inicializar gestor de llamadas
            success = await self.call_manager.initialize()
            if not success:
                logger.error("❌ Error inicializando gestor de llamadas")
                return False
            
            # Configurar callbacks
            self._setup_callbacks()
            
            logger.info("✅ Aplicación inicializada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando aplicación: {e}")
            return False
    
    def _setup_callbacks(self) -> None:
        """Configura callbacks del gestor de llamadas"""
        
        async def on_call_started(call_id: str):
            logger.info(f"📞 Llamada iniciada: {call_id}")
        
        async def on_call_ended(call_id: str):
            logger.info(f"📞 Llamada terminada: {call_id}")
        
        async def on_transcription(call_id: str, transcription):
            logger.info(f"🎤 Transcripción [{call_id}]: {transcription.text[:50]}...")
        
        async def on_ai_response(call_id: str, response):
            logger.info(f"🤖 IA [{call_id}]: {response.text[:50]}...")
        
        self.call_manager.set_call_started_callback(on_call_started)
        self.call_manager.set_call_ended_callback(on_call_ended)
        self.call_manager.set_transcription_callback(on_transcription)
        self.call_manager.set_ai_response_callback(on_ai_response)
    
    async def start(self) -> None:
        """Inicia la aplicación"""
        try:
            logger.info("🚀 Iniciando aplicación...")
            self.is_running = True
            
            # Bucle principal
            while self.is_running and not self.shutdown_event.is_set():
                try:
                    # Aquí puedes agregar lógica adicional del bucle principal
                    # Por ejemplo, procesar números de numbers.txt
                    await self._process_numbers_file()
                    
                    # Esperar un poco antes del siguiente ciclo
                    await asyncio.sleep(10)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error en bucle principal: {e}")
                    await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Error en aplicación: {e}")
        finally:
            await self.shutdown()
    
    async def _process_numbers_file(self) -> None:
        """Procesa el archivo numbers.txt"""
        try:
            import os
            numbers_file = "numbers.txt"
            
            if not os.path.exists(numbers_file):
                logger.debug("Archivo numbers.txt no encontrado")
                return
            
            with open(numbers_file, 'r') as f:
                numbers = [line.strip() for line in f if line.strip()]
            
            if not numbers:
                logger.debug("No hay números para procesar")
                return
            
            # Verificar llamadas activas
            active_calls = self.call_manager.get_active_calls()
            if len(active_calls) >= self.call_manager.max_concurrent_calls:
                logger.debug("Máximo de llamadas concurrentes alcanzado")
                return
            
            # Procesar números
            for number in numbers:
                if self.shutdown_event.is_set():
                    break
                
                # Verificar si ya hay una llamada activa a este número
                for call in active_calls:
                    if call.get('to_number') == number:
                        logger.debug(f"Ya hay llamada activa a {number}")
                        continue
                
                # Realizar llamada
                logger.info(f"📞 Llamando a: {number}")
                call_id = await self.call_manager.make_outgoing_call(number)
                
                if call_id:
                    logger.info(f"✅ Llamada iniciada: {call_id}")
                else:
                    logger.error(f"❌ Error iniciando llamada a: {number}")
                
                # Esperar entre llamadas
                await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"Error procesando números: {e}")
    
    async def make_call(self, destination: str, call_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Realiza una llamada manual"""
        try:
            if not self.is_running:
                logger.error("Aplicación no está ejecutándose")
                return None
            
            call_id = await self.call_manager.make_outgoing_call(destination, call_data)
            
            if call_id:
                logger.info(f"✅ Llamada manual iniciada: {call_id}")
            else:
                logger.error(f"❌ Error en llamada manual a: {destination}")
            
            return call_id
            
        except Exception as e:
            logger.error(f"Error en llamada manual: {e}")
            return None
    
    async def hangup_call(self, call_id: str, reason: Optional[str] = None) -> bool:
        """Cuelga una llamada"""
        try:
            success = await self.call_manager.hangup_call(call_id, reason)
            
            if success:
                logger.info(f"✅ Llamada colgada: {call_id}")
            else:
                logger.error(f"❌ Error colgando llamada: {call_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error colgando llamada: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado de la aplicación"""
        return {
            'is_running': self.is_running,
            'is_shutdown_requested': self.shutdown_event.is_set(),
            'call_manager_stats': self.call_manager.get_manager_stats(),
        }
    
    async def shutdown(self) -> None:
        """Cierra la aplicación"""
        try:
            logger.info("🛑 Cerrando aplicación...")
            
            self.is_running = False
            
            # Cerrar gestor de llamadas
            await self.call_manager.shutdown()
            
            logger.info("✅ Aplicación cerrada correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error cerrando aplicación: {e}")

async def main():
    """Función principal"""
    app = SIPAIApplication()
    
    try:
        # Inicializar aplicación
        success = await app.initialize()
        if not success:
            logger.error("❌ No se pudo inicializar la aplicación")
            sys.exit(1)
        
        # Iniciar aplicación
        await app.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Interrupción del usuario")
    except Exception as e:
        logger.error(f"❌ Error en aplicación: {e}")
    finally:
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main()) 