#!/usr/bin/env python3
# ==============================================================================
# Pyeduc - Script Didático de Gerenciamento e Depuração do Banco de Dados SQLite
# Localização: scripts/manage_db.py
# ==============================================================================

import sqlite3
import os
import sys
from pathlib import Path

# Definição de Cores ANSI para Terminal
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
BLUE = "\033[1;34m"
BOLD = "\033[1m"
RESET = "\033[0m"

def prompt_input(msg=""):
    try:
        return input(msg)
    except (EOFError, KeyboardInterrupt):
        print(f"\n{GREEN}Saindo... Até logo!{RESET}\n")
        sys.exit(0)

def get_db_path():
    user_db = Path.home() / ".pyeduc" / "pyeduc.db"
    local_db = Path("data") / "pyeduc.db"
    
    if user_db.exists() and local_db.exists():
        print(f"{CYAN}Encontrados dois bancos de dados:{RESET}")
        print(f"1) {user_db} (Padrão do Usuário)")
        print(f"2) {local_db} (Diretório local do projeto)")
        try:
            choice = input(f"{BOLD}Escolha qual utilizar [1]: {RESET}").strip()
            if choice == "2":
                return local_db
        except (EOFError, KeyboardInterrupt):
            pass
        return user_db
    elif user_db.exists():
        return user_db
    elif local_db.exists():
        return local_db
    else:
        user_db.parent.mkdir(parents=True, exist_ok=True)
        return user_db

