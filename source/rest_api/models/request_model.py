from dataclasses import dataclass

@dataclass
class AgendamentoRequest:
    """Modelo de dados para representar uma solicitação de agendamento de envio de comunicação."""
    # Data e hora para o envio da comunicação (string)
    data_hora_envio: str
    # Destinatário da comunicação (string)
    destinatario: str
    # Mensagem a ser entregue (string)
    mensagem: str