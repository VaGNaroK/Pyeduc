# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato baseia-se em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [1.2.2] - 2026-07-27

### Corrigido
- **Bug da Dupla Janela no Flatpak (`src/executor.py`):** Corrigido o erro crítico onde o `sys.executable` apontava para o binário C++ do Flutter dentro do pacote `serious_python`. Isso causava a abertura de uma segunda janela fantasma e travamentos de renderização (erro `kInvalidArguments`) ao inicializar o interpretador interativo em background. Agora, o ambiente detecta se está empacotado (`FLET_EMBEDDED`) e força a invocação do `python3` do sistema base do Linux.
- **Falha de Carregamento de Lições no Flatpak (`src/gui.py`):** Removido o argumento de string absoluto `"content/lessons.json"` na inicialização do `ContentManager`. Isso reativou o sistema inteligente de roteamento de caminhos da classe, permitindo que a aplicação ache corretamente os dados em `/app/opt/pyeduc/content/lessons.json` dentro do sandbox do Flatpak.
- **Certificado SSL no Windows (`src/main.py`):** Adicionado um bypass condicional (`_create_unverified_context`) exclusivo para o Windows para evitar o erro `CERTIFICATE_VERIFY_FAILED` ao inicializar o download do motor do Flet.
- **Renderização de Imagens e API Descontinuada (`src/main.py`):** Migração do comando `ft.app()` para `ft.run()`. Adicionado o parâmetro `assets_dir=project_root`, consertando o bug onde imagens ilustrativas locais (ex: `variavel_exemple.png` na Aula 8) não carregavam na tela.
- **Responsividade e Espaçamento do Quiz (`src/ui/lesson_view.py`):** Corrigido o bug onde as Atividades de Fixação não atualizavam visualmente a fonte ao clicar em `A+`/`A-` nem mostravam estado instantâneo de correção. Também foram removidos contêineres de espaçamento redundantes, enxugando áreas vazias no layout.
- **Bloqueio de Execução Local no Venv (`src/main.py`):** Removida a injeção incondicional da variável `FLET_EMBEDDED="true"`. Essa injeção travava a execução local no desktop forçando o Flet a tentar escutar via soquete invisível (Dart bridge) em vez de abrir a janela. A variável agora é injetada nativamente apenas no Flatpak.
- **Falha de Escalonamento de Fonte na Interface (`src/gui.py`):** Corrigido o bug onde os botões de Acessibilidade ("A+" e "A-") redimensionavam apenas o console interativo. Agora, a folha de estilos do Markdown (`md_style_sheet`) foi injetada corretamente no carregamento dinâmico das lições. Toda a área teórica, textos descritivos de exercícios, títulos e opções de Atividades de Fixação (Quiz) escalonam o tamanho de suas fontes harmoniosamente e de maneira reativa.
- **Falso Positivo no Corretor Automático (`src/main_window.py`)**: Resolvido o "Falso Positivo de Colisão" onde o console avaliava exercícios aleatórios fora de ordem. A checagem agora é estritamente sequencial, exigindo conclusão ordenada.
- **Atalho de Rolagem Teórica (`src/main_window.py`)**: Adicionado o recurso para rolar a visão da aula atual usando `Alt + Page Down` e `Alt + Page Up`, permitindo navegação teórica fluida sem perder o foco do teclado no terminal.
- **Tutor IA - Regex de SyntaxError (`src/tutor_guardrails.py`)**: Ajustado o regex de diagnóstico estático que confundia erroneamente variáveis/expressões matemáticas (ex: `print(a + b)`) com strings não envelopadas por aspas.
- **Tutor IA - Alucinação de Prompt (`src/tutor_guardrails.py`)**: Removidos exemplos hardcoded do prompt do sistema, evitando que modelos locais menores papagaiem instruções do sistema ao invés de responder o aluno de fato.
- **Tutor IA - Precisão no TypeError (`src/tutor_guardrails.py`)**: Expandida a lógica de detecção de erros de tipo. O Tutor agora entende corretamente quando o aluno confunde métodos baseados em índice vs string (ex: `.pop('uva')` vs `.remove('uva')`).
- **Poluição Visual de Terminal (`src/executor.py`)**: Filtrados os códigos de terminal (OSC Escape `]633;...`) que novas versões do Python (3.13+) injetam silenciosamente no REPL, o que estava corrompendo a leitura da saída e sujando o console de erros.
## [1.2.1] - 2026-07-25

