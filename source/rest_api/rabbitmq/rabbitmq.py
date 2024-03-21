# Importando as bibliotecas necessárias 
import pika
import time

class RabbitMQ:
    def __init__(self, rabbitmq_host):
        """
        Inicializando a instância do RabbitMQ.

        Args:
            rabbitmq_host (str): O endereço do host do RabbitMQ.
        """
        self.rabbitmq_host = rabbitmq_host
        self.connection = None
        self.channel = None

    def connect(self):
        """
        Estabelecendo conexão com o RabbitMQ.

        Returns:
            pika.BlockingConnection: A conexão estabelecida.
        """
        while True:
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbitmq_host, heartbeat=600))
                print("Conexão estabelecida com RabbitMQ.")
                return self.connection
            except pika.exceptions.AMQPConnectionError:
                print("Falha ao conectar com RabbitMQ. Tentando novamente em 10 segundos...")
                time.sleep(10)

    def get_channel(self):
        """
        Retornando um canal do RabbitMQ.

        Returns:
            pika.channel.Channel: O canal do RabbitMQ.
        """
        if not self.connection or self.connection.is_closed:
            self.connect()

        if not self.channel or self.channel.is_closed:
            self.channel = self.connection.channel()

        return self.channel

    def create_queue(self, queue_name):
        """
        Criando uma fila no RabbitMQ.

        Args:
            queue_name (str): nome da fila para ser criada.
        """
        channel = self.get_channel()
        channel.queue_declare(queue=queue_name)


def consume_messages(rabbitmq):
    """
    Iniciando o consumo de mensagens a partir de uma fila no RabbitMQ.

    Args:
        rabbitmq (RabbitMQ): Instância da classe RabbitMQ.
    """
    def callback(ch, method, properties, body):
        """
        Callback chamado quando uma mensagem é recebida.

        Args:
            ch: Canal de comunicação.
            method: Informações do método de entrega.
            properties: Propriedades da mensagem.
            body (bytes): Corpo da mensagem.
        """
        print("Mensagem recebida:", body)
        # Implemente o processamento da mensagem aqui
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel = rabbitmq.get_channel()
    channel.basic_consume(queue='comunicacoes_queue', on_message_callback=callback)
    print("Consumidor de mensagens iniciado.")
    channel.start_consuming()
