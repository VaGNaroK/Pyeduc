"""
Ponto de entrada do aplicativo Pyeduc.
"""
import os
import sys
import ssl
from pathlib import Path

# Correção para o erro SSL: CERTIFICATE_VERIFY_FAILED restrita ao Windows
# Necessário porque o urllib interno do Python no Windows às vezes falha ao
# verificar o certificado ao baixar o flet-desktop (cliente do Flet).
if sys.platform == "win32":
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

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
    logger.info("FLET ENV VARS: %s", {k: v for k, v in os.environ.items() if "FLET" in k})
    # Verifica dependências (banco de dados)
    pm = ProgressManager()
    
    # Inicia a interface gráfica do Flet
    from gui import main_app
    project_root = str(Path(__file__).parent.parent)
    assets_path = str(Path(project_root) / "content")
    
    try:
        ft.run(main=main_app, assets_dir=assets_path)
    except Exception as e:
        logger.error(f"Erro ao iniciar Flet: {e}", exc_info=True)

if __name__ == "__main__":
    main()
