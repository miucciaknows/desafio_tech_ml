# Importando a biblioteca necessária usar com RabbitMQ
import pika

class RabbitMQ:
    def rabbitmq_connection(self):
        """
        Função/Método para estabelecer uma conexão com o servidor RabbitMQ.

        Returns:
            BlockingConnection: Conexão estabelecida com RabbitMQ.
        """
        # Retornando uma conexão com RabbitMQ

        return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    def create_queue(self, channel, queue_name):
        """
        Função/Método para criar uma fila no RabbitMQ.

        Args:
            channel (pika.Channel): Canal para comunicação com RabbitMQ.
            queue_name (str): Nome da fila a ser criada.
        """
        # Declarando uma fila com o nome fornecido
        channel.queue_declare(queue=queue_name)
