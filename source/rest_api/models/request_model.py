from pydantic import BaseModel

class AgendamentoRequest(BaseModel):
    data_hora_envio: str
    destinatario: str
    mensagem: str
