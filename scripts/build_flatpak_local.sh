#!/bin/bash
set -e

echo "🚀 Iniciando compilação e empacotamento local do Flatpak Pyeduc..."

# 1. Verificar dependências necessárias
command -v flatpak >/dev/null 2>&1 || { echo "❌ Erro: 'flatpak' não está instalado no seu sistema."; exit 1; }
command -v flatpak-builder >/dev/null 2>&1 || { echo "❌ Erro: 'flatpak-builder' não está instalado no seu sistema."; exit 1; }

# Resolver comando do Flet CLI (PATH ou venv)
if command -v flet >/dev/null 2>&1; then
    FLET_CMD="flet"
elif [ -f "./venv/bin/flet" ]; then
    FLET_CMD="./venv/bin/flet"
elif [ -f "./.venv/bin/flet" ]; then
    FLET_CMD="./.venv/bin/flet"
else
    FLET_CMD="python3 -m flet"
fi

echo "ℹ️ Utilizando comando Flet: $FLET_CMD"

# 2. Configurar repositório Flathub no escopo do usuário se não existir
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# 3. Compilar a aplicação Linux via Flet caso build/linux não exista
if [ ! -d "build/linux" ]; then
    echo "🧹 Limpando diretórios __pycache__ anteriores..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo "📦 Compilando binários Linux via Flet ($FLET_CMD)..."
    $FLET_CMD build linux --module-name main --exclude .git .github .agents venv .venv data logs __pycache__ "*.pyc" "*.pyo" tests scripts flatpak "*.txt" "*.bat" "*.sh" "*.md" build-dir .flatpak-builder --project pyeduc
fi

# 4. Construir a estrutura Flatpak
echo "🛠️ Construindo diretório Flatpak via flatpak-builder..."
flatpak-builder --user --disable-rofiles-fuse --install-deps-from=flathub --force-clean build-dir flatpak/org.pyeduc.App.yml

# 5. Exportar repositório e gerar o pacote .flatpak standalone
echo "📦 Exportando repositório e gerando arquivo pyeduc.flatpak..."
flatpak build-export repo build-dir
flatpak build-bundle repo pyeduc.flatpak org.pyeduc.App

# 6. Instalar localmente para teste imediato
echo "📥 Instalando/Atualizando o Flatpak no ambiente local (--user)..."
flatpak install --user --reinstall -y pyeduc.flatpak || flatpak install --user -y pyeduc.flatpak

echo ""
echo "✅ Empacotamento e instalação local do Flatpak concluídos!"
echo ""
echo "----------------------------------------------------------------------"
echo "🛠️ GUIA DE DEBUGGING LOCAL DO FLATPAK:"
echo "----------------------------------------------------------------------"
echo "1. Executar a aplicação Flatpak instalada:"
echo "   flatpak run org.pyeduc.App"
echo ""
echo "2. Inspecionar o ambiente/arquivos dentro da Sandbox Flatpak via BASH:"
echo "   flatpak run --command=bash org.pyeduc.App"
echo ""
echo "3. Verificar arquivos instalados em /app/opt/pyeduc/ na Sandbox:"
echo "   flatpak run --command=ls org.pyeduc.App -la /app/opt/pyeduc/content/"
echo ""
echo "4. Inspecionar variáveis de ambiente e caminhos no Sandbox:"
echo "   flatpak run --command=env org.pyeduc.App"
echo ""
echo "5. Ver o log da aplicação gravado no banco/home:"
echo "   cat ~/.pyeduc/pyeduc.db"
echo "----------------------------------------------------------------------"
