#!/bin/bash

echo "🚀 Iniciando Instalação do ROCKNIX Manager v0.1..."

# 1. Atualizar e instalar dependências do sistema
echo "📦 Instalando dependências do sistema (sudo pode ser solicitado)..."
if [ -f /etc/debian_version ]; then
    sudo apt update
    sudo apt install -y python3-pip python3-pyqt6 7zip libretro-common-dat gvfs-bin smbclient
elif [ -f /etc/fedora-release ]; then
    sudo dnf install -y python3-pip python3-pyqt6 7zip gvfs-smb
fi

# 2. Instalar bibliotecas Python
echo "🐍 Instalando bibliotecas Python..."
pip3 install -r requirements.txt

# 3. Dar permissão de execução
chmod +x rocknix_manager.py

echo "✅ Instalação concluída!"
echo "Para abrir o app, use: ./rocknix_manager.py"
