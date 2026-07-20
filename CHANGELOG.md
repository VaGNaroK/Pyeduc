# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato baseia-se em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

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
