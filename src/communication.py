"""
Camada de Comunicação: Callbacks e Controle (Flet)
"""
from typing import Callable, Optional
from executor import PersistentPythonShell


class ConsoleController:
    """Controla a interação entre a interface Flet e o motor de execução"""
    
    def __init__(self):
        self.shell = PersistentPythonShell(timeout=5)
        
        # Callbacks que a interface (gui.py) irá registrar
        self.on_execution_start: Optional[Callable[[], None]] = None
        self.on_execution_finish: Optional[Callable[[str, str, int], None]] = None
    
    def execute_code(self, code: str):
        """
        Executa o código chamando o shell persistente.
        Como o Flet executa os manipuladores de evento de cliques em threads 
        separadas, podemos bloquear esta função sem travar a UI.
        """
        # Avisa a UI que a execução começou (ex: para desabilitar o botão e limpar console)
        if self.on_execution_start:
            self.on_execution_start()
            
        # Bloqueia até a execução terminar (seguro no Flet)
        stdout, stderr = self.shell.execute_line(code)
        returncode = 1 if stderr else 0
        
        # Avisa a UI que a execução terminou para que possa exibir os resultados
        if self.on_execution_finish:
            self.on_execution_finish(stdout, stderr, returncode)
