"""
Camada de Persistência: Gerenciamento de progresso do usuário via SQLite
"""
import sqlite3
import json
from logger import logger
from pathlib import Path
from typing import List, Optional

class ProgressManager:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            user_data = Path.home() / ".pyeduc"
            user_data.mkdir(exist_ok=True)
            self.data_dir = user_data

        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / "pyeduc.db"
        self.current_user_id: Optional[int] = None
        self.current_username: Optional[str] = None
        self._init_db()

    def _init_db(self):
        """Inicializa as tabelas do banco de dados SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Tabela de Usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            # Tabela de Progresso
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progress (
                    user_id INTEGER,
                    lesson_id INTEGER,
                    completed BOOLEAN DEFAULT 0,
                    PRIMARY KEY (user_id, lesson_id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            # Tabela de Estado da Sessão
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_state (
                    user_id INTEGER PRIMARY KEY,
                    current_lesson INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()

    def register(self, username: str, password: str) -> bool:
        """Registra um novo usuário no banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                user_id = cursor.lastrowid
                # Aula default inicial = 0 (Bem-vindo)
                cursor.execute('INSERT INTO user_state (user_id, current_lesson) VALUES (?, 0)', (user_id,))
                conn.commit()
                logger.info(f"Usuário registrado com sucesso: {username} (ID: {user_id})")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Tentativa de registrar usuário já existente: {username}")
            return False # Usuário já existe

    def login(self, username: str, password: str) -> bool:
        """Faz login do usuário"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
            result = cursor.fetchone()
            if result:
                self.current_user_id = result[0]
                self.current_username = username
                logger.info(f"Login efetuado: {username}")
                return True
            logger.warning(f"Falha de login para usuário: {username}")
            return False

    def is_logged_in(self) -> bool:
        return self.current_user_id is not None

    def get_current_username(self) -> Optional[str]:
        """Retorna o nome do usuário logado"""
        return self.current_username
        
    def logout(self):
        logger.info(f"Logout efetuado: {self.current_username}")
        self.current_user_id = None
        self.current_username = None

    def mark_lesson_completed(self, lesson_id: int) -> None:
        """Marca uma lição como concluída para o usuário logado"""
        if not self.is_logged_in(): return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO progress (user_id, lesson_id, completed) 
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, lesson_id) DO UPDATE SET completed=1
            ''', (self.current_user_id, lesson_id))
            conn.commit()
            logger.info(f"Usuário {self.current_username} concluiu a lição {lesson_id}")

    def set_current_lesson(self, lesson_id: int) -> None:
        """Define a lição atual para o usuário logado"""
        if not self.is_logged_in(): return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_state (user_id, current_lesson) 
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET current_lesson=?
            ''', (self.current_user_id, lesson_id, lesson_id))
            conn.commit()

    def get_current_lesson(self) -> int:
        """Retorna a lição atual do usuário logado"""
        if not self.is_logged_in(): return 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT current_lesson FROM user_state WHERE user_id = ?', (self.current_user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_completed_lessons(self) -> List[int]:
        """Retorna lista de lições concluídas do usuário logado"""
        if not self.is_logged_in(): return []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT lesson_id FROM progress WHERE user_id = ? AND completed = 1', (self.current_user_id,))
            return [row[0] for row in cursor.fetchall()]

    def is_lesson_completed(self, lesson_id: int) -> bool:
        """Verifica se uma lição foi concluída pelo usuário logado"""
        if not self.is_logged_in(): return False
        return lesson_id in self.get_completed_lessons()

    def reset_progress(self) -> None:
        """Reseta o progresso do usuário logado"""
        if not self.is_logged_in(): return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM progress WHERE user_id = ?', (self.current_user_id,))
            cursor.execute('UPDATE user_state SET current_lesson = 0 WHERE user_id = ?', (self.current_user_id,))
            conn.commit()

    def export_progress(self, filepath: str) -> bool:
        """Exporta o progresso do usuário logado para um arquivo JSON"""
        if not self.is_logged_in():
            logger.warning("Tentativa de exportar progresso sem usuário logado.")
            return False
        try:
            data = {
                "version": "1.0",
                "username": self.current_username,
                "current_lesson": self.get_current_lesson(),
                "completed_lessons": self.get_completed_lessons()
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Progresso exportado com sucesso para: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao exportar progresso: {e}")
            return False

    def import_progress(self, filepath: str) -> bool:
        """Importa o progresso do usuário a partir de um arquivo JSON"""
        if not self.is_logged_in():
            logger.warning("Tentativa de importar progresso sem usuário logado.")
            return False
        path = Path(filepath)
        if not path.exists():
            logger.error(f"Arquivo de importação não encontrado: {filepath}")
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not isinstance(data, dict) or "completed_lessons" not in data or "current_lesson" not in data:
                logger.error("Formato de arquivo de progresso inválido.")
                return False

            completed_lessons = data.get("completed_lessons", [])
            current_lesson = data.get("current_lesson", 0)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for lesson_id in completed_lessons:
                    cursor.execute('''
                        INSERT INTO progress (user_id, lesson_id, completed)
                        VALUES (?, ?, 1)
                        ON CONFLICT(user_id, lesson_id) DO UPDATE SET completed=1
                    ''', (self.current_user_id, lesson_id))
                
                cursor.execute('''
                    INSERT INTO user_state (user_id, current_lesson)
                    VALUES (?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET current_lesson=?
                ''', (self.current_user_id, current_lesson, current_lesson))
                conn.commit()

            logger.info(f"Progresso importado com sucesso de: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao importar progresso: {e}")
            return False

