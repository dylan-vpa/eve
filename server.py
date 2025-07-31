#!/usr/bin/env python3
"""
Punto de entrada para el servidor API del Sistema de Llamadas SIP con IA
Ejecuta el servidor en el puerto 8000
"""

import asyncio
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.server import run_server

def main():
    """Función principal para ejecutar el servidor"""
    print("🚀 SISTEMA DE LLAMADAS SIP CON IA - SERVIDOR API")
    print("================================================")
    print("📡 Servidor ejecutándose en: http://localhost:8000")
    print("📚 Documentación: http://localhost:8000/docs")
    print("🔍 Estado del sistema: http://localhost:8000/health")
    print("📞 Gestión de llamadas: http://localhost:8000/calls")
    print("")
    print("🛑 Para detener: Ctrl+C")
    print("")
    
    # Ejecutar el servidor
    run_server(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main() 