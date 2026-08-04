import flet as ft
from ui.app_state import AppState
import config

class Sidebar(ft.Container):
    def __init__(self, state: AppState, on_lesson_select, on_open_ai):
        super().__init__()
        self.state = state
        self.on_lesson_select = on_lesson_select
        self.on_open_ai = on_open_ai
        self.expand = 30000
        
        cm = self.state.content_manager
        
        self.progress_bar = ft.ProgressBar(value=0.0, color="#10b981", bgcolor="#e2e8f0", border_radius=5)
        self.progress_text = ft.Text(f"{cm.get_ui_string('lbl_progress', 'Progresso:')} 0%", size=12, weight="bold", color="#64748b")
        
        self.lesson_list = ft.ListView(expand=True, spacing=5, padding=10)
        
        self.btn_open_ai = ft.ElevatedButton(
            "Abrir Tutor IA",
            icon=ft.Icons.SMART_TOY_ROUNDED,
            bgcolor="#7c3aed",
            color="white",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=12
            ),
            on_click=lambda e: self.on_open_ai()
        )
        self.sidebar_ai_container = ft.Container(
            content=self.btn_open_ai,
            padding=10,
            alignment=ft.Alignment.CENTER,
            visible=False
        )

        self.lbl_modules = ft.Text(cm.get_ui_string("tab_theory", "Módulos"), size=18, weight="bold", color="#1e293b")

        self.content = ft.Column([
            self.lbl_modules,
            ft.Column([
                ft.Row([self.progress_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.progress_bar
            ], spacing=5),
            ft.Divider(height=2, color="#cbd5e1"),
            self.lesson_list,
            self.sidebar_ai_container
        ])
        
        self.bgcolor = "white"
        self.padding = 15
        self.width = 250
        self.visible = False
        
        self.state.on_progress_changed_callbacks.append(self.update_ui)
        self.state.on_lesson_changed_callbacks.append(self.update_ui)

    def update_ui(self):
        # Update progress bar
        completed_lessons = self.state.progress_manager.get_completed_lessons()
        if not self.state.all_lessons:
            return
            
        total_lessons = len(self.state.all_lessons)
        progress_val = len(completed_lessons) / total_lessons if total_lessons > 0 else 0
        self.progress_bar.value = progress_val
        cm = self.state.content_manager
        self.progress_text.value = f"{cm.get_ui_string('lbl_progress', 'Progresso:')} {int(progress_val * 100)}%"

        # Rebuild lesson list
        self.lesson_list.controls.clear()
        
        admin = self.state.admin_mode_enabled
        
        for i, lesson in enumerate(self.state.all_lessons):
            lesson_id = lesson.get("id", i)
            is_completed = lesson_id in completed_lessons
            
            # Lock logic
            is_locked = False
            if not admin:
                if i > 0:
                    prev_id = self.state.all_lessons[i-1].get("id", i-1)
                    if prev_id not in completed_lessons:
                        is_locked = True
                        
            is_current = (i == self.state.current_lesson_idx)
            
            if is_locked:
                icon = ft.Icons.LOCK_OUTLINE
                color = "#94a3b8"
                bg_color = "transparent"
            elif is_completed:
                icon = ft.Icons.CHECK_CIRCLE
                color = "#10b981"
                bg_color = "#f0fdf4" if is_current else "transparent"
            else:
                icon = ft.Icons.PLAY_CIRCLE_OUTLINE
                color = "#3b82f6" if is_current else "#64748b"
                bg_color = "#eff6ff" if is_current else "transparent"
                
            def make_click_handler(idx, locked):
                def handler(e):
                    if locked:
                        return
                    self.on_lesson_select(idx)
                return handler
                
            btn = ft.Container(
                content=ft.Row([
                    ft.Icon(icon, color=color, size=20),
                    ft.Text(lesson["title"], color=color, weight="bold" if is_current else "normal", size=13, expand=True)
                ]),
                padding=10,
                border_radius=8,
                bgcolor=bg_color,
                ink=True if not is_locked else False,
                on_click=make_click_handler(i, is_locked)
            )
            self.lesson_list.controls.append(btn)
            
        # self.update() removido para permitir renderização em lote pelo componente pai (Single Truth Render)

    def update_strings(self):
        cm = self.state.content_manager
        self.btn_open_ai.content = cm.get_ui_string("btn_ask_ai")
        # Modules text
        if hasattr(self, "lbl_modules"):
            self.lbl_modules.value = cm.get_ui_string("tab_theory", "Módulos")
        self.update_ui()
