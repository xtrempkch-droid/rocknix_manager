#!/bin/bash

# Script de instalação para Rocknix Manager
# Este script configura o ambiente Python e instala as dependências

# Cores para o terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # Sem cor

echo -e "${BLUE}=== Rocknix Manager: Iniciando Instalação ===${NC}"

# 1. Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Erro: Python 3 não encontrado. Por favor, instale o Python 3.${NC}"
    exit 1
fi

# 2. Verificar se o arquivo requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Erro: Arquivo requirements.txt não encontrado no diretório atual.${NC}"
    exit 1
fi

# 3. Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Criando ambiente virtual (venv)...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Erro ao criar venv. Verifique se possui o pacote python3-venv instalado.${NC}"
        exit 1
    fi
fi

# 4. Ativar venv e instalar dependências
echo -e "${BLUE}Ativando ambiente virtual e atualizando PIP...${NC}"
source venv/bin/activate

pip install --upgrade pip

echo -e "${BLUE}Instalando dependências...${NC}"
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dependências instaladas com sucesso!${NC}"
else
    echo -e "${RED}Erro ao instalar dependências. Verifique sua conexão ou o arquivo requirements.txt.${NC}"
    exit 1
fi

# 5. Configurar permissões de execução
echo -e "${BLUE}Configurando permissões de execução...${NC}"
if [ -f "main.py" ]; then
    chmod +x main.py
fi

echo -e "${GREEN}=== Instalação Concluída ===${NC}"
echo -e "Para iniciar o programa, use:"
echo -e "${BLUE}source venv/bin/activate && python main.py${NC}"
