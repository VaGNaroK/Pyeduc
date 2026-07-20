@echo off
REM Script para executar o Pyeduc no Windows

echo.
echo ================================
echo   Pyeduc - App Educacional
echo ================================
echo.

REM Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Erro: Python não encontrado no PATH
    echo Instale Python 3.8+ de https://www.python.org
    pause
    exit /b 1
)

REM Cria ambiente virtual se não existir
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

REM Ativa ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instala dependências
echo Instalando dependências...
pip install -q -r requirements.txt

REM Executa a aplicação
echo.
echo Iniciando Pyeduc...
echo.
python src/main.py

pause
