# endpoints.py

from flask import Flask, request, jsonify
import json
from db.config import data_base_connection, verify_table_agendamentos
from rabbitmq.rabbitmq import rabbitmq_connection, create_queue
from models.request_model import AgendamentoRequest

app = Flask(__name__)

db_connection = data_base_connection()
verify_table_agendamentos(db_connection)

connection = rabbitmq_connection()
channel = connection.channel()
create_queue(channel, 'comunicacoes_queue')


@app.route('/agendamento', methods=['POST'])
def agendar_comunicacao():
    try:
        request_data = AgendamentoRequest(**request.json)
    except ValueError as e:
        return jsonify({'erro': 'Erro de validação: {}'.format(str(e))}), 400

    try:
        with db_connection.cursor() as database_cursor:
            database_cursor.execute("INSERT INTO agendamentos (data_hora_envio, destinatario, mensagem) VALUES (%s, %s, %s)",
                                    (request_data.data_hora_envio, request_data.destinatario, request_data.mensagem))
            db_connection.commit()
    except Exception as e:
        return jsonify({'erro': f"Erro ao inserir agendamento no banco de dados: {e}"}), 500

    channel.basic_publish(exchange='',
                          routing_key='comunicacoes_queue',
                          body=json.dumps(request_data.model_dump()))

    return jsonify({'mensagem': 'Agendamento realizado com sucesso'}), 201


@app.route('/consulta/<destinatario>', methods=['GET'])
def consultar_comunicacao(destinatario):
    try:
        with db_connection.cursor() as cur:
            cur.execute("SELECT * FROM agendamentos WHERE destinatario = %s", (destinatario,))
            communications_recipient= cur.fetchall()
    except Exception as e:
        return jsonify({'erro': f"Erro ao consultar comunicação: {e}"}), 500

    if not communications_recipient:
        return jsonify({'mensagem': 'Nenhuma comunicação encontrada para o destinatário'}), 404

    comunicacoes_dict = [{'id': row[0], 'data_hora_envio': row[1], 'destinatario': row[2], 'mensagem': row[3], 'status': row[4]} for row in communications_recipient]

    return jsonify(comunicacoes_dict), 200


@app.route('/cancelamento/<int:id>', methods=['DELETE'])
def cancelar_comunicacao(id):
    try:
        with db_connection.cursor() as database_cursor:
            database_cursor.execute("SELECT * FROM agendamentos WHERE id = %s", (id,))
            if database_cursor.rowcount == 0:
                print("Comunicação não encontrada")
                return jsonify({'erro': 'Comunicação não encontrada'}), 404
            
            database_cursor.execute("UPDATE agendamentos SET status = 'cancelado' WHERE id = %s", (id,))
            db_connection.commit()
    except Exception as e:
        return jsonify({'erro': f"Erro ao cancelar comunicação: {e}"}), 500

    return jsonify({'mensagem': 'Cancelamento realizado com sucesso'}), 200

if __name__ == '__main__':
    app.run(debug=True)
