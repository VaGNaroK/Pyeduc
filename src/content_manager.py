"""
Camada de Conteúdo Didático: Gerenciamento de lições
"""
import json
from pathlib import Path
from typing import List, Optional, Dict, Any


class ContentManager:
    def __init__(self, content_file: str = "content/lessons.json"):
        self.content_file = Path(content_file)
        self.lessons = self._load_lessons()

    def _load_lessons(self) -> List[Dict[str, Any]]:
        """Carrega as lições do arquivo JSON"""
        if not self.content_file.exists():
            return []
        
        with open(self.content_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("lessons", [])

    def get_lesson(self, lesson_id: int) -> Optional[Dict[str, Any]]:
        """Retorna uma lição pelo ID"""
        for lesson in self.lessons:
            if lesson["id"] == lesson_id:
                return lesson
        return None

    def get_all_lessons(self) -> List[Dict[str, Any]]:
        """Retorna todas as lições"""
        return self.lessons

    def get_lesson_count(self) -> int:
        """Retorna o número de lições disponíveis"""
        return len(self.lessons)

    def get_lesson_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Retorna uma lição pelo índice"""
        if 0 <= index < len(self.lessons):
            return self.lessons[index]
        return None

    def get_next_lesson(self, current_id: int) -> Optional[Dict[str, Any]]:
        """Retorna a próxima lição após a lição atual"""
        current_index = None
        for i, lesson in enumerate(self.lessons):
            if lesson["id"] == current_id:
                current_index = i
                break
        
        if current_index is not None and current_index + 1 < len(self.lessons):
            return self.lessons[current_index + 1]
        return None

    def get_previous_lesson(self, current_id: int) -> Optional[Dict[str, Any]]:
        """Retorna a lição anterior à lição atual"""
        current_index = None
        for i, lesson in enumerate(self.lessons):
            if lesson["id"] == current_id:
                current_index = i
                break
        
        if current_index is not None and current_index - 1 >= 0:
            return self.lessons[current_index - 1]
        return None
