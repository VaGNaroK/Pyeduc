import flet as ft
from content_manager import ContentManager
from progress_manager import ProgressManager
from communication import ConsoleController
from llm_client import OllamaClient
from rag_module import LessonRAG
import config

class AppState:
    """
    Holds global state for the application.
    Shared across all UI components.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        
        # Managers
        self.content_manager = ContentManager()
        self.progress_manager = ProgressManager("data")
        self.console_controller = ConsoleController()
        
        self.all_lessons = self.content_manager.get_all_lessons()
        self.current_lesson_idx = 0
        self.admin_mode_enabled = config.ADMIN_MODE
        
        # AI and RAG
        self.ollama_client = OllamaClient()
        self.lesson_rag = LessonRAG(self.all_lessons)
        self.is_ai_generating = False
        self.ai_chat_history = []
        
        # Font settings
        self.font_sizes = [11, 13, 15, 18, 22, 28]
        self.current_font_idx = 2
        
        # Callbacks for reactive updates
        self.on_lesson_changed_callbacks = []
        self.on_font_size_changed_callbacks = []
        self.on_progress_changed_callbacks = []
        
        # Transient state for the current lesson
        self.completed_exercises_indices = set()
        
    @property
    def current_lesson(self):
        if self.current_lesson_idx is not None and 0 <= self.current_lesson_idx < len(self.all_lessons):
            return self.all_lessons[self.current_lesson_idx]
        return None
        
    def get_lesson_index_by_id(self, lesson_id: int) -> int:
        for idx, lesson in enumerate(self.all_lessons):
            if lesson.get("id", idx) == lesson_id:
                return idx
        return 0
        
    @property
    def current_font_size(self):
        return self.font_sizes[self.current_font_idx]

    def notify_lesson_changed(self, new_idx: int = None):
        if new_idx is not None:
            self.current_lesson_idx = new_idx
            lesson_id = self.current_lesson.get("id", self.current_lesson_idx)
            self.progress_manager.set_current_lesson(lesson_id)
            
            # Carrega do banco de dados o estado parcial desta lição
            saved_activities = self.progress_manager.get_completed_activities(lesson_id)
            self.completed_exercises_indices = set(saved_activities)
            
        for cb in self.on_lesson_changed_callbacks:
            cb()
            
    def notify_font_size_changed(self):
        for cb in self.on_font_size_changed_callbacks:
            cb()
            
    def notify_progress_changed(self):
        for cb in self.on_progress_changed_callbacks:
            cb()
