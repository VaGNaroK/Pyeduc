import pytest
from src.rag_module import LessonRAG

@pytest.fixture
def sample_lessons():
    return [
        {
            "id": 1,
            "title": "Introdução ao Python",
            "content": "Python é uma linguagem de programação interpretada. É muito fácil de aprender.",
        },
        {
            "id": 2,
            "title": "Variáveis",
            "sections": [
                {"content": "Variáveis guardam dados como textos e inteiros."}
            ],
            "ai_context": {
                "key_concepts": ["memória", "tipagem", "valores"]
            }
        },
        {
            "id": 3,
            "title": "Operadores de Fluxo",
            "content": "O if serve para condições e o for para repetições.",
        }
    ]

def test_rag_empty_query(sample_lessons):
    rag = LessonRAG(sample_lessons)
    result = rag.get_relevant_context("")
    assert result == ""

def test_rag_no_lessons():
    rag = LessonRAG([])
    result = rag.get_relevant_context("python")
    assert result == ""

def test_rag_finds_relevant_lesson(sample_lessons):
    rag = LessonRAG(sample_lessons)
    # The term 'interpretada' should match Lesson 1
    result = rag.get_relevant_context("O que é uma linguagem interpretada?")
    assert "Introdução ao Python" in result
    assert "Variáveis" not in result

def test_rag_sections_and_ai_context(sample_lessons):
    rag = LessonRAG(sample_lessons)
    # The term 'memória' is in ai_context, and 'textos' in sections
    result = rag.get_relevant_context("Como as variáveis usam a memória para textos?")
    assert "Variáveis" in result
    assert "Introdução ao Python" not in result

def test_rag_future_lesson_blocking(sample_lessons):
    rag = LessonRAG(sample_lessons)
    # se o current_lesson for 2, a lição 3 não deve retornar mesmo se houver match forte.
    # vamos buscar "condições" que existe apenas na lição 3
    result = rag.get_relevant_context("condições repetições fluxo?", current_lesson_id=2)
    assert result == ""
    
    # se estivermos na lição 3, ela pode retornar
    result2 = rag.get_relevant_context("condições repetições fluxo?", current_lesson_id=3)
    assert "Operadores de Fluxo" in result2

def test_rag_max_chunks(sample_lessons):
    # Crio lições extras para testar o limite
    many_lessons = sample_lessons + [
        {"id": 4, "title": "Outro sobre Python", "content": "Python também é orientado a objetos."},
        {"id": 5, "title": "Mais Python", "content": "Python roda no Windows e Linux."}
    ]
    rag = LessonRAG(many_lessons)
    result = rag.get_relevant_context("python", max_chunks=2)
    # Pode haver até 2 separadores " | ", logo no máximo 2 lições
    count_lessons = result.count("Lição [")
    assert count_lessons <= 2
