# Importando a biblioteca necessária usar com RabbitMQ
import pika


class RabbitMQ:
    def rabbitmq_connection(self, rabbitmq_host):
        """
        Função/Método para estabelecer uma conexão com o servidor RabbitMQ.

        Args:
            rabbitmq_host (str): Endereço IP ou nome do host do servidor RabbitMQ.

        Returns:
            BlockingConnection: Conexão estabelecida com RabbitMQ.
        """
        # Retornando uma conexão com RabbitMQ
        return pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))


    def create_queue(self, channel, queue_name):
        """
        Função/Método para criar uma fila no RabbitMQ.

        Args:
            channel (pika.Channel): Canal para comunicação com RabbitMQ.
            queue_name (str): Nome da fila a ser criada.
        """
        # Declarando uma fila com o nome fornecido
        channel.queue_declare(queue=queue_name)
