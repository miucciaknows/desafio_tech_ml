# importando as bibliotecas necessárias 

from flask import Flask, request, jsonify
import json
from db.config import DatabaseConfig
from rabbitmq.rabbitmq import RabbitMQ
from models.request_model import AgendamentoRequest
from helpers.message_processing import message_processing, send_to_queue


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
        # Conectando com o RabbitMQ
        self.rabbitmq_connection = self.rabbitmq.connect()
        # Criando fila "comunicacoes_queue"
        self.rabbitmq.create_queue('comunicacoes_queue')
        # Obtendo o canal do RabbitMQ
        self.rabbitmq_channel = self.rabbitmq.get_channel() 

        self.routes()

    def processar_mensagem(self, ch, method, properties, body):
        """
        Função responsável por processar mensagens recebidas.
        
        Args:
            ch (objeto): Canal de comunicação.
            method (objeto): Informações do método de entrega.
            properties (objeto): Propriedades da mensagem.
            body (str): Corpo da mensagem.
            """
        message_processing(ch, method, properties, body, AgendamentoRequest, self.db_connection, self.rabbitmq_channel)
   


    def enviar_para_fila(self, mensagem, database_id):
        """
        Função para enviar uma mensagem para a fila do RabbitMQ.

        Args:
            mensagem (dict): Dados da mensagem a ser enviada para a fila.
            database_id (int): ID gerado pelo banco de dados para a comunicação.
        """
        send_to_queue(mensagem, database_id, self.rabbitmq_channel)
        
  

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
                    database_cursor.execute("INSERT INTO agendamentos (data_hora_envio, destinatario, mensagem) VALUES (%s, %s, %s) RETURNING id",
                                            (request_data.data_hora_envio, request_data.destinatario, request_data.mensagem))
                    self.db_connection.commit()
                    database_id = database_cursor.fetchone()[0]  # Obter o ID gerado pelo banco de dados

                    # Montando a mensagem para enviar para a fila
                    mensagem = {
                        'id': database_id,  # Incluir o ID gerado no corpo da mensagem
                        'data_hora_envio': request_data.data_hora_envio,
                        'destinatario': request_data.destinatario,
                        'mensagem': request_data.mensagem,
                        'status': 'agendado' 
                    }

                    # Enviando a mensagem para a fila 
                    self.enviar_para_fila(mensagem, database_id)

            except Exception as e:
                return jsonify({'erro': f"Erro ao inserir agendamento no banco de dados: {e}"}), 500

            return jsonify({'mensagem': 'Agendamento realizado com sucesso'}), 201


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
            Função para Rota de consultar comunicações por destinatário.
            Args:
            id(int): id a ser consultado
            """
            try:
                # Atualizando o status no banco de dados
                with self.db_connection.cursor() as database_cursor:
                    database_cursor.execute("UPDATE agendamentos SET status = 'cancelado' WHERE id = %s", (id,))
                    self.db_connection.commit()
            except Exception as e:
                return jsonify({'erro': f"Erro ao cancelar comunicação: {e}"}), 500

            return jsonify({'mensagem': 'Cancelamento realizado com sucesso'}), 200

    def run(self):
        # Definindo porta 8080
        self.app.run(debug=True, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    # Instanciando uma instância CommunicationScheduler 
    communication_scheduler = CommunicationScheduler()
    # Iniciando a aplicação
    communication_scheduler.run()
