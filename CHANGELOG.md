# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato baseia-se em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [1.1.2] - 2026-07-21

### Adicionado
- **Integração Nativa do Tutor IA Ollama (`src/llm_client.py`):** Cliente REST interno conectando ao Ollama (`http://localhost:11434`) com detecção automática do Sistema Operacional (Linux/Windows/macOS) e verificação do binário do Ollama no PATH do sistema.
- **Residência de Modelo na VRAM & Descarregamento Automático (`OLLAMA_KEEP_ALIVE`):** Implementação da opção `OLLAMA_KEEP_ALIVE = "-1m"` no payload da API para manter os modelos (`qwen2.5-coder:1.5b` e `qwen2.5-coder:3b`) residentes na VRAM/RAM continuamente durante os estudos do aluno, e descarregamento imediato automático da GPU (`keep_alive: 0` via `unload_model()`) ao fechar a janela do aplicativo.

- **Módulo RAG Leve de Lições (`src/rag_module.py`):** Indexação e busca de termos e teoria relevantes em `content/lessons.json` para enriquecer os prompts do Tutor IA.
- **Guardrails Educacionais Sócráticos (`src/tutor_guardrails.py`):** Módulo de controle que impede vazamento de código pronto, exige diálogos didáticos em 2ª pessoa e formata as respostas em 3 tópicos limpos (`**💡 Conceito**:`, `**❓ Pergunta Guiada**:`, `**🔍 Dica Progressiva**:`).
- **Diagnóstico Estático Determinístico do Console:** Análise estática no `build_user_message` que detecta a classe exata do erro (`NameError` com sugestão de variável, `SyntaxError` de aspas em textos, `IndentationError`, `TypeError`, `ZeroDivisionError`), injetando a causa exata no prompt para impedir alucinações de modelos compactos de IA.
- **Sanitização de Respostas e Stop Tokens:** Método `sanitize_response` e adição de stop tokens no payload (`num_predict: 200`, `stop: [...]`) para cortar seções extras (`Resposta:`, `Explicação:`), evitar repetições em loop e formatar cabeçalhos em negrito com quebras de linha duplas.
- **Divisor Arrastável Lateral (`sidebar_splitter`):** Puxador vertical (`ft.GestureDetector`) entre o painel de conteúdo e a barra lateral direita para redimensionar a largura do chat do Tutor IA.

### Alterado
- **Modelo de IA Padrão Recomendado:** Alterado `OLLAMA_DEFAULT_MODEL` em `src/config.py` de `codellama:7b` (6GB-8GB VRAM) para `qwen2.5-coder:3b` e `qwen2.5-coder:1.5b` (~1.5GB-2.2GB VRAM), com seleção automática dinâmica do modelo mais leve instalado na máquina.
- **Formatação de Bolhas no Chat:** Remoção da largura fixa (`width=260`) no `add_chat_message` em favor de `expand=True`, permitindo mensagens em formato fluido e responsivo no painel lateral.
- **Gerenciamento de Threads da Interface (`src/gui.py`):** Substituição de `threading.Thread` nativo por **`page.run_thread()`**, corrigindo a dessincronização da interface Flet/Flutter no Linux Desktop e garantindo atualização imediata em tempo real do chat e da roleta de carregamento sem precisar focar/minimizar a janela.

### Removido
- **Seção de Referências:** Remoção completa dos botões e container de "Referências" da barra lateral e da lógica em `load_lesson`.

## [1.0.1] - 2026-07-20


### Adicionado
- **Imagens Ilustrativas:** Injeção de imagens didáticas via hardcode (`gui.py`) nas Aulas 11 (Booleanos), 12 (Operadores Aritméticos), 13 (Listas) e 21 (Atribuição Múltipla).
- **Regra de Speckit:** Registro formal no `AGENTS.md` (Regra 11) sobre o novo padrão arquitetural de injeção de imagens via código (`lesson_container.content.controls.append`).

### Alterado
- **Teoria da Aula 12:** Incremento e melhoria didática na explicação sobre os operadores aritméticos em `lessons.json`.

