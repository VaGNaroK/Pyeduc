"""
Ponto de entrada do aplicativo Pyeduc para empacotamento Serious Python / Flatpak.
"""
import os
import sys
from pathlib import Path

# ============================================================================
# 1. INJEÇÃO DEFENSIVA ABSOLUTA (SEM CONDICIONAIS, SEM ESPAÇOS)
# Deve ocorrer ANTES de qualquer importação do flet
# ============================================================================
os.environ["FLET_PLATFORM"] = "linux"
os.environ["FLET_EMBEDDED"] = "true"

# ============================================================================
# 2. CONFIGURAÇÃO DE PATH
# ============================================================================
sys.path.insert(0, str(Path(__file__).parent))

# ============================================================================
# 3. HANDLER DE EXCEÇÕES GLOBAIS
# ============================================================================
try:
    from logger import logger
    def exception_handler(exctype, value, traceback):
        logger.error("Uncaught exception", exc_info=(exctype, value, traceback))
    sys.excepthook = exception_handler
except ImportError:
    pass

# ============================================================================
# 4. DELEGAÇÃO PARA O MÓDULO PRINCIPAL
# NOTA: NÃO chamamos ft.app() aqui.
# ============================================================================
from src.main import main as app_main

if __name__ == "__main__":
    app_main()