from pydantic import BaseModel
from typing import Optional

class ProfissionalCreate(BaseModel):
    email: str                    # ← Mudado de EmailStr para str (temporário)
    password: str
    nome_completo: str
    especialidade: Optional[str] = None
    numero_licenca: Optional[str] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Modelo para refresh token"""
    refresh_token: str