### Corrigido
- **Case-Sensitivity no Auto-Grader:** A função `fuzzy_clean` em `src/gui.py` agora converte a saída para letras minúsculas (usando `.lower()`), garantindo que o alerta laranja de "Quase lá" seja disparado quando o aluno errar a capitalização da resposta esperada (como "P" vs "p" em "Python").

## [1.0.0] - Adoção Oficial do Flet e Persistência Sólida

### Adicionado
- **Motor de Renderização Flet:** Migração completa da arquitetura gráfica antiga (PyQt/PySide/Flet-Qt) para o puro `Flet`, garantindo interfaces responsivas e mais modernas para desktop no formato "Single-File" (`gui.py`).
- **Persistent Python Subprocess (`executor.py`):** Ao invés de lançar um executável novo em cada run do usuário, um shell persistente avalia inputs, comunicando-se via `---CMD-BOUND-OUT---` garantindo melhor estabilidade, feedback, e suporte de estado interno na aula.
- **Divisor de Painéis Dinâmico (Splitter):** Implementação de um `GestureDetector` customizado. Permite que o aluno redimensione livremente a leitura teórica e a prática na tela (`expand` bounds dinâmicos).
- **Auto-Grader:** `gui.py` checa o código do aluno linha a linha contra a output esperada presente nos objetos de exercícios do JSON, repassando feedbacks espertos na tela.
- **Conteúdo Didático Completo (Aulas 0 ao 13):** Estruturação robusta em Teoria (Aulas de História do Python, Compilação, Ecossistema) e Prática Guiada com Console ativo (Variáveis, Operadores, Listas). Inclui a nova Lição "Welcome" (Aula 0).
- **Modo Admin:** Possibilidade de navegação ilimitada pelas aulas através de credenciais fixas de sistema sem a exigência de progressão de exercícios, excelente para debugar a API da GUI.
- **Sistemas de Secções (`sections`):** O `lessons.json` agora apoia aulas super desenvolvidas dividindo seu miolo teórico, e englobando múltiplos exercícios em seções modulares ao invés do clássico monobloco antigo.

### Alterado
- **Rebranding Completo (Pyeduc -> Pyeduc):** Remoção oficial da letra "Q" (referência ao extinto Qt) do nome da aplicação e toda documentação residual.
- **Migração para SQLite (`progress_manager.py`):** O antigo padrão JSON (que repousava sobre `progress.json`) foi substituído por uma engine relacional rápida `SQLite`, escrevendo em `data/pyeduc.db` impedindo corrupção fácil dos scores dos usuários.
- **Centralização da Documentação e Layout:** Documentos altamente redundantes gerados antes (`QUICKSTART.md`, `START_HERE.md`, `INDEX.md`, `PROJECT_SUMMARY.md`) foram limpos do repositório, com seus detalhes mesclados de maneira unificada nas raízes oficias do `README.md` e `INSTALL.md`. 
- **Auto-organização Inteligente de Layout:** A interface agora adapta seus pesos (`expand`) automaticamente de acordo com o `type` (theory, coding). Aulas teóricas cedem 65% do espaço inferior aos cards visuais do Quiz.
- **Estilização Markdown:** Nomes de arquivos referenciados no material didático agora ficam sublinhados pelo negrito nativo e não usam itálicos problemáticos no visual do background.

### Corrigido
- **Crash Silencioso de Cores do Flet:** Correção do mapeamento de estado de botões no quiz. Substituição da sintaxe inválida de string vazia `""` por `ft.ControlState.DEFAULT`, o que evitava a corrupção oculta e travamento de `page.update()`.
- **KeyError em Lições sem Quiz:** Inclusão de verificações defensivas (`.get("quiz", {})`) para que a aplicação não quebre o painel lateral ao carregar lições comemorativas da Raiz do JSON.
- **Vazamento do Console de Código:** Adição de rotina estrita para varrer o terminal de execução inferior (setando valores vazios) durante transição de telas, impedindo que o aluno veja o histórico de debugs de aulas passadas ao prosseguir na jornada.

---
*Pyeduc - App Educacional Python com Flet*
