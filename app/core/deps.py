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
    bloqueado = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
    if bloqueado:
        raise HTTPException(status_code=401, detail="Token revogado")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Token inválido")

        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")

        return {
            "email": email,
            "role": payload.get("role"),
            "unidade_saude_id": payload.get("unidade_saude_id"),
            "id": payload.get("id")                     # id do ProfissionalSaude
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")