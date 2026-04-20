from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.db_models import UnidadeSaude, ProfissionalSaude
from app.core.deps import get_current_user
from app.core.rbac import verificar_permissao

router = APIRouter(tags=["unidades-saude"])

class UnidadeSaudeCreate(BaseModel):
    nome: str
    tipo: str                     # hospital, clinica, posto_saude...
    dominio: str
    provincia: str

@router.post("/", status_code=201)
def criar_unidade(
    unidade: UnidadeSaudeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    verificar_permissao(current_user, "gerir_unidades")

    nova = UnidadeSaude(
        nome=unidade.nome,
        tipo=unidade.tipo,
        dominio=unidade.dominio,
        provincia=unidade.provincia
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@router.post("/{unidade_id}/profissionais/{email}")
def associar_profissional(
    unidade_id: int,
    email: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    verificar_permissao(current_user, "gerir_unidades")

    prof = db.query(ProfissionalSaude).filter(ProfissionalSaude.email == email).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    prof.unidade_saude_id = unidade_id
    db.commit()
    return {"mensagem": f"{email} associado à unidade {unidade_id}"}