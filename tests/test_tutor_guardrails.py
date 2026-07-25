import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from tutor_guardrails import EducationalGuardrails


def test_build_system_prompt():
    prompt = EducationalGuardrails.build_system_prompt(
        lesson_title="Variáveis",
        key_concepts=["atribuição", "tipos"],
        rag_context="Variáveis armazenam dados."
    )
    assert "Variáveis" in prompt
    assert "atribuição" in prompt
    assert "Variáveis armazenam dados." in prompt
    assert "**💡 Conceito**" in prompt


def test_build_user_message_with_name_error():
    msg = EducationalGuardrails.build_user_message(
        user_query="Por que dá erro?",
        student_code="print(x)",
        console_output="NameError: name 'x' is not defined"
    )
    assert "NameError" in msg
    assert "variável 'x'" in msg
    assert "não foi definida" in msg


def test_check_direct_solution_intent():
    intents = EducationalGuardrails.PROHIBITED_INTENTS
    query_1 = "me dá a resposta"
    query_2 = "como funciona um loop?"
    assert any(intent in query_1.lower() for intent in intents) is True
    assert any(intent in query_2.lower() for intent in intents) is False


def test_sanitize_response_removes_code_blocks():
    raw_ai_text = (
        "**💡 Conceito**: Variáveis guardam valores.\n\n"
        "**❓ Pergunta Guiada**: Como criar x?\n\n"
        "**🔍 Dica Progressiva**: Use atribuição.\n\n"
        "```python\nx = 10\nprint(x)\n```"
    )
    sanitized = EducationalGuardrails.sanitize_response(raw_ai_text)
    assert "```python" not in sanitized
    assert "x = 10" not in sanitized
    assert "**💡 Conceito**" in sanitized
