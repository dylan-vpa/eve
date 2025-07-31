#!/usr/bin/env python3
"""
Script de prueba para verificar las APIs de Deepgram y ElevenLabs
antes de ejecutar el sistema principal.
"""

import os
import asyncio
import aiohttp
import tempfile
import wave
import numpy as np
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID")

async def test_deepgram():
    """Prueba la API de Deepgram con un archivo de audio de prueba"""
    print("🔍 Probando Deepgram API...")
    
    if not DEEPGRAM_API_KEY:
        print("❌ DEEPGRAM_API_KEY no configurada")
        return False
    
    try:
        # Crear un archivo de audio de prueba (tono de 1kHz por 2 segundos)
        sample_rate = 16000
        duration = 2.0
        frequency = 1000
        
        # Generar tono
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Guardar como WAV
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            # Enviar a Deepgram
            headers = {
                'Authorization': f'Token {DEEPGRAM_API_KEY}',
                'Content-Type': 'audio/wav'
            }
            
            async with aiohttp.ClientSession() as session:
                with open(temp_file.name, 'rb') as audio_file:
                    async with session.post(
                        'https://api.deepgram.com/v1/listen',
                        headers=headers,
                        data=audio_file
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            print("✅ Deepgram API funciona correctamente")
                            print(f"   Respuesta: {result}")
                            return True
                        else:
                            print(f"❌ Error en Deepgram: {response.status}")
                            return False
                            
    except Exception as e:
        print(f"❌ Error probando Deepgram: {e}")
        return False

async def test_elevenlabs():
    """Prueba la API de ElevenLabs generando audio de prueba"""
    print("🎤 Probando ElevenLabs API...")
    
    if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
        print("❌ ELEVENLABS_API_KEY o ELEVENLABS_VOICE_ID no configuradas")
        return False
    
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        
        headers = {
            'Accept': 'audio/mpeg',
            'Content-Type': 'application/json',
            'xi-api-key': ELEVENLABS_API_KEY
        }
        
        data = {
            'text': 'Hola, esta es una prueba del sistema de llamadas SIP con IA.',
            'model_id': 'eleven_monolingual_v1',
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.5
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    print("✅ ElevenLabs API funciona correctamente")
                    print(f"   Audio generado: {len(audio_data)} bytes")
                    
                    # Guardar archivo de prueba
                    with open('test_audio.mp3', 'wb') as f:
                        f.write(audio_data)
                    print("   Archivo guardado como: test_audio.mp3")
                    return True
                else:
                    print(f"❌ Error en ElevenLabs: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error probando ElevenLabs: {e}")
        return False

async def test_sip_credentials():
    """Prueba las credenciales SIP básicas"""
    print("📞 Verificando credenciales SIP...")
    
    sip_host = os.environ.get("SIP_HOST")
    sip_username = os.environ.get("SIP_USERNAME")
    sip_password = os.environ.get("SIP_PASSWORD")
    
    if not all([sip_host, sip_username, sip_password]):
        print("❌ Credenciales SIP incompletas")
        print(f"   SIP_HOST: {sip_host}")
        print(f"   SIP_USERNAME: {sip_username}")
        print(f"   SIP_PASSWORD: {'*' * len(sip_password) if sip_password else 'No configurada'}")
        return False
    
    print("✅ Credenciales SIP configuradas")
    print(f"   Host: {sip_host}")
    print(f"   Usuario: {sip_username}")
    return True

async def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas de APIs...")
    print("=" * 50)
    
    # Probar credenciales SIP
    sip_ok = await test_sip_credentials()
    print()
    
    # Probar Deepgram
    deepgram_ok = await test_deepgram()
    print()
    
    # Probar ElevenLabs
    elevenlabs_ok = await test_elevenlabs()
    print()
    
    # Resumen
    print("=" * 50)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"   SIP: {'✅' if sip_ok else '❌'}")
    print(f"   Deepgram: {'✅' if deepgram_ok else '❌'}")
    print(f"   ElevenLabs: {'✅' if elevenlabs_ok else '❌'}")
    
    if all([sip_ok, deepgram_ok, elevenlabs_ok]):
        print("\n🎉 Todas las APIs funcionan correctamente!")
        print("   Puedes ejecutar: python3 main.py")
    else:
        print("\n⚠️  Algunas APIs fallaron. Revisa la configuración.")
        print("   Verifica las variables de entorno en .env")

if __name__ == "__main__":
    asyncio.run(main()) 