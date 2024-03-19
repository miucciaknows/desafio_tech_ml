# Importando a biblioteca necessária usar com RabbitMQ
import pika

import pika

class RabbitMQ:
    def __init__(self, rabbitmq_host):
        """
        Função/Método para estabelecer uma conexão com o servidor RabbitMQ.

        Args:
            rabbitmq_host (str): Endereço IP ou nome do host do servidor RabbitMQ.
        """
        self.rabbitmq_host = rabbitmq_host
        self.connection = None
        self.channel = None

    def connect(self):
        """
        Função/Método para estabelecer uma conexão com o servidor RabbitMQ.

        Returns:
            pika.BlockingConnection: Conexão estabelecida com RabbitMQ.
        """
        # Retornando uma conexão com RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbitmq_host))
        return self.connection

    def create_queue(self, queue_name):
        """
        Função/Método para criar uma fila no RabbitMQ.

        Args:
            queue_name (str): Nome da fila a ser criada.
        """
        if self.connection is None:
            raise Exception("Conexão com o RabbitMQ não estabelecida.")

        # Abrindo um canal
        self.channel = self.connection.channel()

        # Declarando uma fila com o nome fornecido
        self.channel.queue_declare(queue=queue_name)
