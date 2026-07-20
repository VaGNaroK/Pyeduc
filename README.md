# Pyeduc - App Educacional Python

Um aplicativo educacional interativo desenvolvido em Python com **Flet** (interface baseada no Flutter), projetado para ensinar conceitos fundamentais de programação Python através de uma interface intuitiva, responsiva e console Python integrado.

## 🎯 Características

- **Interface Pedagógica Dividida**: 
  - Parte superior: explicações teóricas, exemplos e exercícios interativos.
  - Parte inferior: console Python interativo (`PersistentPythonShell`).
- **Execução Segura de Código**: O código do aluno é executado em um subprocesso persistente, com timeout e captura segura de `stdout`/`stderr`.
- **Rastreamento de Progresso**: Salva automaticamente as lições concluídas em um banco de dados local **SQLite** (`data/pyeduc.db`).
- **Auto-Grader**: Verificação automática e linha a linha das saídas esperadas de exercícios propostos nas lições práticas.
- **Modo Admin**: Faça login com `admin`/`admin` para poder navegar livremente por todo o currículo sem restrições.

## 📚 Conteúdo Didático

O conteúdo fica no arquivo JSON `content/lessons.json` e é dividido entre lições de Teoria e Prática:

- **Teoria Inicial:**
  - Bem-vindo ao Pyeduc!
  - A História do Python, O Ecossistema Python, Compilada vs Interpretada, Código Fonte e Arquivos .py, Versões do Python (2 vs 3), Regras para Nomear Variáveis.
- **Prática (com Console, Auto-Grader e Múltiplos Exercícios):**
  - Variáveis e Textos (Strings), Números Inteiros (Int), Números Decimais (Float), Valores Booleanos (Bool), Operadores Aritméticos, Listas e Iteração.

## 📋 Requisitos

- Python 3.8+
- Flet (`pip install flet`)

## 🚀 Instalação e Execução

Para ver o passo a passo de como configurar seu ambiente virtual, instalar dependências e rodar o projeto localmente, acesse o guia oficial em **[INSTALL.md](INSTALL.md)**.

## 📁 Estrutura Principal do Projeto

- `src/gui.py`: Camada de Interface Flet (`main_app`).
- `src/communication.py`: Callbacks fazendo a ponte entre GUI e o Executor.
- `src/executor.py`: Subprocesso persistente do Python em que os códigos rodam (`PersistentPythonShell`).
- `src/content_manager.py`: Controlador de conteúdo (carrega o `lessons.json`).
- `src/progress_manager.py`: Sistema de gravação e gerenciamento do histórico SQLite em `data/pyeduc.db`.
- `content/lessons.json`: Onde a magia do currículo acontece.
- `data/pyeduc.db`: Banco local com o histórico (criado automaticamente caso não exista).

## 🔧 Extensão e Modificações

Se quiser alterar ou criar novas lições, basta adicionar entradas no `lessons.json`. As aulas de tipo `"theory"` geram um painel longo interativo e sem console inferior, enquanto aulas `"coding"` (práticas) exibem o editor.
Lições avançadas (como desafios) podem usar a chave `sections` para intercalar textos com múltiplos exercícios na mesma aula.

## 🛠 Compilação e Distribuição (Build)

```bash
# Windows
flet build windows --project pyeduc

# Linux
flet build linux --project pyeduc

# Deb Package (Debian/Ubuntu)
./scripts/build_deb.sh
```
Nota: Há rotinas no CI em `.github/workflows/build.yml` que podem compilar versões em Flatpak também.

## 📝 Documentação Detalhada

- Leia a fundo as decisões técnicas e regras de design estrutural em [ARCHITECTURE.md](ARCHITECTURE.md).
- Veja instruções detalhadas de como resolver erros locais de instalação no [INSTALL.md](INSTALL.md).
- Consulte as alterações na documentação e de versão no [CHANGELOG.md](CHANGELOG.md).

## 📄 Licença

Este projeto está licenciado sob a **GNU General Public License v3.0 (GPL-3.0)**. 
Veja o arquivo `LICENSE` para mais detalhes.

---

**Desenvolvido para fins educacionais** 🚀
