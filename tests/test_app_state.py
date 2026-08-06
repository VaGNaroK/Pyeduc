import pytest
from unittest.mock import MagicMock, patch
import flet as ft
from src.ui.app_state import AppState

@pytest.fixture
def mock_managers():
    # Patch all the heavy managers instantiated in AppState.__init__
    with patch('src.ui.app_state.ContentManager') as MockCM, \
         patch('src.ui.app_state.ProgressManager') as MockPM, \
         patch('src.ui.app_state.ConsoleController') as MockCC, \
         patch('src.ui.app_state.OllamaClient') as MockOC, \
         patch('src.ui.app_state.LessonRAG') as MockRAG:
        
        # Setup ContentManager mock to return dummy lessons
        mock_cm_instance = MockCM.return_value
        mock_cm_instance.get_all_lessons.return_value = [
            {"id": 0, "title": "Aula 0"},
            {"id": 1, "title": "Aula 1"},
            {"id": 1000, "title": "Aula 1000"}  # Simulating a gap/custom ID
        ]
        
        yield {
            "cm": mock_cm_instance,
            "pm": MockPM.return_value,
            "cc": MockCC.return_value,
            "oc": MockOC.return_value,
            "rag": MockRAG.return_value
        }

@pytest.fixture
def app_state(mock_managers):
    page = MagicMock(spec=ft.Page)
    return AppState(page)

def test_app_state_initialization(app_state, mock_managers):
    assert app_state.current_lesson_idx == 0
    assert len(app_state.all_lessons) == 3
    assert app_state.current_lesson["id"] == 0

def test_get_lesson_index_by_id(app_state):
    # Test valid normal ID
    assert app_state.get_lesson_index_by_id(1) == 1
    
    # Test valid ID with a gap
    assert app_state.get_lesson_index_by_id(1000) == 2
    
    # Test invalid ID (should fallback to 0 as per current implementation)
    assert app_state.get_lesson_index_by_id(999) == 0

def test_current_lesson_property(app_state):
    app_state.current_lesson_idx = 1
    assert app_state.current_lesson["id"] == 1
    
    app_state.current_lesson_idx = 2
    assert app_state.current_lesson["id"] == 1000
    
    # Test out of bounds
    app_state.current_lesson_idx = 5
    assert app_state.current_lesson is None

def test_notify_lesson_changed(app_state, mock_managers):
    mock_pm = mock_managers["pm"]
    mock_pm.get_completed_activities.return_value = [0, 1]
    
    # Register a callback
    cb = MagicMock()
    app_state.on_lesson_changed_callbacks.append(cb)
    
    # Change lesson to index 2 (ID 1000)
    app_state.notify_lesson_changed(2)
    
    assert app_state.current_lesson_idx == 2
    mock_pm.set_current_lesson.assert_called_with(1000)
    mock_pm.get_completed_activities.assert_called_with(1000)
    assert app_state.completed_exercises_indices == {0, 1}
    cb.assert_called_once()
