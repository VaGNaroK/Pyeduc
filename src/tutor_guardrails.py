import re
import ast
from typing import List, Dict, Optional

class EducationalGuardrails:
    BUILTIN_NAMES = {"print", "input", "len", "type", "str", "int", "float", "list", "dict", "set", "tuple", "sum", "max", "min", "range", "open"}

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
**💡 Conceito**: [Explique a regra geral da linguagem relacionada ao erro ou dúvida, de forma simples e direta.]

**❓ Pergunta Guiada**: [Faça uma pergunta que faça o aluno refletir sobre o seu próprio código.]

**🔍 Dica Progressiva**: [Dê uma pequena dica acionável de sintaxe ou de lógica que o coloque no caminho certo, sem dar a resposta.]

CONTEXTO DA LIÇÃO ATUAL:
- Lição: {lesson_title}
- Conceitos: {key_concepts}
{rag_context_section}
"""

    SOCRATIC_SYSTEM_PROMPT_EN = """You are the Pyeduc AI Tutor. Speak DIRECTLY to the student in the 2nd person ("you").

MANDATORY RULES:
1. NEVER mention 'comma' to solve errors in print texts. In Python, phrases and texts (Strings) inside print() MANDATORILY require QUOTES ('...' or "..."). Without quotes, Python understands them as variable names.
2. IT IS FORBIDDEN TO SHOW THE READY SOLUTION OR CORRECTED CODE. NEVER use code blocks (```python) with the answer.
3. Answer EXACTLY following the 3-topic model below with LINE BREAKS between them:
4. IT IS EXTREMELY FORBIDDEN TO GENERATE MORE THAN ONE ANSWER OR REPEAT TOPICS. GENERATE ONLY ONE SINGLE SET WITH THE 3 TOPICS (**💡 Concept**, **❓ Guided Question**, **🔍 Progressive Hint**) AND STOP THE ANSWER IMMEDIATELY.


EXAMPLE OF RESPONSE YOU MUST FOLLOW:
**💡 Concept**: [Explain the general language rule related to the error or doubt, in a simple and direct way.]

**❓ Guided Question**: [Ask a question that makes the student reflect on their own code.]

**🔍 Progressive Hint**: [Give a small actionable syntax or logic hint that puts them on the right path, without giving the answer.]

CURRENT LESSON CONTEXT:
- Lesson: {lesson_title}
- Concepts: {key_concepts}
{rag_context_section}
"""

    @classmethod
    def build_system_prompt(cls, lesson_title: str, key_concepts: List[str], rag_context: str = "", lang: str = "pt") -> str:
        concepts_str = ", ".join(key_concepts) if key_concepts else ("Basic Python" if lang == "en" else "Python básico")
        if lang == "en":
            rag_section = f"- Relevant lesson context: {rag_context}" if rag_context else ""
            template = cls.SOCRATIC_SYSTEM_PROMPT_EN
        else:
            rag_section = f"- Contexto relevante das lições: {rag_context}" if rag_context else ""
            template = cls.SOCRATIC_SYSTEM_PROMPT
            
        return template.format(
            lesson_title=lesson_title,
            key_concepts=concepts_str,
            rag_context_section=rag_section
        )

    @classmethod
    def analyze_code_ast(cls, code: str, lang: str = "pt") -> List[str]:
        """
        Realiza análise estática determinística no AST do código do aluno.
        Retorna uma lista de alertas didáticos identificados.
        """
        if not code or not code.strip():
            return []

        diagnostics = []
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            if lang == "en":
                msg = f"AST Syntax Error (line {e.lineno}): "
                if "was never closed" in str(e) or "parenthesis" in str(e):
                    msg += "A parenthesis or bracket was not closed."
                elif "expected ':'" in str(e) or "colon" in str(e):
                    msg += "Missing colon ':' at the end of the statement (if, def, for, while, etc.)."
                else:
                    msg += f"{e.msg}"
            else:
                msg = f"Erro de Sintaxe no AST (linha {e.lineno}): "
                if "was never closed" in str(e) or "parenthesis" in str(e):
                    msg += "Um parêntese ou colchete não foi fechado."
                elif "expected ':'" in str(e) or "colon" in str(e):
                    msg += "Faltou os dois-pontos ':' no final da instrução (if, def, for, while, etc.)."
                else:
                    msg += f"{e.msg}"
            return [msg]

        # 1. Verificação de sobrescrita de built-ins
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in cls.BUILTIN_NAMES:
                        diagnostics.append(
                            f"The variable '{target.id}' is overwriting the name of a Python built-in function/type ({target.id}). Guide them to change the variable name." if lang == "en" else
                            f"A variável '{target.id}' está sobrescrevendo o nome de uma função/tipo nativo do Python ({target.id}). Oriente a trocar o nome da variável."
                        )

        # 2. Verificação de funções sem comando return
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_return = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node))
                if not has_return:
                    diagnostics.append(
                        f"The function '{node.name}' was defined without a 'return' statement returning a value. Guide them on using 'return'." if lang == "en" else
                        f"A função '{node.name}' foi definida sem a instrução 'return' devolvendo um valor. Oriente sobre o uso do 'return'."
                    )

        # 3. Verificação de laços while True sem break
        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                is_always_true = False
                if isinstance(node.test, ast.Constant) and bool(node.test.value) is True:
                    is_always_true = True
                elif isinstance(node.test, ast.Name) and node.test.id == "True":
                    is_always_true = True
                
                if is_always_true:
                    has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
                    if not has_break:
                        diagnostics.append(
                            "The 'while True' loop has no 'break' statement to interrupt it, risking an infinite loop." if lang == "en" else
                            "O laço 'while True' não possui nenhuma instrução 'break' para interrompê-lo, correndo risco de loop infinito."
                        )

        # 4. Verificação de variáveis declaradas mas não utilizadas
        assigned_vars = set()
        loaded_vars = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    assigned_vars.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    loaded_vars.add(node.id)

        unused = assigned_vars - loaded_vars - cls.BUILTIN_NAMES - {"_"}
        for var in sorted(unused):
            diagnostics.append(
                f"The variable '{var}' was assigned but is never read or used in the code." if lang == "en" else
                f"A variável '{var}' foi atribuída mas nunca é lida ou utilizada no código."
            )

        return diagnostics

    @classmethod
    def build_user_message(
        cls,
        user_query: str,
        student_code: Optional[str] = None,
        console_output: Optional[str] = None,
        quick_action: Optional[str] = None,
        exercise_status: Optional[List[str]] = None,
        lang: str = "pt"
    ) -> str:
        """
        Monta a mensagem estruturada do usuário em 1ª pessoa ("Eu") com diagnóstico determinístico prévio e status de exercícios.
        """
        parts = []

        if quick_action == "error_help":
            parts.append("I need help understanding the error in my console." if lang == "en" else "Preciso de ajuda para entender o erro que deu no meu console.")
        elif quick_action == "hint_no_spoiler":
            parts.append("Give me a spoiler-free hint on how to proceed." if lang == "en" else "Me dê uma dica sem spoiler sobre como avançar nesta lição.")
        elif quick_action == "explain_concept":
            parts.append("Can you explain the main concept of this lesson simply?" if lang == "en" else "Pode me explicar o conceito principal desta lição de forma simples?")

        if user_query:
            parts.append(f"My question: \"{user_query}\"" if lang == "en" else f"Minha dúvida: \"{user_query}\"")

        if exercise_status and len(exercise_status) > 0:
            status_text = "\n".join(exercise_status)
            header = "[CURRENT LESSON EXERCISE STATUS:\n" if lang == "en" else "[STATUS DOS EXERCÍCIOS DA LIÇÃO ATUAL:\n"
            parts.append(f"\n{header}{status_text}]")

        if student_code and student_code.strip():
            header = "My current code:\n" if lang == "en" else "Meu código atual:\n"
            parts.append(f"\n{header}```python\n{student_code.strip()}\n```")
            
            # Análise estática AST do código
            ast_alerts = cls.analyze_code_ast(student_code, lang=lang)
            for alert in ast_alerts:
                header = "[PYEDUC AST STATIC ANALYSIS:" if lang == "en" else "[ANÁLISE ESTÁTICA AST DO PYEDUC:"
                parts.append(f"\n{header} {alert}]")

        if console_output and console_output.strip():
            # Limpa códigos de controle de integração de shell/terminal (ex: ]633;C]633;E...)
            clean_console = re.sub(r"\]633;[A-Za-z0-9;=._-]+", "", console_output)
            clean_console = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", clean_console).strip()
            header = "Error in my Python Console:\n" if lang == "en" else "Erro no meu Console Python:\n"
            parts.append(f"\n{header}```\n{clean_console}\n```")

            # Diagnóstico determinístico do Pyeduc para direcionar a IA corretamente em QUALQUER lição
            if clean_console and student_code:
                diag_header = "[EXACT PYEDUC SYSTEM DIAGNOSIS:" if lang == "en" else "[DIAGNÓSTICO EXATO DO SISTEMA PYEDUC:"
                if "NameError" in clean_console:
                    name_match = re.search(r"name\s*'([^']+)'\s*is not defined", clean_console)
                    did_you_mean = re.search(r"Did you mean:\s*'([^']+)'", clean_console)
                    if name_match:
                        var_used = name_match.group(1)
                        if lang == "en":
                            suggestion = f" (did you mean '{did_you_mean.group(1)}'?)" if did_you_mean else ""
                            msg = f" This is a NameError. The student tried to use the variable '{var_used}', but it was not defined or typed incorrectly{suggestion}. It is NOT a missing quotes issue; guide them on typing or defining the variable name.]"
                        else:
                            suggestion = f" (você quis dizer '{did_you_mean.group(1)}'?)" if did_you_mean else ""
                            msg = f" Trata-se de um NameError. O aluno tentou usar a variável '{var_used}', mas ela não foi definida ou seu nome foi digitado incorretamente{suggestion}. NÃO é falta de aspas em texto; oriente sobre a digitação ou definição do nome da variável.]"
                        parts.append(f"\n{diag_header}{msg}")
                elif "SyntaxError" in clean_console:
                    if re.search(r"print\s*\(\s*[a-zA-ZÀ-ÿ_]+(?:\s+[a-zA-ZÀ-ÿ_]+)+\s*\)", student_code):
                        msg = " This is a SyntaxError due to a string without quotes in print(). It is strictly missing quotes around the text.]" if lang == "en" else " Trata-se de um SyntaxError por frase/texto sem aspas no print(). É obrigatoriamente ausência de aspas ao redor do texto.]"
                        parts.append(f"\n{diag_header}{msg}")
                elif "IndentationError" in clean_console:
                    msg = " This is an IndentationError. The error is related to spaces/tabs at the beginning of the line. Guide the student on Python indentation.]" if lang == "en" else " Trata-se de um IndentationError. O erro é de recuo/espaçamento no início da linha (faltou dar TAB/espaço ou colocou espaços extras). Oriente o aluno sobre a indentação em Python.]"
                    parts.append(f"\n{diag_header}{msg}")
                elif "TypeError" in clean_console:
                    if "cannot be interpreted as an integer" in clean_console and "str" in clean_console:
                        msg = " This is a TypeError. The student passed a string to a function/method that expected a numerical index. Common example: using .pop('text') instead of .remove('text') or string as index. Guide them to remove by value using the appropriate function, or pass an integer.]" if lang == "en" else " Trata-se de um TypeError. O aluno passou um texto (string) para uma função ou método que esperava uma posição numérica (índice inteiro). Exemplo comum: usar .pop('texto') em vez de .remove('texto') ou usar string como índice. Oriente a remover o texto pelo nome usando a função apropriada, ou passar um número.]"
                    else:
                        msg = " This is a TypeError. The student tried to operate or use incompatible types (e.g. adding string and number). Guide them on correct type usage or conversion (str, int, float).]" if lang == "en" else " Trata-se de um TypeError. O aluno tentou operar ou usar tipos incompatíveis (ex: somar texto com número). Oriente sobre o uso correto dos tipos ou conversão (str, int, float).]"
                    parts.append(f"\n{diag_header}{msg}")
                elif "ZeroDivisionError" in clean_console:
                    msg = " This is a ZeroDivisionError. The student tried to divide by zero.]" if lang == "en" else " Trata-se de um ZeroDivisionError. O aluno tentou realizar uma divisão por zero na matemática do Python.]"
                    parts.append(f"\n{diag_header}{msg}")

                # Diagnóstico determinístico de divergência de saída para exercícios pendentes (sem exceção Python)
                if exercise_status and not any(err in clean_console for err in ["NameError", "SyntaxError", "IndentationError", "TypeError", "ZeroDivisionError"]):
                    for item in exercise_status:
                        is_pending = "PENDENTE" in item or "PENDING" in item
                        if is_pending and ("Saída esperada:" in item or "Expected output:" in item):
                            match_expected = re.search(r'(?:Saída esperada|Expected output):\s*"([^"]+)"', item)
                            if match_expected:
                                expected_out = match_expected.group(1).strip()
                                actual_out = clean_console.strip()
                                if expected_out and actual_out != expected_out:
                                    autograder_header = "[EXACT PYEDUC AUTOGRADER DIAGNOSIS:" if lang == "en" else "[DIAGNÓSTICO EXATO DO AUTOGRADER PYEDUC:"
                                    if lang == "en":
                                        msg = f" The student's code ran without Python errors and generated the output \"{actual_out}\", but the expected output for the pending exercise is \"{expected_out}\". There is a divergence in the printed result. Help the student realize what is missing or different in the generated output compared to the expected one, WITHOUT giving the ready code!]"
                                    else:
                                        msg = f" O código do aluno executou sem erros de Python e gerou a saída \"{actual_out}\", porém a saída esperada para o exercício pendente é \"{expected_out}\". Existe uma divergência no resultado impresso. Ajude o aluno a perceber o que está faltando ou diferente na saída gerada (ex: itens na lista, elementos esquecidos em passos anteriores) em comparação com a saída esperada, SEM dar o código pronto!]"
                                    parts.append(f"\n{autograder_header}{msg}")
                                    break

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
        quick_action: Optional[str] = None,
        exercise_status: Optional[List[str]] = None,
        lang: str = "pt"
    ) -> List[Dict[str, str]]:
        """
        Prepara a lista de mensagens no formato exigido pela API Ollama /api/chat.
        """
        system_prompt = cls.build_system_prompt(lesson_title, key_concepts or [], rag_context, lang=lang)
        formatted_user_msg = cls.build_user_message(user_query, student_code, console_output, quick_action, exercise_status, lang=lang)

        messages = [{"role": "system", "content": system_prompt}]

        # Adiciona histórico limpo recente (máximo 6 últimas trocas de mensagens)
        recent_history = history[-12:] if len(history) > 12 else history
        for msg in recent_history:
            if msg.get("role") in ["user", "assistant"] and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": formatted_user_msg})
        return messages

    @classmethod
    def sanitize_response(cls, response: str, student_code: Optional[str] = None, lang: str = "pt") -> str:
        """
        Sanitiza a resposta da IA garantindo a extração estrita de apenas 1 conjunto dos 3 tópicos sócráticos.
        """
        if not response:
            return response
            
        import re
        # Corta qualquer seção de encerramento extra como Resposta:, Explicação:, Corrigindo, Observação:, Nota:, CONTEXTO DA LIÇÃO ATUAL:
        cleaned = re.split(r"\n*(?:Resposta:|Answer:|Explicação:|Explanation:|Corrigindo|Correcting|Código corrigido|Observação:|Nota:|Espero que|Vamos corrigir|CONTEXTO DA LIÇÃO|CONTEXTO|Lição:).*", response, flags=re.IGNORECASE | re.DOTALL)[0]

        lbl_concept = "**💡 Concept**" if lang == "en" else "**💡 Conceito**"
        lbl_question = "**❓ Guided Question**" if lang == "en" else "**❓ Pergunta Guiada**"
        lbl_hint = "**🔍 Progressive Hint**" if lang == "en" else "**🔍 Dica Progressiva**"
        lbl_apply = "*(Apply the tip in your code editor!)*" if lang == "en" else "*(Aplique a dica no seu editor de código!)*"

        # Tenta a extração estrita dos 3 tópicos sócráticos (Conceito, Pergunta Guiada e Dica Progressiva)
        conceito_match = re.search(r"(?:💡\s*)?(?:\*\*)?(?:Conceito|Concept):\s*(?:\*\*)?(.*?)(?=(?:❓|Pergunta|Question|Dica|Hint|$))", cleaned, flags=re.IGNORECASE | re.DOTALL)
        pergunta_match = re.search(r"(?:❓\s*)?(?:\*\*)?(?:Pergunta(?:\s+Guiada)?|Guided\s+Question):\s*(?:\*\*)?(.*?)(?=(?:🔍|Dica|Hint|$))", cleaned, flags=re.IGNORECASE | re.DOTALL)
        dica_match = re.search(r"(?:🔍\s*)?(?:\*\*)?(?:Dica(?:\s+Progressiva|\s+Sugerida|\s+de\s+código)?|Progressive\s+Hint):\s*(?:\*\*)?(.*?)(?=(?:💡|\*\*💡|Conceito|Concept:|Pergunta|Question|Dica|Hint|$))", cleaned, flags=re.IGNORECASE | re.DOTALL)

        if conceito_match and pergunta_match and dica_match:
            c_text = conceito_match.group(1).strip()
            p_text = pergunta_match.group(1).strip()
            d_text = dica_match.group(1).strip()

            # Remove blocos de código com a solução da dica
            def _clean_code_block(match):
                return lbl_apply
            d_text = re.sub(r"```(?:python)?\s*\n?(.*?)\n?```", _clean_code_block, d_text, flags=re.DOTALL)

            return f"{lbl_concept}: {c_text}\n\n{lbl_question}: {p_text}\n\n{lbl_hint}: {d_text}"

        # Trunca repetições de ciclo no fallback
        second_concept = re.search(r"\n\s*(?:💡\s*)?(?:\*\*)?(?:Conceito|Concept):\s*(?:\*\*)?", cleaned[15:], flags=re.IGNORECASE)
        if second_concept:
            cleaned = cleaned[:15 + second_concept.start()].strip()

        # Fallback de higienização caso a IA não tenha usado a estrutura padrão de 3 tópicos
        cleaned = re.sub(r"(?:💡\s*)?(?:\*\*)?(?:Conceito|Concept):\s*(?:\*\*)?", f"{lbl_concept}: ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"(?:\n\s*)?(?:❓\s*)?(?:\*\*)?(?:Pergunta(?:\s+Guiada)?|Guided\s+Question):\s*(?:\*\*)?", f"\n\n{lbl_question}: ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"(?:\n\s*)?(?:🔍\s*)?(?:\*\*)?(?:Dica(?:\s+Progressiva|\s+Sugerida|\s+de\s+código)?|Progressive\s+Hint):\s*(?:\*\*)?", f"\n\n{lbl_hint}: ", cleaned, flags=re.IGNORECASE)

        def _clean_code_block2(match):
            return lbl_apply

        cleaned = re.sub(r"```(?:python)?\s*\n?(.*?)\n?```", _clean_code_block2, cleaned, flags=re.DOTALL)
        return cleaned.strip()








