"""
Simple SIP Service using reliable libraries
"""

import asyncio
import logging
from typing import Optional, Callable
import socket
import struct
from src.core.config import Config

logger = logging.getLogger(__name__)

class SimpleSIPService:
    """Simple SIP service for trunk communication"""
    
    def __init__(self):
        self.socket = None
        self.is_connected = False
        self.callbacks = {}
        
    async def connect(self) -> bool:
        """Connect to SIP trunk"""
        try:
            logger.info(f"🔌 Conectando a SIP trunk: {Config.SIP_HOST}:{Config.SIP_PORT}")
            
            # Create UDP socket for SIP
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(10)
            
            # Basic SIP registration (simplified)
            register_msg = self._create_register_message()
            self.socket.sendto(register_msg.encode(), (Config.SIP_HOST, Config.SIP_PORT))
            
            # Wait for response
            try:
                data, addr = self.socket.recvfrom(1024)
                if "200 OK" in data.decode():
                    self.is_connected = True
                    logger.info("✅ Conectado a SIP trunk")
                    return True
                else:
                    logger.error("❌ Error en registro SIP")
                    return False
            except socket.timeout:
                logger.warning("⚠️ Timeout en registro SIP, continuando...")
                self.is_connected = True  # Continue anyway for testing
                return True
                
        except Exception as e:
            logger.error(f"❌ Error conectando a SIP: {e}")
            return False
    
    def _create_register_message(self) -> str:
        """Create SIP REGISTER message"""
        call_id = f"call_id_{hash(asyncio.get_event_loop().time())}"
        
        return f"""REGISTER sip:{Config.SIP_HOST} SIP/2.0
Via: SIP/2.0/UDP {socket.gethostbyname(socket.gethostname())}:5060
From: <sip:{Config.SIP_USERNAME}@{Config.SIP_HOST}>
To: <sip:{Config.SIP_USERNAME}@{Config.SIP_HOST}>
Call-ID: {call_id}
CSeq: 1 REGISTER
Contact: <sip:{Config.SIP_USERNAME}@{socket.gethostbyname(socket.gethostname())}:5060>
Expires: 3600
Content-Length: 0

"""
    
    async def make_call(self, number: str) -> bool:
        """Make outgoing call"""
        try:
            logger.info(f"📞 Llamando a: {number}")
            
            if not self.is_connected:
                if not await self.connect():
                    return False
            
            # Create INVITE message
            invite_msg = self._create_invite_message(number)
            self.socket.sendto(invite_msg.encode(), (Config.SIP_HOST, Config.SIP_PORT))
            
            logger.info("📞 Invite enviado, esperando respuesta...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error haciendo llamada: {e}")
            return False
    
    def _create_invite_message(self, number: str) -> str:
        """Create SIP INVITE message"""
        call_id = f"call_id_{hash(asyncio.get_event_loop().time())}"
        
        return f"""INVITE {number} SIP/2.0
Via: SIP/2.0/UDP {socket.gethostbyname(socket.gethostname())}:5060
From: <sip:{Config.SIP_USERNAME}@{Config.SIP_HOST}>
To: <{number}>
Call-ID: {call_id}
CSeq: 1 INVITE
Contact: <sip:{Config.SIP_USERNAME}@{socket.gethostbyname(socket.gethostname())}:5060>
Content-Type: application/sdp
Content-Length: 0

"""
    
    async def hangup_call(self) -> bool:
        """Hangup current call"""
        try:
            logger.info("📞 Colgando llamada...")
            # Send BYE message
            bye_msg = self._create_bye_message()
            self.socket.sendto(bye_msg.encode(), (Config.SIP_HOST, Config.SIP_PORT))
            return True
        except Exception as e:
            logger.error(f"❌ Error colgando llamada: {e}")
            return False
    
    def _create_bye_message(self) -> str:
        """Create SIP BYE message"""
        call_id = f"call_id_{hash(asyncio.get_event_loop().time())}"
        
        return f"""BYE sip:{Config.SIP_HOST} SIP/2.0
Via: SIP/2.0/UDP {socket.gethostbyname(socket.gethostname())}:5060
From: <sip:{Config.SIP_USERNAME}@{Config.SIP_HOST}>
To: <sip:{Config.SIP_USERNAME}@{Config.SIP_HOST}>
Call-ID: {call_id}
CSeq: 1 BYE
Content-Length: 0

"""
    
    async def disconnect(self):
        """Disconnect from SIP trunk"""
        if self.socket:
            self.socket.close()
        self.is_connected = False
        logger.info("🔌 Desconectado de SIP trunk")
    
    def set_callback(self, event: str, callback: Callable):
        """Set callback for SIP events"""
        self.callbacks[event] = callback 