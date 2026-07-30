import flet as ft
from ui.app_state import AppState
import config

class LessonView(ft.Container):
    def __init__(self, state: AppState, on_copy_example):
        super().__init__()
        self.state = state
        self.on_copy_example = on_copy_example
        
        self.active_exercises_rows = []
        
        # Markdown & Exercises containers
        self.lesson_content_md = ft.Column(spacing=15)
        self.exercise_content_md = ft.Column(spacing=15)
        self.exercises_col = ft.Column(spacing=10)
        self.tips_col = ft.Column(spacing=5)
        
        self.example_text = ft.TextField(
            multiline=True,
            read_only=True,
            text_style=ft.TextStyle(font_family="Consolas", size=13),
            bgcolor="#f8fafc",
            border_color="#e2e8f0"
        )
        
        self.btn_copy_example = ft.ElevatedButton(
            content=self.state.content_manager.get_ui_string("lbl_copy_example", "Copiar Exemplo"),
            icon=ft.Icons.CONTENT_COPY,
            on_click=lambda e: self.on_copy_example(self.example_text.value)
        )
        
        self.coding_elements = ft.Column([
            ft.Divider(color="#e2e8f0"),
            ft.Text(f"{self.state.content_manager.get_ui_string('lbl_example', 'Exemplo')}:", weight="bold", size=14, color="#334155"),
            self.example_text,
            self.btn_copy_example,
            ft.Divider(color="#e2e8f0"),
            ft.Text(f"{self.state.content_manager.get_ui_string('lbl_exercises', 'Exercícios')}:", weight="bold", size=14, color="#334155"),
            self.exercise_content_md,
            self.exercises_col
        ])
        
        self.coding_elements_container = ft.Container(content=self.coding_elements)
        
        # Central Theory Quiz (Activity Container)
        self.theory_question = ft.Text("", size=18, weight="bold", color="#1e293b", text_align=ft.TextAlign.CENTER)
        self.theory_options_col = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.theory_feedback = ft.Text("", size=16, weight="bold", text_align=ft.TextAlign.CENTER)
        
        cm = self.state.content_manager
        self.lbl_activity = ft.Text(cm.get_ui_string("lbl_activity", "Atividade de Fixação"), size=14, color="#64748b", weight="bold")
        
        self.activity_container = ft.Container(
            content=ft.Column([
                self.lbl_activity,
                self.theory_question,
                self.theory_feedback,
                self.theory_options_col
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20, scroll=ft.ScrollMode.AUTO),
            bgcolor="#f8fafc",
            padding=30,
            expand=50,
            visible=False
        )
        
        # Main Layout Structure
        self.content_column = ft.Column([
            self.lesson_content_md,
            self.coding_elements_container
        ], scroll=ft.ScrollMode.ALWAYS, spacing=10)
        
        self.content = self.content_column
        self.bgcolor = "white"
        self.padding = 20
        self.expand = 50000
        
        self.state.on_lesson_changed_callbacks.append(self.render_lesson)
        self.state.on_font_size_changed_callbacks.append(self.render_lesson)

    def get_exercise_statuses(self):
        ex_statuses = []
        for idx, r in enumerate(self.active_exercises_rows, 1):
            is_done = False
            if r.controls and isinstance(r.controls[0], ft.Icon):
                is_done = (r.controls[0].icon == ft.Icons.CHECK_CIRCLE)
            desc = ""
            for ctrl in r.controls:
                if isinstance(ctrl, ft.Markdown):
                    desc = ctrl.value
            expected_val = str(getattr(r, "data", "") or "").strip()
            expected_str = f" (Saída esperada: \"{expected_val}\")" if expected_val else ""
            status_tag = "✅ CONCLUÍDO" if is_done else "⏳ PENDENTE/EM ANDAMENTO"
            ex_statuses.append(f"- Exercício {idx} [{status_tag}]: {desc}{expected_str}")
        return ex_statuses

    def handle_markdown_link(self, e):
        # We will dispatch this to the main app to open the zoom modal
        if hasattr(self.state, "on_zoom_image"):
            self.state.on_zoom_image(e.data)

    def render_lesson(self):
        lesson = self.state.current_lesson
        if not lesson:
            return
            
        self.active_exercises_rows.clear()
        self.content_column.controls.clear()
        
        sz = self.state.current_font_size
        md_style = ft.MarkdownStyleSheet(
            p_text_style=ft.TextStyle(size=sz),
            h1_text_style=ft.TextStyle(size=sz + 6, weight=ft.FontWeight.BOLD),
            h2_text_style=ft.TextStyle(size=sz + 4, weight=ft.FontWeight.BOLD),
            h3_text_style=ft.TextStyle(size=sz + 2, weight=ft.FontWeight.BOLD),
            code_text_style=ft.TextStyle(size=max(10, sz - 1), font_family="Consolas"),
            list_bullet_text_style=ft.TextStyle(size=sz)
        )
        
        sections = lesson.get("sections")
        if not sections:
            sections = []
            sec = {}
            if lesson.get("content"): sec["content"] = lesson["content"]
            if lesson.get("example"): sec["example"] = lesson["example"]
            if lesson.get("exercise"): sec["exercise"] = lesson["exercise"]
            if lesson.get("exercises"): sec["exercises"] = lesson["exercises"]
            sections.append(sec)
            
        for sec in sections:
            if "content" in sec:
                self.content_column.controls.append(
                    ft.Markdown(sec["content"], selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED, md_style_sheet=md_style, on_tap_link=self.handle_markdown_link)
                )
                
                # Hardcoded image injections from gui.py
                if lesson.get("id") == 10:
                    self.content_column.controls.append(ft.Container(content=ft.Image(src="images/variavel_exemple.png", width=1200), alignment=ft.Alignment.CENTER, margin=ft.Margin(top=20, bottom=20, left=0, right=0)))
                elif lesson.get("id") == 13:
                    self.content_column.controls.append(ft.Container(content=ft.Image(src="images/boolean.png", width=1200), alignment=ft.Alignment.CENTER, margin=ft.Margin(top=20, bottom=20, left=0, right=0)))
                elif lesson.get("id") == 14:
                    self.content_column.controls.append(ft.Container(content=ft.Image(src="images/aritmetics.png", width=1200), alignment=ft.Alignment.CENTER, margin=ft.Margin(top=20, bottom=20, left=0, right=0)))
                elif lesson.get("id") == 15:
                    self.content_column.controls.append(ft.Container(content=ft.Image(src="images/list.png", width=1200), alignment=ft.Alignment.CENTER, margin=ft.Margin(top=20, bottom=20, left=0, right=0)))
            
            coding_controls = []
            if sec.get("example"):
                ex_text = ft.TextField(
                    value=sec["example"],
                    multiline=True, read_only=True,
                    text_style=ft.TextStyle(font_family="Consolas", size=max(10, sz - 1)),
                    bgcolor="#f8fafc", border_color="#e2e8f0"
                )
                btn_copy = ft.ElevatedButton(
                    content=self.state.content_manager.get_ui_string("lbl_copy_example", "Copiar Exemplo"),
                    icon=ft.Icons.CONTENT_COPY,
                    on_click=lambda e, t=sec["example"]: self.on_copy_example(t)
                )
                coding_controls.extend([
                    ft.Divider(color="#e2e8f0"),
                    ft.Text(f"{self.state.content_manager.get_ui_string('lbl_example', 'Exemplo')}:", weight="bold", size=max(13, sz), color="#334155"),
                    ex_text, btn_copy
                ])
                
                if lesson.get("id") == 22 and "quadrados = " in sec["example"]:
                    coding_controls.append(ft.Container(content=ft.Image(src="images/list2.png", width=1200), alignment=ft.Alignment.CENTER, margin=ft.Margin(top=20, bottom=20, left=0, right=0)))
                elif lesson.get("id") == 23 and "# Gerando a sequência de Fibonacci" in sec["example"]:
                    coding_controls.append(ft.Container(content=ft.Image(src="images/atribuition.png", width=1200), alignment=ft.Alignment.CENTER, margin=ft.Margin(top=20, bottom=20, left=0, right=0)))
                
            if sec.get("exercises") or sec.get("exercise"):
                coding_controls.extend([
                    ft.Divider(color="#e2e8f0"),
                    ft.Text(f"{self.state.content_manager.get_ui_string('lbl_exercises', 'Exercícios')}:", weight="bold", size=max(13, sz), color="#334155")
                ])
                if sec.get("exercise"):
                    coding_controls.append(
                        ft.Markdown(sec["exercise"], selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED, md_style_sheet=md_style, on_tap_link=self.handle_markdown_link)
                    )
                if sec.get("exercises"):
                    sec_ex_col = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                    for ex in sec["exercises"]:
                        expected_out = ex.get("expected_output", "")
                        
                        lesson_id = lesson.get("id")
                        is_lesson_completed = lesson_id in self.state.progress_manager.get_completed_lessons()
                        is_completed = is_lesson_completed or (len(self.active_exercises_rows) in self.state.completed_exercises_indices)
                        
                        if expected_out:
                            icon_name = ft.Icons.CHECK_CIRCLE if is_completed else ft.Icons.RADIO_BUTTON_UNCHECKED
                            icon_color = "#10b981" if is_completed else "#94a3b8"
                            
                            row = ft.Row([
                                ft.Icon(icon_name, color=icon_color, size=max(16, sz + 2)),
                                ft.Markdown(ex["description"], selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED, md_style_sheet=md_style, on_tap_link=self.handle_markdown_link, expand=True)
                            ], vertical_alignment=ft.CrossAxisAlignment.START)
                        else:
                            row = ft.Row([
                                ft.Icon(ft.Icons.SUBDIRECTORY_ARROW_RIGHT, color="#94a3b8", size=max(16, sz + 2)),
                                ft.Markdown(ex["description"], selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED, md_style_sheet=md_style, on_tap_link=self.handle_markdown_link, expand=True)
                            ], vertical_alignment=ft.CrossAxisAlignment.START)
                        row.data = expected_out
                        sec_ex_col.controls.append(row)
                        self.active_exercises_rows.append(row)
                    coding_controls.append(sec_ex_col)
                    
            if coding_controls:
                self.content_column.controls.append(
                    ft.Container(content=ft.Column(coding_controls))
                )

        if lesson.get("id") == 0:
            self.content_column.controls.append(
                ft.Container(
                    content=ft.Image(src=config.APP_ICON, width=600),
                    alignment=ft.Alignment.CENTER,
                    margin=ft.Margin(top=30, bottom=20, left=0, right=0)
                )
            )

        self.tips_col.controls = [ft.Text(f"• {t}", size=max(12, sz - 2), color="#451a03") for t in lesson.get("tips", [])]
        
        self.render_theory_quiz(lesson, sz)
        self.update()
        try:
            self.activity_container.update()
        except RuntimeError:
            pass

    def render_theory_quiz(self, lesson, sz):
        is_theory = lesson.get("type") == "theory"
        self.activity_container.visible = is_theory
        
        if is_theory:
            self.theory_question.value = lesson["quiz"]["question"]
            self.theory_question.size = max(18, sz + 3)
            self.theory_feedback.value = ""
            self.theory_feedback.size = max(16, sz + 1)
            self.theory_feedback.visible = False
            self.theory_options_col.controls.clear()
            
            is_multi = isinstance(lesson["quiz"]["answer"], list)
            selected_indices = set()

            if is_multi:
                def confirm_multi(e):
                    correct_answers = set(lesson["quiz"]["answer"])
                    if selected_indices == correct_answers:
                        self.theory_feedback.value = "Correto! Excelente!"
                        self.theory_feedback.color = "#16a34a"
                        self.theory_feedback.visible = True
                        self.state.progress_manager.mark_lesson_completed(lesson["id"])
                        self.state.notify_progress_changed()
                        for btn in self.theory_options_col.controls[:-1]:
                            is_correct = btn.data in correct_answers
                            btn.style = ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                bgcolor={
                                    ft.ControlState.DISABLED: "#22c55e" if is_correct else "#f8fafc",
                                    ft.ControlState.DEFAULT: "#22c55e" if is_correct else "#f8fafc"
                                },
                                color={
                                    ft.ControlState.DISABLED: "white" if is_correct else "#94a3b8",
                                    ft.ControlState.DEFAULT: "white" if is_correct else "#94a3b8"
                                }
                            )
                            btn.disabled = True
                        e.control.disabled = True
                    else:
                        self.theory_feedback.value = "Incorreto. Verifique suas opções!"
                        self.theory_feedback.color = "#dc2626"
                        self.theory_feedback.visible = True
                    try:
                        self.activity_container.update()
                    except RuntimeError:
                        pass

                def toggle_option(idx):
                    def on_click(e):
                        if idx in selected_indices:
                            selected_indices.remove(idx)
                            e.control.bgcolor = "white"
                            e.control.color = "#334155"
                        else:
                            selected_indices.add(idx)
                            e.control.bgcolor = "#bfdbfe"
                            e.control.color = "#1e3a8a"
                        try:
                            self.activity_container.update()
                        except RuntimeError:
                            pass
                    return on_click

                for i, opt in enumerate(lesson["quiz"]["options"]):
                    btn = ft.ElevatedButton(
                        content=ft.Text(opt, size=sz),
                        data=i,
                        width=400,
                        height=50,
                        bgcolor="white",
                        color="#334155",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=toggle_option(i)
                    )
                    self.theory_options_col.controls.append(btn)
                
                btn_confirm = ft.ElevatedButton(
                    content=ft.Text(self.state.content_manager.get_ui_string("btn_confirm_answers", "Confirmar Respostas"), size=sz),
                    width=400,
                    height=50,
                    bgcolor="#8b5cf6",
                    color="white",
                    on_click=confirm_multi
                )
                self.theory_options_col.controls.append(btn_confirm)
            else:
                def make_option_click(idx):
                    def on_click(e):
                        is_correct = idx == lesson["quiz"]["answer"]
                        if is_correct:
                            self.theory_feedback.value = "Correto! Excelente!"
                            self.theory_feedback.color = "#16a34a"
                            self.theory_feedback.visible = True
                            self.state.progress_manager.mark_lesson_completed(lesson["id"])
                            self.state.notify_progress_changed()
                        else:
                            self.theory_feedback.value = "Incorreto. Tente novamente!"
                            self.theory_feedback.color = "#dc2626"
                            self.theory_feedback.visible = True
                        
                        if is_correct:
                            for i, btn in enumerate(self.theory_options_col.controls):
                                is_btn_correct = i == lesson["quiz"]["answer"]
                                btn.style = ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    bgcolor={
                                        ft.ControlState.DISABLED: "#22c55e" if is_btn_correct else "#f8fafc",
                                        ft.ControlState.DEFAULT: "#22c55e" if is_btn_correct else "#f8fafc"
                                    },
                                    color={
                                        ft.ControlState.DISABLED: "white" if is_btn_correct else "#94a3b8",
                                        ft.ControlState.DEFAULT: "white" if is_btn_correct else "#94a3b8"
                                    }
                                )
                                btn.disabled = True
                        else:
                            e.control.bgcolor = "#ef4444"
                            e.control.color = "white"
                        try:
                            self.activity_container.update()
                        except RuntimeError:
                            pass
                    return on_click
                
                for i, opt in enumerate(lesson["quiz"]["options"]):
                    btn = ft.ElevatedButton(
                        content=ft.Text(opt, size=sz),
                        width=400,
                        height=50,
                        bgcolor="white",
                        color="#334155",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=make_option_click(i)
                    )
                    self.theory_options_col.controls.append(btn)

    def update_strings(self):
        cm = self.state.content_manager
        self.btn_copy_example.text = cm.get_ui_string("lbl_copy_example")
        if hasattr(self, 'lbl_activity'):
            self.lbl_activity.value = cm.get_ui_string("lbl_activity", "Atividade de Fixação")
        self.update()
