from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import UserCreate, Token
from app.models.db_models import User
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

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
    token = create_access_token({"sub": db_user.email, "role": db_user.role})
    return {"access_token": token, "token_type": "bearer"}