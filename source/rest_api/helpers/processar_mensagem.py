def processar_mensagem(self, ch, method, properties, body):
    """
    Função responsável por processar mensagens recebidas.
        
    Args:
        ch (objeto): Canal de comunicação.
        method (objeto): Informações do método de entrega.
        properties (objeto): Propriedades da mensagem.
        body (str): Corpo da mensagem.
    """
    try:
        # Processando a mensagem
        request_data = AgendamentoRequest(**json.loads(body))

        # Inserindo o agendamento no banco de dados e recuperando o ID gerado
        with self.db_connection.cursor() as database_cursor:
            database_cursor.execute("INSERT INTO agendamentos (data_hora_envio, destinatario, mensagem) VALUES (%s, %s, %s) RETURNING id",
                                        (request_data.data_hora_envio, request_data.destinatario, request_data.mensagem))
            # Confirmando a transação
            self.db_connection.commit()  
            database_id = database_cursor.fetchone()[0]

            # Enviando a mensagem para a fila com o ID correto
            self.enviar_para_fila(request_data.dict(), database_id)

            # Confirmando que a mensagem foi processada com sucesso
            ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # Caso ocorra um erro ao processar a mensagem, descartar a mensagem
        print(f"Erro ao processar mensagem: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def enviar_para_fila(self, mensagem, database_id):
    """
    Função para enviar uma mensagem para a fila do RabbitMQ.

    Args:
        mensagem (dict): Dados da mensagem a ser enviada para a fila.
        database_id (int): ID gerado pelo banco de dados para a comunicação.
    """
    mensagem['id'] = database_id
    self.rabbitmq_channel.basic_publish(exchange='', routing_key='comunicacoes_queue', body=json.dumps(mensagem))