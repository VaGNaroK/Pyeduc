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
| GUI | `src/gui.py` | Flet widgets, all UI in one function (`main_app`) |
| Communication | `src/communication.py` | Callbacks bridging GUI ↔ Executor |
| Execution | `src/executor.py` | Persistent Python subprocess (`PersistentPythonShell`) |
| Content | `src/content_manager.py` | Loads `content/lessons.json` |
| Persistence | `src/progress_manager.py` | SQLite at `data/pyeduc.db` |
| Config | `src/config.py` | Constants (window size, timeout, admin flag) |

Entry point: `src/main.py` → `flet.app(target=main_app)`

## Key Quirks

- **Single-file GUI**: `gui.py` is ~770 lines, all UI logic in one `main_app()` closure. No classes.
- **Persistent subprocess**: `executor.py` keeps a running Python REPL subprocess with custom delimiters (`---CMD-BOUND-OUT---`) to capture output. Not a fresh subprocess per execution.
- **SQLite, not JSON**: `progress_manager.py` uses SQLite (`data/pyeduc.db`), despite ARCHITECTURE.md saying JSON. `data/progress.json` is a stale artifact.
- **Admin mode**: Login with `admin`/`admin` toggles admin mode (hardcoded in `gui.py:209`). Admin can navigate freely without completing lessons.
- **Auto-grader**: `gui.py:316-353` checks exercise output against expected values using line-by-line matching.
- **No tests**: No test framework, no test files. `verify.bat` only checks file structure existence.
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
- **Flet Threading (`src/gui.py`)**: Use `page.run_thread(fn)` instead of `threading.Thread(...)` for real-time background UI updates.
- **Tutor IA Chat Reset (`src/gui.py`)**: `load_lesson()` must run `ai_chat_history.clear()`, `ai_chat_list.controls.clear()`, and `ai_input_field.value = ""` on lesson transitions to prevent stale context.
- **ProgressManager Username (`src/progress_manager.py`)**: Use `progress_manager.get_current_username()` to fetch current logged-in username.
- **High Contrast Console UI**: `console_input` uses `#38bdf8` (Cyan) border, `console_output_container` uses `#10b981` (Emerald) border with `#0f172a` outer container.
- **Popup Modal Responsiveness**: Inner Columns inside `ft.AlertDialog` must declare `tight=True` (`ft.Column([..., tight=True])`) to fit content height dynamically.


