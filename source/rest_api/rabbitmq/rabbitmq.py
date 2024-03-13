import pika

class RabbitMQ:
    def rabbitmq_connection(self):
        return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    def create_queue(self, channel, queue_name):
        channel.queue_declare(queue=queue_name)
