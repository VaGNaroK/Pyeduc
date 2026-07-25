import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from progress_manager import ProgressManager


@pytest.fixture
def progress_mgr(tmp_path):
    # Cria uma instância usando um diretório temporário isolado
    mgr = ProgressManager(data_dir=str(tmp_path))
    return mgr


def test_user_registration_and_login(progress_mgr):
    assert progress_mgr.register("aluno_teste", "senha123") is True
    # Usuário duplicado deve falhar
    assert progress_mgr.register("aluno_teste", "senha123") is False

    assert progress_mgr.login("aluno_teste", "senha123") is True
    assert progress_mgr.is_logged_in() is True
    assert progress_mgr.get_current_username() == "aluno_teste"

    # Login incorreto
    assert progress_mgr.login("aluno_teste", "senha_errada") is False


def test_lesson_completion_and_state(progress_mgr):
    progress_mgr.register("aluno_1", "pass")
    progress_mgr.login("aluno_1", "pass")

    assert progress_mgr.get_current_lesson() == 0
    assert progress_mgr.get_completed_lessons() == []

    progress_mgr.mark_lesson_completed(1)
    progress_mgr.mark_lesson_completed(2)
    progress_mgr.set_current_lesson(3)

    assert progress_mgr.get_completed_lessons() == [1, 2]
    assert progress_mgr.is_lesson_completed(1) is True
    assert progress_mgr.is_lesson_completed(3) is False
    assert progress_mgr.get_current_lesson() == 3

    progress_mgr.reset_progress()
    assert progress_mgr.get_completed_lessons() == []
    assert progress_mgr.get_current_lesson() == 0


def test_export_and_import_progress(progress_mgr, tmp_path):
    progress_mgr.register("aluno_export", "pass123")
    progress_mgr.login("aluno_export", "pass123")

    progress_mgr.mark_lesson_completed(1)
    progress_mgr.mark_lesson_completed(5)
    progress_mgr.set_current_lesson(6)

    export_file = tmp_path / "backup_progresso.json"
    assert progress_mgr.export_progress(str(export_file)) is True
    assert export_file.exists()

    # Valida conteúdo do arquivo exportado
    with open(export_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["username"] == "aluno_export"
    assert data["current_lesson"] == 6
    assert set(data["completed_lessons"]) == {1, 5}

    # Novo banco/gerenciador para simular restauração
    new_mgr = ProgressManager(data_dir=str(tmp_path / "novo_db"))
    new_mgr.register("aluno_novo", "pass123")
    new_mgr.login("aluno_novo", "pass123")

    assert new_mgr.get_completed_lessons() == []
    assert new_mgr.import_progress(str(export_file)) is True
    assert set(new_mgr.get_completed_lessons()) == {1, 5}
    assert new_mgr.get_current_lesson() == 6
