# Guia de Contribuição - Pyeduc 🚀

Obrigado por seu interesse em contribuir com o **Pyeduc**! Este documento orienta desenvolvedores e instrutores sobre a arquitetura do projeto, ambiente de desenvolvimento, padrões de código e diretrizes para criação de novas lições.

**Toda e qualquer forma de contribuição é muito bem-vinda!** Sejam ideias, correções ou códigos enviados por desenvolvedores iniciantes, experientes ou até mesmo gerados por agentes de Inteligência Artificial (desde que o código seja previamente testado e validado antes do envio).

---

## 🏗️ 1. Arquitetura do Projeto

O Pyeduc utiliza uma arquitetura em 5 camadas com a interface desktop em **Flet** (Flutter para Python):

| Camada | Arquivo Principal | Responsabilidade |
| :--- | :--- | :--- |
| **GUI Orquestrador** | `src/main_window.py` | Classe `PyeducApp` que gerencia layouts, splitters e integra os componentes visuais |
| **Componentes UI** | `src/ui/` | Classes Flet independentes (`app_state.py`, `editor_console.py`, `lesson_view.py`, etc.) |
| **Comunicação** | `src/communication.py` | Callbacks que conectam a GUI ao Executor |
| **Execução** | `src/executor.py` | REPL Python persistente em subprocesso (`PersistentPythonShell`) |
| **Conteúdo** | `src/content_manager.py` | Leitor e gerenciador de `content/lessons.json` |
| **Persistência** | `src/progress_manager.py` | Banco SQLite em `data/pyeduc.db` |
| **Tutor IA** | `src/tutor_guardrails.py` & `src/llm_client.py` | Cliente REST Ollama e guardrails sócraticos determinísticos |

---

## 🛠️ 2. Configuração do Ambiente e Testes

### Pré-requisitos
- Python 3.10 ou superior
- Virtualenv (`venv`)

### Instalação
```bash
# Clone e entre no repositório
git clone https://github.com/VaGNaroK/Pyeduc.git
cd Pyeduc

# Ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# no Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

### Executando a Aplicação
```bash
python src/main.py
```

### Executando a Suíte de Testes
```bash
pytest -v --cov=src
```

---

## ⚠️ 3. Regras de Ouro da Interface Flet (Prevenção de Bugs)

A interface em Flet converte código Python para a engine Dart/Flutter. Siga rigorosamente os padrões abaixo:

1. **Threading Obrigatório**:
   - **NUNCA** use `threading.Thread(...)` simples para atualizar elementos da UI Flet.
   - Use **SEMPRE** `page.run_thread(fn)` para despachar tarefas assíncronas (como requisições da IA ou atualizações em segundo plano).

2. **Alinhamento e Expansão de Painéis**:
   - Em layouts 70/30 (Esquerda/Direita) dentro de uma `ft.Row(expand=True)`, use `vertical_alignment=ft.CrossAxisAlignment.STRETCH`.
   - Na coluna esquerda, defina `expand=7` e obrigatoriamente `horizontal_alignment=ft.CrossAxisAlignment.STRETCH` para evitar vãos cinzas.

3. **Estados de Botões**:
   - Ao definir estilos de estado em `bgcolor={...}`, **NUNCA** use a string vazia `""` para o estado normal. Use estritamente o enum oficial `ft.ControlState.DEFAULT`.

4. **Popups e Modais Responsivos (`ft.AlertDialog`)**:
   - Qualquer `ft.Column` dentro de um `ft.AlertDialog` (como modais de quiz) **DEVE** conter `tight=True` (`ft.Column([..., tight=True])`) para ajustar dinamicamente a altura.

---

## 📚 4. Adicionando ou Modificando Lições (`content/lessons.json`)

As aulas ficam centralizadas no arquivo `content/lessons.json`.

### Tipos de Aula
- `"type": "presentation"`: Tela introdutória ou de apresentação sem terminal.
- `"type": "theory"`: Aula teórica focada em leitura + Quiz interativo grande.
- `"type": "coding"`: Aula prática com editor de código Python e terminal REPL.

### 🚨 Regra dos IDs para Novas Aulas (Preservação de Progresso)
- Se você for inserir uma nova aula **no meio do currículo existente**, **NÃO reordene os IDs originais** (ex: não mude o ID da aula 14 para 15).
- **Atribua IDs altos a partir de 1001** (ex: `1001`, `1002`). Isso garante que os alunos veteranos mantenham seu histórico inalterado no banco SQLite `pyeduc.db`.

---

## 🤖 5. Diretrizes do Tutor IA Sócratico

O Tutor IA se comunica com a instância local do Ollama (`http://localhost:11434`):
- Modelo recomendado: `qwen2.5-coder:3b` ou `1.5b`.
- O Tutor **NUNCA** deve fornecer a solução completa ou blocos de código com respostas prontas.
- As respostas devem obrigatoriamente seguir a estrutura de **3 tópicos Markdown**:
  - `**💡 Conceito**:`
  - `**❓ Pergunta Guiada**:`
  - `**🔍 Dica Progressiva**:`

---

## 📑 6. Fluxo de Pull Requests

1. Crie uma branch com o padrão: `feature/nome-da-feature` ou `fix/nome-do-bug`.
2. Garanta que toda a suíte de testes passe executando `pytest`.
3. Certifique-se de que nenhum warning de sintaxe ou erro Flet ocorra.
4. Abra o Pull Request descrevendo claramente as alterações realizadas.
