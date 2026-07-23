"""
Módulo RAG (Retrieval-Augmented Generation) leve para recuperar contexto de lições do Pyeduc.
Indexa o conteúdo de lessons.json usando busca por termos e palavras-chave.
"""

from typing import List, Dict, Any, Optional


class LessonRAG:
    def __init__(self, lessons: List[Dict[str, Any]]):
        self.lessons = lessons

    def get_relevant_context(self, user_query: str, current_lesson_id: Optional[int] = None, max_chunks: int = 2) -> str:
        """
        Recupera trechos relevantes de lições passadas ou da lição atual baseados na dúvida do usuário.
        """
        if not user_query or not self.lessons:
            return ""

        query_terms = set(user_query.lower().split())
        scored_snippets = []

        for lesson in self.lessons:
            l_id = lesson.get("id")
            l_title = lesson.get("title", "")
            
            # Não incluir lições futuras em relação à lição atual
            if current_lesson_id is not None and isinstance(l_id, int) and isinstance(current_lesson_id, int):
                if l_id > current_lesson_id and l_id < 1000:
                    continue

            # Extrai textos da lição (teoria, explicações, ai_context)
            text_blocks = []
            if lesson.get("content"):
                text_blocks.append(lesson["content"])
            
            if lesson.get("sections"):
                for sec in lesson["sections"]:
                    if sec.get("content"):
                        text_blocks.append(sec["content"])

            ai_ctx = lesson.get("ai_context", {})
            if ai_ctx.get("key_concepts"):
                text_blocks.append(" ".join(ai_ctx["key_concepts"]))

            full_text = " ".join(text_blocks)
            text_lower = full_text.lower()

            # Calcula pontuação simples baseada em correspondência de termos
            score = 0
            for term in query_terms:
                if len(term) > 3:  # Ignora palavras muito curtas
                    count = text_lower.count(term)
                    score += count

            if score > 0:
                # Truncar texto do trecho para caber no prompt
                snippet = full_text[:300].replace("\n", " ").strip()
                scored_snippets.append((score, f"Lição [{l_title}]: {snippet}..."))

        # Ordena pelos trechos de maior pontuação
        scored_snippets.sort(key=lambda x: x[0], reverse=True)
        top_snippets = [item[1] for item in scored_snippets[:max_chunks]]
        return " | ".join(top_snippets)
