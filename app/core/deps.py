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
    logger.info(f"Recebido token para validação: {token[:30]}...")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        if db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first():
            logger.warning("Token encontrado na blacklist")
            raise credentials_exception

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Payload decodificado: {payload}")

        email = payload.get("sub")
        if email is None:
            logger.error("Payload sem 'sub'")
            raise credentials_exception

        return {
            "email": email,
            "role": payload.get("role"),
            "unidade_saude_id": payload.get("unidade_saude_id"),
            "id": payload.get("id")
        }

    except JWTError as e:
        logger.error(f"JWTError ao decodificar token: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Erro inesperado em get_current_user: {e}")
        raise credentials_exception