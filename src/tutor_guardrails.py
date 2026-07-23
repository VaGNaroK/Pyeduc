"""
Módulo de Guardrails Educacionais e Gestão de Prompts Sócraticos para o Tutor de IA.
Garante que a IA ajude o aluno sem fornecer respostas prontas ("spoilers").
"""

import re
from typing import List, Dict, Optional



class EducationalGuardrails:
    PROHIBITED_INTENTS = [
        "me da a resposta",
        "me dá a resposta",
        "faça o exercicio para mim",
        "codigo completo",
        "código completo",
        "resolve para mim",
        "copiar e colar"
    ]

    SOCRATIC_SYSTEM_PROMPT = """Você é o Tutor IA do Pyeduc. Converse DIRETAMENTE com o aluno em 2ª pessoa ("você").

REGRAS OBRIGATÓRIAS:
1. NUNCA mencione 'vírgula' para resolver erros em textos no print. Em Python, frases e textos (Strings) dentro do print() exigem OBRIGATORIAMENTE ASPAS ('...' ou "..."). Sem aspas, o Python entende como nomes de variáveis.
2. É PROIBIDO MOSTRAR A SOLUÇÃO PRONTA OU CÓDIGO CORRIGIDO. NUNCA use blocos de código (```python) com a resposta.
3. Responda EXATAMENTE seguindo o modelo de 3 tópicos abaixo com QUEBRAS DE LINHA entre eles:
4. É EXTREMAMENTE PROIBIDO GERAR MAIS DE UMA RESPOSTA OU REPETIR OS TÓPICOS. GERE APENAS UM ÚNICO CONJUNTO COM OS 3 TÓPICOS (**💡 Conceito**, **❓ Pergunta Guiada**, **🔍 Dica Progressiva**) E PARE A RESPOSTA IMEDIATAMENTE.


EXEMPLO DE RESPOSTA QUE VOCÊ DEVE SEGUIR:
**💡 Conceito**: Em Python, textos e frases são chamados de Strings e precisam obrigatoriamente estar entre aspas para que a linguagem não confunda com variáveis.

**❓ Pergunta Guiada**: Você verificou se envolveu toda a sua frase em aspas dentro do print?

**🔍 Dica Progressiva**: Tente colocar aspas simples ou duplas no começo e no final da frase.

CONTEXTO DA LIÇÃO ATUAL:
- Lição: {lesson_title}
- Conceitos: {key_concepts}
{rag_context_section}
"""




    @classmethod
    def build_system_prompt(cls, lesson_title: str, key_concepts: List[str], rag_context: str = "") -> str:
        concepts_str = ", ".join(key_concepts) if key_concepts else "Python básico"
        rag_section = f"- Contexto relevante das lições: {rag_context}" if rag_context else ""
        return cls.SOCRATIC_SYSTEM_PROMPT.format(
            lesson_title=lesson_title,
            key_concepts=concepts_str,
            rag_context_section=rag_section
        )

    @classmethod
    def build_user_message(
        cls,
        user_query: str,
        student_code: Optional[str] = None,
        console_output: Optional[str] = None,
        quick_action: Optional[str] = None
    ) -> str:
        """
        Monta a mensagem estruturada do usuário em 1ª pessoa ("Eu") com diagnóstico determinístico prévio.
        """
        parts = []

        if quick_action == "error_help":
            parts.append("Preciso de ajuda para entender o erro que deu no meu console.")
        elif quick_action == "hint_no_spoiler":
            parts.append("Me dê uma dica sem spoiler sobre como avançar nesta lição.")
        elif quick_action == "explain_concept":
            parts.append("Pode me explicar o conceito principal desta lição de forma simples?")

        if user_query:
            parts.append(f"Minha dúvida: \"{user_query}\"")

        if student_code and student_code.strip():
            parts.append(f"\nMeu código atual:\n```python\n{student_code.strip()}\n```")

        if console_output and console_output.strip():
            # Limpa códigos de controle de integração de shell/terminal (ex: ]633;C]633;E...)
            clean_console = re.sub(r"\]633;[A-Za-z0-9;=._-]+", "", console_output)
            clean_console = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", clean_console).strip()
            parts.append(f"\nErro no meu Console Python:\n```\n{clean_console}\n```")

            # Diagnóstico determinístico do Pyeduc para direcionar a IA corretamente em QUALQUER lição
            if clean_console and student_code:
                if "NameError" in clean_console:
                    name_match = re.search(r"name\s*'([^']+)'\s*is not defined", clean_console)
                    did_you_mean = re.search(r"Did you mean:\s*'([^']+)'", clean_console)
                    if name_match:
                        var_used = name_match.group(1)
                        suggestion = f" (você quis dizer '{did_you_mean.group(1)}'?)" if did_you_mean else ""
                        parts.append(f"\n[DIAGNÓSTICO EXATO DO SISTEMA PYEDUC: Trata-se de um NameError. O aluno tentou usar a variável '{var_used}', mas ela não foi definida ou seu nome foi digitado incorretamente{suggestion}. NÃO é falta de aspas em texto; oriente sobre a digitação ou definição do nome da variável.]")
                elif "SyntaxError" in clean_console:
                    if re.search(r"print\s*\(\s*[^'\"0-9\(\)]+\s+[^'\"0-9\(\)]+.*?\)", student_code):
                        parts.append("\n[DIAGNÓSTICO EXATO DO SISTEMA PYEDUC: Trata-se de um SyntaxError por frase/texto sem aspas no print(). É obrigatoriamente ausência de aspas ao redor do texto.]")
                elif "IndentationError" in clean_console:
                    parts.append("\n[DIAGNÓSTICO EXATO DO SISTEMA PYEDUC: Trata-se de um IndentationError. O erro é de recuo/espaçamento no início da linha (faltou dar TAB/espaço ou colocou espaços extras). Oriente o aluno sobre a indentação em Python.]")
                elif "TypeError" in clean_console:
                    parts.append("\n[DIAGNÓSTICO EXATO DO SISTEMA PYEDUC: Trata-se de um TypeError. O aluno tentou operar ou concatenar tipos incompatíveis (ex: somar texto com número). Oriente sobre a conversão de tipos como str(), int() ou float().]")
                elif "ZeroDivisionError" in clean_console:
                    parts.append("\n[DIAGNÓSTICO EXATO DO SISTEMA PYEDUC: Trata-se de um ZeroDivisionError. O aluno tentou realizar uma divisão por zero na matemática do Python.]")

        return "\n".join(parts)



    @classmethod
    def prepare_chat_payload(
        cls,
        history: List[Dict[str, str]],
        user_query: str,
        lesson_title: str = "Lição de Python",
        key_concepts: List[str] = None,
        rag_context: str = "",
        student_code: Optional[str] = None,
        console_output: Optional[str] = None,
        quick_action: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Prepara a lista de mensagens no formato exigido pela API Ollama /api/chat.
        """
        system_prompt = cls.build_system_prompt(lesson_title, key_concepts or [], rag_context)
        formatted_user_msg = cls.build_user_message(user_query, student_code, console_output, quick_action)

        messages = [{"role": "system", "content": system_prompt}]

        # Adiciona histórico limpo recente (máximo 6 últimas trocas de mensagens)
        recent_history = history[-12:] if len(history) > 12 else history
        for msg in recent_history:
            if msg.get("role") in ["user", "assistant"] and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": formatted_user_msg})
        return messages

    @classmethod
    def sanitize_response(cls, response: str, student_code: Optional[str] = None) -> str:
        """
        Sanitiza a resposta da IA garantindo a extração estrita de apenas 1 conjunto dos 3 tópicos sócráticos.
        """
        if not response:
            return response
            
        import re
        # Corta qualquer seção de encerramento extra como Resposta:, Explicação:, Corrigindo, Observação:, Nota:, CONTEXTO DA LIÇÃO ATUAL:
        cleaned = re.split(r"\n*(?:Resposta:|Explicação:|Corrigindo|Código corrigido|Observação:|Nota:|Espero que|Vamos corrigir|CONTEXTO DA LIÇÃO|CONTEXTO|Lição:).*", response, flags=re.IGNORECASE | re.DOTALL)[0]

        # Tenta a extração estrita dos 3 tópicos sócráticos (Conceito, Pergunta Guiada e Dica Progressiva)
        conceito_match = re.search(r"(?:💡\s*)?(?:\*\*)?Conceito:\s*(?:\*\*)?(.*?)(?=(?:❓|Pergunta Guiada:|$))", cleaned, flags=re.IGNORECASE | re.DOTALL)
        pergunta_match = re.search(r"(?:❓\s*)?(?:\*\*)?Pergunta Guiada:\s*(?:\*\*)?(.*?)(?=(?:🔍|Dica Progressiva:|$))", cleaned, flags=re.IGNORECASE | re.DOTALL)
        dica_match = re.search(r"(?:🔍\s*)?(?:\*\*)?Dica Progressiva:\s*(?:\*\*)?(.*?)(?=(?:💡|\*\*💡|Conceito:|Pergunta Guiada:|Dica Progressiva:|$))", cleaned, flags=re.IGNORECASE | re.DOTALL)

        if conceito_match and pergunta_match and dica_match:
            c_text = conceito_match.group(1).strip()
            p_text = pergunta_match.group(1).strip()
            d_text = dica_match.group(1).strip()

            # Remove blocos de código com a solução da dica
            def _clean_code_block(match):
                return "*(Aplique a dica no seu editor de código!)*"
            d_text = re.sub(r"```(?:python)?\s*\n?(.*?)\n?```", _clean_code_block, d_text, flags=re.DOTALL)

            return f"**💡 Conceito**: {c_text}\n\n**❓ Pergunta Guiada**: {p_text}\n\n**🔍 Dica Progressiva**: {d_text}"

        # Fallback de higienização caso a IA não tenha usado a estrutura padrão de 3 tópicos
        cleaned = re.sub(r"(?:💡\s*)?(?:\*\*)?Conceito:\s*(?:\*\*)?", "**💡 Conceito**: ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"(?:\n\s*)?(?:❓\s*)?(?:\*\*)?Pergunta Guiada:\s*(?:\*\*)?", "\n\n**❓ Pergunta Guiada**: ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"(?:\n\s*)?(?:🔍\s*)?(?:\*\*)?Dica Progressiva:\s*(?:\*\*)?", "\n\n**🔍 Dica Progressiva**: ", cleaned, flags=re.IGNORECASE)

        def _clean_code_block(match):
            return "*(Aplique a dica no seu editor de código!)*"

        cleaned = re.sub(r"```(?:python)?\s*\n?(.*?)\n?```", _clean_code_block, cleaned, flags=re.DOTALL)
        return cleaned.strip()








