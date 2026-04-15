from groq import AsyncGroq
from dotenv import load_dotenv
import os
import asyncio
from typing import List, Dict

from app.models.db_models import CasoClinico

load_dotenv()

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