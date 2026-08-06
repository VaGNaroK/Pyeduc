import json
import sqlite3
import shutil
import os
import sys

def migrate_database():
    db_path = os.path.expanduser("~/.pyeduc/pyeduc.db")
    if not os.path.exists(db_path):
        # Tentativa local (se existir)
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'pyeduc.db')
        if not os.path.exists(db_path):
            print("Nenhum banco de dados pyeduc.db encontrado para migrar.")
            return

    mapping_file = os.path.join(os.path.dirname(__file__), '..', 'content', 'id_mapping.json')
    if not os.path.exists(mapping_file):
        print(f"Arquivo de mapeamento não encontrado: {mapping_file}")
        return

    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
        
    print(f"Fazendo backup do banco de dados em {db_path}...")
    shutil.copy(db_path, db_path + ".migrate.bak")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Atualizar user_state (current_lesson)
    print("Atualizando tabela user_state...")
    cur.execute("SELECT user_id, current_lesson FROM user_state")
    states = cur.fetchall()
    
    for user_id, curr_lesson in states:
        str_id = str(curr_lesson)
        if str_id in mapping:
            new_id = mapping[str_id]
            if new_id != curr_lesson:
                cur.execute("UPDATE user_state SET current_lesson = ? WHERE user_id = ?", (new_id, user_id))
                print(f"Usuário {user_id}: current_lesson movida de {curr_lesson} para {new_id}")

    # Atualizar progress (lesson_id)
    print("Atualizando tabela progress...")
    cur.execute("SELECT user_id, lesson_id, completed, completed_activities FROM progress")
    progresses = cur.fetchall()
    
    # Excluir todo o progresso e reinserir para evitar conflito de Primary Key (user_id, lesson_id)
    cur.execute("DELETE FROM progress")
    
    inserted_count = 0
    for row in progresses:
        user_id, lesson_id, completed, completed_activities = row
        str_id = str(lesson_id)
        if str_id in mapping:
            new_id = mapping[str_id]
        else:
            new_id = lesson_id # fallback se algo deu errado
            
        cur.execute("""
            INSERT INTO progress (user_id, lesson_id, completed, completed_activities)
            VALUES (?, ?, ?, ?)
        """, (user_id, new_id, completed, completed_activities))
        inserted_count += 1
        if new_id != lesson_id:
            print(f"Usuário {user_id}: progresso da lição {lesson_id} migrado para {new_id}")

    conn.commit()
    conn.close()
    
    print(f"Migração concluída com sucesso! {len(states)} usuários verificados e {inserted_count} registros de progresso migrados.")

if __name__ == "__main__":
    migrate_database()
