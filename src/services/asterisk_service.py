import asyncio
import logging
import socket
from typing import Optional, Callable
from src.core.config import Config

logger = logging.getLogger(__name__)

class AsteriskService:
    def __init__(self):
        self.ami_host = "localhost"
        self.ami_port = 5038
        self.ami_username = "admin"
        self.ami_secret = "paradixe123"
        self.socket = None
        self.is_connected = False
        self.callbacks = {}

    async def connect(self) -> bool:
        try:
            logger.info("🔌 Conectando a Asterisk AMI...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.ami_host, self.ami_port))
            
            # Login to AMI
            login_msg = f"Action: Login\r\nUsername: {self.ami_username}\r\nSecret: {self.ami_secret}\r\n\r\n"
            self.socket.send(login_msg.encode())
            
            response = self.socket.recv(1024).decode()
            if "Success" in response:
                self.is_connected = True
                logger.info("✅ Conectado a Asterisk AMI")
                return True
            else:
                logger.error("❌ Error en login AMI")
                return False
        except Exception as e:
            logger.error(f"❌ Error conectando a Asterisk: {e}")
            return False

    async def make_call(self, number: str) -> bool:
        try:
            if not self.is_connected:
                if not await self.connect():
                    return False
            
            # Remove + and @ from number for dialing
            clean_number = number.replace("+", "").replace("@1998010101.tscpbx.net", "")
            
            logger.info(f"📞 Llamando a: {clean_number}")
            
            # Originate call via AMI
            originate_msg = f"""Action: Originate
Channel: SIP/paradixe01/{clean_number}
Context: paradixe
Exten: s
Priority: 1
Callerid: paradixe01
\r\n"""
            
            self.socket.send(originate_msg.encode())
            response = self.socket.recv(1024).decode()
            
            if "Success" in response:
                logger.info("✅ Llamada iniciada correctamente")
                return True
            else:
                logger.error(f"❌ Error iniciando llamada: {response}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error haciendo llamada: {e}")
            return False

    async def hangup_call(self, channel: str) -> bool:
        try:
            hangup_msg = f"""Action: Hangup
Channel: {channel}
\r\n"""
            self.socket.send(hangup_msg.encode())
            return True
        except Exception as e:
            logger.error(f"❌ Error colgando llamada: {e}")
            return False

    async def disconnect(self):
        if self.socket:
            self.socket.close()
        self.is_connected = False
        logger.info("🔌 Desconectado de Asterisk AMI")

    def set_callback(self, event: str, callback: Callable):
        self.callbacks[event] = callback 