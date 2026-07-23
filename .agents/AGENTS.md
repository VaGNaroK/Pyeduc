# Speckit / Project Guidelines: Pyeduc

Este arquivo contém as regras arquiteturais, padrões de design e histórico de bugs importantes do projeto Pyeduc. Qualquer assistente de IA que modificar este código no futuro deve ler estas regras para evitar quebrar o layout e a arquitetura.

## 1. Tecnologia de Interface (GUI)
- O projeto foi **migrado do PySide6 para Flet**.
- **Jamais reintegre ou sugira bibliotecas do PyQt/PySide**. Flet é a tecnologia oficial para renderização responsiva web-like em Desktop.
- Os callbacks não utilizam QThread ou Signals/Slots. O controle de processos subprocess (para execução de código Python do usuário) é feito via threading padrão do Python no arquivo `src/executor.py` e se comunica via callbacks com a interface no `src/gui.py`.

## 2. Padrões de Layout Flet (Prevenção de Quebras)
O layout do Flet pode ser traiçoeiro com expansões em eixos opostos. Se for criar ou modificar Colunas e Linhas, lembre-se destas regras que consertaram bugs graves de responsividade no passado:
- Ao criar um layout 70/30 (Esquerda/Direita) dentro de uma `ft.Row(expand=True)`:
  - Adicione `vertical_alignment=ft.CrossAxisAlignment.STRETCH` na `Row` principal para forçar a altura total da tela.
  - Na Coluna da esquerda (`left_panel`), use `expand=7` E OBRIGATORIAMENTE `horizontal_alignment=ft.CrossAxisAlignment.STRETCH`. Se esquecer o alinhamento horizontal, a caixa não irá esticar para encostar no painel lateral direito, deixando vãos cinzas vazios caso o texto seja curto.
  - **Evite envolver Flex containers (Colunas) com Containers invisíveis** apenas para aplicar o `expand`. Isso quebra o repasse da expansão vertical para os filhos (`lesson_container`, `console_container`, etc).

## 3. Dinâmica das Aulas (Tipos Teóricos vs Práticos)
- O arquivo `content/lessons.json` possui um array de aulas.
- Cada aula DEVE TER a propriedade `"type"`. Pode ser `"theory"` ou `"coding"`.
  - **Theory (Teórica)**: Não apresenta o terminal Python (`console_container`). Em vez disso, exibe a propriedade `"quiz"` da aula num componente visual interativo (`activity_container`) bem grande e centralizado na área de baixo. A sidebar não deve exibir a caixa secundária de "Mini Quiz".
  - **Coding (Prática)**: Exibe o editor de texto superior e o terminal Python interativo inferior, ocultando o quiz interativo central. O "Mini Quiz" deve aparecer normalmente na barra lateral.
  - **Estruturação de Conteúdo Coding Avançado**: Para maior aprofundamento prático (ex: aulas 18 a 24), a aula deve usar a propriedade `"sections"`, que é um array de objetos onde cada um contém `content` (texto teórico), `example` (código de exemplo) e `exercises` (lista de exercícios daquela seção). O sistema da GUI irá renderizá-los sequencialmente de forma intercalada. Lições mais simples podem continuar usando as propriedades `"content"`, `"example"` e `"exercises"` na raiz.

## 4. Estado da Aplicação (ProgressManager)
- O progresso do usuário é salvo localmente num arquivo `data/progress.json`.
- A interface chama `progress_manager.mark_lesson_completed(id)` e depois invoca `update_progress_ui()` para atualizar os marcadores verdes/vermelhos (checks) no painel lateral.

## 5. Armadilhas de Estilos e Estados no Flet (Crashes Silenciosos)
- O Flet converte Python para Dart/Flutter internamente. Se você errar a sintaxe de um dicionário de estilo (ex: em `ButtonStyle`), o front-end (Dart) quebra e aborta o render da tela silenciosamente, sem emitir exceções no console Python.
- **Regra de Ouro:** Ao definir dicionários de estados como `bgcolor={...}`, **NUNCA** use uma string vazia `""` para definir o estado normal do botão. Use estritamente o enum oficial `ft.ControlState.DEFAULT`. O uso de `""` interrompe a atualização de `page.update()` inteira e congela o aplicativo de forma invisível.

