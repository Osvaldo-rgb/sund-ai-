from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.ticket import TicketCreate
from app.models.db_models import Ticket
from app.core.deps import get_current_user

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("/", status_code=201)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    novo_ticket = Ticket(**ticket.model_dump())
    db.add(novo_ticket)
    db.commit()
    db.refresh(novo_ticket)
    return novo_ticket

@router.get("/")
def list_tickets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Ticket).all()