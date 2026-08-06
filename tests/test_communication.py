import pytest
from unittest.mock import MagicMock
from src.communication import ConsoleController

def test_console_controller_callbacks():
    controller = ConsoleController()
    
    # Mock the persistent shell to prevent actual execution
    controller.shell = MagicMock()
    controller.shell.execute_line.return_value = ("stdout_result", "stderr_result")
    
    # Flags to check if callbacks were called
    start_called = False
    finish_called = False
    finish_args = None
    
    def on_start():
        nonlocal start_called
        start_called = True
        
    def on_finish(stdout, stderr, returncode):
        nonlocal finish_called, finish_args
        finish_called = True
        finish_args = (stdout, stderr, returncode)
        
    controller.on_execution_start = on_start
    controller.on_execution_finish = on_finish
    
    controller.execute_code("print('hello')")
    
    assert start_called is True
    assert finish_called is True
    assert finish_args == ("stdout_result", "stderr_result", 1) # returncode 1 because stderr is not empty
    controller.shell.execute_line.assert_called_once_with("print('hello')")

def test_console_controller_no_stderr():
    controller = ConsoleController()
    controller.shell = MagicMock()
    controller.shell.execute_line.return_value = ("success", "")
    
    finish_args = None
    def on_finish(stdout, stderr, returncode):
        nonlocal finish_args
        finish_args = (stdout, stderr, returncode)
        
    controller.on_execution_finish = on_finish
    controller.execute_code("print('hello')")
    
    assert finish_args == ("success", "", 0) # returncode 0 because stderr is empty