## 6. Divisor Arrastável (Splitter) Customizado
- Como o Flet não possui um `QSplitter` nativo, utilizamos um `ft.GestureDetector` (nomeado `drag_splitter`) entre os painéis superior (`lesson_container`) e inferiores.
- Ele ajusta a altura utilizando a propriedade `.expand` (peso) que varia de 10 a 90, somando ou subtraindo o `e.delta_y` capturado pelo cursor.

## 7. Auto-Organização do Layout
- Dependendo do tipo de aula, o peso do layout (`expand`) é reajustado automaticamente na função `load_lesson`:
  - **Aulas Teóricas**: Distribuem 65% do espaço para baixo (`activity_container`) para não cortar os múltiplos botões de quiz (o scroll do container superior assume se o texto for grande).
  - **Aulas Práticas**: Retornam ao padrão 50/50.
  - **Aulas Welcome**: Ocultam o `drag_splitter` completamente, pois não há atividade inferior para o usuário redimensionar.

## 8. Limpeza de Estado nas Transições (Prevenção de Vazamento e KeyErrors)
- Ao trocar de lição (dentro de `load_lesson`), é mandatório **zerar o estado completo do terminal**. Isso significa limpar não apenas o código do usuário (`console_input.value = ""`), mas também os logs de resultados da aula anterior (`console_output.value = ""`), evitando a confusão visual de "vazamento" de estado.
- **Prevenção de dicionários rasos**: Para componentes secundários (como o `quiz_question` na barra lateral), nunca presuma a existência de chaves no dicionário `lesson`. Sempre tente extrair chaves de forma defensiva usando `.get("quiz", {})` para não disparar um `KeyError` na tela quando lições exclusivas (como `"type": "welcome"`) omitirem essas informações no JSON.

## 9. Tratamento de Chaves Vazias nas Aulas (Layout Condicional)
- **Cuidado ao renderizar o JSON na GUI**: Ao processar as chaves `"example"`, `"exercise"` ou `"exercises"` (seja na raiz da `lesson` ou dentro de objetos do array `"sections"`), sempre verifique se o valor não é vazio (ex: use `if sec.get("example"):` em vez de apenas `if "example" in sec:`).
- Caso você use `in` em vez de `.get()`, a GUI renderizará contêineres vazios, divisórias (Dividers) e botões "Copiar Exemplo" desnecessariamente nas Aulas Teóricas, pois o JSON muitas vezes declara essas propriedades como strings vazias `""` em vez de omiti-las por completo.

## 10. Inserção de Aulas e Provas Intermediárias
- **Preservação de Progresso**: Se precisar inserir uma nova aula ou Prova Prática (ex: Projeto Calculadora) no meio do currículo atual (arquivo `lessons.json`), **NÃO USE IDs sequenciais pequenos** (ex: não mova a aula 14 para o ID 15 para encaixar a Prova). Isso corrompe o progresso dos usuários no banco de dados SQLite.
- **Solução**: Sempre atribua **IDs altos (a partir de 1001)** para aulas inseridas no meio. Assim, o banco rastreará a nova lição como `1001` e os usuários veteranos manterão seu histórico inalterado nas lições originais.

## 11. Injeção de Imagens Ilustrativas nas Aulas
- Quando necessário adicionar imagens para ilustrar conceitos teóricos (como tabelas de variáveis ou diagramas de booleanos), elas não vêm diretamente do JSON.
- O padrão do projeto é realizar a **injeção via hardcode** no `src/gui.py`, logo após a renderização do markdown (`ft.Markdown`).
- A injeção deve ser feita validando o ID da lição (`if lesson.get("id") == X:`) e fazendo um `.append` na lista de `controls` do `lesson_container.content`. O container da imagem deve ter largura (`width=1200`), alinhamento centralizado (`alignment=ft.Alignment.CENTER`) e margens apropriadas.

## 12. Arquitetura do Tutor IA Sócratico (Ollama REST Integration)
- A comunicação com o Ollama (`http://localhost:11434`) é feita via cliente REST nativo (`src/llm_client.py`), sem utilizar bibliotecas externas pesadas (como `langchain` ou `ollama-python`).
- **Verificação de Saúde & SO**: O método `check_health()` usa `platform.system()` e `shutil.which("ollama")` para verificar o executável no SO (Linux/Windows/macOS), exibindo mensagens de status amigáveis no topo da barra lateral.
- **Residência em VRAM & Descarregamento no Fechamento**: Todas as chamadas POST para a API REST usam a opção `"keep_alive": "-1m"` para manter o modelo pré-carregado em VRAM/RAM continuamente durante o uso do aluno. Ao fechar o aplicativo (`on_window_event("close")` ou `on_disconnect`), o Pyeduc dispara `ollama_client.unload_model()`, enviando `"keep_alive": 0` para descarregar o modelo da VRAM imediatamente e liberar toda a memória GPU/RAM.

