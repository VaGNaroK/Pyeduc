# AGENTS.md

## Quick Start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Architecture

Flet (Flutter-based GUI) educational app. 5-layer structure:

| Layer | File | Role |
|-------|------|------|
| GUI | `src/main_window.py` | PyeducApp class orchestrates UI components in `src/ui/` |
| Communication | `src/communication.py` | Callbacks bridging GUI ↔ Executor |
| Execution | `src/executor.py` | Persistent Python subprocess (`PersistentPythonShell`) |
| Content | `src/content_manager.py` | Loads `content/lessons.json` |
| Persistence | `src/progress_manager.py` | SQLite at `data/pyeduc.db` |
| Config | `src/config.py` | Constants (window size, timeout, admin flag) |

Entry point: `src/main.py` → `flet.app(target=main_app)`

## Key Quirks

- **Componentized GUI**: `main_window.py` orchestrates OOP classes from `src/ui/` instead of a monolithic file.
- **Persistent subprocess**: `executor.py` keeps a running Python REPL subprocess with custom delimiters (`---CMD-BOUND-OUT---`) to capture output. Not a fresh subprocess per execution.
- **SQLite, not JSON**: `progress_manager.py` uses SQLite (`data/pyeduc.db`), despite ARCHITECTURE.md saying JSON. `data/progress.json` is a stale artifact.
- **Admin mode**: Login with `admin`/`admin` toggles admin mode (handled in `main_window.py`). Admin can navigate freely without completing lessons.
- **Auto-grader**: `main_window.py` (`on_exec_result`) checks exercise output against expected values using line-by-line matching.
- **UI Tests**: Pytest suite exists in `tests/test_ui_components.py` ensuring UI and state stability.
- **No lint/typecheck**: No mypy, ruff, flake8, or pyproject.toml configured.

## Running & Building

```bash
# Development
python src/main.py

# Production build (Flet)
flet build windows --project pyeduc   # Windows
flet build linux --project pyeduc    # Linux

# DEB package
./scripts/build_deb.sh
```

CI (`.github/workflows/build.yml`) triggers on `v*` tags or manual dispatch. Builds Windows, Linux DEB, and Linux Flatpak.

## Content System

Lessons live in `content/lessons.json`. Each lesson has:
- `type`: `"presentation"` | `"theory"` | `"coding"` — controls which UI panels are visible
- `quiz`: Object with `question`, `options`, `answer` (index or list for multi-select)
- `exercises`: Array with `description` and `expected_output` for auto-grading
- Lessons are locked sequentially unless admin mode is on

## File Structure Gotchas

- Two venvs exist: `venv/` and `.venv/` — prefer `venv/`
- `old_chunk.txt` is stale/leftover
- `Pyeduc.7z` is a distributable archive
- `.gitignore` excludes `data/progress.json` but NOT `data/pyeduc.db` (add if committing)
- `ARCHITECTURE.md` references PyQt signals — outdated, app uses Flet callbacks
- **Ollama AI Tutor (`src/llm_client.py`)**: Local REST API integration, `OLLAMA_KEEP_ALIVE="-1m"` while open, auto-unloads from VRAM (`keep_alive: 0` via `unload_model()`) when app closes. Recommended models: `qwen2.5-coder:3b` / `1.5b`.

