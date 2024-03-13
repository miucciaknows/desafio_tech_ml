from flask import Flask, request, jsonify
import json
from db.config import DatabaseConfig
from rabbitmq.rabbitmq import RabbitMQ
import json
from db.config import DatabaseConfig
from rabbitmq.rabbitmq import RabbitMQ
from models.request_model import AgendamentoRequest

class CommunicationScheduler:
    def __init__(self):
        self.app = Flask(__name__)
        self.db_config = DatabaseConfig()
        self.rabbitmq = RabbitMQ()

        self.db_connection = self.db_config.data_base_connection()
        self.db_config.verify_table_agendamentos(self.db_connection)

        self.connection = self.rabbitmq.rabbitmq_connection()
        self.channel = self.connection.channel()
        self.rabbitmq.create_queue(self.channel, 'comunicacoes_queue')

        self.routes()

    def routes(self):
        @self.app.route('/agendamento', methods=['POST'])
        def agendar_comunicacao():
            try:
                request_data = AgendamentoRequest(**request.json)
            except ValueError as e:
                return jsonify({'erro': 'Erro de validação: {}'.format(str(e))}), 400

            try:
                with self.db_connection.cursor() as database_cursor:
                    database_cursor.execute("INSERT INTO agendamentos (data_hora_envio, destinatario, mensagem) VALUES (%s, %s, %s)",
                                            (request_data.data_hora_envio, request_data.destinatario, request_data.mensagem))
                    self.db_connection.commit()
            except Exception as e:
                return jsonify({'erro': f"Erro ao inserir agendamento no banco de dados: {e}"}), 500

            self.channel.basic_publish(exchange='',
                                  routing_key='comunicacoes_queue',
                                  body=json.dumps(request_data.model_dump()))

            return jsonify({'mensagem': 'Agendamento realizado com sucesso'}), 201

        @self.app.route('/consulta/<destinatario>', methods=['GET'])
        def consultar_comunicacao(destinatario):
            try:
                with self.db_connection.cursor() as cur:
                    cur.execute("SELECT * FROM agendamentos WHERE destinatario = %s", (destinatario,))
                    communications_recipient = cur.fetchall()
            except Exception as e:
                return jsonify({'erro': f"Erro ao consultar comunicação: {e}"}), 500

            if not communications_recipient:
                return jsonify({'mensagem': 'Nenhuma comunicação encontrada para o destinatário'}), 404

            comunicacoes_dict = [{'id': row[0], 'data_hora_envio': row[1], 'destinatario': row[2], 'mensagem': row[3], 'status': row[4]} for row in communications_recipient]

            return jsonify(comunicacoes_dict), 200

        @self.app.route('/cancelamento/<int:id>', methods=['DELETE'])
        def cancelar_comunicacao(id):
            try:
                with self.db_connection.cursor() as database_cursor:
                    database_cursor.execute("SELECT * FROM agendamentos WHERE id = %s", (id,))
                    if database_cursor.rowcount == 0:
                        print("Comunicação não encontrada")
                        return jsonify({'erro': 'Comunicação não encontrada'}), 404
                    
                    database_cursor.execute("UPDATE agendamentos SET status = 'cancelado' WHERE id = %s", (id,))
                    self.db_connection.commit()
            except Exception as e:
                return jsonify({'erro': f"Erro ao cancelar comunicação: {e}"}), 500

            return jsonify({'mensagem': 'Cancelamento realizado com sucesso'}), 200

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    communication_scheduler = CommunicationScheduler()
    communication_scheduler.run()
