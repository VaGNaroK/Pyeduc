import flet as ft
from ui.app_state import AppState
from tutor_guardrails import EducationalGuardrails

class TutorPanel(ft.Container):
    def __init__(self, state: AppState):
        super().__init__()
        self.state = state
        
        self.ai_status_icon = ft.Icon(ft.Icons.CIRCLE, color="#94a3b8", size=10)
        self.ai_status_text = ft.Text("Ollama: verificando...", color="#94a3b8", size=11)
        self.ai_chat_list = ft.ListView(height=260, spacing=10, auto_scroll=True, padding=5)
        self.ai_loading_ring = ft.ProgressRing(width=18, height=18, stroke_width=2, visible=False)
        
        self.ai_input_field = ft.TextField(
            hint_text="Pergunte algo ao Tutor...",
            expand=True,
            border_radius=8,
            border_color="#cbd5e1",
            content_padding=10,
            text_size=13,
            on_submit=lambda e: self.send_to_ai()
        )
        self.btn_send_ai = ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color="#7c3aed", on_click=lambda e: self.send_to_ai())

        self.content = ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.SMART_TOY_ROUNDED, color="#7c3aed", size=24),
                    ft.Text("Tutor IA Sócratico", weight="bold", size=16, color="#1e1b4b"),
                ]),
                ft.Row([self.ai_status_icon, self.ai_status_text])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=1, color="#e2e8f0"),
            ft.Text("Ajuda Rápida:", size=12, weight="bold", color="#64748b"),
            ft.Row([
                ft.OutlinedButton("💡 Dica", on_click=lambda e: self.send_to_ai(quick_action="hint_no_spoiler"), style=ft.ButtonStyle(padding=4)),
                ft.OutlinedButton("❌ Erro", on_click=lambda e: self.send_to_ai(quick_action="error_help"), style=ft.ButtonStyle(padding=4)),
                ft.OutlinedButton("📘 Conceito", on_click=lambda e: self.send_to_ai(quick_action="explain_concept"), style=ft.ButtonStyle(padding=4)),
            ], spacing=5, wrap=True),
            ft.Divider(height=1, color="#e2e8f0"),
            self.ai_chat_list,
            ft.Row([self.ai_input_field, self.ai_loading_ring, self.btn_send_ai], spacing=5)
        ], expand=True, spacing=10)
        
        self.padding = 15
        self.expand = True
        
        self.state.on_lesson_changed_callbacks.append(self.clear_chat)

    def clear_chat(self):
        self.state.ai_chat_history.clear()
        self.ai_chat_list.controls.clear()
        self.ai_input_field.value = ""
        if self.page:
            self.update()

    def update_ollama_status(self):
        def _check():
            online, msg = self.state.ollama_client.check_health()
            self.ai_status_text.value = msg
            if online:
                if "nenhum modelo" in msg.lower():
                    self.ai_status_icon.color = "#f59e0b"
                    self.ai_status_text.color = "#d97706"
                else:
                    self.ai_status_icon.color = "#10b981"
                    self.ai_status_text.color = "#10b981"
            else:
                self.ai_status_icon.color = "#ef4444"
                self.ai_status_text.color = "#ef4444"
            self.update()
        self.state.page.run_thread(_check)

    def add_chat_message(self, role: str, text: str):
        is_user = role == "user"
        bg = "#e0e7ff" if is_user else "#f3e8ff"
        fg = "#1e1b4b" if is_user else "#581c87"
        align = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        title_prefix = "Você:" if is_user else "🤖 Tutor IA:"

        msg_box = ft.Container(
            content=ft.Column([
                ft.Text(title_prefix, weight="bold", size=11, color=fg),
                ft.Markdown(text, selectable=True) if not is_user else ft.Text(text, size=13, color=fg)
            ], spacing=3),
            bgcolor=bg,
            padding=10,
            border_radius=8,
            expand=True
        )
        self.ai_chat_list.controls.append(ft.Row([msg_box], alignment=align))
        try:
            self.ai_chat_list.update()
        except Exception:
            pass
        self.state.page.update()

    def send_to_ai(self, quick_action=None):
        if self.state.is_ai_generating:
            return

        text = self.ai_input_field.value.strip()
        if not text and not quick_action:
            return

        self.ai_input_field.value = ""
        self.state.is_ai_generating = True
        self.ai_loading_ring.visible = True
        self.btn_send_ai.disabled = True
        try:
            self.ai_loading_ring.update()
            self.btn_send_ai.update()
            self.ai_input_field.update()
        except Exception:
            pass
        self.state.page.update()

        display_text = text
        if not display_text and quick_action:
            if quick_action == "hint_no_spoiler": display_text = "Quero uma dica sem spoiler sobre este exercício."
            elif quick_action == "error_help": display_text = "Por que meu código gerou erro no console?"
            elif quick_action == "explain_concept": display_text = "Explique o conceito principal desta lição."

        self.add_chat_message("user", display_text)

        def _worker():
            try:
                lesson = self.state.current_lesson or {}
                title = lesson.get("title", "Python")
                concepts = lesson.get("ai_context", {}).get("key_concepts", [title])
                
                rag_ctx = self.state.lesson_rag.get_relevant_context(
                    user_query=text or display_text,
                    current_lesson_id=lesson.get("id")
                )

                ex_statuses = getattr(self.state, 'get_exercise_statuses', lambda: [])()
                student_code = getattr(self.state, 'get_student_code', lambda: "")()
                console_out = getattr(self.state, 'get_console_output', lambda: "")()

                payload = EducationalGuardrails.prepare_chat_payload(
                    history=self.state.ai_chat_history,
                    user_query=text,
                    lesson_title=title,
                    key_concepts=concepts,
                    rag_context=rag_ctx,
                    student_code=student_code,
                    console_output=console_out,
                    quick_action=quick_action,
                    exercise_status=ex_statuses
                )

                raw_reply = self.state.ollama_client.chat(payload)
                reply = EducationalGuardrails.sanitize_response(raw_reply, student_code)
                self.state.ai_chat_history.append({"role": "user", "content": display_text})
                self.state.ai_chat_history.append({"role": "assistant", "content": reply})

                self.add_chat_message("assistant", reply)

            except Exception as ex:
                self.add_chat_message("assistant", f"⚠️ Ocorreu um erro ao comunicar com a IA: {str(ex)}")
            finally:
                self.state.is_ai_generating = False
                self.ai_loading_ring.visible = False
                self.btn_send_ai.disabled = False
                try:
                    self.ai_loading_ring.update()
                    self.btn_send_ai.update()
                except Exception:
                    pass
                self.state.page.update()

        self.state.page.run_thread(_worker)
