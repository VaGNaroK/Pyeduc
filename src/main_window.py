import flet as ft
from ui.app_state import AppState
from ui.sidebar import Sidebar
from ui.top_bar import TopBar
from ui.lesson_view import LessonView
from ui.editor_console import EditorConsole
from ui.tutor_panel import TutorPanel
import config

class PyeducApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Pyeduc - App Educacional Python"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.spacing = 0
        self.page.bgcolor = "#e2e8f0"
        self.page.window.icon = config.APP_ICON
        self.page.window.min_width = 800
        self.page.window.min_height = 600

        self.state = AppState(page)
        
        self.page.window.on_event = self.on_window_event
        self.page.on_disconnect = lambda e: self.state.ollama_client.unload_model()

        self.setup_ui()
        self.setup_callbacks()
        
        # Iniciar interface inicial (Login)
        self.top_bar.visible = False
        self.sidebar.visible = False
        self.lesson_view.visible = False
        self.editor_console.visible = False
        self.lesson_view.activity_container.visible = False
        self.footer.visible = False
        self.welcome_container.visible = True
        self.page.update()
        
    def on_window_event(self, e):
        if e.data == "close":
            try:
                self.state.ollama_client.unload_model()
            except Exception:
                pass

    def setup_ui(self):
        # Initialize components
        self.sidebar = Sidebar(self.state, self.on_lesson_select, self.toggle_ai_sidebar)
        self.top_bar = TopBar(self.state, self.do_export_progress, self.do_import_progress, self.on_logout)
        self.lesson_view = LessonView(self.state, self.on_copy_example)
        self.editor_console = EditorConsole(self.state, self.execute_code, self.ask_ai_error)
        self.tutor_panel = TutorPanel(self.state)
        
        # Wiring cross-component dependencies
        self.state.get_student_code = lambda: self.editor_console.console_input.value
        self.state.get_console_output = lambda: self.editor_console.console_output.value
        self.state.get_exercise_statuses = self.lesson_view.get_exercise_statuses
        self.state.on_zoom_image = self.on_zoom_image

        # Welcome Container
        cm = self.state.content_manager
        
        # Obter linguagens disponíveis no diretório
        available_langs = cm.get_available_languages()
        options = []
        for l in available_langs:
            options.append(ft.dropdown.Option(l["code"], l["name"]))
            
        # Fallback if somehow no files are found yet
        if not options:
            options = [ft.dropdown.Option("pt", "Português")]
            
        current_lang = self.state.progress_manager.get_user_language()
        if not any(opt.key == current_lang for opt in options):
            current_lang = options[0].key
            
        self.lang_dropdown = ft.Dropdown(
            options=options,
            value=current_lang,
            width=150,
            on_select=self.on_lang_changed,
            border_color="#cbd5e1",
            color="black"
        )
        
        self.tf_username = ft.TextField(label=cm.get_ui_string("lbl_username"), width=300, bgcolor="white", color="black", border_color="#cbd5e1")
        self.tf_password = ft.TextField(label=cm.get_ui_string("lbl_password"), password=True, can_reveal_password=True, width=300, bgcolor="white", color="black", border_color="#cbd5e1")
        self.btn_login = ft.ElevatedButton(cm.get_ui_string("btn_login"), bgcolor="#3b82f6", color="white", on_click=self.on_login, width=140)
        self.btn_register = ft.ElevatedButton(cm.get_ui_string("btn_register"), bgcolor="#10b981", color="white", on_click=self.on_register, width=140)
        
        self.welcome_title = ft.Text(cm.get_ui_string("lbl_welcome"), size=32, weight="bold", color="#1e293b")
        self.welcome_subtitle = ft.Text(cm.get_ui_string("lbl_login_msg"), size=14, color="#64748b")
        
        login_content = ft.Container(
            content=ft.Column([
                ft.Image(src=config.APP_ICON, width=250),
                self.welcome_title,
                self.welcome_subtitle,
                ft.Container(height=20),
                self.tf_username,
                self.tf_password,
                ft.Row([self.btn_login, self.btn_register], alignment=ft.MainAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment.CENTER,
            left=0, right=0, top=0, bottom=0
        )
        
        lang_selector_container = ft.Container(
            content=self.lang_dropdown,
            top=20,
            right=20
        )
        
        self.welcome_container = ft.Container(
            content=ft.Stack([
                login_content,
                lang_selector_container
            ]),
            bgcolor="#f8fafc",
            expand=50000,
            visible=True
        )

        # Footer
        self.footer_status_text = ft.Text("...", color="white", size=12)
        self.admin_switch = ft.Switch(label="Modo Admin", value=self.state.admin_mode_enabled, on_change=self.on_admin_toggle, label_position=ft.LabelPosition.LEFT)
        self.admin_switch_container = ft.Container(content=self.admin_switch, visible=False)
        self.btn_prev = ft.OutlinedButton(cm.get_ui_string("btn_prev"), icon=ft.Icons.ARROW_BACK, on_click=self.on_prev_lesson, style=ft.ButtonStyle(color="white"))
        self.btn_next = ft.ElevatedButton(cm.get_ui_string("btn_next"), icon=ft.Icons.ARROW_FORWARD, bgcolor="#10b981", color="white", on_click=self.on_next_lesson)
        
        self.footer = ft.Container(
            content=ft.Row([
                ft.Row([self.footer_status_text, self.admin_switch_container], spacing=20),
                ft.Row([self.btn_prev, self.btn_next], spacing=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#0f172a",
            padding=10,
            visible=False
        )

        # Splitters
        self.drag_splitter_container = ft.Container(
            height=10, bgcolor="#cbd5e1", border_radius=5, alignment=ft.Alignment.CENTER,
            content=ft.Icon(ft.Icons.DRAG_HANDLE, size=16, color="#64748b"),
            margin=ft.Margin.symmetric(vertical=2, horizontal=10),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )
        self.drag_splitter = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.RESIZE_UP_DOWN,
            on_pan_update=self.on_pan_update_splitter, on_hover=self.on_hover_splitter,
            content=self.drag_splitter_container
        )

        self.sidebar_splitter_container = ft.Container(
            width=6, bgcolor="#cbd5e1", border_radius=3, margin=ft.Margin.symmetric(vertical=10, horizontal=2),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )
        self.sidebar_splitter = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
            on_pan_update=self.on_pan_update_sidebar_splitter, on_hover=self.on_hover_sidebar_splitter,
            content=self.sidebar_splitter_container
        )

        self.ai_splitter_container = ft.Container(
            width=6, bgcolor="#cbd5e1", border_radius=3, margin=ft.Margin.symmetric(vertical=10, horizontal=2),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            visible=False
        )
        self.ai_splitter = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
            on_pan_update=self.on_pan_update_ai_splitter, on_hover=self.on_hover_ai_splitter,
            content=self.ai_splitter_container,
            visible=False
        )

        self.ai_sidebar_container = ft.Container(
            content=self.tutor_panel,
            expand=30000,
            visible=False,
            bgcolor="#f8fafc"
        )

        self.left_panel = ft.Column([
            self.lesson_view,
            self.drag_splitter,
            self.editor_console,
            self.lesson_view.activity_container,
            self.welcome_container
        ], expand=70000, spacing=0, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

        self.main_row = ft.Row([
            self.sidebar,
            self.sidebar_splitter,
            self.left_panel,
            self.ai_splitter,
            self.ai_sidebar_container
        ], expand=True, spacing=0, vertical_alignment=ft.CrossAxisAlignment.STRETCH)

        # Build Page
        self.page.add(
            ft.Column([
                self.top_bar,
                self.main_row,
                self.footer
            ], expand=True, spacing=0)
        )
        
        # AI Drawer removed in favor of side panel

        # Modals
        self.file_picker = ft.FilePicker()
        self.page.services.append(self.file_picker)

        self.zoom_image = ft.Image(src="", fit=ft.BoxFit.CONTAIN)
        self.zoom_viewer = ft.InteractiveViewer(content=self.zoom_image, min_scale=0.5, max_scale=5.0, boundary_margin=ft.Margin.all(20), expand=True)
        self.zoom_modal = ft.AlertDialog(content=ft.Container(content=self.zoom_viewer, width=800, height=600), actions=[ft.TextButton("Fechar", on_click=lambda e: self.page.pop_dialog())])
        
        self.page.on_keyboard_event = self.on_keyboard_event

    def on_keyboard_event(self, e: ft.KeyboardEvent):
        if e.alt:
            if e.key in ("Page Down", "PageDown"):
                self.lesson_view.content_column.scroll_to(delta=400, duration=150)
            elif e.key in ("Page Up", "PageUp"):
                self.lesson_view.content_column.scroll_to(delta=-400, duration=150)

    def on_lang_changed(self, e):
        lang = self.lang_dropdown.value
        self.state.progress_manager.set_user_language(lang)
        self.state.content_manager.set_language(lang)
        self.state.all_lessons = self.state.content_manager.get_all_lessons()
        from rag_module import LessonRAG
        self.state.lesson_rag = LessonRAG(self.state.all_lessons)
        self.update_ui_strings()
        self.page.update()

    def update_ui_strings(self, skip_lesson_select=False):
        cm = self.state.content_manager
        self.tf_username.label = cm.get_ui_string("lbl_username")
        self.tf_password.label = cm.get_ui_string("lbl_password")
        self.btn_login.content = cm.get_ui_string("btn_login")
        self.btn_register.content = cm.get_ui_string("btn_register")
        self.welcome_title.value = cm.get_ui_string("lbl_welcome")
        self.welcome_subtitle.value = cm.get_ui_string("lbl_login_msg")
        self.btn_prev.content = cm.get_ui_string("btn_prev")
        self.btn_next.content = cm.get_ui_string("btn_next")
        
        # Dispatch to other components
        if hasattr(self.sidebar, 'update_strings'): self.sidebar.update_strings()
        if hasattr(self.top_bar, 'update_strings'): self.top_bar.update_strings()
        if hasattr(self.lesson_view, 'update_strings'): self.lesson_view.update_strings()
        if hasattr(self.editor_console, 'update_strings'): self.editor_console.update_strings()
        if hasattr(self.tutor_panel, 'update_strings'): self.tutor_panel.update_strings()
        
        # Trigger re-render of current lesson content
        if not skip_lesson_select and self.state.current_lesson_idx is not None:
            self.on_lesson_select(self.state.current_lesson_idx)
            
        self.update_footer()

    def setup_callbacks(self):
        self.state.console_controller.on_execution_start = self.on_exec_start
        self.state.console_controller.on_execution_finish = self.on_execution_finish_wrapper

    def on_execution_finish_wrapper(self, stdout, stderr, returncode):
        if returncode == 0 and not stderr:
            self.on_exec_result(stdout)
        else:
            error_msg = stderr.strip() if stderr else stdout.strip()
            self.on_exec_error(error_msg)

    def on_lesson_select(self, idx):
        self.state.notify_lesson_changed(idx)
        
        # Clear console and smart messages when changing lessons
        self.editor_console.smart_messages_panel.content = ft.Text("")
        self.editor_console.smart_messages_panel.bgcolor = "#1e293b"
        self.editor_console.smart_messages_panel.visible = False
        self.editor_console.btn_ask_ai_err.visible = False
        self.editor_console.console_output.value = ""
        
        self.update_layout_for_lesson()
        self.update_footer()

    def update_layout_for_lesson(self):
        lesson = self.state.current_lesson
        if not lesson: return
        is_theory = lesson.get("type") == "theory"
        is_presentation = lesson.get("type") == "presentation"

        self.editor_console.visible = not is_theory and not is_presentation
        self.lesson_view.coding_elements_container.visible = not is_theory and not is_presentation
        self.sidebar.sidebar_ai_container.visible = not is_theory and not is_presentation
        if is_theory or is_presentation:
            self.ai_sidebar_container.visible = False
            self.ai_splitter.visible = False
            self.ai_splitter_container.visible = False
            self.left_panel.expand = 100000 - self.sidebar.expand

        if is_presentation:
            self.state.progress_manager.mark_lesson_completed(lesson["id"])
            self.state.notify_progress_changed()
            self.drag_splitter.visible = False
        else:
            self.drag_splitter.visible = True

        if is_theory:
            self.lesson_view.expand = 40000
            self.lesson_view.activity_container.expand = 60000
        else:
            self.lesson_view.expand = 50000
            self.editor_console.expand = 50000
            
        self.page.update()

    def update_footer(self):
        total = len(self.state.all_lessons)
        idx = self.state.current_lesson_idx
        pct = 0
        if idx is not None and total > 0:
            pct = int(((idx + 1) / total) * 100)
            
        username = self.state.progress_manager.get_current_username() or "Aluno"
        cm = self.state.content_manager
        
        lbl_student = cm.get_ui_string("lbl_student", "Aluno")
        lbl_lesson = cm.get_ui_string("lbl_lesson", "Lição")
        lbl_of = cm.get_ui_string("lbl_of", "de")
        lbl_completed = cm.get_ui_string("lbl_completed", "% concluído")
        
        idx_display = (idx + 1) if idx is not None else 0
        self.footer_status_text.value = f"{lbl_student}: {username} | {lbl_lesson} {idx_display} {lbl_of} {total} ({pct}{lbl_completed})"
        self.btn_prev.disabled = (idx is None or idx == 0)
        self.btn_next.disabled = (idx is None or idx == total - 1)
        self.page.update()

    def on_admin_toggle(self, e):
        self.state.admin_mode_enabled = self.admin_switch.value
        self.state.notify_lesson_changed() # Trigger re-render of sidebar

    def on_prev_lesson(self, e):
        if self.state.current_lesson_idx > 0:
            self.on_lesson_select(self.state.current_lesson_idx - 1)

    def on_next_lesson(self, e):
        if self.state.current_lesson_idx < len(self.state.all_lessons) - 1:
            if not self.state.admin_mode_enabled:
                curr_id = self.state.current_lesson.get("id", self.state.current_lesson_idx)
                if curr_id not in self.state.progress_manager.get_completed_lessons():
                    self.show_snack("Complete a lição atual antes de avançar!", "#f59e0b")
                    return
            self.on_lesson_select(self.state.current_lesson_idx + 1)

    def show_snack(self, msg, color="#10b981"):
        snack = ft.SnackBar(ft.Text(msg, color="white"), bgcolor=color)
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()

    def on_login(self, e):
        cm = self.state.content_manager
        u, p = self.tf_username.value.strip(), self.tf_password.value.strip()
        if not u or not p: return self.show_snack("Preencha todos os campos!", "#f59e0b")
        if self.state.progress_manager.login(u, p):
            # Save the currently selected dropdown language to the database
            selected_lang = self.lang_dropdown.value
            self.state.progress_manager.set_user_language(selected_lang)
            self.state.content_manager.set_language(selected_lang)
            self.state.all_lessons = self.state.content_manager.get_all_lessons()
            from rag_module import LessonRAG
            self.state.lesson_rag = LessonRAG(self.state.all_lessons)
            self.update_ui_strings(skip_lesson_select=True)
            
            self.sidebar.visible = True
            self.footer.visible = True
            self.top_bar.visible = True
            self.lesson_view.visible = True
            self.welcome_container.visible = False
            is_admin = (u == "admin" and p == "admin")
            self.admin_switch_container.visible = is_admin
            self.admin_switch.value = is_admin
            self.state.admin_mode_enabled = is_admin
            lesson_id = self.state.progress_manager.get_current_lesson()
            self.on_lesson_select(self.state.get_lesson_index_by_id(lesson_id))
            self.show_snack(cm.get_ui_string("msg_welcome_back").replace("{}", u))
        else:
            self.show_snack(cm.get_ui_string("msg_invalid_login"), "#dc2626")

    def on_register(self, e):
        cm = self.state.content_manager
        u, p = self.tf_username.value.strip(), self.tf_password.value.strip()
        if not u or not p: return self.show_snack("Preencha todos os campos!", "#f59e0b")
        if self.state.progress_manager.register(u, p):
            self.state.progress_manager.set_user_language(self.lang_dropdown.value)
            self.show_snack(cm.get_ui_string("msg_user_created"))
            self.tf_password.value = ""
            self.page.update()
        else:
            self.show_snack(cm.get_ui_string("msg_user_exists"), "#dc2626")

    def on_logout(self, e):
        cm = self.state.content_manager
        self.state.progress_manager.logout()
        
        self.state.admin_mode_enabled = False
        self.admin_switch.value = False
        
        self.state.current_lesson_idx = None
        
        self.top_bar.visible = False
        self.sidebar.visible = False
        self.footer.visible = False
        self.lesson_view.visible = False
        
        # Clear smart messages panel to prevent previous session messages leaking
        self.editor_console.smart_messages_panel.content = ft.Text("")
        self.editor_console.smart_messages_panel.bgcolor = "#1e293b"
        self.editor_console.smart_messages_panel.visible = False
        self.editor_console.btn_ask_ai_err.visible = False
        self.editor_console.visible = False
        self.ai_sidebar_container.visible = False
        self.ai_splitter.visible = False
        self.ai_splitter_container.visible = False
        self.admin_switch_container.visible = False
        self.drag_splitter.visible = False
        self.lesson_view.activity_container.visible = False
        self.welcome_container.visible = True
        
        self.tf_password.value = ""
        
        self.page.update()
        self.show_snack(cm.get_ui_string("msg_logged_out", "Logout efetuado com sucesso!"))

    def toggle_ai_sidebar(self):
        self.tutor_panel.update_ollama_status()
        self.ai_sidebar_container.visible = not self.ai_sidebar_container.visible
        self.ai_splitter_container.visible = self.ai_sidebar_container.visible
        self.ai_splitter.visible = self.ai_sidebar_container.visible
        if self.ai_sidebar_container.visible:
            self.left_panel.expand = 100000 - self.sidebar.expand - self.ai_sidebar_container.expand
        else:
            self.left_panel.expand = 100000 - self.sidebar.expand
        self.page.update()

    def do_export_progress(self, e):
        async def _export():
            u = self.state.progress_manager.get_current_username() or "pyeduc"
            p = await self.file_picker.save_file(dialog_title="Exportar Progresso", file_name=f"progresso_{u}.json", allowed_extensions=["json"])
            if p:
                if self.state.progress_manager.export_progress(p): self.show_snack("Progresso exportado! 💾")
                else: self.show_snack("Erro ao exportar! ❌", "#ef4444")
        self.page.run_task(_export)

    def do_import_progress(self, e):
        async def _import():
            fs = await self.file_picker.pick_files(dialog_title="Importar Progresso", allowed_extensions=["json"])
            if fs:
                try:
                    if self.state.progress_manager.import_progress(fs[0].path):
                        self.show_snack(self.state.content_manager.get_ui_string("msg_success", "Sucesso") + "!")
                        lesson_id = self.state.progress_manager.get_current_lesson()
                        self.on_lesson_select(self.state.get_lesson_index_by_id(lesson_id))
                except Exception as ex:
                    self.show_snack("Arquivo inválido! ❌", "#ef4444")
        self.page.run_task(_import)

    def on_zoom_image(self, src):
        self.zoom_image.src = src
        self.page.dialog = self.zoom_modal
        self.zoom_modal.open = True
        self.page.update()

    def on_copy_example(self, text):
        self.editor_console.console_input.value = text
        self.editor_console.update()

    def execute_code(self, code):
        self.state.console_controller.execute_code(code)

    def ask_ai_error(self):
        self.toggle_ai_sidebar()
        self.tutor_panel.send_to_ai(quick_action="error_help")

    def on_exec_start(self):
        self.editor_console.btn_execute.disabled = True
        self.editor_console.update()

    def on_exec_result(self, result):
        import re
        self.editor_console.btn_execute.disabled = False
        self.editor_console.console_output.value += result + "\n"
        self.editor_console.btn_ask_ai_err.visible = False
        self.editor_console.smart_messages_panel.visible = True
        
        cm = self.state.content_manager
        
        self.editor_console.smart_messages_panel.content = ft.Column([
            ft.Text(cm.get_ui_string("msg_all_good_title", "Tudo certo por enquanto!"), weight="bold", size=14, color="white"),
            ft.Text(cm.get_ui_string("msg_all_good_desc", "Continue o bom trabalho."), color="#94a3b8", size=13, italic=True)
        ], spacing=6)
        self.editor_console.smart_messages_panel.bgcolor = "#1e293b"
        
        active_rows = self.lesson_view.active_exercises_rows
        pending_exercises = [
            r for r in active_rows 
            if str(getattr(r, "data", "")).strip() and r.controls and isinstance(r.controls[0], ft.Icon) and r.controls[0].icon != ft.Icons.CHECK_CIRCLE
        ]
        
        if result and result.strip():
            output_lines = [line.strip() for line in result.split('\n') if line.strip()]
            
            def fuzzy_clean(text):
                return re.sub(r'[\.,;:\!\?]+$', '', text.strip()).strip().lower()
            
            available_lines = list(output_lines)
            available_fuzzy = [fuzzy_clean(l) for l in available_lines]
            
            any_exact_match = False
            any_fuzzy_match = False
            
            # Verificação Sequencial: processa exercícios pendentes em ordem
            pending_exercises = [
                r for r in active_rows 
                if str(getattr(r, "data", "")).strip() and r.controls and isinstance(r.controls[0], ft.Icon) and r.controls[0].icon != ft.Icons.CHECK_CIRCLE
            ]

            for row in pending_exercises:
                expected = str(getattr(row, "data", "")).strip()
                expected_lines = [line.strip() for line in expected.split('\n') if line.strip()]
                fuzzy_expected_lines = [fuzzy_clean(line) for line in expected_lines]
                n = len(expected_lines)
                
                is_match = False
                is_fuzzy = False
                
                # Tentativa Exata
                if n == 1:
                    exp = expected_lines[0]
                    if exp in available_lines:
                        idx = available_lines.index(exp)
                        available_lines.pop(idx)
                        available_fuzzy.pop(idx)
                        is_match = True
                elif n > 1:
                    for i in range(len(available_lines) - n + 1):
                        if available_lines[i:i+n] == expected_lines:
                            for _ in range(n):
                                available_lines.pop(i)
                                available_fuzzy.pop(i)
                            is_match = True
                            break
                
                # Tentativa Fuzzy
                if not is_match:
                    if n == 1:
                        exp_fuzz = fuzzy_expected_lines[0]
                        if exp_fuzz in available_fuzzy:
                            idx = available_fuzzy.index(exp_fuzz)
                            available_lines.pop(idx)
                            available_fuzzy.pop(idx)
                            is_match = True
                            is_fuzzy = True
                    elif n > 1:
                        for i in range(len(available_fuzzy) - n + 1):
                            if available_fuzzy[i:i+n] == fuzzy_expected_lines:
                                for _ in range(n):
                                    available_lines.pop(i)
                                    available_fuzzy.pop(i)
                                is_match = True
                                is_fuzzy = True
                                break

                if is_match:
                    row.controls[0].icon = ft.Icons.CHECK_CIRCLE
                    row.controls[0].color = "#10b981"
                    try:
                        idx = self.lesson_view.active_exercises_rows.index(row)
                        self.state.completed_exercises_indices.add(idx)
                        lesson_id = self.state.current_lesson.get("id")
                        if lesson_id is not None:
                            self.state.progress_manager.mark_activity_completed(lesson_id, idx)
                    except ValueError:
                        pass
                    
                    if is_fuzzy:
                        any_fuzzy_match = True
                    else:
                        any_exact_match = True
                else:
                    # Enforça ordem sequencial: se o atual não bateu, ignora os próximos!
                    break

            if any_exact_match:
                gradable_rows = [r for r in active_rows if str(getattr(r, "data", "")).strip() and r.controls and isinstance(r.controls[0], ft.Icon)]
                all_done = gradable_rows and all(r.controls[0].icon == ft.Icons.CHECK_CIRCLE for r in gradable_rows)
                if all_done:
                    lid = self.state.current_lesson.get("id")
                    if lid is not None:
                        self.state.progress_manager.mark_lesson_completed(lid)
                        self.state.notify_progress_changed()
                    self.editor_console.smart_messages_panel.content = ft.Text(cm.get_ui_string("msg_all_exercises_done", "🎉 Parabéns! Todos os exercícios desta aula foram concluídos!"), color="white", size=13, weight="bold")
                    self.editor_console.smart_messages_panel.bgcolor = "#15803d"
                else:
                    self.editor_console.smart_messages_panel.content = ft.Text(cm.get_ui_string("msg_exercise_done", "✅ Muito bem! Exercício concluído com sucesso."), color="white", size=13, weight="bold")
                    self.editor_console.smart_messages_panel.bgcolor = "#15803d"
            elif any_fuzzy_match:
                self.editor_console.smart_messages_panel.content = ft.Text(cm.get_ui_string("msg_almost_there", "💡 Quase lá!\n\nSeu código imprimiu quase o valor esperado. Verifique se você não colocou um ponto final, espaço a mais, ou errou uma letra maiúscula/minúscula na saída."), color="white", size=13)
                self.editor_console.smart_messages_panel.bgcolor = "#b45309"
            elif pending_exercises:
                self.editor_console.smart_messages_panel.content = ft.Column([
                    ft.Text(cm.get_ui_string("msg_output_mismatch_title", "⚠️ Saída não corresponde ao exercício:"), weight="bold", size=14, color="white"),
                    ft.Text(cm.get_ui_string("msg_output_mismatch_desc", "Seu código imprimiu um resultado, mas a saída não atende ao esperado pelos exercícios pendentes."), size=13, color="white")
                ], spacing=6)
                self.editor_console.smart_messages_panel.bgcolor = "#b45309"
        elif pending_exercises:
            self.editor_console.smart_messages_panel.content = ft.Column([
                ft.Text(cm.get_ui_string("msg_no_output_title", "⚠️ Nenhum resultado impresso na tela:"), weight="bold", size=14, color="white"),
                ft.Text(cm.get_ui_string("msg_no_output_desc", "Seu código foi executado sem erros, mas não imprimiu nada. Lembre-se de usar a função print(...) para exibir o resultado."), size=13, color="white")
            ], spacing=6)
            self.editor_console.smart_messages_panel.bgcolor = "#b45309"

        self.editor_console.update()
        self.lesson_view.update()

    def on_exec_error(self, error):
        self.editor_console.btn_execute.disabled = False
        self.editor_console.console_output.value += f"ERRO:\n{error}\n"
        self.editor_console.btn_ask_ai_err.visible = True
        self.editor_console.smart_messages_panel.visible = True
        
        cm = self.state.content_manager
        
        if "SyntaxError" in error:
            self.editor_console.smart_messages_panel.content = ft.Column([
                ft.Text(cm.get_ui_string("msg_syntax_error_title", "Erro de Sintaxe (SyntaxError):"), weight="bold", size=14, color="white"),
                ft.Text(cm.get_ui_string("msg_syntax_error_desc", "Parece que há um erro na escrita do código. Verifique aspas, parênteses ou digitação."), size=13, color="white")
            ], spacing=6)
            self.editor_console.smart_messages_panel.bgcolor = "#991b1b"
        elif "NameError" in error:
            self.editor_console.smart_messages_panel.content = ft.Column([
                ft.Text(cm.get_ui_string("msg_name_error_title", "Erro de Nome (NameError):"), weight="bold", size=14, color="white"),
                ft.Text(cm.get_ui_string("msg_name_error_desc", "Você tentou usar uma variável ou função inexistente."), size=13, color="white")
            ], spacing=6)
            self.editor_console.smart_messages_panel.bgcolor = "#991b1b"
        elif "IndentationError" in error:
            self.editor_console.smart_messages_panel.content = ft.Column([
                ft.Text(cm.get_ui_string("msg_indentation_error_title", "Erro de Indentação (IndentationError):"), weight="bold", size=14, color="white"),
                ft.Text(cm.get_ui_string("msg_indentation_error_desc", "Verifique os espaços no começo das linhas."), size=13, color="white")
            ], spacing=6)
            self.editor_console.smart_messages_panel.bgcolor = "#991b1b"
        elif "TypeError" in error:
            self.editor_console.smart_messages_panel.content = ft.Column([
                ft.Text(cm.get_ui_string("msg_type_error_title", "Erro de Tipo (TypeError):"), weight="bold", size=14, color="white"),
                ft.Text(cm.get_ui_string("msg_type_error_desc", "Você tentou misturar tipos incompatíveis."), size=13, color="white")
            ], spacing=6)
            self.editor_console.smart_messages_panel.bgcolor = "#991b1b"
        else:
            self.editor_console.smart_messages_panel.content = ft.Column([
                ft.Text(cm.get_ui_string("msg_execution_error_title", "Erro de Execução:"), weight="bold", size=14, color="white"),
                ft.Text(cm.get_ui_string("msg_execution_error_desc", "Verifique o erro retornado no console."), size=13, color="white")
            ], spacing=6)
            self.editor_console.smart_messages_panel.bgcolor = "#991b1b"

        self.editor_console.update()

    def on_pan_update_splitter(self, e):
        change = int((e.local_delta.y if e.local_delta else 0) * 100)
        if change != 0:
            new_expand = max(20000, min(80000, self.lesson_view.expand + change))
            self.lesson_view.expand = new_expand
            self.editor_console.expand = 100000 - new_expand
            self.lesson_view.activity_container.expand = 100000 - new_expand
            self.welcome_container.expand = 100000 - new_expand
            self.page.update()

    def on_hover_splitter(self, e):
        self.drag_splitter_container.bgcolor = "#38bdf8" if e.data == "true" else "#cbd5e1"
        self.drag_splitter_container.update()

    def on_pan_update_sidebar_splitter(self, e):
        delta = e.local_delta.x if e.local_delta else 0
        change = int(delta * 80)
        if change != 0:
            new_exp = max(15000, min(45000, self.sidebar.expand + change))
            self.sidebar.expand = new_exp
            ai_exp = self.ai_sidebar_container.expand if self.ai_sidebar_container.visible else 0
            self.left_panel.expand = 100000 - new_exp - ai_exp
            self.page.update()

    def on_hover_sidebar_splitter(self, e):
        self.sidebar_splitter_container.bgcolor = "#38bdf8" if e.data == "true" else "#cbd5e1"
        self.sidebar_splitter_container.update()

    def on_pan_update_ai_splitter(self, e):
        delta = e.local_delta.x if e.local_delta else 0
        change = int(delta * -80)
        if change != 0:
            new_exp = max(15000, min(50000, self.ai_sidebar_container.expand + change))
            self.ai_sidebar_container.expand = new_exp
            self.left_panel.expand = 100000 - self.sidebar.expand - new_exp
            self.page.update()

    def on_hover_ai_splitter(self, e):
        self.ai_splitter_container.bgcolor = "#38bdf8" if e.data == "true" else "#cbd5e1"
        self.ai_splitter_container.update()
