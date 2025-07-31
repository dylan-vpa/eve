#!/bin/bash

# Script para instalar PJSIP y pjsua2 desde la fuente
# Ejecutar en Ubuntu 20.04/22.04

set -e

echo "Instalando dependencias del sistema..."
sudo apt update
sudo apt install -y build-essential libssl-dev python3-dev libasound-dev portaudio19-dev

echo "Descargando PJSIP..."
cd /tmp
wget https://github.com/pjsip/pjproject/archive/refs/tags/2.13.tar.gz
tar -xzf 2.13.tar.gz
cd pjproject-2.13

echo "Configurando PJSIP..."
./configure --enable-shared --disable-sound --disable-resample --disable-video --disable-opencore-amr

echo "Compilando PJSIP..."
make dep && make

echo "Instalando PJSIP..."
sudo make install

echo "Configurando variables de entorno..."
echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
echo 'export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH' >> ~/.bashrc

echo "Instalando pjsua2 para Python..."
cd pjsip-apps/src/python
python3 setup.py build
sudo python3 setup.py install

echo "Verificando instalación..."
python3 -c "import pjsua2; print('PJSIP instalado correctamente')"

echo "Instalación completada. Reinicia tu terminal o ejecuta: source ~/.bashrc" 