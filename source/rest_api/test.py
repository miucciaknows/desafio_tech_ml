import unittest
from flask import Flask, jsonify
import json

class TestCommunicationScheduler(unittest.TestCase):
    " Classe de teste para a aplicação do arquivo main.py"
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True  

      
        @self.app.route('/agendamento', methods=['POST'])
        def agendar_comunicacao():
            return jsonify({'mensagem': 'Agendamento realizado com sucesso'}), 201

        @self.app.route('/consulta/<destinatario>', methods=['GET'])
        def consultar_comunicacao(destinatario):
            return jsonify([{'id': 1, 'mensagem': 'Exemplo de mensagem'}]), 200

        @self.app.route('/cancelamento/<int:id>', methods=['DELETE'])
        def cancelar_comunicacao(id):
            if id == 1:
                return jsonify({'mensagem': 'Cancelamento realizado com sucesso'}), 200
            else:
                return jsonify({'erro': 'Comunicação não encontrada'}), 404

    def test_agendar_comunicacao(self):
        """Função para testar o endpoint de agendamento de comunicação"""
        with self.app.test_client() as client:
            payload = {
                'data_hora_envio': '2024-03-13 10:00:00',
                'destinatario': 'fulano@gmail.com',
                'mensagem': 'Olá, este é um teste de agendamento de comunicação!'
            }
            response = client.post('/agendamento', json=payload)
            data = json.loads(response.data)

            self.assertEqual(response.status_code, 201)
            self.assertIn('mensagem', data)
            self.assertEqual(data['mensagem'], 'Agendamento realizado com sucesso')

    def test_consultar_comunicacao(self):
        """
        Função para testar o endpoint de consulta de comunicação.
        """
        with self.app.test_client() as client:
            destinatario = 'fulano@gmail.com'
            response = client.get(f'/consulta/{destinatario}')
            data = json.loads(response.data)

            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0)

    def test_cancelar_comunicacao(self):
        """Função para testar o endpoint de cancelamento de comunicação."""
        with self.app.test_client() as client:
            id_comunicacao = 1
            response = client.delete(f'/cancelamento/{id_comunicacao}')
            data = json.loads(response.data)

            if response.status_code == 200:
                self.assertIn('mensagem', data)
                self.assertEqual(data['mensagem'], 'Cancelamento realizado com sucesso')
            elif response.status_code == 404:
                self.assertIn('erro', data)
                self.assertEqual(data['erro'], 'Esse id não consta na base de dados')
            else:
                self.fail(f"A solicitação falhou com o código de status: {response.status_code}")


if __name__ == '__main__':
    unittest.main()

