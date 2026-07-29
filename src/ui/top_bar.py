import flet as ft
from ui.app_state import AppState
import config

class TopBar(ft.Container):
    def __init__(self, state: AppState, on_export, on_import, on_logout):
        super().__init__()
        self.state = state
        self.on_export = on_export
        self.on_import = on_import
        self.on_logout = on_logout
        
        cm = self.state.content_manager
        self.title_text = ft.Text(cm.get_ui_string("top_bar_title", "Aula de Exemplo"), size=20, weight="bold", color="white")
        
        self.btn_font_reset_text = ft.Text("100%", size=14, color="#cbd5e1", weight="bold")
        self.btn_font_minus = ft.IconButton(ft.Icons.TEXT_DECREASE, on_click=lambda e: self.change_font_size(-1), tooltip="Diminuir Fonte", icon_color="#cbd5e1")
        self.btn_font_reset = ft.TextButton(content=self.btn_font_reset_text, on_click=lambda e: self.change_font_size(0, reset=True), tooltip="Tamanho Original")
        self.btn_font_plus = ft.IconButton(ft.Icons.TEXT_INCREASE, on_click=lambda e: self.change_font_size(1), tooltip="Aumentar Fonte", icon_color="#cbd5e1")
        
        self.btn_export = ft.ElevatedButton("Exportar Progresso", icon=ft.Icons.UPLOAD_FILE, on_click=self.on_export, bgcolor="#3b82f6", color="white", scale=0.9)
        self.btn_import = ft.ElevatedButton("Importar Progresso", icon=ft.Icons.DOWNLOAD, on_click=self.on_import, bgcolor="#10b981", color="white", scale=0.9)
        self.btn_logout = ft.ElevatedButton(cm.get_ui_string("btn_logout", "Sair"), icon=ft.Icons.LOGOUT, on_click=self.on_logout, bgcolor="#ef4444", color="white", scale=0.9)

        app_logo_icon = ft.Image(src=config.APP_ICON, width=24, height=24)
        
        self.visible = False
        self.content = ft.Row([
            ft.Row([app_logo_icon, self.title_text], spacing=10, alignment=ft.MainAxisAlignment.START),
            ft.Row([
                ft.Row([self.btn_font_minus, self.btn_font_reset, self.btn_font_plus], spacing=4),
                ft.Container(width=1, height=22, bgcolor="#475569"),
                self.btn_export,
                self.btn_import,
                self.btn_logout
            ], spacing=10)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.bgcolor = "#1e293b"
        self.padding = 12
        self.alignment = ft.Alignment.CENTER_LEFT
        
        self.state.on_lesson_changed_callbacks.append(self.update_title)

    def update_title(self):
        if self.state.current_lesson:
            self.title_text.value = self.state.current_lesson["title"]
            self.update()

    def change_font_size(self, delta: int, reset: bool = False):
        if reset:
            self.state.current_font_idx = 2
        else:
            self.state.current_font_idx = max(0, min(len(self.state.font_sizes) - 1, self.state.current_font_idx + delta))
        
        percent = int((self.state.current_font_size / 15.0) * 100)
        self.btn_font_reset_text.value = f"{percent}%"
        self.state.notify_font_size_changed()
        self.update()

    def update_strings(self):
        cm = self.state.content_manager
        self.btn_export.text = cm.get_ui_string("btn_export")
        self.btn_import.text = cm.get_ui_string("btn_import")
        self.btn_logout.text = cm.get_ui_string("btn_logout", "Sair")
        self.update()
