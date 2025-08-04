"""
Main application for SIP AI Call System
"""

import asyncio
import logging
import signal
import sys
import os
from typing import List
from src.core.config import Config
from src.services.call_manager import CallManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SIPAIApplication:
    """Main application class"""
    
    def __init__(self):
        self.call_manager = CallManager()
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("🛑 Señal de cierre recibida...")
        self.shutdown_event.set()
    
    async def initialize(self) -> bool:
        """Initialize the application"""
        try:
            logger.info("🚀 Iniciando Sistema de Llamadas SIP con IA")
            logger.info("=" * 60)
            
            # Validate configuration
            validation = Config.validate()
            if not validation["valid"]:
                logger.error("❌ Errores de configuración:")
                for error in validation["errors"]:
                    logger.error(f"  - {error}")
                logger.info("📝 Configura las variables en .env")
                return False
            
            # Show configuration summary
            config_summary = Config.get_summary()
            logger.info("📋 Configuración:")
            logger.info(f"  SIP: {config_summary['sip']['host']}:{config_summary['sip']['port']}")
            logger.info(f"  AI: {config_summary['ai']['host']} ({config_summary['ai']['model']})")
            logger.info(f"  Server: {config_summary['server']['host']}:{config_summary['server']['port']}")
            
            # Initialize call manager
            if not await self.call_manager.initialize():
                logger.error("❌ Error inicializando Call Manager")
                return False
            
            logger.info("✅ Aplicación inicializada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando aplicación: {e}")
            return False
    
    async def start(self) -> None:
        """Start the application"""
        logger.info("🚀 Iniciando aplicación...")
        self.is_running = True
        
        try:
            # Read numbers from file
            numbers = await self._read_numbers_file()
            if numbers:
                logger.info(f"📞 Procesando {len(numbers)} números...")
                await self.call_manager.process_numbers(numbers)
            else:
                logger.info("📞 No se encontraron números para procesar")
                logger.info("📝 Agrega números en numbers.txt")
            
            # Keep running until shutdown
            while self.is_running and not self.shutdown_event.is_set():
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info("🛑 Aplicación cancelada")
        except Exception as e:
            logger.error(f"❌ Error en aplicación: {e}")
        finally:
            await self.shutdown()
    
    async def _read_numbers_file(self) -> List[str]:
        """Read numbers from numbers.txt file"""
        try:
            if os.path.exists("numbers.txt"):
                with open("numbers.txt", "r") as f:
                    numbers = [line.strip() for line in f.readlines() if line.strip()]
                return numbers
            else:
                logger.warning("⚠️ Archivo numbers.txt no encontrado")
                return []
        except Exception as e:
            logger.error(f"❌ Error leyendo numbers.txt: {e}")
            return []
    
    async def shutdown(self) -> None:
        """Shutdown the application"""
        logger.info("🛑 Cerrando aplicación...")
        self.is_running = False
        await self.call_manager.shutdown()
        logger.info("✅ Aplicación cerrada correctamente")

async def main():
    """Main entry point"""
    app = SIPAIApplication()
    
    try:
        if not await app.initialize():
            logger.error("❌ Error en inicialización")
            sys.exit(1)
        
        await app.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Interrumpido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error en aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 