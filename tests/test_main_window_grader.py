import pytest
from unittest.mock import MagicMock
import flet as ft
from src.main_window import PyeducApp


# Criamos um mock da classe de Row para simular os exercícios pendentes
class MockRow:
    def __init__(self, data_expected):
        self.data = data_expected
        # Simula o ícone na UI que o AutoGrader checa e pinta de verde
        self.icon_mock = MagicMock(spec=ft.Icon)
        self.icon_mock.icon = ft.Icons.RADIO_BUTTON_UNCHECKED
        self.controls = [self.icon_mock]

@pytest.fixture
def main_window_mock():
    # Evita que o __init__ rode e inicie o Flet de verdade
    PyeducApp.__init__ = lambda self, page: None
    window = PyeducApp(MagicMock())
    
    # Mockando o editor console e o painel de mensagens
    window.editor_console = MagicMock()
    window.editor_console.smart_messages_panel = MagicMock()
    
    # Mockando o state e o content_manager interno
    window.state = MagicMock()
    window.state.content_manager = MagicMock()
    window.state.content_manager.get_ui_string = lambda k, default: default
    window.state.current_lesson = {"id": 1}
    window.state.completed_exercises_indices = set()
    
    # Mockando o lesson view e os active_exercises_rows
    window.lesson_view = MagicMock()
    
    return window

def test_autograder_exact_match(main_window_mock):
    # Simulando um exercício que espera "Python" (case-sensitive)
    row = MockRow("Python")
    main_window_mock.lesson_view.active_exercises_rows = [row]
    
    # Chamando on_exec_result com a saída exata "Python"
    main_window_mock.on_exec_result("Python")
    
    # O ícone deve ser setado para CHECK_CIRCLE (Sucesso)
    assert row.controls[0].icon == ft.Icons.CHECK_CIRCLE
    assert row.controls[0].color == "#10b981"
    
    # A mensagem deve ser verde (sucesso)
    assert main_window_mock.editor_console.smart_messages_panel.bgcolor == "#15803d"

def test_autograder_fuzzy_match(main_window_mock):
    # Simulando um exercício que espera "Python"
    row = MockRow("Python")
    main_window_mock.lesson_view.active_exercises_rows = [row]
    
    # Chamando on_exec_result com "python." (letra minúscula e ponto - MATCH FUZZY)
    main_window_mock.on_exec_result("python.")
    
    # O ícone DEVE ficar CHECK_CIRCLE internamente (porque fuzzy_match tenta aprovar ou pelo menos alertar)
    # Ah, espere: o fuzzy_match pinta de verde o icone se acertar mas avisa "Quase lá!" no painel
    assert row.controls[0].icon == ft.Icons.CHECK_CIRCLE
    
    # Mas a cor do painel de mensagens DEVE ser LARANJA (#b45309)
    assert main_window_mock.editor_console.smart_messages_panel.bgcolor == "#b45309"
    # E a mensagem deve ser "Quase lá!"
    content_text = main_window_mock.editor_console.smart_messages_panel.content.value
    assert "Quase lá" in content_text

def test_autograder_no_match(main_window_mock):
    # Simulando um exercício que espera "Estudante"
    row = MockRow("Estudante")
    main_window_mock.lesson_view.active_exercises_rows = [row]
    
    # Chamando on_exec_result com uma saída totalmente diferente "Professor"
    main_window_mock.on_exec_result("Professor")
    
    # O ícone NÃO deve mudar
    assert row.controls[0].icon == ft.Icons.RADIO_BUTTON_UNCHECKED
    
    # A cor do painel de mensagens DEVE ser LARANJA (#b45309) avisando incompatibilidade
    assert main_window_mock.editor_console.smart_messages_panel.bgcolor == "#b45309"
    content_column = main_window_mock.editor_console.smart_messages_panel.content
    assert "Saída não corresponde" in content_column.controls[0].value

def test_autograder_multiline_fuzzy(main_window_mock):
    # Exercício que espera 3 linhas (ex: print triplo)
    row = MockRow("1\n2\n3")
    main_window_mock.lesson_view.active_exercises_rows = [row]
    
    # O aluno enviou com pontos (ex: 1. 2. 3.)
    main_window_mock.on_exec_result("1.\n2.\n3.")
    
    assert row.controls[0].icon == ft.Icons.CHECK_CIRCLE
    assert main_window_mock.editor_console.smart_messages_panel.bgcolor == "#b45309"
