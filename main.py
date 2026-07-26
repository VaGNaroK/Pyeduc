"""
Ponto de entrada do aplicativo Pyeduc para empacotamento Serious Python / Flatpak.
Este arquivo configura o ambiente e delega a execução para src/main.py.
"""
import os
import sys
from pathlib import Path

# ============================================================================
# INJEÇÃO DEFENSIVA ABSOLUTA DE VARIÁVEIS DE AMBIENTE
# Deve ocorrer ANTES de qualquer importação do flet
# ============================================================================
os.environ["FLET_PLATFORM"] = "linux"
os.environ["FLET_EMBEDDED"] = "true"

# ============================================================================
# CONFIGURAÇÃO DE PATH
# ============================================================================
sys.path.insert(0, str(Path(__file__).parent))

# ============================================================================
# CONFIGURAÇÃO DE HANDLER DE EXCEÇÕES GLOBAIS
# ============================================================================
try:
    from logger import logger
    
    def exception_handler(exctype, value, traceback):
        logger.error("Uncaught exception", exc_info=(exctype, value, traceback))
    
    sys.excepthook = exception_handler
except ImportError:
    pass

# ============================================================================
# IMPORTAÇÃO E EXECUÇÃO DA APLICAÇÃO PRINCIPAL
# ============================================================================
from src.main import main as app_main

if __name__ == "__main__":
    app_main()
