from groq import AsyncGroq
from dotenv import load_dotenv
import os
import asyncio
from typing import List, Dict

from app.models.db_models import CasoClinico

load_dotenv()
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.db_models import CasoClinico
from app.core.deps import get_current_user
from app.core.rbac import verificar_permissao, verificar_unidade_obrigatoria   # ← CORRIGIDO

router = APIRouter(tags=["casos-clinicos"])


class CasoClinicoCreate(BaseModel):
    titulo: str
    descricao: str
    prioridade: str = "normal"          # baixa, normal, urgente, emergencia
    paciente_id: int | None = None


@router.post("/", status_code=201)
def criar_caso_clinico(
    caso: CasoClinicoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verificações de segurança
    verificar_unidade_obrigatoria(current_user)                    # ← ALTERADO
    verificar_permissao(current_user, "criar_casos")               # melhor que "criar_tickets"

    novo_caso = CasoClinico(
        titulo=caso.titulo,
        descricao=caso.descricao,
        prioridade=caso.prioridade,
        unidade_saude_id=current_user["unidade_saude_id"],
        criado_por=current_user.get("id"),
        paciente_id=caso.paciente_id
    )

    db.add(novo_caso)
    db.commit()
    db.refresh(novo_caso)

    return {
        "id": novo_caso.id,
        "titulo": novo_caso.titulo,
        "prioridade": novo_caso.prioridade,
        "mensagem": "Caso clínico criado com sucesso"
    }


@router.get("/")
def listar_casos_clinicos(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    verificar_unidade_obrigatoria(current_user)
    verificar_permissao(current_user, "ver_casos")

    query = db.query(CasoClinico)

    if current_user["role"] == "superadmin":
        return query.all()

    # Filtra apenas os casos da unidade do utilizador
    return query.filter(
        CasoClinico.unidade_saude_id == current_user["unidade_saude_id"]
    ).all()


@router.get("/{caso_id}")
def obter_caso_clinico(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    caso = db.query(CasoClinico).filter(CasoClinico.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso clínico não encontrado")

    if current_user.get("role") != "superadmin":
        if caso.unidade_saude_id != current_user.get("unidade_saude_id"):
            raise HTTPException(status_code=403, detail="Sem acesso a este caso")

    return caso
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.1-70b-versatile"   # ou "llama-3.1-8b-instant" se quiseres mais rápido

SYSTEM_PROMPT_CLINICO = """És um assistente clínico aumentado (CliniqCore) para profissionais de saúde em Angola.

Regras obrigatórias:
- Responde SEMPRE em português correto, claro e profissional.
- Faz perguntas clínicas relevantes para refinar o diagnóstico (sintomas, duração, sinais vitais, antecedentes, etc.).
- Sugere diagnósticos diferenciais com ordem de probabilidade aproximada.
- Dá sempre passos concretos de investigação, manejo inicial e critérios de referenciação.
- Tem atenção especial a patologias comuns em Angola: malária, tuberculose, cólera, HIV, desnutrição, etc.
- NUNCA dá um diagnóstico definitivo — reforça sempre que é uma sugestão de apoio ao clínico responsável.
- Prioriza segurança do paciente."""

RESPOSTAS_FALLBACK = [
    "Estou com dificuldades técnicas neste momento. Por favor, tenta novamente em alguns minutos.",
    "O serviço de apoio clínico está temporariamente indisponível. Tenta novamente brevemente.",
    "Erro temporário — a tua mensagem foi guardada e será respondida em breve."
]

async def call_groq(mensagens: List[Dict]) -> str:
    client = AsyncGroq(api_key=GROQ_API_KEY)
    response = await client.chat.completions.create(
        model=MODEL,
        messages=mensagens,
        max_tokens=1024,
        temperature=0.3,
    )
    return response.choices[0].message.content


async def get_cliniq_response(
    historico: List[Dict],
    caso: CasoClinico = None
) -> str:
    """
    Motor principal do SundAI CliniqCore (versão simplificada sem RAG local).
    """
    try:
        mensagens = [
            {"role": "system", "content": SYSTEM_PROMPT_CLINICO}
        ] + historico

        return await call_groq(mensagens)

    except Exception as e:
        print(f"Erro no CliniqCore (Groq): {e}")
        
        # Tentativa de rate limit
        if "rate_limit" in str(e).lower() and "429" in str(e):
            await asyncio.sleep(8)
            try:
                return await call_groq(mensagens)
            except:
                pass
        
        # Fallback
        return RESPOSTAS_FALLBACK[0]


# Função auxiliar desativada por enquanto (RAG será adicionado mais tarde)
async def ingestir_documento_medico(*args, **kwargs):
    print("⚠️  Ingestão de documentos desativada nesta fase (sem Ollama/Chroma)")
    return None