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

    def check_health(self) -> Tuple[bool, str]:
        """
        Verifica a instalação no SO e a acessibilidade da API REST do Ollama.
        Retorna (online, mensagem).
        """
        installed = self.is_ollama_installed()
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    models = [m.get("name") for m in data.get("models", [])]
                    if not models:
                        return True, f"Ollama rodando no {self.os_name}, mas nenhum modelo encontrado."
                    return True, f"Ollama online no {self.os_name} ({len(models)} modelo(s))."
                return False, f"Resposta inesperada do Ollama: HTTP {response.status}"
        except urllib.error.URLError:
            if not installed:
                return False, f"Sem suporte a Tutor IA (Ollama não instalado no {self.os_name})"
            return False, f"Ollama instalado no {self.os_name}, mas serviço está offline em {self.base_url}"
        except Exception as e:
            if not installed:
                return False, f"Sem suporte a Tutor IA (Ollama não instalado no {self.os_name})"
            return False, f"Erro ao conectar com o Ollama: {str(e)}"


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

    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, keep_alive: Optional[str] = None, options: Optional[Dict] = None) -> str:
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
            "stop": ["\nResposta:", "\nExplicação:", "\nCódigo corrigido", "\nCorrigindo", "\nObservação:", "\nEspero que", "\nVamos corrigir", "\nCONTEXTO DA LIÇÃO", "\nCONTEXTO"]
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
                    return f"[Erro Ollama HTTP {response.status}]"
        except urllib.error.URLError as e:
            return f"Não foi possível conectar ao Ollama ({e.reason}). Verifique se o Ollama está rodando."
        except Exception as e:
            return f"Erro na geração da resposta pela IA: {str(e)}"

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

