import psycopg2

class InitialDatabaseConfig:
    """
    Configurações iniciais do banco de dados.
    """
    def create_database_agendamentos(self, conn):
        """
        Cria a tabela 'agendamentos' no banco de dados.
        """
        try:
            with conn.cursor() as database_cursor:
                database_cursor.execute("""
                    CREATE TABLE agendamentos (
                        id SERIAL PRIMARY KEY,
                        data_hora_envio TIMESTAMP,
                        destinatario TEXT,
                        mensagem TEXT,
                        status TEXT DEFAULT 'agendado'
                    )
                """)
                conn.commit()
                print("Tabela 'agendamentos' criada com sucesso.")
        except Exception as e:
            raise Exception(f"Erro ao criar tabela 'agendamentos': {e}")
