import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from llm_client import OllamaClient


def test_ollama_is_installed_boolean():
    client = OllamaClient()
    installed = client.is_ollama_installed()
    assert isinstance(installed, bool)


def test_ollama_check_health_returns_tuple():
    client = OllamaClient()
    online, message = client.check_health()
    assert isinstance(online, bool)
    assert isinstance(message, str)
    assert len(message) > 0


def test_ollama_get_offline_help_message():
    client = OllamaClient()
    msg = client.get_offline_help_message()
    assert "**💡 Conceito**" in msg
    assert "**❓ Pergunta Guiada**" in msg
    assert "**🔍 Dica Progressiva**" in msg
    assert "ollama" in msg.lower()


def test_ollama_chat_offline_fallback():
    # Aponta para uma URL inválida para simular falha de conexão e testar o fallback gracioso
    client = OllamaClient(base_url="http://127.0.0.1:55555")
    messages = [{"role": "user", "content": "Olá"}]
    response = client.chat(messages)
    assert "**💡 Conceito**" in response
    assert "**❓ Pergunta Guiada**" in response
    assert "**🔍 Dica Progressiva**" in response


def test_ollama_resolve_best_model_default():
    client = OllamaClient(base_url="http://127.0.0.1:55555")
    best_model = client.resolve_best_model()
    assert best_model == client.default_model
