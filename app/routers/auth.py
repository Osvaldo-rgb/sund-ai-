from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.deps import oauth2_scheme
from app.database import get_db
from app.models.user import ProfissionalCreate, Token, RefreshRequest
from app.models.db_models import ProfissionalSaude, TokenBlacklist
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    SECRET_KEY, ALGORITHM
)
from app.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(
    profissional: ProfissionalCreate,
    db: Session = Depends(get_db)
):
    existe = db.query(ProfissionalSaude).filter(
        ProfissionalSaude.email == profissional.email
    ).first()

    if existe:
        raise HTTPException(status_code=400, detail="Este email já está registado")

    try:
        novo = ProfissionalSaude(
            email=profissional.email,
            password_hash=hash_password(profissional.password),
            nome_completo=profissional.nome_completo,
            especialidade=profissional.especialidade,
            numero_licenca=profissional.numero_licenca,
            role="medico"
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)

        return {
            "mensagem": "Profissional registado com sucesso",
            "id": novo.id,
            "email": novo.email
        }
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar profissional")


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,                                   # ← Obrigatório para rate limiter
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(ProfissionalSaude).filter(
        ProfissionalSaude.email == form.username
    ).first()

    if not db_user or not verify_password(form.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    payload = {
        "sub": db_user.email,
        "role": db_user.role,
        "unidade_saude_id": db_user.unidade_saude_id,
        "id": db_user.id
    }

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
def refresh(
    request: Request,                                   # ← CORREÇÃO: Adicionado aqui!
    body: RefreshRequest,
    db: Session = Depends(get_db)
):
    """Renova os tokens de acesso"""
    if db.query(TokenBlacklist).filter(TokenBlacklist.token == body.refresh_token).first():
        raise HTTPException(status_code=401, detail="Token de refresh revogado")

    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Tipo de token inválido")

    email = payload.get("sub")
    db_user = db.query(ProfissionalSaude).filter(ProfissionalSaude.email == email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Profissional não encontrado")

    new_payload = {
        "sub": db_user.email,
        "role": db_user.role,
        "unidade_saude_id": db_user.unidade_saude_id,
        "id": db_user.id
    }

    return {
        "access_token": create_access_token(new_payload),
        "refresh_token": create_refresh_token(new_payload),
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(
    body: RefreshRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first():
        db.add(TokenBlacklist(token=token))

    if not db.query(TokenBlacklist).filter(TokenBlacklist.token == body.refresh_token).first():
        db.add(TokenBlacklist(token=body.refresh_token))

    db.commit()
    return {"mensagem": "Logout efectuado com sucesso"}