- **Modelos Recomendados**: O sistema prioriza modelos leves especializados em código (`qwen2.5-coder:3b` e `qwen2.5-coder:1.5b`), resolvendo dinamicamente o melhor modelo instalado na máquina do usuário via `resolve_best_model()`.

## 13. Guardrails Educacionais & Diagnóstico Determinístico (`src/tutor_guardrails.py`)
- **Diálogo Didático e Sócratico**: A IA responde obrigatoriamente em 2ª pessoa ("você"), organizada em 3 tópicos Markdown com quebras de linha duplas (`**💡 Conceito**:`, `**❓ Pergunta Guiada**:`, `**🔍 Dica Progressiva**:`). É terminantemente proibido entregar soluções ou blocos de código com a resposta pronta.
- **Diagnóstico Estático Pré-Prompt**: Antes de chamar a IA, o `build_user_message` analisa o console (`NameError`, `SyntaxError`, `IndentationError`, `TypeError`, `ZeroDivisionError`) e o código do aluno, injetando a causa verdadeira no contexto do prompt. Isso impede alucinações comuns de modelos compactos (ex: sugerir vírgulas em vez de aspas ou erro de espaço).
- **Sanitização de Resposta e Stop Tokens**: O `sanitize_response` trunca seções extras (`Resposta:`, `Explicação:`), stop tokens (`num_predict: 200`, `stop: [...]`), previne repetições de `Conceito:` em loop e aplica a formatação em negrito nos cabeçalhos.

## 14. Gerenciamento de Threads e Renderização Flet (`src/gui.py`)
- **Evitar `threading.Thread` Direto para Atualizações de UI**: **NUNCA** invoque `threading.Thread(target=...).start()` diretamente para atualizar a interface Flet sem usar o despachante nativo do Flet. O uso de `threading.Thread` simples faz com que a interface do Flet Desktop no Linux/Windows congele até que ocorra um evento manual de janela (focar/minimizar).
- **Usar `page.run_thread(fn)`**: Todas as chamadas assíncronas em segundo plano (como requisições da IA em `send_to_ai` e health check em `update_ollama_status`) DEVEM utilizar **`page.run_thread(fn)`**, que faz a notificação direta ao barramento de mensagens do Flutter C++ e força a renderização visual da tela e roleta em tempo real.
- **Divisor Lateral Arrastável (`sidebar_splitter`)**: O redimensionamento do chat da IA na barra lateral direita é controlado por um `ft.GestureDetector` vertical (`sidebar_splitter`) posicionado na `main_row`.

## 15. Regras de Interface, Limpeza do Chat IA e Método Username
- **Limpeza de Estado do Tutor IA em `load_lesson()`**: Ao trocar de lição, é mandatório executar `ai_chat_history.clear()`, `ai_chat_list.controls.clear()` e `ai_input_field.value = ""` para zerar o contexto do chat e impedir vazamento de mensagens da aula anterior.
- **Nome de Usuário em `ProgressManager`**: Para recuperar o nome do usuário ativo na sessão, use estritamente `progress_manager.get_current_username()` (não tente invocar `get_current_user`, que causará um `AttributeError`).
- **Alto Contraste no Console Python**: O container principal do console usa fundo `#0f172a` (Slate Escuro). O editor de código (`console_input`) utiliza borda brilhante **Azul Ciano (`#38bdf8`)** (`min_lines=4`), enquanto a caixa do terminal de saída (`console_output_container`) utiliza borda brilhante **Verde Esmeralda (`#10b981`)** (`min_lines=5`).
- **Responsividade do Popup Modal (`ft.AlertDialog`)**: Qualquer coluna interna dentro de contêineres de Popup Modal (como `quiz_modal`) DEVE obrigatoriamente declarar `tight=True` (`ft.Column([..., tight=True])`) para que a janela envolva dinamicamente a altura exata do seu conteúdo, evitando espaços cinzas vazios verticais.
- **Visibilidade Condicional da Sidebar IA**: O painel do Tutor IA (`sidebar_ai_container`) deve ser visível exclusivamente em lições práticas (`sidebar_ai_container.visible = not is_theory and not is_presentation`), sendo ocultado em aulas teóricas e apresentações.

