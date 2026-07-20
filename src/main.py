"""
Ponto de entrada do aplicativo Pyeduc.
"""
import sys
from pathlib import Path
import flet as ft

# Adiciona o diretório src ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

from config import *
from progress_manager import ProgressManager
from logger import logger

# Configura exceção global hook
def exception_handler(exctype, value, traceback):
    logger.error("Uncaught exception", exc_info=(exctype, value, traceback))

sys.excepthook = exception_handler

def main():
    logger.info("Aplicativo Pyeduc iniciado.")
    # Verifica dependências (banco de dados)
    pm = ProgressManager()
    
    # Inicia a interface gráfica do Flet
    from gui import main_app
    project_root = str(Path(__file__).parent.parent)
    
    try:
        ft.run(main_app, assets_dir=project_root)
    except Exception as e:
        logger.error(f"Erro ao iniciar Flet: {e}", exc_info=True)

if __name__ == "__main__":
    main()
