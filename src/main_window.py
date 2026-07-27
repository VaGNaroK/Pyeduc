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
        self.sidebar = Sidebar(self.state, self.on_lesson_select, self.open_ai_drawer)
        self.top_bar = TopBar(self.state, self.do_export_progress, self.do_import_progress)
        self.lesson_view = LessonView(self.state, self.on_copy_example)
        self.editor_console = EditorConsole(self.state, self.execute_code, self.ask_ai_error)
        self.tutor_panel = TutorPanel(self.state)
        
        # Wiring cross-component dependencies
        self.state.get_student_code = lambda: self.editor_console.console_input.value
        self.state.get_console_output = lambda: self.editor_console.console_output.value
        self.state.get_exercise_statuses = self.lesson_view.get_exercise_statuses
        self.state.on_zoom_image = self.on_zoom_image

        # Welcome Container
        self.tf_username = ft.TextField(label="Nome de Usuário", width=300, bgcolor="white", color="black", border_color="#cbd5e1")
        self.tf_password = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300, bgcolor="white", color="black", border_color="#cbd5e1")
        btn_login = ft.ElevatedButton("Entrar", bgcolor="#3b82f6", color="white", on_click=self.on_login, width=140)
        btn_register = ft.ElevatedButton("Cadastrar", bgcolor="#10b981", color="white", on_click=self.on_register, width=140)
        
        self.welcome_container = ft.Container(
            content=ft.Column([
                ft.Image(src=config.APP_ICON, width=250),
                ft.Text("Pyeduc", size=32, weight="bold", color="#1e293b"),
                ft.Text("Faça login para continuar de onde parou.", size=14, color="#64748b"),
                ft.Container(height=20),
                self.tf_username,
                self.tf_password,
                ft.Row([btn_login, btn_register], alignment=ft.MainAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#f8fafc",
            padding=40,
            expand=50,
            visible=True
        )

        # Footer
        self.footer_status_text = ft.Text("👤 Aluno: ---", color="white", size=12)
        self.admin_switch = ft.Switch(label="Modo Admin", value=self.state.admin_mode_enabled, on_change=self.on_admin_toggle, label_position=ft.LabelPosition.LEFT)
        self.admin_switch_container = ft.Container(content=self.admin_switch, visible=False)
        self.btn_prev = ft.OutlinedButton("Aula Anterior", icon=ft.Icons.ARROW_BACK, on_click=self.on_prev_lesson, style=ft.ButtonStyle(color="white"))
        self.btn_next = ft.ElevatedButton("Próxima Aula", icon=ft.Icons.ARROW_FORWARD, bgcolor="#10b981", color="white", on_click=self.on_next_lesson)
        
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
            mouse_cursor=ft.MouseCursor.RESIZE_UP_DOWN, drag_interval=10,
            on_pan_update=self.on_pan_update_splitter, on_hover=self.on_hover_splitter,
            content=self.drag_splitter_container
        )

        self.sidebar_splitter_container = ft.Container(
            width=6, bgcolor="#cbd5e1", border_radius=3, margin=ft.Margin.symmetric(vertical=10, horizontal=2),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )
        self.sidebar_splitter = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT, drag_interval=10,
            on_pan_update=self.on_pan_update_sidebar_splitter, on_hover=self.on_hover_sidebar_splitter,
            content=self.sidebar_splitter_container
        )

        self.left_panel = ft.Column([
            self.lesson_view,
            self.drag_splitter,
            self.editor_console,
            self.lesson_view.activity_container,
            self.welcome_container
        ], expand=7, spacing=0, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

        self.main_row = ft.Row([
            self.sidebar,
            self.sidebar_splitter,
            self.left_panel
        ], expand=True, spacing=0, vertical_alignment=ft.CrossAxisAlignment.STRETCH)

        # Build Page
        self.page.add(
            ft.Column([
                self.top_bar,
                self.main_row,
                self.footer
            ], expand=True, spacing=0)
        )
        
        # AI Drawer
        self.ai_drawer = ft.NavigationDrawer(controls=[self.tutor_panel])
        self.page.end_drawer = self.ai_drawer

        # Modals
        self.file_picker = ft.FilePicker()
        self.page.services.append(self.file_picker)

        self.zoom_image = ft.Image(src="", fit=ft.BoxFit.CONTAIN)
        self.zoom_viewer = ft.InteractiveViewer(content=self.zoom_image, min_scale=0.5, max_scale=5.0, boundary_margin=ft.Margin.all(20), expand=True)
        self.zoom_modal = ft.AlertDialog(content=ft.Container(content=self.zoom_viewer, width=800, height=600), actions=[ft.TextButton("Fechar", on_click=lambda e: self.page.pop_dialog())])

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

        if is_presentation:
            self.state.progress_manager.mark_lesson_completed(lesson["id"])
            self.state.notify_progress_changed()
            self.drag_splitter.visible = False
        else:
            self.drag_splitter.visible = True

        if is_theory:
            self.lesson_view.expand = 40
            self.lesson_view.activity_container.expand = 60
        else:
            self.lesson_view.expand = 50
            self.editor_console.expand = 50
            
        self.page.update()

    def update_footer(self):
        total = len(self.state.all_lessons)
        idx = self.state.current_lesson_idx
        pct = int(((idx + 1) / total) * 100) if total > 0 else 0
        username = self.state.progress_manager.get_current_username() or "Aluno"
        self.footer_status_text.value = f"👤 Aluno: {username}  |  Lição {idx + 1} de {total} ({pct}% concluído)"
        self.btn_prev.disabled = (idx == 0)
        self.btn_next.disabled = (idx == total - 1)
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
        u, p = self.tf_username.value.strip(), self.tf_password.value.strip()
        if not u or not p: return self.show_snack("Preencha todos os campos!", "#f59e0b")
        if self.state.progress_manager.login(u, p):
            self.sidebar.visible = True
            self.footer.visible = True
            self.top_bar.visible = True
            self.lesson_view.visible = True
            self.welcome_container.visible = False
            is_admin = (u == "admin" and p == "admin")
            self.admin_switch_container.visible = is_admin
            self.admin_switch.value = is_admin
            self.state.admin_mode_enabled = is_admin
            self.on_lesson_select(self.state.progress_manager.get_current_lesson())
            self.show_snack(f"Bem-vindo de volta, {u}!")
        else:
            self.show_snack("Usuário ou senha incorretos!", "#dc2626")

    def on_register(self, e):
        u, p = self.tf_username.value.strip(), self.tf_password.value.strip()
        if not u or not p: return self.show_snack("Preencha todos os campos!", "#f59e0b")
        if self.state.progress_manager.register(u, p):
            self.show_snack(f"Usuário {u} cadastrado! Faça Login.")
            self.tf_password.value = ""
            self.page.update()
        else:
            self.show_snack("Usuário já existe!", "#dc2626")

    def open_ai_drawer(self):
        self.tutor_panel.update_ollama_status()
        self.ai_drawer.open = True
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
                if self.state.progress_manager.import_progress(fs[0].path):
                    self.show_snack("Progresso importado! 🎉")
                    self.on_lesson_select(self.state.progress_manager.get_current_lesson())
                else:
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
        self.open_ai_drawer()
        self.tutor_panel.send_to_ai(quick_action="error_help")

    def on_exec_start(self):
        self.editor_console.btn_execute.disabled = True
        self.editor_console.update()

    def on_exec_result(self, result):
        self.editor_console.btn_execute.disabled = False
        self.editor_console.console_output.value += result + "\n"
        self.editor_console.btn_ask_ai_err.visible = False
        self.editor_console.smart_messages_panel.visible = True
        
        # Auto-grader (Verify active exercises)
        lesson_completed = True
        for row in self.lesson_view.active_exercises_rows:
            expected = getattr(row, "data", "")
            if expected:
                if str(expected).strip() in result.strip():
                    if row.controls: row.controls[0].icon = ft.Icons.CHECK_CIRCLE; row.controls[0].color = "#10b981"
                else:
                    if row.controls: row.controls[0].icon = ft.Icons.RADIO_BUTTON_UNCHECKED; row.controls[0].color = "#94a3b8"
                    lesson_completed = False
            else:
                if row.controls: row.controls[0].icon = ft.Icons.CHECK_CIRCLE; row.controls[0].color = "#10b981"

        if lesson_completed and self.lesson_view.active_exercises_rows:
            lid = self.state.current_lesson.get("id")
            if lid is not None:
                self.state.progress_manager.mark_lesson_completed(lid)
                self.state.notify_progress_changed()

        self.editor_console.update()
        self.lesson_view.update()

    def on_exec_error(self, error):
        self.editor_console.btn_execute.disabled = False
        self.editor_console.console_output.value += f"ERRO: {error}\n"
        self.editor_console.btn_ask_ai_err.visible = True
        self.editor_console.smart_messages_panel.visible = False
        self.editor_console.update()

    def on_pan_update_splitter(self, e):
        change = int((e.local_delta.y if e.local_delta else 0) * 0.5)
        new_expand = max(20, min(80, self.lesson_view.expand + change))
        self.lesson_view.expand = new_expand
        self.editor_console.expand = 100 - new_expand
        self.lesson_view.activity_container.expand = 100 - new_expand
        self.welcome_container.expand = 100 - new_expand
        self.page.update()

    def on_hover_splitter(self, e):
        self.drag_splitter_container.bgcolor = "#38bdf8" if e.data == "true" else "#cbd5e1"
        self.drag_splitter_container.update()

    def on_pan_update_sidebar_splitter(self, e):
        delta = e.local_delta.x if e.local_delta else 0
        if abs(delta) > 2:
            change = 1 if delta < 0 else -1
            new_exp = max(2, min(4, self.sidebar.expand + change))
            self.sidebar.expand = new_exp
            self.left_panel.expand = 10 - new_exp
            self.page.update()

    def on_hover_sidebar_splitter(self, e):
        self.sidebar_splitter_container.bgcolor = "#38bdf8" if e.data == "true" else "#cbd5e1"
        self.sidebar_splitter_container.update()
