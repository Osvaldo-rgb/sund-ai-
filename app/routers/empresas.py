from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.db_models import Empresa, User
from app.core.deps import get_current_user
from app.core.rbac import verificar_permissao

router = APIRouter(prefix="/empresas", tags=["empresas"])

class EmpresaCreate(BaseModel):
    nome: str
    dominio: str

@router.post("/", status_code=201)
def criar_empresa(
    empresa: EmpresaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    verificar_permissao(current_user, "gerir_empresas")
    nova = Empresa(nome=empresa.nome, dominio=empresa.dominio)
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

@router.post("/{empresa_id}/users/{user_email}")
def associar_user(
    empresa_id: int,
    user_email: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    verificar_permissao(current_user, "gerir_empresas")
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado")
    user.empresa_id = empresa_id
    db.commit()
    return {"mensagem": f"{user_email} associado à empresa {empresa_id}"}