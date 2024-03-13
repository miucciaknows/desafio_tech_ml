import pika

def rabbitmq_connection():
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def create_queue(channel, queue_name):
    channel.queue_declare(queue=queue_name)
