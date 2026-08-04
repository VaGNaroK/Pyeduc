import sys
from pathlib import Path

# Garante que o diretório src esteja no sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from executor import PersistentPythonShell


def test_executor_basic_eval():
    shell = PersistentPythonShell(timeout=2)
    try:
        stdout, stderr = shell.execute_line("x = 42")
        assert stderr == ""

        stdout, stderr = shell.execute_line("print(x)")
        assert "42" in stdout
        assert stderr == ""
    finally:
        shell.close()


def test_executor_syntax_error():
    shell = PersistentPythonShell(timeout=2)
    try:
        stdout, stderr = shell.execute_line("if True")
        assert stdout == ""
        assert "SyntaxError" in stderr
    finally:
        shell.close()


def test_executor_multiline_block():
    shell = PersistentPythonShell(timeout=2)
    try:
        shell.execute_line("def soma(a, b):\n    return a + b\n")
        stdout, stderr = shell.execute_line("print(soma(10, 20))")
        assert "30" in stdout
        assert stderr == ""
    finally:
        shell.close()


def test_executor_security_blocks_import_os():
    shell = PersistentPythonShell(timeout=2)
    try:
        stdout, stderr = shell.execute_line("import os\nprint(os.getcwd())")
        assert stdout == ""
        assert "Erro de Segurança" in stderr
        assert "módulo 'os' está bloqueado" in stderr

        stdout, stderr = shell.execute_line("from subprocess import Popen")
        assert stdout == ""
        assert "Erro de Segurança" in stderr
        assert "módulo 'subprocess' está bloqueado" in stderr
    finally:
        shell.close()


def test_executor_security_blocks_eval_exec():
    shell = PersistentPythonShell(timeout=2)
    try:
        stdout, stderr = shell.execute_line("eval('1 + 1')")
        assert stdout == ""
        assert "Erro de Segurança" in stderr
        assert "função 'eval()' está desativada" in stderr
    finally:
        shell.close()


def test_executor_allows_math_and_open():
    is_safe_math, _ = PersistentPythonShell.validate_security("import math\nprint(math.sqrt(16))")
    assert is_safe_math is True

    is_safe_open, _ = PersistentPythonShell.validate_security("with open('test.txt', 'w') as f:\n    f.write('hi')")
    assert is_safe_open is True

