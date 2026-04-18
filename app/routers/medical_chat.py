from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.cliniq_core import get_cliniq_response
from app.core.deps import get_current_user
from app.core.rbac import verificar_unidade_obrigatoria

router = APIRouter(tags=["medical-chat"])


# ===================== MODELOS DE ENTRADA =====================
class MedicalChatRequest(BaseModel):
    mensagem: str = Field(..., min_length=1, max_length=2000)
    historico: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    contexto_adicional: Optional[str] = Field(default=None, max_length=500)


class MedicalChatResponse(BaseModel):
    resposta: str
    fonte: str = "cliniq_core"
    historico_atualizado: Optional[List[Dict]] = None


# ===================== ENDPOINT PRINCIPAL =====================
@router.post("", response_model=MedicalChatResponse)
async def medical_chat(
    body: MedicalChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint robusto de chat clínico direto.
    Aceita histórico e garante formato correto para a IA.
    """
    verificar_unidade_obrigatoria(current_user)

    # ===================== LIMPEZA E VALIDAÇÃO DO HISTÓRICO =====================
    clean_history = []

    for msg in body.historico:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            role = str(msg["role"]).strip().lower()
            content = str(msg["content"]).strip()
            
            if role in ["user", "assistant", "system"] and content:
                clean_history.append({"role": role, "content": content})
        # Ignora mensagens mal formatadas (evita erro 400 da Groq)

    # Adiciona a nova mensagem do utilizador
    clean_history.append({"role": "user", "content": body.mensagem})

    # ===================== CONTEXTO ADICIONAL =====================
    if body.contexto_adicional:
        clean_history.insert(0, {
            "role": "system",
            "content": f"Contexto adicional fornecido pelo utilizador: {body.contexto_adicional}"
        })

    # ===================== CHAMADA AO CLINIQCORE =====================
    try:
        resposta_ia = await get_cliniq_response(clean_history)

        # Retorna também o histórico atualizado (útil para frontend)
        return MedicalChatResponse(
            resposta=resposta_ia,
            historico_atualizado=clean_history + [{"role": "assistant", "content": resposta_ia}]
        )

    except Exception as e:
        print(f"[MedicalChat] Erro crítico: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ocorreu um erro interno ao processar a consulta clínica. Tente novamente."
        )


# ===================== VERSÃO ALTERNATIVA (com histórico completo) =====================
@router.post("/with-history", response_model=MedicalChatResponse)
async def medical_chat_with_history(
    body: MedicalChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Versão alternativa que recebe o histórico completo e retorna apenas a nova resposta"""
    verificar_unidade_obrigatoria(current_user)

    if not body.mensagem.strip():
        raise HTTPException(status_code=400, detail="A mensagem não pode estar vazia")

    clean_history = []
    for msg in body.historico or []:
        if isinstance(msg, dict) and msg.get("role") in ["user", "assistant", "system"]:
            clean_history.append({
                "role": msg["role"],
                "content": str(msg.get("content", "")).strip()
            })

    clean_history.append({"role": "user", "content": body.mensagem})

    try:
        resposta = await get_cliniq_response(clean_history)
        return MedicalChatResponse(resposta=resposta)
    except Exception as e:
        print(f"[MedicalChat With History] Erro: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar a conversa")