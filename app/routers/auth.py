from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.db_models import AuditLog
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr
from app.core.audit import registar
from app.core.deps import oauth2_scheme
from app.database import get_db
from app.models.user import Token
from app.models.db_models import User, TokenBlacklist
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    SECRET_KEY, ALGORITHM
)
from app.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])



class UserCreate(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existe = db.query(User).filter(User.email == user.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="Email já registado")

    try:
        novo = User(
            email=user.email,
            password_hash=hash_password(user.password)
        )
        db.add(novo)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar utilizador")

    return {"mensagem": "Utilizador criado"}


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == form.username).first()

    if not db_user or not verify_password(form.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    payload = {
        "sub": db_user.email,
        "role": db_user.role,
        "empresa_id": db_user.empresa_id
    }

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    registar(
        db,
        acao="LOGIN",
        user_email=db_user.email,
        empresa_id=db_user.empresa_id,
        ip=request.client.host
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
def refresh(
    request: Request,
    body: RefreshRequest,
    db: Session = Depends(get_db)
):
    if db.query(TokenBlacklist).filter(TokenBlacklist.token == body.refresh_token).first():
        raise HTTPException(status_code=401, detail="Token revogado")

    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token inválido")

    email = payload.get("sub")

    if not email:
        raise HTTPException(status_code=401, detail="Token inválido")

    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Utilizador não encontrado")

    payload = {
        "sub": db_user.email,
        "role": db_user.role,
        "empresa_id": db_user.empresa_id
    }

    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
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

    # busca email do token para o log
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], 
                           options={"verify_exp": False})
        registar(db, acao="LOGOUT", user_email=payload.get("sub"))
    except JWTError:
        pass

    return {"mensagem": "Logout efectuado com sucesso"}