### Adicionado
- **Novo Ícone do Projeto (`content/icons/pyeduc.svg`):** Atualização da identidade visual do aplicativo em todas as camadas da interface e empacotamento:
  - **Interface Flet (`src/gui.py` & `src/config.py`):** Configurado `page.window.icon = config.APP_ICON`, marca visual adicionada na barra superior (`top_bar`), na tela de login (`welcome_container`) e na lição de boas-vindas.
  - **Configuração de Build Flet ([pyproject.toml](pyproject.toml)):** Criado o manifesto declarando `[tool.flet] icon = "content/icons/pyeduc.svg"`, garantindo a aplicação do ícone oficial em compilações Windows (`.exe`) e Linux.
  - **Pacote Linux DEB ([scripts/build_deb.sh](scripts/build_deb.sh)):** Atualizado para instalar o ícone em `/usr/share/icons/hicolor/scalable/apps/pyeduc.svg` e `/usr/share/pixmaps/pyeduc.svg` para exibição no menu de aplicativos do SO.
  - **Pacote Linux Flatpak ([flatpak/org.pyeduc.App.yml](flatpak/org.pyeduc.App.yml)):** Atualizado o manifesto de build para instalar o ícone e o atalho `.desktop` no sandbox Flatpak.
- **Diagnóstico Estático do Autograder no Tutor IA (`src/tutor_guardrails.py` & `src/gui.py`):** Injeção automática da comparação de saída esperada versus saída real gerada pelo aluno no prompt do Tutor IA quando o código executa sem exceções Python mas diverge no resultado do exercício pendente.
- **Novos Stop Tokens no Cliente Ollama (`src/llm_client.py`):** Inclusão de tokens de parada adicionais (`\n💡 Conceito`, `\n**💡 Conceito`, `\nConceito:`) para prevenir regeneração em loop de cabeçalhos pela IA.

### Corrigido
- **Manifesto Linux Flatpak e Pacote DEB ([flatpak/org.pyeduc.App.yml](flatpak/org.pyeduc.App.yml) & [scripts/build_deb.sh](scripts/build_deb.sh)):** Efetuado o upgrade de runtime para Freedesktop `24.08`, resolvendo o aviso de fim de vida (EOL) e a falha `g_once_init_enter_pointer`. Adicionadas as instruções de cópia explícita do diretório `content/` para `/app/opt/pyeduc/content/` e ícones para `/app/opt/pyeduc/app/assets/content/icons/pyeduc.svg`, sanando o carregamento de lições e exceções `PathNotFoundException`. Incluído o manifesto AppStream (`org.pyeduc.App.metainfo.xml`), corrigindo o nome para `Pyeduc` no `flatpak list`.
- **Prevenção de Instâncias Duplicadas e Proteção no Login ([src/main.py](src/main.py), [src/content_manager.py](src/content_manager.py), [src/progress_manager.py](src/progress_manager.py) & [src/gui.py](src/gui.py)):** Configurado `view=ft.AppView.WEB_SOCKET` no `src/main.py` sob Serious Python, eliminando o disparo de janelas secundárias pelo Flet. Adicionada busca de caminhos absolutos no `ContentManager` (`/app/opt/pyeduc/content/lessons.json`) e persistência SQLite em `~/.pyeduc/pyeduc.db` em `ProgressManager`. Mapeamentos e travas defensivas contra lista vazia implementados em `load_lesson`, `go_next` e `go_prev` no `src/gui.py`.
- **Pipeline de CI/CD no GitHub Actions ([.github/workflows/build.yml](.github/workflows/build.yml)):** Adicionada a permissão explícita `permissions: contents: write` no job `release` para corrigir erro 403 Forbidden do `GITHUB_TOKEN` ao criar a Release no GitHub. Configurado também o repositório Flathub (`flatpak remote-add`) e a flag `--install-deps-from=flathub` no `flatpak-builder`, além da inclusão de `libmpv-dev` e `mpv` nas dependências dos runners Linux.
- **Empacotamento Linux DEB ([scripts/build_deb.sh](scripts/build_deb.sh)):** Atualizado o campo `Depends:` no `DEBIAN/control` com dependências alternativas (`libmpv2 | libmpv1 | mpv | libmpv-dev`), resolvendo a falha *"A dependência não é contentável: libmpv1"* no Ubuntu 24.04 LTS e Linux Mint 22. Adicionado o script `DEBIAN/postinst` para automação do link simbólico `libmpv.so.1` e `DEBIAN/postrm` para remoção limpa.
- **Guia de Instalação ([INSTALL.md](INSTALL.md)):** Atualizadas as instruções do troubleshooting do `libmpv.so.1` para refletir o empacotamento automatizado via `.deb` e o procedimento manual para execução via código fonte.
- **Higienização e Parsing Flexível de Respostas da IA (`src/tutor_guardrails.py`):** Regex expandida para capturar variações de nomenclatura de cabeçalhos da IA e truncar ciclos repetidos de repetição no fallback.
- **Acompanhamento do Roadmap (`melhorias.txt`):** Atualização completa e auditoria dos itens concluídos, parciais e pendentes.

