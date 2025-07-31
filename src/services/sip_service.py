"""
Servicio SIP para manejo de llamadas
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

try:
    import pjsua2 as pj
except ImportError:
    logging.error("PJSIP no está instalado")
    pj = None

from ..config.settings import SIP_CONFIG, get_sip_uri, get_registrar_uri
from ..config.logging_config import get_logger, CallLogger
from ..models.call import Call, CallStatus, CallDirection, CallQueue

logger = get_logger('sip')

class SIPAccount(pj.Account):
    """Cuenta SIP con manejo de eventos"""
    
    def __init__(self, service: 'SIPService', account_config: pj.AccountConfig):
        pj.Account.__init__(self)
        self.service = service
        self.account_config = account_config
        self.calls: Dict[str, 'SIPCall'] = {}
        self.logger = get_logger('sip.account')
        
    def onRegState(self, prm):
        """Callback de estado de registro"""
        self.logger.info(f"Estado de registro: {prm.code} {prm.reason}")
        self.service.on_registration_state(prm.code, prm.reason)
        
    def onIncomingCall(self, prm):
        """Callback de llamada entrante"""
        self.logger.info(f"Llamada entrante recibida: {prm.callId}")
        call = SIPCall(self, prm.callId, direction=CallDirection.INBOUND)
        self.calls[prm.callId] = call
        self.service.on_incoming_call(call)

class SIPCall(pj.Call):
    """Llamada SIP con manejo de eventos"""
    
    def __init__(self, account: SIPAccount, call_id: Optional[str] = None, direction: CallDirection = CallDirection.OUTBOUND):
        pj.Call.__init__(self, account, call_id)
        self.account = account
        self.direction = direction
        self.call_logger = CallLogger(call_id or "unknown")
        self.is_active = False
        self.media_state = None
        
    def onCallState(self, prm):
        """Callback de estado de llamada"""
        state = prm.e.state
        self.call_logger.info(f"Estado de llamada: {state}")
        
        if state == pj.PJSIP_INV_STATE_CONFIRMED:
            self.is_active = True
            self.call_logger.info("Llamada conectada")
            self.account.service.on_call_connected(self)
        elif state == pj.PJSIP_INV_STATE_DISCONNECTED:
            self.is_active = False
            self.call_logger.info("Llamada terminada")
            self.account.service.on_call_ended(self)
        elif state == pj.PJSIP_INV_STATE_CALLING:
            self.call_logger.info("Llamada iniciando")
        elif state == pj.PJSIP_INV_STATE_INCOMING:
            self.call_logger.info("Llamada entrante")
        elif state == pj.PJSIP_INV_STATE_EARLY:
            self.call_logger.info("Llamada temprana")
            
    def onCallMediaState(self, prm):
        """Callback de estado de media"""
        self.media_state = prm.e.state
        self.call_logger.info(f"Estado de media: {prm.e.state}")
        self.account.service.on_call_media_state(self, prm.e.state)
        
    def onCallTsxState(self, prm):
        """Callback de estado de transacción"""
        self.call_logger.debug(f"Estado de transacción: {prm.e.state}")
        
    def onCallSdpCreated(self, prm):
        """Callback de SDP creado"""
        self.call_logger.debug("SDP creado")
        
    def onCallTransferRequest(self, prm):
        """Callback de solicitud de transferencia"""
        self.call_logger.info("Solicitud de transferencia recibida")
        
    def onCallTransferStatus(self, prm):
        """Callback de estado de transferencia"""
        self.call_logger.info(f"Estado de transferencia: {prm.e.status}")

class SIPService:
    """Servicio principal para manejo SIP"""
    
    def __init__(self):
        self.endpoint: Optional[pj.Endpoint] = None
        self.account: Optional[SIPAccount] = None
        self.call_queue = CallQueue()
        self.active_calls: Dict[str, SIPCall] = {}
        self.logger = get_logger('sip.service')
        
        # Callbacks
        self.on_call_connected_callback: Optional[Callable] = None
        self.on_call_ended_callback: Optional[Callable] = None
        self.on_incoming_call_callback: Optional[Callable] = None
        
        # Estado
        self.is_initialized = False
        self.is_registered = False
        
    async def initialize(self) -> bool:
        """Inicializa el servicio SIP"""
        try:
            if not pj:
                self.logger.error("PJSIP no está disponible")
                return False
            
            # Crear endpoint
            self.endpoint = pj.Endpoint()
            self.endpoint.libCreate()
            
            # Configurar endpoint
            ep_cfg = pj.EpConfig()
            ep_cfg.logConfig.level = 4
            ep_cfg.logConfig.consoleLevel = 4
            self.endpoint.libInit(ep_cfg)
            
            # Configurar transporte UDP
            tcfg = pj.TransportConfig()
            tcfg.port = SIP_CONFIG['port']
            self.endpoint.transportCreate(pj.PJSIP_TRANSPORT_UDP, tcfg)
            
            # Iniciar endpoint
            self.endpoint.libStart()
            
            # Crear cuenta
            await self._create_account()
            
            self.is_initialized = True
            self.logger.info("Servicio SIP inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando servicio SIP: {e}")
            return False
    
    async def _create_account(self) -> None:
        """Crea la cuenta SIP"""
        try:
            # Configurar cuenta
            acc_cfg = pj.AccountConfig()
            acc_cfg.idUri = get_sip_uri()
            acc_cfg.regConfig.registrarUri = get_registrar_uri()
            
            # Credenciales
            cred = pj.AuthCredInfo("digest", "*", SIP_CONFIG['username'], 0, SIP_CONFIG['password'])
            acc_cfg.sipConfig.authCreds.append(cred)
            
            # Crear cuenta
            self.account = SIPAccount(self, acc_cfg)
            self.account.create(acc_cfg)
            
            self.logger.info("Cuenta SIP creada correctamente")
            
        except Exception as e:
            self.logger.error(f"Error creando cuenta SIP: {e}")
            raise
    
    async def make_call(self, destination: str, call_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Realiza una llamada saliente"""
        try:
            if not self.is_initialized or not self.account:
                self.logger.error("Servicio SIP no inicializado")
                return None
            
            # Crear llamada
            call = SIPCall(self.account, direction=CallDirection.OUTBOUND)
            self.account.calls[call.getId()] = call
            
            # Configurar parámetros de llamada
            call_param = pj.CallOpParam(True)
            
            # Realizar llamada
            call.makeCall(destination, call_param)
            
            call_id = call.getId()
            self.active_calls[call_id] = call
            
            self.logger.info(f"Llamada iniciada a {destination} (ID: {call_id})")
            return call_id
            
        except Exception as e:
            self.logger.error(f"Error realizando llamada: {e}")
            return None
    
    async def answer_call(self, call: SIPCall) -> bool:
        """Responde una llamada entrante"""
        try:
            call.answer(200)
            self.logger.info(f"Llamada respondida: {call.getId()}")
            return True
        except Exception as e:
            self.logger.error(f"Error respondiendo llamada: {e}")
            return False
    
    async def hangup_call(self, call_id: str, reason: Optional[str] = None) -> bool:
        """Cuelga una llamada"""
        try:
            if call_id in self.active_calls:
                call = self.active_calls[call_id]
                call.hangup()
                self.logger.info(f"Llamada colgada: {call_id}")
                return True
            else:
                self.logger.warning(f"Llamada no encontrada: {call_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error colgando llamada: {e}")
            return False
    
    async def transfer_call(self, call_id: str, destination: str) -> bool:
        """Transfiere una llamada"""
        try:
            if call_id in self.active_calls:
                call = self.active_calls[call_id]
                call.xfer(destination)
                self.logger.info(f"Llamada transferida: {call_id} -> {destination}")
                return True
            else:
                self.logger.warning(f"Llamada no encontrada para transferir: {call_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error transfiriendo llamada: {e}")
            return False
    
    def get_call_info(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de una llamada"""
        if call_id in self.active_calls:
            call = self.active_calls[call_id]
            return {
                'id': call_id,
                'direction': call.direction.value,
                'is_active': call.is_active,
                'media_state': call.media_state,
            }
        return None
    
    def get_active_calls(self) -> List[Dict[str, Any]]:
        """Obtiene todas las llamadas activas"""
        return [
            {
                'id': call_id,
                'direction': call.direction.value,
                'is_active': call.is_active,
                'media_state': call.media_state,
            }
            for call_id, call in self.active_calls.items()
        ]
    
    def get_service_status(self) -> Dict[str, Any]:
        """Obtiene el estado del servicio"""
        return {
            'initialized': self.is_initialized,
            'registered': self.is_registered,
            'active_calls': len(self.active_calls),
            'account_uri': get_sip_uri() if self.account else None,
        }
    
    # Callbacks de eventos
    def on_registration_state(self, code: int, reason: str) -> None:
        """Callback de estado de registro"""
        self.is_registered = code == 200
        self.logger.info(f"Registro SIP: {code} {reason}")
        
        if self.is_registered:
            self.logger.info("Registro SIP exitoso")
        else:
            self.logger.warning("Registro SIP fallido")
    
    def on_call_connected(self, call: SIPCall) -> None:
        """Callback de llamada conectada"""
        call_id = call.getId()
        self.logger.info(f"Llamada conectada: {call_id}")
        
        if self.on_call_connected_callback:
            asyncio.create_task(self.on_call_connected_callback(call))
    
    def on_call_ended(self, call: SIPCall) -> None:
        """Callback de llamada terminada"""
        call_id = call.getId()
        self.logger.info(f"Llamada terminada: {call_id}")
        
        # Remover de llamadas activas
        if call_id in self.active_calls:
            del self.active_calls[call_id]
        
        if self.on_call_ended_callback:
            asyncio.create_task(self.on_call_ended_callback(call))
    
    def on_incoming_call(self, call: SIPCall) -> None:
        """Callback de llamada entrante"""
        call_id = call.getId()
        self.logger.info(f"Llamada entrante: {call_id}")
        
        self.active_calls[call_id] = call
        
        if self.on_incoming_call_callback:
            asyncio.create_task(self.on_incoming_call_callback(call))
    
    def on_call_media_state(self, call: SIPCall, state: int) -> None:
        """Callback de estado de media"""
        call_id = call.getId()
        self.logger.debug(f"Estado de media para llamada {call_id}: {state}")
    
    # Configuración de callbacks
    def set_call_connected_callback(self, callback: Callable) -> None:
        """Establece callback para llamadas conectadas"""
        self.on_call_connected_callback = callback
    
    def set_call_ended_callback(self, callback: Callable) -> None:
        """Establece callback para llamadas terminadas"""
        self.on_call_ended_callback = callback
    
    def set_incoming_call_callback(self, callback: Callable) -> None:
        """Establece callback para llamadas entrantes"""
        self.on_incoming_call_callback = callback
    
    async def shutdown(self) -> None:
        """Cierra el servicio SIP"""
        try:
            # Colgar todas las llamadas activas
            for call_id in list(self.active_calls.keys()):
                await self.hangup_call(call_id)
            
            # Destruir endpoint
            if self.endpoint:
                self.endpoint.libDestroy()
            
            self.logger.info("Servicio SIP cerrado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error cerrando servicio SIP: {e}") 