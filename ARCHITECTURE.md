# 🏗️ Arquitetura do Pyeduc

## Visão Geral

O Pyeduc é um aplicativo educacional estruturado em **5 camadas de arquitetura**, permitindo manutenção, expansão e estabilidade visual e de dados do sistema.

```
+------------------------------------------+
|      Camada 1: GUI (Flet)                |
|  - main_app() closure (~770 linhas)      |
|  - Layout dinâmico responsivo            |
|  - Gestão de colunas stretch             |
+------------------------------------------+
|   Camada 2: Comunicação (Callbacks)      |
|  - Conecta GUI aos componentes internos  |
|  - Repasse de inputs do usuário          |
+------------------------------------------+
|   Camada 3: Execução (Subprocesso)       |
|  - PersistentPythonShell                 |
|  - Isolado do Flet main thread           |
|  - Comunicação via delimitadores shell   |
+------------------------------------------+
|   Camada 4: Conteúdo (JSON)              |
|  - Armazena lições (Teoria e Prática)    |
|  - Estrutura de subseções                |
+------------------------------------------+
|   Camada 5: Persistência (SQLite)        |
|  - Banco data/pyeduc.db                  |
|  - Salva checks das aulas concluídas     |
+------------------------------------------+
|   Camada 6: Inteligência Artificial (LLM)|
|  - llm_client.py (Ollama REST API)       |
|  - tutor_guardrails.py (Diagnóstico/Regras)|
|  - rag_module.py (Recuperação de lições) |
+------------------------------------------+
```

## Módulos e Responsabilidades

### 1. **gui.py** - Camada de Interface (Flet)
Trabalha como o cérebro visual da aplicação. Ao contrário do paradigma tradicional de POO de GUIs, ele foca em uma abordagem mais declarativa do Flutter encapsulada numa grande função `main_app`.
- **Flet Components**: Utiliza caixas (`ft.Container`), colunas e linhas que esticam dinamicamente.
- **Divisor Arrastável**: Implementa um `ft.GestureDetector` (drag_splitter) que varia o `expand` (peso de layout) para ajustar proporções de tela dinamicamente dependendo do tipo da aula.
- **Auto-Grader**: Faz checagem de exercícios através de line-by-line matching com resultados previstos pela aula.
- **Tutor IA Sócratico Integrado**: Painel de inteligência artificial acoplado para sanar dúvidas do aluno sem fornecer spoilers de código.

### 2. **communication.py** - Camada de Comunicação
- Substituiu o antigo modelo de Sinais do `PyQt`/`PySide`.
- Recebe cliques e eventos do Flet e decide se os engloba em callbacks simples para repasse das diretivas lógicas, impedindo que o motor de tela Flet congele enquanto o código Python do usuário for executado.

### 3. **executor.py** - Camada de Execução
- **`PersistentPythonShell`**: O código Python interativo do usuário *não* inicia um novo executável por clique, ele usa um REPL persistente, comunicando seus *stdout* e *stderr* perfeitamente demarcados via strings de separação customizadas como `---CMD-BOUND-OUT---`.
- Assegura timeout apropriado e isola completamente que erros de digitação de alunos derrubem a aplicação Flet.

### 4. **content_manager.py** - Camada de Conteúdo
- Gerencia a leitura de `content/lessons.json`.
- Processa fluxos de lições que podem ter a propriedade `"type": "theory"` ou `"type": "coding"`.
- Aulas avançadas possuem chaves `"sections"` contendo múltiplos `"exercises"` encadeados no lugar do modelo simples.

### 5. **progress_manager.py** - Camada de Persistência
- Utiliza **SQLite** (gerando o banco local `data/pyeduc.db`).
- Mantém o registro imutável do que o usuário já resolveu.
- Arquivos prévios como `data/progress.json` são legados/stale.
- Fornece métodos visuais que invocam callbacks na GUI para repintar checks verdes nas lições da Sidebar.

### 6. **llm_client.py / tutor_guardrails.py / rag_module.py** - Camada de Inteligência Artificial
- **`llm_client.py`**: Cliente HTTP REST para comunicação nativa com o **Ollama** local via biblioteca padrão `urllib`. Resolve automaticamente o melhor modelo instalado (`qwen2.5-coder`) e gerencia descarregamento dinâmico de VRAM/RAM ao fechar a aplicação (`unload_model()`).
- **`tutor_guardrails.py`**: Análise estática determinística de erros (`NameError`, `SyntaxError`, etc.) e aplicação estrita do formato de resposta sócratico em 3 tópicos (**💡 Conceito**, **❓ Pergunta Guiada**, **🔍 Dica Progressiva**).
- **`rag_module.py`**: Indexador e recuperador de contexto didático em tempo real baseado no conteúdo de `content/lessons.json`.

## Padrões de Design e Prevenção de Erros (Flet Quirks)
1. **Stretch Responsivo**: Ao dividir layout numa row, exige `vertical_alignment=ft.CrossAxisAlignment.STRETCH`. Seus filhos devem declarar `horizontal_alignment=ft.CrossAxisAlignment.STRETCH`.
2. **KeyErrors em Transições**: É regra sempre usar `.get("chave", {})` nas rotinas da GUI, pois lições comemorativas/bem-vindas no JSON excluem as chaves interativas normais.
3. **Limpeza de Estado**: As transições limpam não apenas a input do usuário, mas a caixinha de output antiga do console para impedir a ilusão de "vazamento" de estado de uma aula pra outra.
4. **Login Admin**: O estado da aplicação é completamente relaxado se o usuário acessar com usuário `admin` e senha `admin`, pulando travamento sequencial do progresso de aprendizado.
