#!/usr/bin/env python3
"""
Punto de entrada principal del Sistema de Llamadas SIP con IA
"""

import asyncio
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main

if __name__ == "__main__":
    asyncio.run(main()) 