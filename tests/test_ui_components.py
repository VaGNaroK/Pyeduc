import pytest
from unittest.mock import MagicMock, patch
import flet as ft
import sys
import os

# Ensure src is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ui.app_state import AppState
from ui.top_bar import TopBar
from ui.editor_console import EditorConsole
from ui.sidebar import Sidebar
from ui.tutor_panel import TutorPanel
from ui.lesson_view import LessonView
from main_window import PyeducApp

@pytest.fixture(autouse=True)
def mock_flet_update():
    with patch('flet.controls.base_control.BaseControl.update', return_value=None):
        yield

@pytest.fixture
def mock_page():
    page = MagicMock(spec=ft.Page)
    page.session = MagicMock()
    page.overlay = []
    page.window = MagicMock()
    return page

@pytest.fixture
def mock_managers():
    with patch('ui.app_state.ContentManager') as MockCM, \
         patch('ui.app_state.ProgressManager') as MockPM, \
         patch('ui.app_state.ConsoleController') as MockCC, \
         patch('ui.app_state.OllamaClient') as MockOC, \
         patch('ui.app_state.LessonRAG') as MockRAG:
        
        # Setup mock behavior
        cm_instance = MockCM.return_value
        cm_instance.get_all_lessons.return_value = [
            {"id": 0, "title": "Aula 0", "type": "presentation"},
            {"id": 1, "title": "Aula 1", "type": "theory", "quiz": {"question": "Q?", "options": ["A", "B"], "answer": 0}},
            {"id": 2, "title": "Aula 2", "type": "coding", "sections": [{"example": "print(1)", "exercises": [{"description": "Ex 1", "expected_output": "1"}]}]}
        ]
        
        pm_instance = MockPM.return_value
        pm_instance.get_completed_lessons.return_value = [0]
        pm_instance.get_current_lesson.return_value = 0
        
        yield {
            'cm': cm_instance,
            'pm': pm_instance,
            'cc': MockCC.return_value,
            'oc': MockOC.return_value,
            'rag': MockRAG.return_value
        }

@pytest.fixture
def app_state(mock_page, mock_managers):
    return AppState(mock_page)

def test_app_state_initialization(app_state):
    assert len(app_state.all_lessons) == 3
    assert app_state.current_lesson_idx == 0
    assert app_state.current_lesson["id"] == 0
    
def test_app_state_notify_lesson_changed(app_state):
    callback_mock = MagicMock()
    app_state.on_lesson_changed_callbacks.append(callback_mock)
    
    app_state.notify_lesson_changed(1)
    
    assert app_state.current_lesson_idx == 1
    assert app_state.current_lesson["title"] == "Aula 1"
    callback_mock.assert_called_once()
    app_state.progress_manager.set_current_lesson.assert_called_with(1)

def test_top_bar_initialization(app_state):
    on_export = MagicMock()
    on_import = MagicMock()
    on_logout = MagicMock()
    top_bar = TopBar(app_state, on_export, on_import, on_logout)
    
    assert top_bar.visible is False
    assert len(app_state.on_lesson_changed_callbacks) > 0
    
    # Test title update callback
    app_state.notify_lesson_changed(1)
    assert top_bar.title_text.value == "Aula 1"

def test_top_bar_change_font_size(app_state):
    top_bar = TopBar(app_state, MagicMock(), MagicMock(), MagicMock())
    initial_idx = app_state.current_font_idx
    
    # Increase font
    top_bar.change_font_size(1)
    assert app_state.current_font_idx == initial_idx + 1
    
    # Reset font
    top_bar.change_font_size(0, reset=True)
    assert app_state.current_font_idx == 2

def test_editor_console_initialization(app_state):
    on_exec = MagicMock()
    on_ai = MagicMock()
    editor = EditorConsole(app_state, on_exec, on_ai)
    
    # Should attach to font size changes
    assert len(app_state.on_font_size_changed_callbacks) > 0
    
    # Test execution triggers
    editor.console_input.value = "print('hello')"
    editor.handle_execute(None)
    on_exec.assert_called_with("print('hello')")
    
    # Test clear
    editor.console_output.value = "some text"
    editor.handle_clear(None)
    assert editor.console_output.value == ""

def test_sidebar_initialization_and_update(app_state):
    on_select = MagicMock()
    on_ai = MagicMock()
    sidebar = Sidebar(app_state, on_select, on_ai)
    
    # Trigger update
    sidebar.update_ui()
    
    # 3 lessons = 3 buttons in the list view
    assert len(sidebar.lesson_list.controls) == 3
    # First lesson completed (1/3 = 33%)
    assert sidebar.progress_bar.value == (1 / 3)

def test_tutor_panel_clear_chat(app_state):
    tutor = TutorPanel(app_state)
    app_state.ai_chat_history = [{"role": "user", "content": "hi"}]
    tutor.ai_chat_list.controls.append(ft.Text("mock"))
    
    tutor.clear_chat()
    assert len(app_state.ai_chat_history) == 0
    assert len(tutor.ai_chat_list.controls) == 0

def test_lesson_view_render(app_state):
    on_copy = MagicMock()
    view = LessonView(app_state, on_copy)
    
    # Switch to theory lesson
    app_state.current_lesson_idx = 1
    view.render_lesson()
    
    assert view.activity_container.visible is True
    assert view.theory_question.value == "Q?"
    
    # Switch to coding lesson
    app_state.current_lesson_idx = 2
    view.render_lesson()
    
    assert view.activity_container.visible is False
    assert len(view.active_exercises_rows) == 1
    assert view.active_exercises_rows[0].data == "1"

def test_pyeduc_app_orchestrator(mock_page, mock_managers):
    app = PyeducApp(mock_page)
    
    # Check if all components were instantiated
    assert hasattr(app, "sidebar")
    assert hasattr(app, "top_bar")
    assert hasattr(app, "lesson_view")
    assert hasattr(app, "editor_console")
    
    # Initial state should show welcome container and hide others
    assert app.welcome_container.visible is True
    assert app.top_bar.visible is False
    assert app.sidebar.visible is False
    assert app.lesson_view.visible is False
    
    # Simulate a login
    mock_managers['pm'].login.return_value = True
    app.tf_username.value = "admin"
    app.tf_password.value = "admin"
    app.on_login(None)
    
    # Check if layout toggled correctly
    assert app.welcome_container.visible is False
    assert app.sidebar.visible is True
    assert app.top_bar.visible is True
