import sqlite3
from datetime import datetime
import base64

def salvar_imagem_sqlite(base64_imagem, remetente, nome_arquivo):
    conn = sqlite3.connect("checklist.db")
    cursor = conn.cursor()

    # Cria a tabela se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS imagens_recebidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remetente TEXT,
            nome_arquivo TEXT,
            timestamp TEXT,
            imagem BLOB
        );
    """)

    # Decodifica o base64 para binário
    imagem_binaria = base64.b64decode(base64_imagem)

    # Salva no banco
    cursor.execute("""
        INSERT INTO imagens_recebidas (remetente, nome_arquivo, timestamp, imagem)
        VALUES (?, ?, ?, ?)
    """, (remetente, nome_arquivo, datetime.now().isoformat(), imagem_binaria))

    conn.commit()
    conn.close()
