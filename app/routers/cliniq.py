from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db, SessionLocal
from app.models.db_models import CasoClinico, MensagemClinica
from app.core.cliniq_core import get_cliniq_response
from app.core.deps import get_current_user
from app.core.rbac import verificar_unidade_obrigatoria, verificar_unidade_saude

router = APIRouter(prefix="/cliniq", tags=["cliniq"])


class MensagemInput(BaseModel):
    mensagem: str


# ===================== ENDPOINT HTTP =====================
@router.post("/{caso_id}")
async def chat_clinico(
    caso_id: int,
    body: MensagemInput,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Busca o caso
    caso = db.query(CasoClinico).filter(CasoClinico.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso clínico não encontrado")

    # Verificações de acesso
    verificar_unidade_obrigatoria(current_user)
    if current_user.get("role") != "superadmin":
        verificar_unidade_saude(current_user, caso.unidade_saude_id)

    # Busca histórico recente (últimas 10 mensagens)
    historico_db = db.query(MensagemClinica).filter(
        MensagemClinica.caso_id == caso_id
    ).order_by(MensagemClinica.id.desc()).limit(10).all()

    historico = [{"role": m.role, "content": m.content} for m in reversed(historico_db)]

    # Regista a mensagem do utilizador
    db.add(MensagemClinica(
        caso_id=caso_id,
        role="user",
        content=body.mensagem
    ))
    db.commit()

    # Chama o motor CliniqCore (com RAG)
    resposta = await get_cliniq_response(
        historico + [{"role": "user", "content": body.mensagem}],
        caso
    )

    # Regista a resposta da IA
    db.add(MensagemClinica(
        caso_id=caso_id,
        role="assistant",
        content=resposta
    ))
    db.commit()

    return {
        "resposta": resposta,
        "fonte": "cliniq_core",
        "caso_id": caso_id
    }


# ===================== WEBSOCKET =====================
@router.websocket("/ws/{caso_id}")
async def websocket_clinico(websocket: WebSocket, caso_id: int):
    await websocket.accept()
    db = SessionLocal()

    try:
        while True:
            mensagem = await websocket.receive_text()

            caso = db.query(CasoClinico).filter(CasoClinico.id == caso_id).first()
            if not caso:
                await websocket.send_text("Erro: caso clínico não encontrado")
                break

            # Busca todo o histórico
            historico_db = db.query(MensagemClinica).filter(
                MensagemClinica.caso_id == caso_id
            ).all()

            historico = [{"role": m.role, "content": m.content} for m in historico_db]

            # Regista mensagem do utilizador
            db.add(MensagemClinica(caso_id=caso_id, role="user", content=mensagem))
            db.commit()

            # Gera resposta com CliniqCore
            resposta = await get_cliniq_response(
                historico + [{"role": "user", "content": mensagem}],
                caso
            )

            # Regista resposta da IA
            db.add(MensagemClinica(caso_id=caso_id, role="assistant", content=resposta))
            db.commit()

            # Envia resposta pelo WebSocket
            await websocket.send_text(resposta)

    except WebSocketDisconnect:
        pass
    finally:
        db.close()