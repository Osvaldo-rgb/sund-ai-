from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.ticket import TicketCreate
from app.models.db_models import Ticket
from app.core.deps import get_current_user
from app.core.rbac import verificar_permissao, verificar_empresa_obrigatoria

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("/", status_code=201)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    verificar_empresa_obrigatoria(current_user)
    verificar_permissao(current_user, "criar_tickets")

    novo_ticket = Ticket(
        **ticket.model_dump(),
        empresa_id=current_user["empresa_id"],
        criado_por=current_user.get("id")
    )
    db.add(novo_ticket)
    db.commit()
    db.refresh(novo_ticket)
    return novo_ticket

@router.get("/")
def list_tickets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    verificar_empresa_obrigatoria(current_user)
    verificar_permissao(current_user, "ver_tickets")

    if current_user["role"] == "superadmin":
        return db.query(Ticket).all()

    return db.query(Ticket).filter(
        Ticket.empresa_id == current_user["empresa_id"]
    ).all()