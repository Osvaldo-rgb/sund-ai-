from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.ticket import TicketCreate
from app.models.db_models import Ticket

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("/", status_code=201)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    novo_ticket = Ticket(**ticket.model_dump())
    db.add(novo_ticket)
    db.commit()
    db.refresh(novo_ticket)
    return novo_ticket

@router.get("/")
def list_tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).all()