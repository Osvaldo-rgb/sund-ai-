from pydantic import BaseModel, EmailStr
from typing import Optional

class ProfissionalCreate(BaseModel):
    """Modelo usado no registo de novos profissionais de saúde"""
    email: EmailStr
    password: str
    nome_completo: str
    especialidade: Optional[str] = None
    numero_licenca: Optional[str] = None


class Token(BaseModel):
    """Resposta padrão de autenticação"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Modelo para refresh token"""
    refresh_token: str