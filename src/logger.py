import logging
from logging.handlers import RotatingFileHandler
import os
import sys

def setup_logger(name="PyeducLogger", log_file="logs/app.log", level=logging.INFO):
    """
    Configura e retorna um logger centralizado para o aplicativo Pyeduc.
    """
    # Cria o diretório de logs se não existir
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Se o logger já tem handlers, evitamos duplicação
    if logger.handlers:
        return logger

    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para arquivo rotativo (máximo 5MB por arquivo, guarda até 5 arquivos antigos)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para Console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Instância global para facilitar importações
logger = setup_logger()
