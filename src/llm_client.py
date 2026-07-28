"""
Cliente de comunicação com a API REST do Ollama (IA Local)
Usa urllib.request da biblioteca padrão para evitar dependências extras.
"""

import json
import platform
import shutil
import urllib.request
import urllib.error
from typing import List, Dict, Tuple, Optional
try:
    from config import OLLAMA_BASE_URL, OLLAMA_DEFAULT_MODEL, OLLAMA_TIMEOUT, OLLAMA_KEEP_ALIVE
except ImportError:
    from src.config import OLLAMA_BASE_URL, OLLAMA_DEFAULT_MODEL, OLLAMA_TIMEOUT, OLLAMA_KEEP_ALIVE


class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL, default_model: str = OLLAMA_DEFAULT_MODEL, timeout: int = OLLAMA_TIMEOUT, keep_alive: str = OLLAMA_KEEP_ALIVE):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout
        self.keep_alive = keep_alive
        self.os_name = platform.system()  # Linux, Windows, Darwin


    def is_ollama_installed(self) -> bool:
        """Verifica se o executável do Ollama está instalado no sistema operacional."""
        if shutil.which("ollama"):
            return True
        # Locais comuns no Linux e Windows
        if self.os_name == "Linux" and (shutil.which("/usr/bin/ollama") or shutil.which("/usr/local/bin/ollama")):
            return True
        return False

    def check_health(self, get_ui_string=None) -> Tuple[bool, str]:
        """
        Verifica a instalação no SO e a acessibilidade da API REST do Ollama.
        Retorna (online, mensagem).
        """
        def tr(key, default):
            return get_ui_string(key, default) if get_ui_string else default

        installed = self.is_ollama_installed()
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    models = [m.get("name") for m in data.get("models", [])]
                    if not models:
                        return True, tr("msg_ollama_running_no_models", f"Ollama rodando no {{}}, mas nenhum modelo encontrado.").format(self.os_name)
                    return True, tr("msg_ollama_online", f"Ollama online no {{}} ({{}} modelo(s)).").format(self.os_name, len(models))
                return False, tr("msg_ollama_unexpected", f"Resposta inesperada do Ollama: HTTP {{}}").format(response.status)
        except urllib.error.URLError:
            if not installed:
                return False, tr("msg_ollama_not_installed", f"Sem suporte a Tutor IA (Ollama não instalado no {{}})").format(self.os_name)
            return False, tr("msg_ollama_offline", f"Ollama instalado no {{}}, mas serviço está offline em {{}}").format(self.os_name, self.base_url)
        except Exception as e:
            if not installed:
                return False, tr("msg_ollama_not_installed", f"Sem suporte a Tutor IA (Ollama não instalado no {{}})").format(self.os_name)
            return False, tr("msg_ollama_error", f"Erro ao conectar com o Ollama: {{}}").format(str(e))


    def list_models(self) -> List[str]:
        """
        Retorna a lista de nomes dos modelos instalados no Ollama.
        """
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return [m.get("name") for m in data.get("models", []) if m.get("name")]
        except Exception:
            pass
        return []

    def resolve_best_model(self) -> str:
        """
        Retorna o modelo mais adequado e leve de código disponível no Ollama do usuário.
        Prioriza modelos leves (< 4GB VRAM) especificamente treinados em código.
        """
        installed = self.list_models()
        if not installed:
            return self.default_model

        # Se o modelo padrão configurado estiver instalado, utiliza-o
        if any(self.default_model in m for m in installed):
            return self.default_model

        # Ordem de preferência de modelos leves de código
        preferred_light_models = [
            "qwen2.5-coder:1.5b",
            "qwen2.5-coder:3b",
            "deepseek-coder:1.3b",
            "starcoder2:3b",
            "codellama:7b",
            "codellama:latest"
        ]

        for pref in preferred_light_models:
            for inst in installed:
                if pref in inst:
                    return inst

        # Retorna o primeiro modelo instalado se nenhum preferencial for encontrado
        return installed[0]

    def get_offline_help_message(self, get_ui_string=None) -> str:
        """
        Retorna uma mensagem formatada didaticamente em Markdown orientando o aluno sobre como ativar o Ollama.
        """
        def tr(key, default):
            return get_ui_string(key, default) if get_ui_string else default

        installed = self.is_ollama_installed()
        models = self.list_models()

        if not installed:
            return tr("msg_offline_help_not_installed",
                "**💡 Conceito**: O Tutor IA do Pyeduc funciona localmente no seu computador através do **Ollama**, garantindo privacidade total e uso sem internet.\n\n"
                "**❓ Pergunta Guiada**: Você gostaria de ativar o assistente de IA no seu sistema?\n\n"
                "**🔍 Dica Progressiva**: Siga os passos para ativar:\n"
                "1. Baixe o Ollama em [https://ollama.com](https://ollama.com)\n"
                "2. Abra o terminal ({}) e execute:\n"
                "   `ollama run {}`\n"
                "3. Reenvie sua pergunta no Pyeduc!"
            ).format(self.os_name, self.default_model)
        elif not models:
            return tr("msg_offline_help_no_models",
                "**💡 Conceito**: O serviço Ollama está rodando no seu computador, porém ainda não possui nenhum modelo de código baixado.\n\n"
                "**❓ Pergunta Guiada**: Vamos baixar o modelo recomendado para o Pyeduc?\n\n"
                "**🔍 Dica Progressiva**: Execute no seu terminal:\n"
                "```bash\nollama pull {}\n```\n"
                "Após o término do download, envie sua dúvida novamente!"
            ).format(self.default_model)
        else:
            return tr("msg_offline_help_offline",
                "**💡 Conceito**: O serviço do Ollama está instalado no seu sistema, mas o servidor local está desligado no momento.\n\n"
                "**❓ Pergunta Guiada**: O serviço do Ollama foi iniciado no seu sistema?\n\n"
                "**🔍 Dica Progressiva**: Para ligar o serviço local do Ollama, execute no terminal:\n"
                "```bash\nollama run {}\n```\n"
                "Assim que a mensagem de boas-vindas aparecer, pergunte novamente ao Tutor IA!"
            ).format(self.default_model)

    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, keep_alive: Optional[str] = None, options: Optional[Dict] = None, get_ui_string=None) -> str:
        """
        Envia um histórico de mensagens para a API /api/chat do Ollama.
        messages = [{"role": "system"|"user"|"assistant", "content": "..."}]
        """
        target_model = model or self.resolve_best_model()
        target_keep_alive = keep_alive or self.keep_alive
        
        default_options = {
            "temperature": 0.1,  # Temperatura muito baixa para precisão total sem repetição
            "top_p": 0.9,
            "num_ctx": 4096,
            "num_predict": 220,  # Garante espaço completo para os 3 tópicos didáticos
            "stop": [
                "\nResposta:", "\nExplicação:", "\nCódigo corrigido", "\nCorrigindo",
                "\nObservação:", "\nEspero que", "\nVamos corrigir", "\nCONTEXTO DA LIÇÃO",
                "\nCONTEXTO", "\n💡 Conceito", "\n**💡 Conceito", "\nConceito:", "\n**Conceito", "\n1. Conceito"
            ]
        }





        if options:
            default_options.update(options)

        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "keep_alive": target_keep_alive,
            "options": default_options
        }



        
        url = f"{self.base_url}/api/chat"
        headers = {"Content-Type": "application/json"}
        json_data = json.dumps(payload).encode("utf-8")
        
        try:
            req = urllib.request.Request(url, data=json_data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.status == 200:
                    res_body = json.loads(response.read().decode("utf-8"))
                    msg = res_body.get("message", {})
                    return msg.get("content", "").strip()
                else:
                    def tr(key, default):
                        return get_ui_string(key, default) if get_ui_string else default
                    return tr("msg_ollama_http_error", f"[Erro Ollama HTTP {{}}]").format(response.status)
        except (urllib.error.URLError, ConnectionError, OSError):
            return self.get_offline_help_message(get_ui_string)
        except Exception as e:
            def tr(key, default):
                return get_ui_string(key, default) if get_ui_string else default
            return tr("msg_ai_generation_error", f"Erro na geração da resposta pela IA: {{}}").format(str(e))

    def unload_model(self, model: Optional[str] = None) -> bool:
        """
        Descarrega imediatamente o modelo da VRAM/RAM enviando keep_alive: 0 para a API do Ollama.
        """
        target_model = model or self.resolve_best_model()
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": target_model,
            "messages": [],
            "keep_alive": 0
        }
        headers = {"Content-Type": "application/json"}
        json_data = json.dumps(payload).encode("utf-8")
        try:
            req = urllib.request.Request(url, data=json_data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=3) as response:
                return response.status == 200
        except Exception:
            return False

