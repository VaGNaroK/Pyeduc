"""
Camada de Conteúdo Didático: Gerenciamento de lições
"""
import json
from pathlib import Path
from typing import List, Optional, Dict, Any


from logger import logger


class ContentManager:
    def __init__(self, content_dir: Optional[str] = None, lang: str = "pt"):
        self.lang = lang
        self.data = {}
        self.ui_strings = {}
        self.lessons = []
        
        if content_dir:
            self.content_dir = Path(content_dir)
        else:
            base_dir = Path(__file__).resolve().parent.parent
            possible_paths = [
                Path("/app/opt/pyeduc/content"),
                Path("/opt/pyeduc/content"),
                base_dir / "content",
                Path("content"),
                Path.cwd() / "content",
                base_dir / "app" / "content"
            ]
            target_path = possible_paths[0]
            for p in possible_paths:
                if p.exists() and p.is_dir():
                    target_path = p
                    break
            self.content_dir = target_path

        self._load_data()

    def get_available_languages(self) -> List[Dict[str, str]]:
        """Escaneia a pasta content/ em busca de lessons_*.json e extrai os idiomas disponíveis."""
        languages = []
        if not self.content_dir.exists():
            return languages
            
        for file_path in self.content_dir.glob("lessons_*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    meta = data.get("_meta", {})
                    if "lang_code" in meta and "lang_name" in meta:
                        languages.append({
                            "code": meta["lang_code"],
                            "name": meta["lang_name"]
                        })
            except Exception as e:
                logger.error(f"Erro ao ler metadata de {file_path}: {e}")
        
        # Sort so 'pt' comes first, then others alphabetically
        languages.sort(key=lambda x: (x["code"] != "pt", x["name"]))
        return languages

    def _load_data(self):
        """Carrega os dados completos do arquivo JSON correspondente ao idioma"""
        if not self.content_dir.exists():
            logger.error(f"Diretório de lições não encontrado em: {self.content_dir}")
            return
            
        target_file = self.content_dir / f"lessons_{self.lang}.json"
        if not target_file.exists():
            logger.warning(f"Arquivo para idioma '{self.lang}' não encontrado. Fazendo fallback para 'pt'.")
            self.lang = "pt"
            target_file = self.content_dir / "lessons_pt.json"
            
        if not target_file.exists():
            logger.error(f"Nenhum arquivo de lições encontrado no diretório {self.content_dir}")
            return
        
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
                logger.info(f"Dados carregados de {target_file}")
                
                # Update current references
                self.ui_strings = self.data.get("ui", {})
                self.lessons = self.data.get("lessons", [])
        except Exception as e:
            logger.error(f"Erro ao ler arquivo de lições {target_file}: {e}", exc_info=True)

    def set_language(self, lang: str):
        """Atualiza a linguagem e recarrega as referências de UI e lessons lendo o arquivo correspondente"""
        if self.lang != lang:
            self.lang = lang
            self._load_data()
            logger.info(f"Idioma do ContentManager alterado para: {self.lang}")

    def get_ui_string(self, key: str, default: str = "") -> str:
        """Retorna a string da UI correspondente à chave no idioma atual"""
        return self.ui_strings.get(key, default or key)

    def get_lesson(self, lesson_id: int) -> Optional[Dict[str, Any]]:
        """Retorna uma lição pelo ID"""
        for lesson in self.get_all_lessons():
            if lesson["id"] == lesson_id:
                return lesson
        return None

    def get_all_lessons(self) -> List[Dict[str, Any]]:
        """Retorna todas as lições"""
        if not self.lessons:
            self._load_data()
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
