import flet as ft
from ui.app_state import AppState

class EditorConsole(ft.Container):
    def __init__(self, state: AppState, on_execute, on_ask_ai_error):
        super().__init__()
        self.state = state
        self.on_execute = on_execute
        self.on_ask_ai_error = on_ask_ai_error

        self.console_input = ft.TextField(
            multiline=True,
            min_lines=4,
            max_lines=7,
            text_style=ft.TextStyle(font_family="Consolas", size=14, color="#f8fafc"),
            bgcolor="#1e293b",
            border_color="#38bdf8",
            border_radius=6,
            content_padding=12,
            hint_text=self.state.content_manager.get_ui_string("lbl_type_code", "# Digite seu código Python aqui..."),
            hint_style=ft.TextStyle(color="#94a3b8")
        )
        
        self.console_output = ft.TextField(
            multiline=True,
            read_only=True,
            min_lines=5,
            text_style=ft.TextStyle(font_family="Consolas", size=13, color="#10b981"),
            bgcolor="#090d16",
            border=ft.InputBorder.NONE,
            content_padding=12,
            expand=True
        )
        
        self.console_output_container = ft.Container(
            content=self.console_output,
            bgcolor="#090d16",
            border=ft.Border.all(1.5, "#10b981"),
            border_radius=6,
            padding=2,
            expand=True
        )

        cm = self.state.content_manager
        self.lbl_console_title = ft.Text(cm.get_ui_string("console_title", "Console Python"), color="white", weight="bold", size=14)

        self.btn_execute = ft.ElevatedButton(
            content=cm.get_ui_string("btn_run", "Executar Código"),
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            style=ft.ButtonStyle(
                color={ft.ControlState.DEFAULT: "white"},
                bgcolor={
                    ft.ControlState.HOVERED: "#15803d",
                    ft.ControlState.DEFAULT: "#16a34a"
                },
                elevation={ft.ControlState.HOVERED: 6, ft.ControlState.DEFAULT: 2},
                shape=ft.RoundedRectangleBorder(radius=6),
                animation_duration=200
            ),
            on_click=self.handle_execute
        )

        self.btn_clear = ft.OutlinedButton(
            content=cm.get_ui_string("btn_clear", "Limpar"),
            icon=ft.Icons.DELETE_OUTLINE,
            style=ft.ButtonStyle(
                color={ft.ControlState.HOVERED: "white", ft.ControlState.DEFAULT: "#ef4444"},
                bgcolor={ft.ControlState.HOVERED: "#dc2626", ft.ControlState.DEFAULT: "transparent"},
                elevation={ft.ControlState.HOVERED: 3, ft.ControlState.DEFAULT: 0},
                shape=ft.RoundedRectangleBorder(radius=6),
                animation_duration=200
            ),
            on_click=self.handle_clear
        )

        self.btn_ask_ai_err = ft.ElevatedButton(
            "🤖 Pedir ajuda da IA para este erro",
            icon=ft.Icons.AUTO_AWESOME,
            bgcolor="#7c3aed",
            color="white",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=12),
            on_click=lambda e: self.on_ask_ai_error(),
            visible=False
        )

        self.smart_messages_panel = ft.Container(
            content=ft.Column([
                ft.Text("Tudo certo por enquanto!", weight="bold", size=14, color="white"),
                ft.Text("Continue o bom trabalho.", color="#94a3b8", size=13, italic=True)
            ], spacing=6),
            bgcolor="#1e293b",
            border_radius=6,
            padding=15
        )

        self.smart_messages_column = ft.Column([
            self.smart_messages_panel,
            self.btn_ask_ai_err
        ], spacing=10, expand=3, alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.content = ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.TERMINAL, color="#10b981", size=18),
                    self.lbl_console_title,
                ]),
                ft.Row([self.btn_execute, self.btn_clear])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Row([
                ft.Container(content=self.console_input, expand=7),
                self.smart_messages_column
            ]),
            
            self.console_output_container
        ], spacing=10)
        
        self.bgcolor = "#0f172a"
        self.padding = 15
        self.expand = 50
        
        # Subscribe to font size changes
        self.state.on_font_size_changed_callbacks.append(self.update_font_size)

    def handle_execute(self, e):
        code = self.console_input.value
        if not code.strip():
            return
        self.console_output.value += f"\n>>> Executando código...\n"
        self.update()
        self.on_execute(code)

    def handle_clear(self, e):
        self.console_output.value = ""
        self.update()

    def update_font_size(self):
        sz = self.state.current_font_size
        self.console_input.text_size = sz
        self.console_output.size = max(10, sz - 1)
        self.update()

    def update_strings(self):
        cm = self.state.content_manager
        self.btn_execute.content = cm.get_ui_string("btn_run")
        self.btn_clear.content = cm.get_ui_string("btn_clear")
        self.console_input.hint_text = cm.get_ui_string("lbl_type_code")
        if hasattr(self, 'lbl_console_title'):
            self.lbl_console_title.value = cm.get_ui_string("console_title", "Console Python")
        self.btn_ask_ai_err.content = cm.get_ui_string("lbl_ask_ai_err")
        
        # Update default smart messages panel text
        if hasattr(self, 'smart_messages_panel') and isinstance(self.smart_messages_panel.content, ft.Column):
            if len(self.smart_messages_panel.content.controls) >= 2:
                self.smart_messages_panel.content.controls[0].value = cm.get_ui_string("msg_all_good_title", "Tudo certo por enquanto!")
                self.smart_messages_panel.content.controls[1].value = cm.get_ui_string("msg_all_good_desc", "Continue o bom trabalho.")
                
        self.update()
