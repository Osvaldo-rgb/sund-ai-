from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import oauth2_scheme
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import BaseModel
from app.database import get_db
from app.models.user import UserCreate, Token
from app.models.db_models import User
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    SECRET_KEY, ALGORITHM
)

router = APIRouter(prefix="/auth", tags=["auth"])

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register", status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existe = db.query(User).filter(User.email == user.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="Email já registado")
    novo = User(email=user.email, password_hash=hash_password(user.password))
    db.add(novo)
    db.commit()
    return {"mensagem": "Utilizador criado"}

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == form.username).first()
    if not db_user or not verify_password(form.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = create_access_token({
        "sub": db_user.email,
        "role": db_user.role,
        "empresa_id": db_user.empresa_id  # ← incluído no token
    })
    refresh_token = create_refresh_token({
        "sub": db_user.email,
        "role": db_user.role,
        "empresa_id": db_user.empresa_id
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
@router.post("/refresh", response_model=Token)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token inválido")
        
        email = payload.get("sub")
        role = payload.get("role")
        
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
            
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token expirado")
    
    access_token = create_access_token({"sub": email, "role": role})
    refresh_token = create_refresh_token({"sub": email, "role": role})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
    
@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    from app.models.db_models import TokenBlacklist
    db.add(TokenBlacklist(token=token))
    db.commit()
    return {"mensagem": "Logout efectuado com sucesso"}