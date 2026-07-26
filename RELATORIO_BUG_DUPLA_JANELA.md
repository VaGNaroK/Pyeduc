# Relatório Técnico: Bug da Dupla Janela GTK no Flatpak (Pyeduc / Flet / Serious Python)

Este documento descreve detalhadamente a arquitetura do projeto **Pyeduc**, o diagnóstico do bug de janelas duplicadas ao empacotar via Flatpak, o histórico de tentativas de correção na raiz do código fonte e as perguntas específicas para análise por outra inteligência artificial ou desenvolvedor sênior.

---

## 1. Arquitetura do Projeto

O **Pyeduc** é uma aplicação desktop educacional desenvolvida em **Python** utilizando **Flet** para a camada visual e empacotada para Linux via **Flatpak**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Flatpak Sandbox (Linux)                         │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Flutter C++ Engine (Host)                     │  │
│  │                    (Binário: /app/opt/pyeduc/pyeduc)             │  │
│  │                                                                  │  │
│  │   ┌──────────────────────────────────────────────────────────┐   │  │
│  │   │     Plugin: serious_python_linux (CPython 3.14)          │   │  │
│  │   │                                                          │   │  │
│  │   │   ┌──────────────────────────────────────────────────┐   │   │  │
│  │   │   │ Python Code: main.py -> src/main.py -> gui.py    │   │   │  │
│  │   │   │ (Roda servidor WebSocket interno flet_runtime)   │   │   │  │
│  │   │   └────────────────────────┬─────────────────────────┘   │   │  │
│  │   └────────────────────────────┼─────────────────────────────┘   │  │
│  │                                │ (Conexão IPC/Socket Local)      │  │
│  └────────────────────────────────┴─────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### Componentes Principais:
1. **Frontend Visual**: Flet (framework Python que conecta o estado dos controles Python ao motor C++/Dart do Flutter).
2. **Interpretador Embarcado**: `serious_python` (compila o código Python em um bundle `app.zip` e executa um interpretador CPython embarcado `libpython3.14.so` dentro do processo C++ do Flutter).
3. **Ponto de Entrada**:
   - Raiz: `main.py`
   - Aplicação: `src/main.py`
   - GUI Monolítica: `src/gui.py`
4. **Manifesto Flatpak**: `flatpak/org.pyeduc.App.yml`
5. **Script de Compilação Local**: `scripts/build_flatpak_local.sh`

---

## 2. O Bug da "Dupla Janela" (Dual GTK Window Issue)

### Sintomas Observados no Linux:
Ao executar o aplicativo compilado via Flatpak (`flatpak run org.pyeduc.App`):
1. **Janela #1 (Trás / Fundo)**: Título `"Pyeduc"`, fundo cinza/branco sem controles visíveis.
2. **Janela #2 (Frente)**: Título `"Pyeduc - App Educacional Python"`, contendo a tela de login/aulas.
3. **Falha ao fechar a Janela #1**: Se o usuário fechar a Janela #1 ("Pyeduc"), o processo backend Python é encerrado. A Janela #2 permanece aberta, porém congela e perde a capacidade de responder a cliques ou carregar aulas (disparando erro `IndexError` ou estancando a interface).

---

## 3. Análise da Causa Raiz (Internas do `flet_runtime`)

A biblioteca `flet_runtime` (pacote Python oficial do Flet) gerencia o servidor WebSocket local e o ciclo de vida do cliente visual.

### Trechos Relevantes do Código Fonte da Biblioteca `flet_runtime`:

#### A. Checagem de Ambiente Embarcado (`flet_runtime/utils/__init__.py`):
```python
def is_embedded():
    return os.getenv("FLET_PLATFORM") is not None
```

#### B. Decisão de Abertura de Janela (`flet_runtime/app.py`):
```python
is_socket_server = (
    is_embedded() or view == AppView.FLET_APP or view == AppView.FLET_APP_HIDDEN
) and not force_web_server

...

if (
    (
        view == AppView.FLET_APP
        or view == AppView.FLET_APP_HIDDEN
        or view == AppView.FLET_APP_WEB
    )
    and not force_web_server
    and not is_embedded()   # <--- AQUI ESTÁ O GATILHO!
    and url_prefix is None
):
    fvp, pid_file = await open_flet_view_async(
        conn.page_url,
        assets_dir if view != AppView.FLET_APP_WEB else None,
        view == AppView.FLET_APP_HIDDEN,
    )
```

### O Mecanismo da Falha:
1. Quando o Flatpak inicia, o SO cria a **Janela #1** (a janela C++ nativa do Flutter).
2. O Flutter inicia o interpretador CPython embarcado e executa o código Python `main.py`.
3. O Flet Python runtime executa a função `app_async()`.
4. Se a variável `FLET_PLATFORM` estiver **ausente/nula**:
   - `is_embedded()` retorna `False`.
   - A condição `and not is_embedded()` é avaliada como `True`.
   - O `flet_runtime` assume que está rodando como um script Python independente no terminal e executa `open_flet_view_async()`.
   - `open_flet_view_async()` lança um **subprocesso OS** executando o binário cliente `/app/opt/pyeduc/pyeduc <socket_url>`.
