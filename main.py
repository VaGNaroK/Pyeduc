"""
Ponto de entrada raiz do aplicativo Pyeduc para Flet CLI e executáveis.
"""
import os
import sys
from pathlib import Path

# Configura FLET_PLATFORM no topo absoluto do ponto de entrada principal se estiver empacotado
is_serious_python = (
    "FLATPAK_ID" in os.environ
    or "/opt/pyeduc" in str(Path(__file__).resolve())
    or "/opt/pyeduc" in sys.executable
    or "serious_python" in str(Path(__file__).resolve())
    or os.environ.get("FLET_SERIOUS_PYTHON") == "true"
    or (not sys.executable.endswith("python") and not sys.executable.endswith("python3"))
)
if is_serious_python:
    os.environ["FLET_PLATFORM"] = "linux"

# Adiciona o diretório src ao path para carregar a aplicação
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from main import main

if __name__ == "__main__":
    main()
