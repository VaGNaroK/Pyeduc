"""
Camada de Execução de Código: Execução persistente em subprocesso interativo
"""
import subprocess
import sys
import threading
import queue
import time
from typing import Tuple
from logger import logger


class PersistentPythonShell:
    """
    Mantém uma sessão Python interativa persistente rodando em segundo plano.
    Permite executar comandos preservando o estado das variáveis.
    """
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.process = None
        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()
        self.start()

    def start(self):
        """Inicia o interpretador interativo em um subprocesso"""
        if self.process:
            self.close()

        # Inicia o interpretador interativo (-i) em modo unbuffered (-u) e silencioso (-q)
        self.process = subprocess.Popen(
            [sys.executable, "-i", "-q", "-u"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        logger.info("Interpretador Python interativo iniciado.")
        
        # Threads daemon para consumir a saída sem travar a aplicação
        self.stdout_thread = threading.Thread(
            target=self._read_stream, 
            args=(self.process.stdout, self.stdout_queue), 
            daemon=True
        )
        self.stderr_thread = threading.Thread(
            target=self._read_stream, 
            args=(self.process.stderr, self.stderr_queue), 
            daemon=True
        )
        self.stdout_thread.start()
        self.stderr_thread.start()

    def _read_stream(self, stream, q):
        try:
            for line in iter(stream.readline, ''):
                q.put(line)
        except Exception:
            pass

    def execute_line(self, code: str) -> Tuple[str, str]:
        """
        Executa um código no subprocesso e retorna (stdout, stderr).
        Esta função é thread-safe e deve ser executada a partir de um Worker Thread.
        """
        if not self.process or self.process.poll() is not None:
            self.start()

        # 1. Valida a sintaxe localmente no processo principal para evitar travar o REPL
        try:
            # Compila como 'exec' para aceitar blocos de código multi-linha
            compile(code, '<stdin>', 'exec')
        except SyntaxError as e:
            import traceback
            tb = traceback.format_exception_only(type(e), e)
            return "", "".join(tb)

        # 2. Prepara delimitadores para demarcar o fim da saída
        delimiter_out = "---CMD-BOUND-OUT---"
        delimiter_err = "---CMD-BOUND-ERR---"
        
        # Adicionamos novas linhas extras (\n\n) para encerrar qualquer bloco (ex: loops/condições)
        # e escrevemos os prints delimitadores no stdout e stderr com flush explícito.
        # Atribuímos a '_' para evitar que o REPL interativo imprima o número de caracteres escritos (ex: '20').
        full_input = (
            f"{code}\n\n"
            f"import sys\n"
            f"_ = sys.stdout.write('{delimiter_out}\\n'); _ = sys.stdout.flush()\n"
            f"_ = sys.stderr.write('{delimiter_err}\\n'); _ = sys.stderr.flush()\n"
        )
        
        # Aguarda 50ms para que qualquer saída pendente no pipe do OS seja lida pela thread e chegue às filas
        time.sleep(0.05)
        
        # Esvazia filas antigas
        while not self.stdout_queue.empty():
            self.stdout_queue.get()
        while not self.stderr_queue.empty():
            self.stderr_queue.get()

        # 3. Envia o código ao processo
        try:
            self.process.stdin.write(full_input)
            self.process.stdin.flush()
        except OSError:
            # Subprocesso morreu, reinicia e tenta novamente
            self.start()
            try:
                self.process.stdin.write(full_input)
                self.process.stdin.flush()
            except OSError as e:
                logger.error(f"Erro de E/S fatal no interpretador: {e}")
                return "", f"Erro de E/S no interpretador: {e}"

        # 4. Lê as saídas até receber ambos os delimitadores
        stdout_lines = []
        stderr_lines = []
        out_finished = False
        err_finished = False
        
        start_time = time.time()
        while (not out_finished or not err_finished) and (time.time() - start_time < self.timeout):
            # Processa stdout
            while not self.stdout_queue.empty():
                line = self.stdout_queue.get()
                if delimiter_out in line:
                    out_finished = True
                else:
                    stdout_lines.append(line)

            # Processa stderr
            while not self.stderr_queue.empty():
                line = self.stderr_queue.get()
                if delimiter_err in line:
                    err_finished = True
                elif line.strip() in (">>>", "..."):
                    # Descarta prompts interativos padrão do terminal
                    pass
                else:
                    stderr_lines.append(line)

            time.sleep(0.01)

        # Timeout check
        if time.time() - start_time >= self.timeout:
            # Se deu timeout, provavelmente o código travou (ex: loop infinito)
            # Reiniciamos o interpretador para limpar o estado
            logger.warning(f"Timeout de execução ({self.timeout}s). Código possivelmente em loop infinito. Resetando interpretador.")
            self.start()
            return "", f"Erro: Execução expirou após {self.timeout} segundos (Interpretador resetado para segurança)."

        stdout = "".join(stdout_lines)
        stderr = "".join(stderr_lines)

        # Limpa eventuais resíduos de prompts (>>> ou ...) no final do stderr
        while not self.stderr_queue.empty():
            line = self.stderr_queue.get()
            if line.strip() not in (">>>", "..."):
                stderr += line

        return stdout.rstrip("\n"), stderr.rstrip("\n")

    def close(self):
        """Fecha o subprocesso de forma limpa"""
        if self.process:
            try:
                self.process.stdin.write("exit()\n")
                self.process.stdin.flush()
            except Exception:
                pass
            self.process.terminate()
            self.process = None
            logger.info("Interpretador Python interativo encerrado.")


class PythonExecutor:
    """Classe legada mantida para compatibilidade de testes/APIs"""
    def __init__(self, timeout: int = 5):
        self.shell = PersistentPythonShell(timeout)

    def execute(self, code: str) -> Tuple[str, str, int]:
        stdout, stderr = self.shell.execute_line(code)
        # Retorna código de erro fictício dependendo de ter stderr ou não
        returncode = 1 if stderr else 0
        return stdout, stderr, returncode
