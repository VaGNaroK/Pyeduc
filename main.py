"""
Ponto de entrada raiz do aplicativo Pyeduc para Flet CLI e executáveis.
"""
import sys
from pathlib import Path

# Adiciona o diretório src ao path para carregar a aplicação
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from main import main

if __name__ == "__main__":
    main()