## [1.2.0] - 2026-07-25

### Adicionado
- **Suíte de Testes Automatizados (`pytest`):** Criados 14 testes unitários cobrindo o leitor de lições (`ContentManager`), o interpretador REPL (`PersistentPythonShell`), o banco de dados (`ProgressManager`) e os guardrails do Tutor IA (`EducationalGuardrails`).
- **Guia de Contribuição ([CONTRIBUTING.md](CONTRIBUTING.md)):** Documento orientativo detalhando a arquitetura em 5 camadas do Pyeduc, ambiente de desenvolvimento, padrões Flet e diretrizes de preservação de progresso (**IDs >= 1001**).
- **Exportação e Importação de Progresso em JSON:** Funcionalidade de backup/restauração no `ProgressManager` e botões visuais na barra superior (`top_bar`) integrados via `ft.FilePicker`.
- **Análise Estática de Código com AST Python no Tutor IA:** Implementado analisador determinístico `analyze_code_ast()` no `EducationalGuardrails` ([src/tutor_guardrails.py](src/tutor_guardrails.py)), capaz de identificar variáveis não utilizadas, sobrescrita de funções nativas (built-ins), funções sem `return`, risco de loop infinito (`while True` sem `break`) e erros de sintaxe detalhados.
- **Expansão do Currículo Didático (9 Novas Aulas):** Adicionadas as aulas de Tuplas (ID 1003), Dicionários (ID 1004), Conjuntos (ID 1005), Aprofundamento em Funções (ID 1006), Módulos (ID 1007), Tratamento de Erros (ID 1008), Manipulação de Arquivos (ID 1009), Orientação a Objetos (ID 1010) e a Prova Prática Integradora 3 (ID 1011).
- **Travas de Limites e Alça Visual nos Divisores Arrastáveis:** Limitação de redimensionamento dos painéis entre 20% e 80% (`drag_splitter`) e 20% a 40% (`sidebar_splitter`), com alça visual `DRAG_HANDLE` e destaque de hover em Azul Ciano (`#38bdf8`).
- **Micro-Animações e Elevação Dinâmica nos Botões:** Adicionados efeitos de hover com transição suave (`animation_duration=200ms`) e elevação dinâmica nos botões "Exportar", "Importar", "Executar Código", "Limpar" e "Responder Quiz da Lição".
- **Modo Offline Gracioso e Diagnóstico do Ollama:** Adicionado fallback no `OllamaClient` ([src/llm_client.py](src/llm_client.py)) para exibir instruções de inicialização em Markdown no chat quando a IA estiver offline ou desinstalada, além do indicador tri-estado na barra lateral (Verde, Amarelo e Vermelho).
- **Whitelist de Módulos e Validação de Segurança no Executor REPL:** Implementada inspeção estática via AST no `PersistentPythonShell` ([src/executor.py](src/executor.py)), bloqueando a importação de módulos de sistema inseguros (`os`, `subprocess`, etc.) e chamadas perigosas (`eval()`, `exec()`), preservando `open()` para as lições práticas do currículo.
- **Sistema de Acessibilidade Visual e Zoom de Fonte (`[ A- ]` `[ 100% ]` `[ A+ ]`):** Adicionados controles de zoom de fonte na barra superior (`top_bar`), aplicando escala dinâmica (11px a 22px) na teoria das aulas via `md_style_sheet`, nos códigos de exemplo, nos títulos, nas descrições de exercícios e no console Python.



