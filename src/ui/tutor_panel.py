import flet as ft
from ui.app_state import AppState
from tutor_guardrails import EducationalGuardrails

class TutorPanel(ft.Container):
    def __init__(self, state: AppState):
        super().__init__()
        self.state = state
        cm = self.state.content_manager
        
        self.ai_status_icon = ft.Icon(ft.Icons.CIRCLE, color="#94a3b8", size=10)
        self.ai_status_text = ft.Text("Ollama: verificando...", color="#94a3b8", size=11)
        self.ai_chat_list = ft.ListView(height=260, spacing=10, auto_scroll=True, padding=5)
        self.ai_loading_ring = ft.ProgressRing(width=18, height=18, stroke_width=2, visible=False)
        self.ai_header_title = ft.Text(cm.get_ui_string("tutor_title", "Tutor IA Sócratico"), weight="bold", size=16, color="#1e1b4b")
        
        self.ai_input_field = ft.TextField(
            hint_text=cm.get_ui_string("lbl_type_msg", "Pergunte algo ao Tutor..."),
            expand=True,
            border_radius=8,
            border_color="#cbd5e1",
            content_padding=10,
            text_size=13,
            on_submit=lambda e: self.send_to_ai()
        )
        self.ai_send_btn = ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color="#7c3aed", on_click=lambda e: self.send_to_ai())

        self.btn_hint = ft.OutlinedButton(cm.get_ui_string("btn_hint", "💡 Dica"), on_click=lambda e: self.send_to_ai(quick_action="hint_no_spoiler"), style=ft.ButtonStyle(padding=4))
        self.btn_error = ft.OutlinedButton(cm.get_ui_string("btn_error", "❌ Erro"), on_click=lambda e: self.send_to_ai(quick_action="error_help"), style=ft.ButtonStyle(padding=4))
        self.btn_concept = ft.OutlinedButton(cm.get_ui_string("btn_concept", "📘 Conceito"), on_click=lambda e: self.send_to_ai(quick_action="explain_concept"), style=ft.ButtonStyle(padding=4))
        self.lbl_quick_help = ft.Text(cm.get_ui_string("btn_quick_help", "Ajuda Rápida:"), size=12, weight="bold", color="#64748b")

        self.quick_actions = ft.Container(
            content=ft.Column([
                self.lbl_quick_help,
                ft.Row([
                    self.btn_hint,
                    self.btn_error,
                    self.btn_concept,
                ], spacing=5, wrap=True)
            ])
        )

        self.content = ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.SMART_TOY_ROUNDED, color="#7c3aed", size=24),
                    self.ai_header_title,
                ]),
                ft.Row([self.ai_status_icon, self.ai_status_text])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=1, color="#e2e8f0"),
            self.quick_actions,
            ft.Divider(height=1, color="#e2e8f0"),
            self.ai_chat_list,
            ft.Row([self.ai_input_field, self.ai_loading_ring, self.ai_send_btn], spacing=5)
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
            cm = self.state.content_manager
            online, msg = self.state.ollama_client.check_health(get_ui_string=cm.get_ui_string)
            self.ai_status_text.value = msg
            if online:
                # Assuming "nenhum modelo" or "no model" might be in the string
                if "nenhum modelo" in msg.lower() or "no model" in msg.lower():
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
        cm = self.state.content_manager
        is_user = role == "user"
        bg = "#e0e7ff" if is_user else "#f3e8ff"
        fg = "#1e1b4b" if is_user else "#581c87"
        align = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        title_prefix = cm.get_ui_string("lbl_you", "Você:") if is_user else cm.get_ui_string("lbl_ai_tutor_prefix", "🤖 Tutor IA:")

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
        self.ai_send_btn.disabled = True
        try:
            self.ai_loading_ring.update()
            self.ai_send_btn.update()
            self.ai_input_field.update()
        except Exception:
            pass
        self.state.page.update()

        display_text = text
        if quick_action:
            cm = self.state.content_manager
            if quick_action == "hint_no_spoiler": display_text = cm.get_ui_string("msg_hint_prompt", "Quero uma dica sem spoiler sobre este exercício.")
            elif quick_action == "error_help": display_text = cm.get_ui_string("msg_error_prompt", "Por que meu código gerou erro no console?")
            elif quick_action == "explain_concept": display_text = cm.get_ui_string("msg_concept_prompt", "Explique o conceito principal desta lição.")
            else: display_text = quick_action
            prompt = display_text
        else:
            prompt = text

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
                    exercise_status=ex_statuses,
                    lang=self.state.content_manager.lang
                )

                raw_reply = self.state.ollama_client.chat(payload, get_ui_string=self.state.content_manager.get_ui_string)
                cm = self.state.content_manager
                reply = EducationalGuardrails.sanitize_response(raw_reply, student_code, cm.lang)
                self.state.ai_chat_history.append({"role": "user", "content": display_text})
                self.state.ai_chat_history.append({"role": "assistant", "content": reply})

                self.add_chat_message("assistant", reply)

            except Exception as ex:
                cm = self.state.content_manager
                self.add_chat_message("assistant", f"{cm.get_ui_string('msg_ai_error', '⚠️ Ocorreu um erro ao comunicar com a IA:')} {str(ex)}")
            finally:
                self.state.is_ai_generating = False
                self.ai_loading_ring.visible = False
                self.ai_send_btn.disabled = False
                try:
                    self.ai_loading_ring.update()
                    self.ai_send_btn.update()
                except Exception:
                    pass
                self.state.page.update()

        self.state.page.run_thread(_worker)

    def update_strings(self):
        cm = self.state.content_manager
        if hasattr(self, "ai_header_title"): self.ai_header_title.value = cm.get_ui_string("tutor_title", "Tutor IA Sócratico")
        if hasattr(self, "ai_input_field"): self.ai_input_field.hint_text = cm.get_ui_string("lbl_type_msg", "Pergunte algo ao Tutor...")
        if hasattr(self, "ai_send_btn"): self.ai_send_btn.text = cm.get_ui_string("btn_send", "Enviar")
        if hasattr(self, "ai_status_text"):
            if "verificando" in self.ai_status_text.value.lower() or "checking" in self.ai_status_text.value.lower():
                self.ai_status_text.value = cm.get_ui_string("msg_ollama_checking", "Ollama: verificando...")
            else:
                self.update_ollama_status()
        if hasattr(self, "btn_hint"):
            self.btn_hint.content = cm.get_ui_string("btn_hint", "💡 Dica")
        if hasattr(self, "btn_error"):
            self.btn_error.content = cm.get_ui_string("btn_error", "❌ Erro")
        if hasattr(self, "btn_concept"):
            self.btn_concept.content = cm.get_ui_string("btn_concept", "📘 Conceito")
        if hasattr(self, "lbl_quick_help"):
            self.lbl_quick_help.value = cm.get_ui_string("btn_quick_help", "Ajuda Rápida:")
        self.update()
