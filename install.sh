#!/bin/bash
# Script de instalação automatizada para Rocknix Manager

set -e

REPO_URL="https://github.com/xtrempkch-droid/rocknix_manager.git"
TARGET_DIR="$HOME/rocknix_manager"

echo "------------------------------------------"
echo "  Rocknix Manager - Setup Tool"
echo "------------------------------------------"

# Verificar se o Git está instalado
if ! command -v git &> /dev/null; then
    echo "❌ Erro: Git não encontrado. Por favor, instale o git."
    exit 1
fi

# Clonar ou Atualizar
if [ -d "$TARGET_DIR" ]; then
    echo "📂 Pasta detectada. Atualizando arquivos..."
    cd "$TARGET_DIR"
    git pull
else
    echo "📥 Clonando repositório..."
    git clone "$REPO_URL" "$TARGET_DIR"
    cd "$TARGET_DIR"
fi

# Configurar Python VENV
echo "🐍 Configurando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Caso o arquivo não exista, instala as básicas do seu projeto
    pip install requests pillow
fi

echo ""
echo "✅ Instalação concluída com sucesso!"
echo "------------------------------------------"
echo "Para rodar o programa:"
echo "cd ~/rocknix_manager && source venv/bin/activate && python3 main.py"
echo "------------------------------------------"