DB_PATH = get_db_path()

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER,
            lesson_id INTEGER,
            completed BOOLEAN DEFAULT 0,
            completed_activities TEXT DEFAULT '[]',
            PRIMARY KEY (user_id, lesson_id),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_state (
            user_id INTEGER PRIMARY KEY,
            current_lesson INTEGER DEFAULT 0,
            language TEXT DEFAULT 'pt',
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    conn.commit()

def header():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}   🛠️  Pyeduc - Gerenciador & Debugger do Banco de Dados SQLite{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")
    print(f"{YELLOW}Arquivo SQLite em uso:{RESET} {BOLD}{DB_PATH}{RESET}\n")

def list_users(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, u.password, 
               COALESCE(us.current_lesson, 0) as current_lesson,
               (SELECT COUNT(*) FROM progress p WHERE p.user_id = u.id AND p.completed = 1) as completed_count
        FROM users u
        LEFT JOIN user_state us ON u.id = us.user_id
        ORDER BY u.id ASC
    ''')
    users = cursor.fetchall()
    
    print(f"{BOLD}{GREEN}📋 Usuários Cadastrados ({len(users)}):{RESET}\n")
    if not users:
        print(f"  {YELLOW}(Nenhum usuário cadastrado no banco de dados.){RESET}\n")
        return []

    print(f"{BOLD}{'ID':<6} | {'Usuário':<18} | {'Senha':<12} | {'Aula Atual':<12} | {'Aulas Concluídas'}{RESET}")
    print("-" * 70)
    for u in users:
        uid, uname, upass, curr_l, comp_c = u
        print(f"{uid:<6} | {uname:<18} | {upass:<12} | {curr_l:<12} | {comp_c}")
    print()
    return users

def view_user_details(conn):
    users = list_users(conn)
    if not users:
        prompt_input("Pressione ENTER para voltar ao menu...")
        return
    
    uid_str = prompt_input(f"{BOLD}Digite o ID do usuário para ver detalhes: {RESET}").strip()
    if not uid_str.isdigit():
        print(f"{RED}ID inválido.{RESET}")
        prompt_input("Pressione ENTER para continuar...")
        return
    
    uid = int(uid_str)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE id = ?", (uid,))
    user = cursor.fetchone()
    if not user:
        print(f"{RED}Usuário com ID {uid} não encontrado.{RESET}")
        prompt_input("Pressione ENTER para continuar...")
        return

    cursor.execute("SELECT current_lesson, language FROM user_state WHERE user_id = ?", (uid,))
    st = cursor.fetchone()
    curr_lesson = st[0] if st else 0
    lang = st[1] if st else 'pt'

    cursor.execute("SELECT lesson_id, completed, completed_activities FROM progress WHERE user_id = ? ORDER BY lesson_id ASC", (uid,))
    progs = cursor.fetchall()

    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{GREEN}🔍 Detalhes do Usuário #{user[0]} - {user[1]}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}ID:{RESET} {user[0]}")
    print(f"{BOLD}Usuário:{RESET} {user[1]}")
    print(f"{BOLD}Senha:{RESET} {user[2]}")
    print(f"{BOLD}Aula Atual (Index/ID):{RESET} {curr_lesson}")
    print(f"{BOLD}Idioma Configurado:{RESET} {lang}")
    print(f"{BOLD}Aulas com Registro de Progresso ({len(progs)}):{RESET}")
    
    if not progs:
        print(f"  {YELLOW}(Nenhum progresso registrado para este usuário){RESET}")
    else:
        for p in progs:
            lid, comp, acts = p
            status = f"{GREEN}Concluída ✔{RESET}" if comp else f"{YELLOW}Em andamento ⏳{RESET}"
            print(f"  • Lição ID {lid:<4} -> Status: {status} | Atividades: {acts}")
    print(f"{CYAN}{'='*60}{RESET}\n")
    prompt_input("Pressione ENTER para voltar ao menu...")

def reset_user_progress(conn):
    users = list_users(conn)
    if not users:
        prompt_input("Pressione ENTER para voltar ao menu...")
        return
    
    uid_str = prompt_input(f"{BOLD}Digite o ID do usuário para resetar o progresso das aulas: {RESET}").strip()
    if not uid_str.isdigit():
        print(f"{RED}ID inválido.{RESET}")
        prompt_input("Pressione ENTER para continuar...")
        return
    
    uid = int(uid_str)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (uid,))
    user = cursor.fetchone()
    if not user:
        print(f"{RED}Usuário com ID {uid} não encontrado.{RESET}")
        prompt_input("Pressione ENTER para continuar...")
        return

    conf = prompt_input(f"{RED}Tem certeza que deseja resetar todo o progresso do usuário '{user[0]}'? (s/N): {RESET}").strip().lower()
    if conf == 's':
        cursor.execute("DELETE FROM progress WHERE user_id = ?", (uid,))
        cursor.execute("UPDATE user_state SET current_lesson = 0 WHERE user_id = ?", (uid,))
        conn.commit()
        print(f"\n{GREEN}✅ Progresso do usuário '{user[0]}' resetado com sucesso!{RESET}")
    else:
        print(f"\n{YELLOW}Operação cancelada.{RESET}")
    prompt_input("Pressione ENTER para continuar...")

def unlock_all_lessons(conn):
    users = list_users(conn)
    if not users:
        prompt_input("Pressione ENTER para voltar ao menu...")
        return
    
    uid_str = prompt_input(f"{BOLD}Digite o ID do usuário para desbloquear todas as aulas: {RESET}").strip()
    if not uid_str.isdigit():
        print(f"{RED}ID inválido.{RESET}")
        prompt_input("Pressione ENTER para continuar...")
        return
    
    uid = int(uid_str)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (uid,))
    user = cursor.fetchone()
    if not user:
        print(f"{RED}Usuário com ID {uid} não encontrado.{RESET}")
        prompt_input("Pressione ENTER para continuar...")
        return

    # Marca lições de 0 a 38 como concluídas
    for lid in range(39):
        cursor.execute('''
            INSERT INTO progress (user_id, lesson_id, completed, completed_activities)
            VALUES (?, ?, 1, '[]')
            ON CONFLICT(user_id, lesson_id) DO UPDATE SET completed = 1
        ''', (uid, lid))
    
    cursor.execute("UPDATE user_state SET current_lesson = 38 WHERE user_id = ?", (uid,))
    conn.commit()
    print(f"\n{GREEN}🔓 Todas as 39 lições foram marcadas como concluídas para '{user[0]}'!{RESET}")
    prompt_input("Pressione ENTER para continuar...")

def delete_user(conn):
    users = list_users(conn)
    if not users:
        prompt_input("Pressione ENTER para voltar ao menu...")
        return
    
    uid_str = prompt_input(f"{BOLD}Digite o ID do usuário a ser excluído: {RESET}").strip()
    if not uid_str.isdigit():
        print(f"{RED}ID inválido.{RESET}")
        prompt_input("Pressione ENTER para continuar...")
        return
    
    uid = int(uid_str)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (uid,))
    user = cursor.fetchone()
    if not user:
        print(f"{RED}Usuário com ID {uid} não encontrado.{RESET}")
        prompt_input("Pressione ENTER para continuar...")
        return

    conf = prompt_input(f"{RED}⚠️ ATENÇÃO: Apagar o usuário '{user[0]}' excluirá permanentemente sua conta e histórico. Confirmar? (s/N): {RESET}").strip().lower()
    if conf == 's':
        cursor.execute("DELETE FROM progress WHERE user_id = ?", (uid,))
        cursor.execute("DELETE FROM user_state WHERE user_id = ?", (uid,))
        cursor.execute("DELETE FROM users WHERE id = ?", (uid,))
        conn.commit()
        print(f"\n{GREEN}🗑️ Usuário '{user[0]}' removido com sucesso.{RESET}")
    else:
        print(f"\n{YELLOW}Exclusão cancelada.{RESET}")
    prompt_input("Pressione ENTER para continuar...")

def create_user(conn):
    print(f"{BOLD}{GREEN}➕ Adicionar Novo Usuário:{RESET}\n")
    username = prompt_input("Nome de Usuário: ").strip()
    if not username:
        print(f"{RED}Nome de usuário não pode ser vazio.{RESET}")
        prompt_input("Pressione ENTER para continuar...")
        return
    
    password = prompt_input("Senha: ").strip()
    if not password:
        print(f"{RED}Senha não pode ser vazia.{RESET}")
        prompt_input("Pressione ENTER para continuar...")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        uid = cursor.lastrowid
        cursor.execute("INSERT INTO user_state (user_id, current_lesson) VALUES (?, 0)", (uid,))
        conn.commit()
        print(f"\n{GREEN}✅ Usuário '{username}' (ID: {uid}) criado com sucesso!{RESET}")
    except sqlite3.IntegrityError:
        print(f"\n{RED}Erro: Já existe um usuário cadastrado com o nome '{username}'.{RESET}")
    prompt_input("Pressione ENTER para continuar...")

def main_menu():
    conn = get_connection()
    init_tables(conn)
    
    while True:
        header()
        print(f"{BOLD}Menu de Gerenciamento:{RESET}")
        print(" [1] 📋 Listar todos os usuários")
        print(" [2] 🔍 Ver detalhes de um usuário")
        print(" [3] ➕ Criar novo usuário")
        print(" [4] 🧹 Resetar progresso de aulas de um usuário")
        print(" [5] 🔓 Desbloquear TODAS as aulas para um usuário")
        print(" [6] 🗑️ Excluir um usuário")
        print(" [0] 🚪 Sair")
        print()
        
        choice = prompt_input(f"{BOLD}Escolha uma opção [0-6]: {RESET}").strip()
        
        if choice == "1":
            header()
            list_users(conn)
            prompt_input("Pressione ENTER para continuar...")
        elif choice == "2":
            header()
            view_user_details(conn)
        elif choice == "3":
            header()
            create_user(conn)
        elif choice == "4":
            header()
            reset_user_progress(conn)
        elif choice == "5":
            header()
            unlock_all_lessons(conn)
        elif choice == "6":
            header()
            delete_user(conn)
        elif choice == "0":
            print(f"\n{GREEN}Saindo do gerenciador... Até logo!{RESET}\n")
            conn.close()
            sys.exit(0)
        else:
            print(f"\n{RED}Opção inválida! Escolha um número entre 0 e 6.{RESET}")
            prompt_input("Pressione ENTER para continuar...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Operação interrompida pelo usuário. Saindo...{RESET}\n")
        sys.exit(0)
