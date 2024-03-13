import unittest
import json

from main import CommunicationScheduler

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = CommunicationScheduler().app.test_client()
        self.app.testing = True

    def test_agendamento(self):
        payload = {
            'data_hora_envio': '2024-03-12 10:00:00',
            'destinatario': 'exemplo@example.com',
            'mensagem': 'Teste de mensagem'
        }
        response = self.app.post('/agendamento', json=payload)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)  
        self.assertIn('mensagem', data)
        print("Teste de agendamento bem-sucedido.")

        payload = {'mensagem': 'Teste de mensagem'}
        response = self.app.post('/agendamento', json=payload)
        self.assertEqual(response.status_code, 400)
        print("Teste de agendamento com campos ausentes bem-sucedido.")

    def test_consulta(self):
        recipient = 'exemplo@example.com'
        response = self.app.get(f'/consulta/{recipient}')
        self.assertEqual(response.status_code, 200)
        print("Teste de consulta bem-sucedido.")

        recipient = 'fulano@example.com'
        response = self.app.get(f'/consulta/{recipient}')
        self.assertEqual(response.status_code, 404)
        print("Teste de consulta para destinatário fulano.")
    
    def test_cancelamento(self):
        id_comunicacao = 9999  
        response = self.app.delete(f'/cancelamento/{id_comunicacao}')
        self.assertEqual(response.status_code, 404)
        print("Teste de cancelamento bem-sucedido.")

if __name__ == '__main__':
    unittest.main()
