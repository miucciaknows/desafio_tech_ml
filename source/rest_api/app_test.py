import unittest
from flask import Flask, jsonify
import json
from db.config import DatabaseConfig

class TestCommunicationScheduler(unittest.TestCase):
    " Classe de teste para a aplicação do arquivo main.py"
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True  

        # Configurando o banco de dados para os testes
        self.db_config = DatabaseConfig()
        self.db_connection = self.db_config.connect_to_database()

        # Registrando as rotas manualmente no aplicativo de teste
        self.register_routes()

    def register_routes(self):
        """
        Registrando as rotas necessárias no aplicativo de teste.
        """
        @self.app.route('/agendamento', methods=['POST'])
        def agendar_comunicacao():
            # Função para agendandamento
            try:
                with self.db_connection.cursor() as database_cursor:
                    database_cursor.execute("INSERT INTO agendamentos (data_hora_envio, destinatario, mensagem, status) VALUES (%s, %s, %s, %s) RETURNING id",
                                            ('2024-03-13 10:00:00', 'janedoe@mail.com', 'Olá, este é um teste de agendamento de comunicação!', 'agendado'))
                    self.db_connection.commit()
                    # Obtendo o ID gerado pelo banco de dados
                    database_id = database_cursor.fetchone()[0] 
            except Exception as e:
                return jsonify({'erro': f"Erro ao inserir agendamento no banco de dados: {e}"}), 500

            return jsonify({'id': database_id, 'mensagem': 'Agendamento realizado com sucesso'}), 201

        @self.app.route('/consulta/<destinatario>', methods=['GET'])
        def consultar_comunicacao(destinatario):
            """
            Função para Rota de consultar comunicações por destinatário.
            destinatario(str): e-mail do destinatario a ser consultado
            """
            # Verificando se existem comunicações para o destinatário especificado
            try:
                with self.db_connection.cursor() as cur:
                    cur.execute("SELECT * FROM agendamentos WHERE destinatario = %s", (destinatario,))
                    communications_recipient = cur.fetchall()
            except Exception as e:
                return jsonify({'erro': f"Erro ao consultar comunicação: {e}"}), 500

            if not communications_recipient:
                return jsonify({'mensagem': 'Nenhuma comunicação encontrada para o destinatário'}), 404
            
            # Convertendo as comunicações em um formato de dicionário
            comunicacoes_dict = [{'id': row[0], 'data_hora_envio': row[1], 'destinatario': row[2], 'mensagem': row[3], 'status': row[4]} for row in communications_recipient]

            return jsonify(comunicacoes_dict), 200

        @self.app.route('/cancelamento/<int:id>', methods=['DELETE'])
        def cancelar_comunicacao(id):
            """
            Função para Rota de cancelar comunicação.
            Args:
            id(int): id da comunicação a ser cancelada
            """
            try:
                # Atualizando o status no banco de dados
                with self.db_connection.cursor() as database_cursor:
                    database_cursor.execute("UPDATE agendamentos SET status = 'cancelado' WHERE id = %s", (id,))
                    self.db_connection.commit()
            except Exception as e:
                return jsonify({'erro': f"Erro ao cancelar comunicação: {e}"}), 500

            return jsonify({'mensagem': 'Cancelamento realizado com sucesso'}), 200

    def test_agendamento_comunicacao(self):
        """Função para testar a rota de agendamento de comunicação"""
        with self.app.test_client() as client:
            response = client.post('/agendamento')

            # Verificando se a resposta não está vazia
            self.assertNotEqual(response.data, b'')

            # Verificando se a resposta está no formato JSON esperado
            try:
                data = json.loads(response.data)
            except json.JSONDecodeError as e:
                self.fail(f"Erro ao decodificar a resposta JSON: {e}")

            # Verificando se a mensagem na resposta é a que se espera
            self.assertIn('mensagem', data)
            self.assertEqual(data['mensagem'], 'Agendamento realizado com sucesso')

    def test_consultar_comunicacao(self):
        """
        Função para testar a rota de consulta de comunicação.
        """
        with self.app.test_client() as client:
            destinatario = 'janedoe@mail.com'
            response = client.get(f'/consulta/{destinatario}')
            data = json.loads(response.data)

            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0)

    def test_cancelar_comunicacao(self):
        """Função para testar a rota de cancelamento de comunicação."""
        # Agendamento de comunicação para obter um ID
        with self.app.test_client() as client:
            response = client.post('/agendamento')
            data = json.loads(response.data)
            communication_id = data['id']

        # Cancelamento da comunicação utilizando o ID obtido
        with self.app.test_client() as client:
            response = client.delete(f'/cancelamento/{communication_id}')
            data = json.loads(response.data)

            self.assertEqual(response.status_code, 200)
            self.assertIn('mensagem', data)
            self.assertEqual(data['mensagem'], 'Cancelamento realizado com sucesso')

            # Verificando se o status no banco de dados foi realmente atualizado para 'cancelado'
            with self.db_connection.cursor() as cur:
                cur.execute("SELECT status FROM agendamentos WHERE id = %s", (communication_id,))
                communication_status = cur.fetchone()[0]
                self.assertEqual(communication_status, 'cancelado')

if __name__ == '__main__':
    unittest.main()