- **Educational Guardrails (`src/tutor_guardrails.py`)**: Deterministic static error analysis for `NameError`, `SyntaxError`, `IndentationError`, `TypeError`, `ZeroDivisionError`, strictly 3 Socratic topics with bold markdown, no code leakage.
- **Flet Threading (`src/ui/*`)**: Use `page.run_thread(fn)` instead of `threading.Thread(...)` for real-time background UI updates.
- **Tutor IA Chat Reset (`src/ui/tutor_panel.py`)**: `clear_chat()` must clear chat history on lesson transitions to prevent stale context.
- **ProgressManager Username (`src/progress_manager.py`)**: Use `progress_manager.get_current_username()` to fetch current logged-in username.
- **High Contrast Console UI**: `console_input` uses `#38bdf8` (Cyan) border, `console_output_container` uses `#10b981` (Emerald) border with `#0f172a` outer container.
- **Popup Modal Responsiveness**: Inner Columns inside `ft.AlertDialog` must declare `tight=True` (`ft.Column([..., tight=True])`) to fit content height dynamically.
- **Flatpak/serious_python Subprocess Bug (Phantom Double Window)**: When spawning background Python REPLs (like in `executor.py`), **DO NOT** use `sys.executable` if `os.environ.get("FLET_EMBEDDED") == "true"`. In a `serious_python` bundle, `sys.executable` points to the C++ Flutter app itself. Using it will spawn a second instance of the GUI and cause `kInvalidArguments` crashes on exit. Fallback to `"python3"` manually.
- **ContentManager Instantiation (Flatpak Path Resolution)**: Never pass hardcoded relative paths like `ContentManager("content/lessons.json")` in `app_state.py`. This disables the internal fallback path mechanism required to find the JSON inside the Flatpak sandbox (`/app/opt/pyeduc/...`). Always instantiate with `ContentManager()` without arguments.
- **Visibilidade Condicional da Sidebar IA**: O painel do Tutor IA (`sidebar_ai_container`) deve ser visível exclusivamente em lições práticas (`sidebar_ai_container.visible = not is_theory and not is_presentation`), sendo ocultado em aulas teóricas e apresentações.

## 16. Prevenção de Falsos Positivos no Auto-Grader e Tutor IA
- **Auto-Grader Sequencial (`src/main_window.py`)**: A verificação de saída dos exercícios no console deve ser **Estritamente Sequencial**. É imperativo parar a checagem (fazer um `break`) no primeiro exercício pendente que não tiver sua saída confirmada no terminal. Isso previne o "Falso Positivo de Colisão", onde a saída do aluno completa erroneamente exercícios futuros.
- **Tutor IA - Regex de SyntaxError (`src/tutor_guardrails.py`)**: Para identificar strings sem aspas no `print()`, NÃO utilize regex negadas (`[^'"]`). Use grupos restritivos de caracteres (`[a-zA-ZÀ-ÿ_]+`) separados por espaços. A regex negada gera falsos positivos com expressões matemáticas válidas (ex: `print(a + b)`).
- **Tutor IA - Prompt Socrático (`src/tutor_guardrails.py`)**: NUNCA coloque exemplos hardcoded no *System Prompt*. Modelos compactos tendem a papagaiar/replicar a string do template. Utilize sempre placeholders dinâmicos (ex: `[Explique a regra...]`).
- **Tutor IA - Filtro de ANSI Escape (`src/executor.py`)**: Novas versões do Python (3.13+) injetam códigos OSC (`]633;...`) no terminal interativo. Ao invocar `subprocess.Popen` para o REPL, sempre injete as variáveis de ambiente `TERM="dumb"` e `PYTHON_BASIC_REPL="1"` para neutralizar essas decorações.

## 17. Tradução de Arquivos de Lições e Auto-Grader
- **Sincronia de `expected_output`**: Ao traduzir ou modularizar as lições (como `lessons_pt.json` para `lessons_en.json`), nunca preserve cegamente os campos `expected_output` se as descrições dos exercícios (`description`) sofrerem traduções de strings literais (ex: "Crie a variável com o valor 'Estudante'" -> "Create the variable with the value 'Student'"). O Auto-Grader usa `expected_output` para validar a saída no console do aluno. Se a string na descrição mudar, o `expected_output` DEVE ser ajustado para corresponder exatamente à nova expectativa em inglês, evitando quebras lógicas e falsos positivos no sistema de avaliação.

## 18. Tratamento de Estado Ausente (Sessão Deslogada)
- **Proteção contra `NoneType`**: Ao manipular variáveis interativas do progresso (como `current_lesson_idx` do `AppState` ou no recálculo em `update_footer`), **SEMPRE** utilize `if idx is not None` antes de engatilhar atualizações ou contas matemáticas da interface. Variáveis de sessão perdem seu valor `0` para se tornarem `None` no processo de Logout. Não injetar essas guardas provocará crashs como "Property has no setter" e "unsupported operand type(s) for +: 'NoneType' and 'int'".
