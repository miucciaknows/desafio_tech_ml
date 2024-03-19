from flask import Flask, request, jsonify
import json
import pika
import time
from db.config import DatabaseConfig
from rabbitmq.rabbitmq import RabbitMQ
from models.request_model import AgendamentoRequest

class CommunicationScheduler:
    """
    Inicializando a aplicação Flask, configurando o banco de dados e a mensageria,
    Criando as rotas e definindo os métodos para agendar, consultar e cancelar comunicações.
    """
    def __init__(self):
         # Iniciando a aplicação Flask
        self.app = Flask(__name__)
        # Configurando o banco de dados
        self.db_config = DatabaseConfig()
         # Configurando a mensageria
        # Passando o host do RabbitMQ durante a inicialização
        self.rabbitmq = RabbitMQ('rabbitmq') 
        # Estabelecendo a conexão com o banco de dados 
        self.db_connection = self.db_config.connect_to_database()
        # Verificando se a tabela de agendamentos existe
        self.db_config.verify_table_agendamentos(self.db_connection)

        # Estabelecendo a conexão com o RabbitMQ
        self.rabbitmq_connection = self.connect_to_rabbitmq()

        # Configurando rotas
        self.routes()

    def connect_to_rabbitmq(self):
        """
        Função para estabelecer uma conexão com o RabbitMQ.
        """
        rabbitmq_host = 'rabbitmq'
        while True:
            try:
                return pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
            except pika.exceptions.AMQPConnectionError:
                print("Aguardando conexão com RabbitMQ...")
                time.sleep(10)

    def routes(self):
        """
        Definindo as rotas da aplicação para agendar, consultar e cancelar comunicações.
        """
        @self.app.route('/agendamento', methods=['POST'])
        def agendar_comunicacao():
            """
            Função para Rota para agendar uma comunicação.
            """
            # Obtendo os dados da solicitação
            try:
                request_data = AgendamentoRequest(**request.json)
            except ValueError as e:
                return jsonify({'erro': 'Erro de validação: {}'.format(str(e))}), 400
            
            # Inserindo o agendamento no banco de dados
            try:
                with self.db_connection.cursor() as database_cursor:
                    database_cursor.execute("INSERT INTO agendamentos (data_hora_envio, destinatario, mensagem) VALUES (%s, %s, %s)",
                                            (request_data.data_hora_envio, request_data.destinatario, request_data.mensagem))
                    self.db_connection.commit()
            except Exception as e:
                return jsonify({'erro': f"Erro ao inserir agendamento no banco de dados: {e}"}), 500
            
            # Enviando o agendamento para a fila da mensageria
            self.rabbitmq_connection.channel().basic_publish(exchange='',
                                  routing_key='comunicacoes_queue',
                                  body=json.dumps(request_data.model_dump()))

            return jsonify({'mensagem': 'Agendamento realizado com sucesso'}), 201

        @self.app.route('/consulta/<destinatario>', methods=['GET'])
        def consultar_comunicacao(destinatario):
            """
            Função para Rota de consultar comunicações por destinatário.
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
        # Defindo porta 8080
        self.app.run(debug=True, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    # Criando uma instância de CommunicationScheduler
    communication_scheduler = CommunicationScheduler()
    communication_scheduler.run()