## [1.1.3] - 2026-07-22


### Adicionado
- **Destaque do Tutor IA no Topo da Sidebar:** Posicionamento do painel do Tutor IA Sócratico no topo da barra lateral direita para acesso imediato ao chat de dúvidas sem necessidade de rolagem de tela.
- **Quiz da Lição em Popup Modal (`ft.AlertDialog`):** Migração do questionário de fixação para uma janela popup centralizada acionada pelo botão `🎯 Responder Quiz da Lição`. O botão é exibido dinamicamente apenas em lições com quiz.
- **Console Python de Alto Contraste:** Fundo do console em Azul Slate Escuro (`#0f172a`), com o editor de código (`console_input`) destacado por **borda Azul Ciano (`#38bdf8`)** e o terminal de saída (`console_output_container`) por **borda Verde Esmeralda (`#10b981`)**.
- **Rodapé Dinâmico de Progresso (`footer`):** Exibição em tempo real do status do aluno logado e percentual de conclusão do curso (ex: `👤 Aluno: vagner | Lição 10 de 24 (41% concluído)`).

### Alterado
- **Responsividade Vertical de Popup Modal (`tight=True`):** Adicionada a propriedade `tight=True` na coluna interna do `quiz_modal`, fazendo com que a janela envolva dinamicamente a altura exata das perguntas e alternativas.
- **Ajuste de Linhas e Visibilidade Simultânea no Console:** Linhas mínimas ajustadas (`min_lines=4` no editor e `min_lines=5` no terminal de saída), garantindo exibição simultânea de ambas as caixas sem cortes ou necessidade de rolagem.
- **Purificação da Barra Superior (Top Bar):** Remoção do botão redundante `🤖 Tutor IA` do cabeçalho da aplicação.
- **Limpeza Automática de Chat por Lição:** Inclusão de `ai_chat_history.clear()`, `ai_chat_list.controls.clear()` e `ai_input_field.value = ""` na função `load_lesson()`, zerando a conversa do Tutor IA a cada transição de aula.
- **Padronização do Modelo Oficial Ollama:** Atualizado o modelo oficial recomendado no `README.md` e `INSTALL.md` para `qwen2.5-coder:3b`.

### Corrigido
- **Correção na Avaliação do Auto-Grader (`src/gui.py`):** Reestruturação do algoritmo de validação em duas passadas com consumo de linhas de saída (1ª passada: exata, 2ª passada: fuzzy). Corrige o falso alarme *"💡 Quase lá!"* quando o código do aluno dava match exato em um exercício (ex: Aula 8), mas outros exercícios pendentes na aula reutilizavam erroneamente a saída no match fuzzy.
- **Conclusão Automática de Aulas Práticas:** Integração com `progress_manager.mark_lesson_completed()` ao concluir todos os exercícios de uma aula no console.
- **NameError em `sidebar_quiz_container`:** Removidas referências obsoletas da antiga caixa do quiz na barra lateral durante a navegação entre aulas.
- **AttributeError em `get_current_username`:** Criado e utilizado o método oficial `progress_manager.get_current_username()` para recuperar o nome do usuário logado na sessão.
- **Atualização das Regras do Projeto ([AGENTS.md](AGENTS.md)):** Registro da Seção 15 travando o projeto contra regressões visuais e de lógica.

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
