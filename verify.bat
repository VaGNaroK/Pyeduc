@echo off
REM Script de verificação da estrutura do projeto Pyeduc

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║    VERIFICAÇÃO DA ESTRUTURA - Pyeduc Project           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

setlocal enabledelayedexpansion

set "found_count=0"
set "missing_count=0"

REM Função para verificar arquivo
echo Verificando estrutura de diretórios...
echo.

REM Verificar diretórios
if exist "src\" (
    echo ✅ src/ - OK
    set /a found_count+=1
) else (
    echo ❌ src/ - FALTANDO
    set /a missing_count+=1
)

if exist "content\" (
    echo ✅ content/ - OK
    set /a found_count+=1
) else (
    echo ❌ content/ - FALTANDO
    set /a missing_count+=1
)

if exist "data\" (
    echo ✅ data/ - OK
    set /a found_count+=1
) else (
    echo ❌ data/ - FALTANDO
    set /a missing_count+=1
)

echo.
echo Verificando arquivos críticos...
echo.

REM Arquivos Python
for %%f in (
    "src\main.py"
    "src\gui.py"
    "src\communication.py"
    "src\executor.py"
    "src\content_manager.py"
    "src\progress_manager.py"
    "src\config.py"
) do (
    if exist %%f (
        echo ✅ %%f - OK
        set /a found_count+=1
    ) else (
        echo ❌ %%f - FALTANDO
        set /a missing_count+=1
    )
)

echo.
echo Verificando conteúdo...
echo.

if exist "content\lessons.json" (
    echo ✅ content\lessons.json - OK
    set /a found_count+=1
) else (
    echo ❌ content\lessons.json - FALTANDO
    set /a missing_count+=1
)

echo.
echo Verificando documentação...
echo.

for %%f in (
    "README.md"
    "QUICKSTART.md"
    "INSTALL.md"
    "ARCHITECTURE.md"
    "INDEX.md"
    "PROJECT_SUMMARY.md"
) do (
    if exist %%f (
        echo ✅ %%f - OK
        set /a found_count+=1
    ) else (
        echo ⚠️  %%f - FALTANDO
    )
)

echo.
echo Verificando scripts...
echo.

if exist "run.bat" (
    echo ✅ run.bat - OK
    set /a found_count+=1
) else (
    echo ❌ run.bat - FALTANDO
    set /a missing_count+=1
)

if exist "requirements.txt" (
    echo ✅ requirements.txt - OK
    set /a found_count+=1
) else (
    echo ❌ requirements.txt - FALTANDO
    set /a missing_count+=1
)

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║    RESULTADO FINAL                                       ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo Arquivos encontrados: !found_count!
echo Arquivos faltando: !missing_count!
echo.

if !missing_count! equ 0 (
    echo ✅ ESTRUTURA COMPLETA E VÁLIDA!
    echo.
    echo Próximos passos:
    echo   1. pip install -r requirements.txt
    echo   2. python src/main.py
    echo.
    exit /b 0
) else (
    echo ❌ ESTRUTURA INCOMPLETA!
    echo.
    echo Arquivos faltando: !missing_count!
    echo Por favor, recrie o projeto.
    echo.
    exit /b 1
)

pause
