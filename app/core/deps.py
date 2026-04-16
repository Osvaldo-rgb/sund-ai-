from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.security import SECRET_KEY, ALGORITHM
from app.database import get_db
from app.models.db_models import TokenBlacklist

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Obtém o utilizador atual a partir do token JWT"""
    
    # Verifica se o token está na blacklist
    bloqueado = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
    if bloqueado:
        raise HTTPException(status_code=401, detail="Token revogado")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Token inválido (não é access token)")

        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")

        return {
            "email": email,
            "role": payload.get("role"),
            "unidade_saude_id": payload.get("unidade_saude_id"),   # ← Essencial para evitar o erro NOT NULL
            "id": payload.get("id")
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erro ao processar token: {str(e)}")


# Dependência auxiliar (opcional, mas útil)
def get_current_profissional(
    current_user: dict = Depends(get_current_user)
):
    """Retorna o dicionário do utilizador atual"""
    if not current_user.get("id"):
        raise HTTPException(status_code=401, detail="Profissional não identificado")
    return current_user