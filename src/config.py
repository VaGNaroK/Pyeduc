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

# Configurações do Tutor Ollama (IA Local)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_DEFAULT_MODEL = "qwen2.5-coder:3b"  # Modelo recomendado (~2.2GB VRAM), raciocínio muito superior sem alucinações


OLLAMA_TIMEOUT = 30  # segundos
MAX_CHAT_HISTORY = 50
OLLAMA_KEEP_ALIVE = "-1m"  # Mantém o modelo residente na VRAM/RAM indefinidamente (evita unload por idle)


