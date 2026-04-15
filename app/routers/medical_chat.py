from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.database import get_db
from sqlalchemy.orm import Session
from app.core.cliniq_core import get_cliniq_response
from app.core.deps import get_current_user
from app.core.rbac import verificar_unidade_obrigatoria

router = APIRouter(prefix="/medical-chat", tags=["medical-chat"])


class MedicalChatRequest(BaseModel):
    mensagem: str
    historico: Optional[List[dict]] = None   # lista de {"role": "user"|"assistant", "content": str}
    contexto_adicional: Optional[str] = None  # ex: idade do paciente, sintomas principais, etc.


class MedicalChatResponse(BaseModel):
    resposta: str
    fonte: str = "cliniq_core"
    request_id: Optional[str] = None


@router.post("/", response_model=MedicalChatResponse)
async def medical_chat(
    body: MedicalChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint principal de chat clínico direto (sem necessidade de criar caso primeiro).
    Ideal para consultas rápidas e testes.
    """
    verificar_unidade_obrigatoria(current_user)

    # Prepara o histórico
    if body.historico is None:
        body.historico = []

    # Adiciona contexto adicional se fornecido
    if body.contexto_adicional:
        contexto = f"Contexto clínico adicional: {body.contexto_adicional}"
        body.historico.append({"role": "system", "content": contexto})

    # Adiciona a mensagem atual do utilizador
    mensagens_para_ia = body.historico + [{"role": "user", "content": body.mensagem}]

    try:
        # Chama o motor CliniqCore
        resposta_ia = await get_cliniq_response(mensagens_para_ia)

        return MedicalChatResponse(
            resposta=resposta_ia,
            fonte="cliniq_core"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar a consulta clínica: {str(e)}"
        )


# Endpoint alternativo com histórico completo (útil para apps mobile/web)
@router.post("/with-history", response_model=MedicalChatResponse)
async def medical_chat_with_history(
    body: MedicalChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Versão que recebe o histórico completo e retorna apenas a nova resposta"""
    verificar_unidade_obrigatoria(current_user)

    if not body.mensagem:
        raise HTTPException(status_code=400, detail="Mensagem não pode estar vazia")

    mensagens = body.historico or []
    mensagens.append({"role": "user", "content": body.mensagem})

    try:
        resposta = await get_cliniq_response(mensagens)
        return MedicalChatResponse(resposta=resposta)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno no motor clínico")