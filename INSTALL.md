# 🚀 Guia de Instalação e Início Rápido - Pyeduc

Este documento contém tudo o que você precisa para configurar o ambiente e rodar o Pyeduc na sua máquina, além da solução dos problemas mais comuns (Troubleshooting).

## ⚠️ Pré-requisitos

Para executar o Pyeduc, você precisa instalar:
1. **Python 3.8+**
2. **Flet** (instalado automaticamente via `requirements.txt`)

## 📥 Passo 1: Instalar Python

### ✅ Windows
1. Acesse: https://www.python.org/downloads/
2. Baixe a versão mais recente.
3. **IMPORTANTE**: Marque a opção **"Add Python to PATH"** durante a instalação!
4. Abra o PowerShell ou CMD e teste: `python --version`

### ✅ macOS e Linux
```bash
# macOS (Homebrew)
brew install python3

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip python3-venv
```
*(Confirme a instalação rodando `python3 --version` no terminal)*

## 📋 Passo 2: Clonar ou Extrair o Projeto

```bash
cd caminho/para/Pyeduc
```

## ⚙️ Passo 3: Configurar Ambiente e Instalar

Recomendamos o uso de um Ambiente Virtual (`venv`) para evitar sujeira global nas suas libs Python.

### Windows (PowerShell)
```powershell
# Criação
python -m venv venv
# Ativação
.\venv\Scripts\Activate.ps1
# Instalação
pip install -r requirements.txt
```

### macOS/Linux (Bash)
```bash
# Criação
python3 -m venv venv
# Ativação
source venv/bin/activate
# Instalação
pip install -r requirements.txt
```

> **Atalho Rápido:** Você também pode usar os scripts executáveis da raiz (`.\run.bat` no Windows ou `bash run.sh` no Linux/Mac) para inicializar rapidamente e abrir a aplicação.

## ▶️ Passo 4: Executar a Aplicação

Sempre com o seu ambiente virtual ativo, use:
```bash
python src/main.py
```

Se tudo estiver certo, uma janela elegante interativa do Flet se abrirá! 🎉

## 🤖 Passo 5 (Opcional): Configurar o Tutor IA Sócratico (Ollama)

O Pyeduc possui suporte a um **Tutor IA local inteligente** rodando via [Ollama](https://ollama.com). O uso é 100% gratuito, privado e não requer chaves de API pagas.

1. **Instalar o Ollama:**
   - **Linux / macOS:**
     ```bash
     curl -fsSL https://ollama.com/install.sh | sh
     ```
   - **Windows:** Baixe o instalador oficial em [Ollama.com/download](https://ollama.com/download)

2. **Baixar um modelo leve de código (recomendado):**
   ```bash
   ollama pull qwen2.5-coder:1.5b
   # ou
   ollama pull qwen2.5-coder:3b
   ```

3. **Pronto!** O Pyeduc detectará o Ollama automaticamente e exibirá a indicação `Ollama online` no topo da barra lateral e nas lições práticas.

## 🆘 Solução de Problemas (Troubleshooting)

### ❌ "python não é reconhecido"
- Reinstale o Python marcando a caixa de "Add Python to PATH".
- Reinicie o terminal ou PowerShell.
- No Windows, as vezes o comando é `py` ao invés de `python`. Tente `py -m venv venv`.

### ❌ "ModuleNotFoundError: No module named 'Flet'"
```bash
pip install --upgrade pip
pip install Flet
```

### ❌ Erro "libmpv.so.1" no Linux Mint / Ubuntu
Ao rodar o Flet pela primeira vez em ecossistemas Debian-like mais novos, o Flet (que puxa binários do motor Flutter) pode buscar por nomes hardcoded de bibliotecas não encontradas. Para corrigir:

**1. Instalar as bases necessárias:**
```bash
sudo apt update
sudo apt install -y libmpv-dev mpv
```

**2. Criar o Symlink pra enganar o framework:**
```bash
sudo ln -s /usr/lib/x86_64-linux-gnu/libmpv.so /usr/lib/libmpv.so.1
```

**3. Instalar bibliotecas gráficas extras comuns do GTK e Clang:**
```bash
sudo apt install -y binutils clang cmake llvm lld ninja-build pkg-config libgtk-3-dev libsecret-1-0 libsecret-1-dev libunwind-dev
```

### ❌ A aplicação não abre ou trava no boot
- Feche o terminal.
- Certifique-se de que o Python instalado é versão 3.8 ou superior.
- Cheque o Flet com `pip list | grep flet`. Se não constar, instale-o.

## 📞 Contato / Suporte
Verifique a sintaxe base da sua máquina com `python --version` e certifique-se de ver `(venv)` no começo do terminal antes de reportar problemas gerais.

---
**Feito com ❤️ para educação em Python**
