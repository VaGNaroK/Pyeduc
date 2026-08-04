#!/bin/bash

# Script para executar o Pyeduc no macOS/Linux

echo ""
echo "================================"
echo "  Pyeduc - App Educacional"
echo "================================"
echo ""

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python 3 não encontrado"
    echo "Instale Python 3.8+ de https://www.python.org"
    exit 1
fi

# Cria ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativa ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Instala dependências
echo "Instalando dependências..."
pip install -q -r requirements.txt

# Executa a aplicação
echo ""
echo "Iniciando Pyeduc..."
echo ""
python3 src/main.py
