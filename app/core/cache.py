import hashlib
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

class ResponseCache:
    def __init__(self):
        self.cache = {}
        self.ttl_minutos = 60  # cache válida 1 hora

    def _chave(self, ticket_id: int, mensagem: str) -> str:
        texto = f"{ticket_id}:{mensagem.lower().strip()}"
        return hashlib.md5(texto.encode()).hexdigest()

    def get(self, ticket_id: int, mensagem: str):
        chave = self._chave(ticket_id, mensagem)
        if chave in self.cache:
            entrada = self.cache[chave]
            if datetime.now() < entrada["expira"]:
                return entrada["resposta"]
            del self.cache[chave]
        return None

    def set(self, ticket_id: int, mensagem: str, resposta: str):
        chave = self._chave(ticket_id, mensagem)
        self.cache[chave] = {
            "resposta": resposta,
            "expira": datetime.now() + timedelta(minutes=self.ttl_minutos)
        }

cache = ResponseCache()