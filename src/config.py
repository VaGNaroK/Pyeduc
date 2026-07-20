"""
Configurações da aplicação Pyeduc
"""

# Caminho para os arquivos de conteúdo
CONTENT_FILE = "content/lessons.json"

# Caminho para o diretório de dados (progresso)
DATA_DIR = "data"

# Configurações de execução
PYTHON_EXECUTOR_TIMEOUT = 5  # segundos

# Configurações de UI
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Pyeduc - App Educacional Python"

# Proporções do QSplitter (vertical)
SPLITTER_RATIO_TOP = 3  # Conteúdo da lição (60%)
SPLITTER_RATIO_BOTTOM = 2  # Console Python (40%)

# Estilos de cor
THEME = {
    "code_editor_bg": "#2b2b2b",
    "code_editor_fg": "#f8f8f2",
    "console_bg": "#1e1e1e",
    "console_fg": "#00ff00",
    "font_family": "Courier New",
}

# Configurações de fonte
FONTS = {
    "title": 16,
    "subtitle": 11,
    "default": 10,
    "console": 9,
}

# Configurações de Teste/Admin
ADMIN_MODE = False