5. Esse subprocesso gera a **Janela #2**, que conecta no socket da Janela #1 e altera o título da Janela #2 para `"Pyeduc - App Educacional Python"`.

---

## 4. Histórico de Tentativas de Correção e Descobertas

| Tentativa | Local da Modificação | Ação Realizada | Resultado | Motivo da Falha |
|---|---|---|---|---|
| **1** | `src/main.py` (função `main()`) | Adicionado `os.environ["FLET_PLATFORM"] = "linux"` antes de `ft.app()` | ❌ Falhou (Ainda abria 2 janelas) | `import flet as ft` ocorria no topo de `src/main.py`. A biblioteca `flet_runtime` lia o estado das variáveis de ambiente durante a importação do módulo, antes da função `main()` rodar. |
| **2** | `src/main.py` (topo) | Mover a checagem e atribuição de `FLET_PLATFORM` para o topo do arquivo | ❌ Falhou (Ainda abria 2 janelas) | O ponto de entrada primário do Serious Python é o `main.py` na **raiz do repositório**, que importava `src/main.py` posteriormente. |
| **3** | `main.py` (raiz), `src/main.py`, `src/gui.py` | Injetar a checagem `if "FLATPAK_ID" in os.environ:` no topo de todos os pontos de entrada Python | ⚠️ Parcial | Depender de condicionais Python no runtime pode falhar se alguma variável de ambiente da sandbox não for populada a tempo ou se a condição de detecção falhar. |
| **4 (Atual)** | `flatpak/org.pyeduc.App.yml` | Adicionado `- --env=FLET_PLATFORM=linux` nas `finish-args` do manifesto Flatpak | ✅ Sucesso | A sandbox do Flatpak injeta a variável no ambiente do processo antes mesmo do binário Flutter C++ ou CPython inicializarem. |

---

## 5. Resumo da Solução Atual Aplicada

### 1. Manifesto Flatpak (`flatpak/org.pyeduc.App.yml`)
```yaml
app-id: org.pyeduc.App
runtime: org.freedesktop.Platform
runtime-version: '24.08'
sdk: org.freedesktop.Sdk
command: pyeduc
finish-args:
  - --share=network
  - --socket=x11
  - --socket=wayland
  - --device=dri
  - --env=FLET_PLATFORM=linux    # <--- Garante que o processo pai receba a variável nativamente
```

### 2. Ponto de Entrada Raiz (`main.py`)
```python
import os
import sys
from pathlib import Path

# Configura FLET_PLATFORM no topo absoluto do ponto de entrada principal se estiver empacotado
is_serious_python = (
    "FLATPAK_ID" in os.environ
    or "container" in os.environ
    or "/opt/pyeduc" in str(Path(__file__).resolve())
    or "/opt/pyeduc" in sys.executable
    or "serious_python" in str(Path(__file__).resolve())
    or os.environ.get("FLET_SERIOUS_PYTHON") == "true"
    or (not sys.executable.endswith("python") and not sys.executable.endswith("python3"))
)
if is_serious_python:
    os.environ["FLET_PLATFORM"] = "linux"
```

### 3. Remoção do Bug de Renderização de Texto (`src/gui.py`)
Adicionalmente, identificou-se que a propriedade `md_style_sheet=md_style` em `ft.Markdown` causava falha silenciosa de deserialização de estilos no Flutter Desktop SDK. A remoção de `md_style_sheet` restaurou a exibição do texto em Markdown das lições.

---

## 6. Questões para Segunda Opinião de IA / Peer Review

Solicitamos uma análise crítica de outro agente de IA ou especialista nos seguintes pontos:

1. **Abordagem de Empacotamento**: A inclusão de `--env=FLET_PLATFORM=linux` no manifesto Flatpak (`finish-args`) é considerada a melhor prática para projetos Flet empacotados com Serious Python no Linux, ou existe um parâmetro nativo na CLI do Flet (`flet build linux`) que deveria fazer isso automaticamente?
2. **Ordem de Inicialização do Flet**: Por que o Flet CLI não injeta `FLET_PLATFORM` no `main.py` gerado durante a etapa de bundling do `serious_python`?
3. **Efeitos Colaterais**: Existe algum impacto secundário conhecido ao definir `FLET_PLATFORM=linux` em um ambiente Desktop Linux empacotado que deva ser monitorado (ex: comportamento de diálogos, barras de janela ou webviews)?
4. **Resiliência da Solução**: A estrutura atual de pontos de entrada (`main.py` na raiz -> `src/main.py` -> `src/gui.py`) com injeção defensiva de variáveis no topo é robusta contra regressões em futuros updates do Flet?

---

*Relatório gerado em 26 de Julho de 2026 para auditoria do projeto Pyeduc.*
