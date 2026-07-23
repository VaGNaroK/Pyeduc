"""
Camada de Interface Gráfica (GUI) usando Flet
"""
# pyrefly: ignore [missing-import]
import flet as ft
from content_manager import ContentManager
from progress_manager import ProgressManager
from communication import ConsoleController
import config
import re
import threading
from logger import logger
from llm_client import OllamaClient
from tutor_guardrails import EducationalGuardrails
from rag_module import LessonRAG


def main_app(page: ft.Page):
    # Configurações da página
    page.title = "Pyeduc - App Educacional Python"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#e2e8f0"
    
    # Propriedades da Janela (Evita bug de minimizar no Linux/Wayland)
    page.window.min_width = 800
    page.window.min_height = 600

    # Handler para descarregar o modelo de IA da VRAM ao fechar o aplicativo
    def on_window_event(e):
        if e.data == "close":
            try:
                ollama_client.unload_model()
            except Exception:
                pass
    page.window.on_event = on_window_event
    page.on_disconnect = lambda e: ollama_client.unload_model()

    
    # Gerenciadores
    content_manager = ContentManager("content/lessons.json")
    progress_manager = ProgressManager("data")
    console_controller = ConsoleController()
    
    all_lessons = content_manager.get_all_lessons()
    current_lesson_idx = 0
    admin_mode_enabled = config.ADMIN_MODE
    
    # ---------------------------------------------------------
    # Componentes da IA Ollama (Tutor Sócratico)
    # ---------------------------------------------------------
    ollama_client = OllamaClient()
    lesson_rag = LessonRAG(all_lessons)
    ai_chat_history = []
    is_ai_generating = False

    ai_status_icon = ft.Icon(ft.Icons.CIRCLE, color="#94a3b8", size=10)
    ai_status_text = ft.Text("Ollama: verificando...", color="#94a3b8", size=11)
    ai_chat_list = ft.ListView(height=260, spacing=10, auto_scroll=True, padding=5)
    ai_loading_ring = ft.ProgressRing(width=18, height=18, stroke_width=2, visible=False)


    def update_ollama_status():
        def _check():
            online, msg = ollama_client.check_health()
            ai_status_text.value = msg
            if online:
                ai_status_icon.color = "#10b981"
                ai_status_text.color = "#10b981"
            else:
                ai_status_icon.color = "#ef4444"
                ai_status_text.color = "#ef4444"
            page.update()
        page.run_thread(_check)



    def add_chat_message(role: str, text: str):
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
        ai_chat_list.controls.append(ft.Row([msg_box], alignment=align))
        try:
            ai_chat_list.update()
        except Exception:
            pass
        page.update()



    def send_to_ai(user_prompt="", quick_action=None):
        nonlocal is_ai_generating
        if is_ai_generating:
            return

        text = user_prompt.strip() or ai_input_field.value.strip()
        if not text and not quick_action:
            return

        ai_input_field.value = ""
        is_ai_generating = True
        ai_loading_ring.visible = True
        btn_send_ai.disabled = True
        try:
            ai_loading_ring.update()
            btn_send_ai.update()
            ai_input_field.update()
        except Exception:
            pass
        page.update()

        display_text = text
        if not display_text and quick_action:
            if quick_action == "hint_no_spoiler": display_text = "Quero uma dica sem spoiler sobre este exercício."
            elif quick_action == "error_help": display_text = "Por que meu código gerou erro no console?"
            elif quick_action == "explain_concept": display_text = "Explique o conceito principal desta lição."

        add_chat_message("user", display_text)

        def _worker():
            nonlocal is_ai_generating
            try:
                lesson = all_lessons[current_lesson_idx] if current_lesson_idx < len(all_lessons) else {}
                title = lesson.get("title", "Python")
                concepts = lesson.get("ai_context", {}).get("key_concepts", [title])
                
                rag_ctx = lesson_rag.get_relevant_context(
                    user_query=text or display_text,
                    current_lesson_id=lesson.get("id")
                )

                payload = EducationalGuardrails.prepare_chat_payload(
                    history=ai_chat_history,
                    user_query=text,
                    lesson_title=title,
                    key_concepts=concepts,
                    rag_context=rag_ctx,
                    student_code=console_input.value,
                    console_output=console_output.value,
                    quick_action=quick_action
                )

                raw_reply = ollama_client.chat(payload)
                reply = EducationalGuardrails.sanitize_response(raw_reply, console_input.value)
                ai_chat_history.append({"role": "user", "content": display_text})
                ai_chat_history.append({"role": "assistant", "content": reply})

                add_chat_message("assistant", reply)

            except Exception as ex:
                add_chat_message("assistant", f"⚠️ Ocorreu um erro ao comunicar com a IA: {str(ex)}")
            finally:
                is_ai_generating = False
                ai_loading_ring.visible = False
                btn_send_ai.disabled = False
                try:
                    ai_loading_ring.update()
                    btn_send_ai.update()
                except Exception:
                    pass
                page.update()

        page.run_thread(_worker)



    ai_input_field = ft.TextField(
        hint_text="Pergunte algo ao Tutor...",
        expand=True,
        border_radius=8,
        border_color="#cbd5e1",
        content_padding=10,
        text_size=13,
        on_submit=lambda e: send_to_ai()
    )
    btn_send_ai = ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color="#7c3aed", on_click=lambda e: send_to_ai())

    ai_drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.SMART_TOY_ROUNDED, color="#7c3aed", size=24),
                            ft.Text("Tutor IA Sócratico", weight="bold", size=16, color="#1e1b4b"),
                        ]),
                        ft.Row([ai_status_icon, ai_status_text])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=1, color="#e2e8f0"),
                    ft.Text("Ajuda Rápida:", size=12, weight="bold", color="#64748b"),
                    ft.Row([
                        ft.OutlinedButton("💡 Dica", on_click=lambda e: send_to_ai(quick_action="hint_no_spoiler"), style=ft.ButtonStyle(padding=4)),
                        ft.OutlinedButton("❌ Erro", on_click=lambda e: send_to_ai(quick_action="error_help"), style=ft.ButtonStyle(padding=4)),
                        ft.OutlinedButton("📘 Conceito", on_click=lambda e: send_to_ai(quick_action="explain_concept"), style=ft.ButtonStyle(padding=4)),
                    ], spacing=5, wrap=True),
                    ft.Divider(height=1, color="#e2e8f0"),
                    ai_chat_list,
                    ft.Row([ai_input_field, ai_loading_ring, btn_send_ai], spacing=5)
                ], expand=True, spacing=10),
                padding=15,
                expand=True
            )
        ]
    )
    page.end_drawer = ai_drawer

    def open_ai_drawer(e=None):
        update_ollama_status()
        ai_drawer.open = True
        page.update()

    # ---------------------------------------------------------
    # Componentes da Top Bar
    # ---------------------------------------------------------
    title_text = ft.Text("Aula 1: Introdução às Variáveis", color="white", weight="bold", size=16)
    top_bar = ft.Container(visible=False,
        content=ft.Row([title_text], alignment=ft.MainAxisAlignment.START),
        bgcolor="#1e293b",
        padding=12,
        alignment=ft.Alignment.CENTER_LEFT
    )

    
    
    # ---------------------------------------------------------
    # Modal de Zoom de Imagem
    # ---------------------------------------------------------
    zoom_image = ft.Image(src="", fit=ft.BoxFit.CONTAIN)
    zoom_viewer = ft.InteractiveViewer(
        content=zoom_image,
        min_scale=0.5,
        max_scale=5.0,
        boundary_margin=ft.Margin.all(20),
        expand=True
    )
    
    def close_zoom_modal(e):
        page.pop_dialog()
        
    zoom_modal = ft.AlertDialog(
        content=ft.Container(zoom_viewer, width=800, height=600, bgcolor="black"),
        content_padding=0,
        actions=[ft.TextButton("Fechar", on_click=close_zoom_modal)],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def handle_markdown_link(e):
        # Se for um link de imagem (png, jpg), abre no modal
        url = e.data
        if url.endswith(".png") or url.endswith(".jpg"):
            zoom_image.src = url
            page.show_dialog(zoom_modal)
            page.update()
        else:
            page.launch_url(url)

    # ---------------------------------------------------------
    # Painel Esquerdo: Conteúdo da Lição
    # ---------------------------------------------------------
    lesson_content_md = ft.Markdown(
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
        on_tap_link=handle_markdown_link
    )
    
    exercise_content_md = ft.Markdown(
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
        on_tap_link=handle_markdown_link
    )
    exercises_col = ft.Column(spacing=10)
    active_exercises_rows = []

    
    # ---------------------------------------------------------
    # Painel Esquerdo: Console Python (Input e Output)
    # ---------------------------------------------------------
    console_input = ft.TextField(
        multiline=True,
        min_lines=4,
        max_lines=7,
        text_style=ft.TextStyle(font_family="Consolas", size=14, color="#f8fafc"),
        bgcolor="#1e293b",
        border_color="#38bdf8", # Borda Azul Ciano Brilhante de Alto Contraste
        border_radius=6,
        content_padding=12,
        hint_text="# Digite seu código Python aqui...",
        hint_style=ft.TextStyle(color="#94a3b8")
    )
    
    console_output = ft.TextField(
        multiline=True,
        read_only=True,
        min_lines=5,
        text_style=ft.TextStyle(font_family="Consolas", size=13, color="#10b981"),
        bgcolor="#090d16",
        border=ft.InputBorder.NONE,
        content_padding=12,
        expand=True
    )
    
    console_output_container = ft.Container(
        content=console_output,
        bgcolor="#090d16",
        border=ft.Border.all(1.5, "#10b981"), # Borda Verde Esmeralda Brilhante de Alto Contraste
        border_radius=6,
        padding=2,
        expand=True
    )
    
    def on_execute_click(e):
        code = console_input.value
        if not code.strip():
            return
        console_output.value += f"\n>>> Executando código...\n"
        page.update()
        console_controller.execute_code(code)
        
    btn_execute = ft.ElevatedButton(
        content="Executar Código",
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        color="white",
        bgcolor="#4ade80",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=4)),
        on_click=on_execute_click
    )
    
    def on_clear_console(e):
        console_output.value = ""
        page.update()
        
    btn_clear = ft.TextButton(
        content="Limpar",
        icon=ft.Icons.DELETE_OUTLINE,
        icon_color="#cbd5e1",
        style=ft.ButtonStyle(color="#cbd5e1"),
        on_click=on_clear_console
    )
    
    btn_ask_ai_err = ft.ElevatedButton(
        "🤖 Pedir ajuda da IA para este erro",
        icon=ft.Icons.AUTO_AWESOME,
        bgcolor="#7c3aed",
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=12),
        on_click=lambda e: send_to_ai(quick_action="error_help"),
        visible=False
    )

    # Painel de mensagens inteligentes do console
    smart_messages_panel = ft.Container(
        content=ft.Column([
            ft.Text("Tudo certo por enquanto!", weight="bold", size=14, color="white"),
            ft.Text("Continue o bom trabalho.", color="#94a3b8", size=13, italic=True)
        ], spacing=6),
        bgcolor="#1e293b",
        border_radius=6,
        padding=15
    )

    smart_messages_column = ft.Column([
        smart_messages_panel,
        btn_ask_ai_err
    ], spacing=10, expand=3, alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    console_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Console Python", color="white", weight="bold", size=14),
                ft.Row([btn_execute, btn_clear])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Row([
                ft.Container(content=console_input, expand=7), # 70% do espaço para o editor
                smart_messages_column
            ]),
            
            console_output_container
        ], spacing=10),
        bgcolor="#0f172a", # Fundo Azul Slate Escuro Elegante
        padding=15,
        expand=50
    )
    
    def on_copy_example(e):
        console_input.value = example_text.value
        page.update()
        
    btn_copy_example = ft.ElevatedButton(
        content="Copiar Exemplo",
        icon=ft.Icons.CONTENT_COPY,
        on_click=on_copy_example
    )
    
    example_text = ft.TextField(
        multiline=True,
        read_only=True,
        text_style=ft.TextStyle(font_family="Consolas", size=13),
        bgcolor="#f8fafc",
        border_color="#e2e8f0"
    )

    coding_elements = ft.Column([
        ft.Divider(color="#e2e8f0"),
        ft.Text("Exemplo:", weight="bold", size=14, color="#334155"),
        example_text,
        btn_copy_example,
        ft.Divider(color="#e2e8f0"),
        ft.Text("Exercício(s):", weight="bold", size=14, color="#334155"),
        exercise_content_md,
        exercises_col
    ])
    
    coding_elements_container = ft.Container(content=coding_elements)

    lesson_container = ft.Container(
        content=ft.Column([
            lesson_content_md,
            coding_elements_container
        ], scroll=ft.ScrollMode.ALWAYS, spacing=10),
        bgcolor="white",
        padding=20,
        expand=50
    )
    
    # ---------------------------------------------------------
    # Painel Esquerdo: Atividade Teórica (Quiz Central)
    # ---------------------------------------------------------
    theory_question = ft.Text("", size=18, weight="bold", color="#1e293b", text_align=ft.TextAlign.CENTER)
    theory_options_col = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    theory_feedback = ft.Text("", size=16, weight="bold", text_align=ft.TextAlign.CENTER)
    
    activity_container = ft.Container(
        content=ft.Column([
            ft.Text("Atividade de Fixação", size=14, color="#64748b", weight="bold"),
            theory_question,
            ft.Container(height=5),
            theory_feedback,
            ft.Container(height=10),
            theory_options_col
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10, scroll=ft.ScrollMode.AUTO),
        bgcolor="#f8fafc",
        padding=30,
        expand=50,
        visible=False
    )
    
    # ---------------------------------------------------------
    # Painel Esquerdo: Bem-Vindo     # ---------------------------------------------------------
    def on_login_click(e):
        username = tf_username.value.strip()
        password = tf_password.value.strip()
        if not username or not password:
            snack = ft.SnackBar(ft.Text("Preencha todos os campos!"))
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return
            
        if progress_manager.login(username, password):
            # Login sucesso

            sidebar.visible = True
            footer.visible = True
            top_bar.visible = True
            lesson_container.visible = True
            welcome_container.visible = False
            
            # Controle de modo administrador
            is_admin = (username == "admin" and password == "admin")
            admin_switch_container.visible = is_admin
            if not is_admin:
                nonlocal admin_mode_enabled
                admin_mode_enabled = False
                admin_switch.value = False

            current = progress_manager.get_current_lesson()
            update_progress_ui()
            load_lesson(current)
            snack = ft.SnackBar(ft.Text(f"Bem-vindo de volta, {username}!", color="white"), bgcolor="#10b981")
            page.overlay.append(snack)
            snack.open = True
            page.update()
        else:
            snack = ft.SnackBar(ft.Text("Usuário ou senha incorretos!"), bgcolor="#dc2626")
            page.overlay.append(snack)
            snack.open = True
            page.update()

    def on_register_click(e):
        username = tf_username.value.strip()
        password = tf_password.value.strip()
        if not username or not password:
            snack = ft.SnackBar(ft.Text("Preencha todos os campos!"))
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return
            
        if progress_manager.register(username, password):
            snack = ft.SnackBar(ft.Text(f"Usuário {username} cadastrado com sucesso! Faça Login."), bgcolor="#10b981")
            page.overlay.append(snack)
            snack.open = True
            page.update()
            tf_password.value = ""
            page.update()
        else:
            snack = ft.SnackBar(ft.Text("Usuário já existe!"), bgcolor="#dc2626")
            page.overlay.append(snack)
            snack.open = True
            page.update()

    tf_username = ft.TextField(label="Nome de Usuário", width=300, bgcolor="white", color="black", border_color="#cbd5e1")
    tf_password = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300, bgcolor="white", color="black", border_color="#cbd5e1")
    
    btn_login = ft.ElevatedButton("Entrar", bgcolor="#3b82f6", color="white", on_click=on_login_click, width=140)
    btn_register = ft.ElevatedButton("Cadastrar", bgcolor="#10b981", color="white", on_click=on_register_click, width=140)

    welcome_container = ft.Container(
        content=ft.Column([
            ft.Image(src="content/images/PyeducLOGO.png", width=250),
            ft.Text("Pyeduc", size=32, weight="bold", color="#1e293b"),
            ft.Text("Faça login para continuar de onde parou.", size=14, color="#64748b"),
            ft.Container(height=20),
            tf_username,
            tf_password,
            ft.Row([btn_login, btn_register], alignment=ft.MainAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#f8fafc",
        padding=40,
        expand=50,
        visible=False
    )
    
    def on_pan_update_splitter(e: ft.DragUpdateEvent):
        # Ajusta o expand baseado no arrasto do mouse
        # Multiplicador pequeno para suavizar o movimento
        change = int((e.local_delta.y if e.local_delta else 0) * 0.5)
        
        # Limita a expansão entre 10 e 90 para não esmagar os painéis
        new_lesson_expand = max(10, min(90, lesson_container.expand + change))
        
        lesson_container.expand = new_lesson_expand
        console_container.expand = 100 - new_lesson_expand
        activity_container.expand = 100 - new_lesson_expand
        welcome_container.expand = 100 - new_lesson_expand
        page.update()

    drag_splitter = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.RESIZE_UP_DOWN,
        drag_interval=10,
        on_pan_update=on_pan_update_splitter,
        content=ft.Container(
            height=6,
            bgcolor="#cbd5e1", # Cinza claro
            border_radius=3,
            margin=ft.Margin.symmetric(vertical=4, horizontal=10)
        )
    )
    
    left_panel = ft.Column([
        lesson_container,
        drag_splitter,
        console_container,
        activity_container,
        welcome_container
    ], expand=7, spacing=0, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    def on_pan_update_sidebar_splitter(e):
        change = 1 if (e.local_delta and e.local_delta.x < 0) else (-1 if (e.local_delta and e.local_delta.x > 0) else 0)
        new_sidebar_expand = max(2, min(6, sidebar.expand + change))
        sidebar.expand = new_sidebar_expand
        left_panel.expand = 10 - new_sidebar_expand
        page.update()

    sidebar_splitter = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
        drag_interval=10,
        on_pan_update=on_pan_update_sidebar_splitter,
        content=ft.Container(
            width=6,
            bgcolor="#cbd5e1",
            border_radius=3,
            margin=ft.Margin.symmetric(vertical=10, horizontal=2)
        )
    )

    
    # ---------------------------------------------------------
    # Callbacks do Console Controller
    # ---------------------------------------------------------
    def on_exec_start():
        btn_execute.disabled = True
        page.update()
        
    def on_exec_finish(stdout, stderr, ret):
        btn_execute.disabled = False
        out = ""
        
        smart_messages_panel.content = ft.Column([
            ft.Text("Tudo certo por enquanto!", weight="bold", size=14, color="white"),
            ft.Text("Continue o bom trabalho.", color="#94a3b8", size=13, italic=True)
        ], spacing=6)
        smart_messages_panel.bgcolor = "#1e293b"
        btn_ask_ai_err.visible = False
        
        if stdout:
            out += stdout + "\n"
        if stderr:
            out += "ERRO:\n" + stderr + "\n"
            btn_ask_ai_err.visible = True

            # Tradutor de Erros com texto ampliado e separado do botão
            if "SyntaxError" in stderr:
                smart_messages_panel.content = ft.Column([
                    ft.Text("Erro de Sintaxe (SyntaxError):", weight="bold", size=14, color="white"),
                    ft.Text("Parece que há um erro na escrita do código. Verifique aspas, parênteses ou digitação.", size=13, color="white")
                ], spacing=6)
                smart_messages_panel.bgcolor = "#991b1b"
            elif "NameError" in stderr:
                smart_messages_panel.content = ft.Column([
                    ft.Text("Erro de Nome (NameError):", weight="bold", size=14, color="white"),
                    ft.Text("Você tentou usar uma variável ou função inexistente.", size=13, color="white")
                ], spacing=6)
                smart_messages_panel.bgcolor = "#991b1b"
            elif "IndentationError" in stderr:
                smart_messages_panel.content = ft.Column([
                    ft.Text("Erro de Indentação (IndentationError):", weight="bold", size=14, color="white"),
                    ft.Text("Verifique os espaços no começo das linhas.", size=13, color="white")
                ], spacing=6)
                smart_messages_panel.bgcolor = "#991b1b"
            elif "TypeError" in stderr:
                smart_messages_panel.content = ft.Column([
                    ft.Text("Erro de Tipo (TypeError):", weight="bold", size=14, color="white"),
                    ft.Text("Você tentou misturar tipos incompatíveis.", size=13, color="white")
                ], spacing=6)
                smart_messages_panel.bgcolor = "#991b1b"
            else:
                smart_messages_panel.content = ft.Column([
                    ft.Text("Erro de Execução:", weight="bold", size=14, color="white"),
                    ft.Text("Verifique o erro retornado no console.", size=13, color="white")
                ], spacing=6)
                smart_messages_panel.bgcolor = "#991b1b"

        
        console_output.value += out
        
        # Auto-Grader Check
        if stdout:
            # Divide o output em linhas limpas
            output_lines = [line.strip() for line in stdout.split('\n') if line.strip()]
            
            # Helper para fuzzy matching (remove pontuação no final e espaços extras e ignora case)
            def fuzzy_clean(text):
                return re.sub(r'[\.,;:\!\?]+$', '', text.strip()).strip().lower()
            
            fuzzy_output_lines = [fuzzy_clean(line) for line in output_lines]
            
            from collections import Counter
            output_counts = Counter(output_lines)
            fuzzy_output_counts = Counter(fuzzy_output_lines)
            newly_marked_counts = {}
            newly_marked_fuzzy_counts = {}
            
            almost_correct = False
            
            for row in active_exercises_rows:
                expected = str(row.data).strip()
                if not expected:
                    continue
                
                icon = row.controls[0]
                if icon.icon == ft.Icons.CHECK_CIRCLE:
                    continue # Já completado
                
                expected_lines = [line.strip() for line in expected.split('\n') if line.strip()]
                fuzzy_expected_lines = [fuzzy_clean(line) for line in expected_lines]
                n = len(expected_lines)
                
                is_match = False
                if n == 1:
                    exp = expected_lines[0]
                    f_exp = fuzzy_expected_lines[0]
                    
                    used = newly_marked_counts.get(exp, 0)
                    f_used = newly_marked_fuzzy_counts.get(f_exp, 0)
                    
                    # Exact Match
                    if output_counts.get(exp, 0) > used:
                        is_match = True
                        newly_marked_counts[exp] = used + 1
                    # Fuzzy Match
                    elif fuzzy_output_counts.get(f_exp, 0) > f_used:
                        almost_correct = True
                        newly_marked_fuzzy_counts[f_exp] = f_used + 1
                        logger.info(f"Auto-grader (Quase): Esperava '{exp}', Aluno digitou algo fuzzy match")
                elif n > 1:
                    # Verifica match sequencial (Exato)
                    for i in range(len(output_lines) - n + 1):
                        if output_lines[i:i+n] == expected_lines:
                            is_match = True
                            break
                    if not is_match:
                        # Verifica match sequencial (Fuzzy)
                        for i in range(len(fuzzy_output_lines) - n + 1):
                            if fuzzy_output_lines[i:i+n] == fuzzy_expected_lines:
                                almost_correct = True
                                logger.info(f"Auto-grader (Quase multiline)")
                                break
                
                if is_match:
                    icon.icon = ft.Icons.CHECK_CIRCLE
                    icon.color = "#10b981"
            
            if almost_correct and not is_match:
                smart_messages_panel.content = ft.Text("💡 Quase lá!\n\nSeu código imprimiu quase o valor esperado. Verifique se você não colocou um ponto final, espaço a mais, ou errou uma letra maiúscula/minúscula na saída.", color="white", size=13)
                smart_messages_panel.bgcolor = "#b45309" # Laranja escuro
        
        # Faz scroll para o final
        page.update()
        
    console_controller.on_execution_start = on_exec_start
    console_controller.on_execution_finish = on_exec_finish
    
    # ---------------------------------------------------------
    # Painel Direito: Sidebar
    # ---------------------------------------------------------
    tips_col = ft.Column(spacing=5)
    refs_col = ft.Column(spacing=5)
    prog_col = ft.Column(spacing=5, height=250, scroll=ft.ScrollMode.AUTO)
    
    quiz_question = ft.Text(weight="bold", color="#334155")
    quiz_options = ft.RadioGroup(content=ft.Column([]))
    quiz_feedback = ft.Text(size=12, weight="bold")
    
    def on_quiz_submit(e):
        lesson = all_lessons[current_lesson_idx]
        ans = quiz_options.value
        if ans == str(lesson["quiz"]["answer"]):
            quiz_feedback.value = "Correto! Muito bem!"
            quiz_feedback.color = "#059669" # Verde escuro
            progress_manager.mark_lesson_completed(lesson["id"])
            update_progress_ui()
        else:
            quiz_feedback.value = "Incorreto. Tente novamente."
            quiz_feedback.color = "#dc2626" # Vermelho
        page.update()
        
    btn_quiz = ft.ElevatedButton(
        "Responder", 
        on_click=on_quiz_submit,
        color="white",
        bgcolor="#8b5cf6", # Roxo
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=4))
    )
    
    # Modal Popup do Quiz da Lição
    def close_quiz_modal(e=None):
        page.pop_dialog()

    btn_close_quiz_modal = ft.TextButton("Fechar", on_click=close_quiz_modal)
    quiz_modal_container = ft.Container(
        content=ft.Column([
            quiz_question,
            quiz_options,
            btn_quiz,
            quiz_feedback
        ], spacing=10, tight=True),
        width=450,
        padding=10
    )
    quiz_modal = ft.AlertDialog(
        title=ft.Row([
            ft.Icon(ft.Icons.QUIZ_ROUNDED, color="#7c3aed", size=22),
            ft.Text("Mini Quiz de Fixação", weight="bold", size=16, color="#1e293b")
        ], spacing=8),
        content=quiz_modal_container,
        actions=[btn_close_quiz_modal],
        actions_alignment=ft.MainAxisAlignment.END
    )

    def open_quiz_modal(e=None):
        page.show_dialog(quiz_modal)
        page.update()

    btn_open_quiz_modal = ft.ElevatedButton(
        "🎯 Responder Quiz da Lição",
        icon=ft.Icons.QUIZ_ROUNDED,
        bgcolor="#7c3aed",
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), padding=10),
        on_click=open_quiz_modal,
        visible=False
    )

    # Painel Embutido do Tutor IA na Barra Lateral (Posicionado no Topo)
    sidebar_ai_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("🤖 Tutor IA Sócratico", weight="bold", color="#581c87", size=14),
                ai_loading_ring
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                ft.OutlinedButton("💡 Dica", on_click=lambda e: send_to_ai(quick_action="hint_no_spoiler"), style=ft.ButtonStyle(padding=4)),
                ft.OutlinedButton("❌ Erro", on_click=lambda e: send_to_ai(quick_action="error_help"), style=ft.ButtonStyle(padding=4)),
                ft.OutlinedButton("📘 Conceito", on_click=lambda e: send_to_ai(quick_action="explain_concept"), style=ft.ButtonStyle(padding=4)),
            ], spacing=4, wrap=True),
            ft.Divider(height=1, color="#ddd6fe"),
            ai_chat_list,
            ft.Row([
                ai_input_field,
                btn_send_ai
            ], spacing=5),
            ft.Divider(height=1, color="#ddd6fe"),
            btn_open_quiz_modal
        ], spacing=8),
        bgcolor="#faf5ff",
        padding=12,
        border_radius=8,
        border=ft.Border.all(1, "#c084fc")
    )
    
    sidebar_content = ft.Column([
        sidebar_ai_container,
        # Dicas Rápidas
        ft.Container(
            content=ft.Column([
                ft.Text("Dicas Rápidas:", weight="bold", color="#92400e"),
                tips_col
            ]),
            bgcolor="#fef3c7", # Amarelo pastel
            padding=15,
            border_radius=8,
            border=ft.Border.all(1, "#fde68a")
        ),
        # Progresso
        ft.Container(
            content=ft.Column([
                ft.Text("Progresso:", weight="bold", color="#065f46"),
                prog_col
            ]),
            bgcolor="#ecfdf5", # Verde pastel
            padding=15,
            border_radius=8,
            border=ft.Border.all(1, "#a7f3d0")
        )
    ], scroll=ft.ScrollMode.AUTO, spacing=15)
    
    def toggle_admin_mode(e):
        nonlocal admin_mode_enabled
        admin_mode_enabled = e.control.value
        update_progress_ui()
        page.update()

    admin_switch = ft.Switch(label="Admin Mode", value=config.ADMIN_MODE, on_change=toggle_admin_mode, active_color="#ef4444")
    admin_switch_container = ft.Container(
        content=admin_switch,
        bgcolor="#fee2e2",
        padding=10,
        border_radius=8,
        border=ft.Border.all(1, "#fca5a5"),
        visible=False
    )
    sidebar_content.controls.insert(0, admin_switch_container)

    # Badge de Status do Ollama no Topo da Sidebar
    btn_refresh_ollama = ft.IconButton(
        icon=ft.Icons.REFRESH_ROUNDED,
        icon_size=16,
        tooltip="Verificar Ollama",
        on_click=lambda e: update_ollama_status()
    )
    ollama_status_container = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.SMART_TOY_ROUNDED, color="#7c3aed", size=18),
                ai_status_icon,
                ai_status_text
            ], spacing=6),
            btn_refresh_ollama
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor="#f3e8ff",
        padding=8,
        border_radius=8,
        border=ft.Border.all(1, "#ddd6fe")
    )
    sidebar_content.controls.insert(0, ollama_status_container)
    update_ollama_status()

    
    sidebar = ft.Container(visible=False,
        content=sidebar_content,
        bgcolor="#f8fafc",
        padding=15,
        expand=3,
        border=ft.Border.only(left=ft.BorderSide(1, "#cbd5e1"))
    )
    
    def update_progress_ui():
        prog_col.controls.clear()
        for i, les in enumerate(all_lessons):
            is_done = progress_manager.is_lesson_completed(les["id"])
            icon = ft.Icons.CHECK_CIRCLE if is_done else ft.Icons.RADIO_BUTTON_UNCHECKED
            color = "#10b981" if is_done else "#94a3b8"
            
            def make_on_click(idx):
                def on_click(e):
                    load_lesson(idx)
                    page.update()
                return on_click
            
            row = ft.Row([
                ft.Icon(icon, color=color, size=16),
                ft.Text(les["title"], size=12, color="#334155" if is_done else "#64748b")
            ])
            
            if is_done or admin_mode_enabled:
                item = ft.Container(
                    content=row,
                    on_click=make_on_click(i),
                    tooltip="Clique para acessar esta aula",
                    ink=True,
                    border_radius=4,
                    padding=2
                )
            else:
                item = ft.Container(content=row, padding=2)
                
            prog_col.controls.append(item)
    
    # ---------------------------------------------------------
    # Lógica de Carregamento de Lição
    # ---------------------------------------------------------
    def load_lesson(index):
        nonlocal current_lesson_idx
        current_lesson_idx = index
        progress_manager.set_current_lesson(index)
        lesson = all_lessons[index]
        title_text.value = lesson["title"]
        
        # Reconstrói a área de conteúdo da aula
        active_exercises_rows.clear()
        lesson_container.content.controls.clear()
        
        sections = lesson.get("sections")
        if not sections:
            # Fallback para aulas no formato antigo
            sections = []
            sec = {}
            if lesson.get("content"): sec["content"] = lesson["content"]
            if lesson.get("example"): sec["example"] = lesson["example"]
            if lesson.get("exercise"): sec["exercise"] = lesson["exercise"]
            if lesson.get("exercises"): sec["exercises"] = lesson["exercises"]
            sections.append(sec)
            
        for sec in sections:
            if "content" in sec:
                lesson_container.content.controls.append(
                    ft.Markdown(sec["content"], selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED)
                )
                
                # Injeta a imagem da lição 8 logo abaixo da teoria
                if lesson.get("id") == 8:
                    lesson_container.content.controls.append(
                        ft.Container(
                            content=ft.Image(src="content/images/variavel_exemple.png", width=1200),
                            alignment=ft.Alignment.CENTER,
                            margin=ft.Margin(top=20, bottom=20, left=0, right=0)
                        )
                    )
                elif lesson.get("id") == 11:
                    lesson_container.content.controls.append(
                        ft.Container(
                            content=ft.Image(src="content/images/boolean.png", width=1200),
                            alignment=ft.Alignment.CENTER,
                            margin=ft.Margin(top=20, bottom=20, left=0, right=0)
                        )
                    )
                elif lesson.get("id") == 12:
                    lesson_container.content.controls.append(
                        ft.Container(
                            content=ft.Image(src="content/images/aritmetics.png", width=1200),
                            alignment=ft.Alignment.CENTER,
                            margin=ft.Margin(top=20, bottom=20, left=0, right=0)
                        )
                    )
                elif lesson.get("id") == 13:
                    lesson_container.content.controls.append(
                        ft.Container(
                            content=ft.Image(src="content/images/list.png", width=1200),
                            alignment=ft.Alignment.CENTER,
                            margin=ft.Margin(top=20, bottom=20, left=0, right=0)
                        )
                    )
            
            coding_controls = []
            if sec.get("example"):
                ex_text = ft.TextField(
                    value=sec["example"],
                    multiline=True, read_only=True,
                    text_style=ft.TextStyle(font_family="Consolas", size=13),
                    bgcolor="#f8fafc", border_color="#e2e8f0"
                )
                def make_copy_handler(text_val):
                    def handler(e):
                        console_input.value = text_val
                        page.update()
                    return handler
                btn_copy = ft.ElevatedButton(
                    content="Copiar Exemplo",
                    icon=ft.Icons.CONTENT_COPY,
                    on_click=make_copy_handler(sec["example"])
                )
                coding_controls.extend([
                    ft.Divider(color="#e2e8f0"),
                    ft.Text("Exemplo:", weight="bold", size=14, color="#334155"),
                    ex_text, btn_copy
                ])
                
                if lesson.get("id") == 20 and "quadrados = " in sec["example"]:
                    coding_controls.append(
                        ft.Container(
                            content=ft.Image(src="content/images/list2.png", width=1200),
                            alignment=ft.Alignment.CENTER,
                            margin=ft.Margin(top=20, bottom=20, left=0, right=0)
                        )
                    )
                elif lesson.get("id") == 21 and "# Gerando a sequência de Fibonacci" in sec["example"]:
                    coding_controls.append(
                        ft.Container(
                            content=ft.Image(src="content/images/atribuition.png", width=1200),
                            alignment=ft.Alignment.CENTER,
                            margin=ft.Margin(top=20, bottom=20, left=0, right=0)
                        )
                    )
                
            if sec.get("exercises") or sec.get("exercise"):
                coding_controls.extend([
                    ft.Divider(color="#e2e8f0"),
                    ft.Text("Exercício(s):", weight="bold", size=14, color="#334155")
                ])
                if sec.get("exercise"):
                    coding_controls.append(
                        ft.Markdown(sec["exercise"], selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED)
                    )
                if sec.get("exercises"):
                    sec_ex_col = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                    for ex in sec["exercises"]:
                        expected_out = ex.get("expected_output", "")
                        if expected_out:
                            row = ft.Row([
                                ft.Icon(ft.Icons.RADIO_BUTTON_UNCHECKED, color="#94a3b8", size=20),
                                ft.Markdown(ex["description"], selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED, expand=True)
                            ], vertical_alignment=ft.CrossAxisAlignment.START)
                        else:
                            row = ft.Row([
                                ft.Markdown(ex["description"], selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED, expand=True)
                            ], vertical_alignment=ft.CrossAxisAlignment.START)
                        row.data = expected_out
                        sec_ex_col.controls.append(row)
                        active_exercises_rows.append(row)
                    coding_controls.append(sec_ex_col)
                    
            if coding_controls:
                lesson_container.content.controls.append(
                    ft.Container(content=ft.Column(coding_controls))
                )

        # Injeta logo centralizada na tela de boas-vindas
        if lesson.get("id") == 0:
            lesson_container.content.controls.append(
                ft.Container(
                    content=ft.Image(src="content/images/PyeducLOGO.png", width=600),
                    alignment=ft.Alignment.CENTER,
                    margin=ft.Margin(top=30, bottom=20, left=0, right=0)
                )
            )

        console_input.value = "" # Começa vazio para o aluno digitar
        console_output.value = "" # Limpa qualquer output antigo do console
        
        # Limpa o chat do Tutor IA para não manter conversas da aula anterior
        ai_chat_history.clear()
        ai_chat_list.controls.clear()
        ai_input_field.value = ""
        
        # Atualiza rodapé dinâmico com informações do usuário e progresso
        total_lessons = len(all_lessons)
        user_current = index + 1
        pct = int((user_current / total_lessons) * 100)
        username = progress_manager.get_current_username() or "Aluno"
        footer_status_text.value = f"👤 Aluno: {username}  |  Lição {user_current} de {total_lessons} ({pct}% concluído)"

        # Alterna entre Teórica, Prática e Presentation
        is_theory = lesson.get("type") == "theory"
        is_presentation = lesson.get("type") == "presentation"

        console_container.visible = not is_theory and not is_presentation
        activity_container.visible = is_theory
        coding_elements_container.visible = not is_theory and not is_presentation
        sidebar_ai_container.visible = not is_theory and not is_presentation

        # Configuração do splitter e tamanhos
        if is_presentation:
            progress_manager.mark_lesson_completed(lesson["id"])
            update_progress_ui()
            drag_splitter.visible = False
        else:
            drag_splitter.visible = True
            
        # Mantém os valores de expand fixos e deixa o motor do Flet distribuir o espaço baseado na visibilidade (contorna o bug de redraw)
        if is_theory:
            lesson_container.expand = 40
            activity_container.expand = 60
        else:
            lesson_container.expand = 50
            console_container.expand = 50
        
        # Lógica da Aula Teórica
        if is_theory:
            theory_question.value = lesson["quiz"]["question"]
            theory_feedback.value = ""
            theory_options_col.controls.clear()
            
            is_multi = isinstance(lesson["quiz"]["answer"], list)
            selected_indices = set()

            if is_multi:
                def toggle_option(idx):
                    def on_click(e):
                        if idx in selected_indices:
                            selected_indices.remove(idx)
                            e.control.bgcolor = "white"
                            e.control.color = "#334155"
                        else:
                            selected_indices.add(idx)
                            e.control.bgcolor = "#bfdbfe" # Azul claro
                            e.control.color = "#1e3a8a"
                        page.update()
                    return on_click

                def confirm_multi(e):
                    correct_answers = set(lesson["quiz"]["answer"])
                    if selected_indices == correct_answers:
                        theory_feedback.value = "Correto! Excelente!"
                        theory_feedback.color = "#16a34a"
                        progress_manager.mark_lesson_completed(lesson["id"])
                        update_progress_ui()
                        for btn in theory_options_col.controls[:-1]:
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
                        theory_feedback.value = "Incorreto. Verifique suas opções!"
                        theory_feedback.color = "#dc2626"
                    page.update()

                for i, opt in enumerate(lesson["quiz"]["options"]):
                    btn = ft.ElevatedButton(
                        content=opt,
                        data=i,
                        width=400,
                        height=50,
                        bgcolor="white",
                        color="#334155",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=toggle_option(i)
                    )
                    theory_options_col.controls.append(btn)
                
                btn_confirm = ft.ElevatedButton(
                    content="Confirmar Respostas",
                    width=400,
                    height=50,
                    bgcolor="#8b5cf6",
                    color="white",
                    on_click=confirm_multi
                )
                theory_options_col.controls.append(btn_confirm)
                
            else:
                def make_option_click(idx):
                    def on_click(e):
                        is_correct = idx == lesson["quiz"]["answer"]
                        if is_correct:
                            theory_feedback.value = "Correto! Excelente!"
                            theory_feedback.color = "#16a34a"
                            progress_manager.mark_lesson_completed(lesson["id"])
                            update_progress_ui()
                        else:
                            theory_feedback.value = "Incorreto. Tente novamente!"
                            theory_feedback.color = "#dc2626"
                        
                        if is_correct:
                            for i, btn in enumerate(theory_options_col.controls):
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
                        page.update()
                    return on_click
                
                for i, opt in enumerate(lesson["quiz"]["options"]):
                    btn = ft.ElevatedButton(
                        content=opt,
                        width=400,
                        height=50,
                        bgcolor="white",
                        color="#334155",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=make_option_click(i)
                    )
                    theory_options_col.controls.append(btn)
        
        tips_col.controls = [ft.Text(f"• {t}", size=12, color="#451a03") for t in lesson.get("tips", [])]
        update_progress_ui()

        
        quiz = lesson.get("quiz", {})
        if quiz and "question" in quiz:
            quiz_question.value = quiz["question"]
            opts = []
            for i, opt in enumerate(quiz.get("options", [])):
                opts.append(ft.Radio(value=str(i), label=opt, label_position=ft.LabelPosition.RIGHT))
            quiz_options.content = ft.Column(opts, spacing=5)
            quiz_options.value = None
            quiz_feedback.value = ""
            btn_open_quiz_modal.visible = True
        else:
            quiz_question.value = ""
            quiz_options.content = ft.Column()
            quiz_feedback.value = ""
            btn_open_quiz_modal.visible = False
        
        btn_prev.disabled = (index == 0)
        btn_next.disabled = (index == len(all_lessons) - 1)
        
        page.update()
        
    # ---------------------------------------------------------
    # Footer de Navegação
    # ---------------------------------------------------------
    def go_prev(e):
        nonlocal current_lesson_idx
        if current_lesson_idx > 0:
            current_lesson_idx -= 1
            load_lesson(current_lesson_idx)
            
    def go_next(e):
        nonlocal current_lesson_idx
        current_lesson_id = all_lessons[current_lesson_idx]["id"]
        if not progress_manager.is_lesson_completed(current_lesson_id) and not admin_mode_enabled:
            snack = ft.SnackBar(ft.Text("Complete os exercícios desta lição para poder avançar! 🔒"), bgcolor="#f59e0b")
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return
            
        if current_lesson_idx < len(all_lessons) - 1:
            current_lesson_idx += 1
            load_lesson(current_lesson_idx)
            
    btn_prev = ft.ElevatedButton("Anterior", icon=ft.Icons.ARROW_BACK, on_click=go_prev)
    btn_next = ft.ElevatedButton("Próxima", icon=ft.Icons.ARROW_FORWARD, on_click=go_next)
    
    footer_status_text = ft.Text("Bem-vindo ao Pyeduc!", color="#334155", weight="bold", size=13)
    footer = ft.Container(visible=False,
        content=ft.Row([
            footer_status_text,
            ft.Row([btn_prev, btn_next], alignment=ft.MainAxisAlignment.END, expand=True)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor="#e2e8f0",
        padding=10,
        border=ft.Border.only(top=ft.BorderSide(1, "#cbd5e1"))
    )
    
    # ---------------------------------------------------------
    # Montagem da Estrutura
    # ---------------------------------------------------------
    main_row = ft.Row([left_panel, sidebar_splitter, sidebar], expand=True, spacing=0, vertical_alignment=ft.CrossAxisAlignment.STRETCH)
    
    page.add(
        ft.Column([
            top_bar,
            main_row,
            footer
        ], expand=True, spacing=0)
    )
    
    # Inicia carregando a tela de Login (Bem-Vindo)
    def show_welcome():
        sidebar.visible = False
        sidebar_splitter.visible = False
        footer.visible = False
        top_bar.visible = False
        lesson_container.visible = False
        console_container.visible = False
        activity_container.visible = False
        drag_splitter.visible = False
        welcome_container.visible = True
        welcome_container.expand = 100
        page.update()


    show_welcome()
