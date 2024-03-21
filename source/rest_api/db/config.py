# importando as bibliotecas necessárias 
import os
import psycopg2
# Importando load_dotenv do módulo dotenv para carregar variáveis de ambiente de um arquivo .env
from dotenv import load_dotenv
# Importando a classe InitialDatabaseConfig do módulo db.initial_config
from db.initial_config import InitialDatabaseConfig


class DatabaseConfig:
    """
    Classe para as Configurações relacionadas ao banco de dados.
    """
    def __init__(self):
        """
        Método para a classe carregar as variáveis de ambiente.
        """
        load_dotenv()

    def connect_to_database(self):
        """
        Função para criar e retornando uma conexão com o banco de dados.
        """
        return psycopg2.connect(
            dbname="postgres",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host="aws-0-sa-east-1.pooler.supabase.com",
            port="5432"
        )

    def verify_table_agendamentos(self, conn):
        """
        Função para verificar se a tabela 'agendamentos' existe no banco de dados e a criando caso não exista.
        """
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'agendamentos')")
                existing_table = cur.fetchone()[0]
                if not existing_table:
                    initial_config = InitialDatabaseConfig()
                    initial_config.create_communication_table(conn)
        except Exception as e:
            raise Exception(f"Erro ao verificar a existência da tabela 'agendamentos': {e}")