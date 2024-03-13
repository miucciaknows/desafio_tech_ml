
import psycopg2
import os
from dotenv import load_dotenv

from db.initial_config import create_database_agendamentos

load_dotenv()

def data_base_connection():
    return psycopg2.connect(
        dbname="postgres",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host="aws-0-sa-east-1.pooler.supabase.com",
        port="5432"
    )

def verify_table_agendamentos(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'agendamentos')")
            existing_table = cur.fetchone()[0]
            if not existing_table:
                create_database_agendamentos(conn)
    except Exception as e:
        raise Exception(f"Erro ao verificar a existência da tabela 'agendamentos': {e}")
