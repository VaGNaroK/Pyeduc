import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from content_manager import ContentManager


def test_load_real_lessons():
    cm = ContentManager()
    assert cm.get_lesson_count() > 0

    welcome_lesson = cm.get_lesson(0)
    assert welcome_lesson is not None
    assert welcome_lesson["title"] == "Bem-vindo ao Pyeduc!"
    assert welcome_lesson["type"] == "presentation"

    lesson_1 = cm.get_lesson(1)
    assert lesson_1 is not None
    assert "type" in lesson_1
    assert "content" in lesson_1


def test_lesson_navigation():
    cm = ContentManager()
    next_l = cm.get_next_lesson(0)
    assert next_l is not None
    assert next_l["id"] == 1

    prev_l = cm.get_previous_lesson(1)
    assert prev_l is not None
    assert prev_l["id"] == 0

    assert cm.get_previous_lesson(0) is None


def test_missing_file_handling(tmp_path):
    fake_dir = tmp_path / "non_existent_dir"
    cm = ContentManager(content_dir=str(fake_dir))
    assert len(cm.lessons) == 0
    assert cm.get_lesson_count() == 0


def test_expanded_curriculum_lessons():
    cm = ContentManager()
    assert cm.get_lesson_count() >= 36

    new_lesson_ids = range(3, 12)
    for lid in new_lesson_ids:
        lesson = cm.get_lesson(lid)
        assert lesson is not None, f"Lição {lid} deveria existir"
        assert "type" in lesson
        assert "content" in lesson

