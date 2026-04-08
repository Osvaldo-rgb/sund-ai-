from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db, SessionLocal
from app.models.db_models import Ticket, Message
from app.core.ia import get_ai_response
from app.core.deps import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatInput(BaseModel):
    mensagem: str

@router.post("/{ticket_id}")
async def chat(
    ticket_id: int,
    body: ChatInput,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")

    #    depois — só as últimas 10 mensagens
    historico = db.query(Message).filter(Message.ticket_id == ticket_id).all()

    historico = db.query(Message).filter(
        Message.ticket_id == ticket_id
    ).order_by(Message.id.desc()).limit(10).all()
    historico = list(reversed(historico))
    mensagens = [{"role": m.role, "content": m.content} for m in historico]

    contexto = f"Ticket: {ticket.titulo}\nDescrição: {ticket.descricao}"
    mensagens_com_contexto = [{"role": "user", "content": contexto}] + mensagens
    mensagens_com_contexto.append({"role": "user", "content": body.mensagem})

    db.add(Message(ticket_id=ticket_id, role="user", content=body.mensagem))

    resposta = await get_ai_response(mensagens_com_contexto)

    db.add(Message(ticket_id=ticket_id, role="assistant", content=resposta))
    db.commit()

    return {"resposta": resposta}

@router.get("/{ticket_id}/historico")
def historico(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Message).filter(Message.ticket_id == ticket_id).all()

@router.websocket("/ws/{ticket_id}")
async def websocket_chat(websocket: WebSocket, ticket_id: int):
    await websocket.accept()
    db = SessionLocal()

    try:
        while True:
            mensagem = await websocket.receive_text()

            ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket:
                await websocket.send_text("Erro: ticket não encontrado")
                break

            historico = db.query(Message).filter(Message.ticket_id == ticket_id).all()
            mensagens = [{"role": m.role, "content": m.content} for m in historico]

            contexto = f"Ticket: {ticket.titulo}\nDescrição: {ticket.descricao}"
            mensagens_com_contexto = [{"role": "user", "content": contexto}] + mensagens
            mensagens_com_contexto.append({"role": "user", "content": mensagem})

            db.add(Message(ticket_id=ticket_id, role="user", content=mensagem))
            db.commit()

            resposta = await get_ai_response(mensagens_com_contexto)

            db.add(Message(ticket_id=ticket_id, role="assistant", content=resposta))
            db.commit()

            await websocket.send_text(resposta)

    except WebSocketDisconnect:
            pass
    finally:
        db.close()