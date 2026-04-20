from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import logging

from app.core.security import SECRET_KEY, ALGORITHM
from app.database import get_db
from app.models.db_models import TokenBlacklist

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
logger = logging.getLogger("sundai.auth")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    logger.info(f"[AUTH] Token recebido (primeiros 50 chars): {token[:50]}...")

    try:
        # Verifica blacklist
        if db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first():
            logger.warning("[AUTH] Token encontrado na blacklist!")
            raise HTTPException(status_code=401, detail="Token revogado")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"[AUTH] Payload decodificado com sucesso: {payload}")

        return {
            "email": payload.get("sub"),
            "role": payload.get("role"),
            "unidade_saude_id": payload.get("unidade_saude_id"),
            "id": payload.get("id")
        }

    except JWTError as e:
        logger.error(f"[AUTH] JWTError: {e}")
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    except Exception as e:
        logger.error(f"[AUTH] Erro inesperado: {e}")
        raise HTTPException(status_code=401, detail="Erro ao validar token")