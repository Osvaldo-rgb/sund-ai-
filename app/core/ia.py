from groq import AsyncGroq
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """És um assistente de suporte técnico interno.
Recebes tickets de problemas técnicos e respondes de forma clara e objectiva.
Fazes perguntas para ter uma ideia exacta sobre o problema.
Dás sempre passos concretos para resolver o problema.
Respondes em português."""

RESPOSTAS_FALLBACK = [
    "Estou com dificuldades técnicas de momento. Por favor tenta novamente em alguns minutos.",
    "O serviço de IA está temporariamente indisponível. Um agente humano irá responder brevemente.",
    "Erro temporário — a tua mensagem foi guardada e será respondida em breve.",
]

async def get_ai_response(historico: list[dict], tentativa: int = 0) -> str:
    try:
        client = AsyncGroq(api_key=GROQ_API_KEY)
        mensagens = [{"role": "system", "content": SYSTEM_PROMPT}] + historico

        response = await client.chat.completions.create(
            model=MODEL,
            messages=mensagens,
            max_tokens=1024
        )
        return response.choices[0].message.content

    except Exception as e:
        erro = str(e)

        # rate limit — espera e tenta de novo uma vez
        if "rate_limit" in erro and tentativa == 0:
            import asyncio
            await asyncio.sleep(5)
            return await get_ai_response(historico, tentativa=1)

        # fallback — resposta humana
        return RESPOSTAS_FALLBACK[tentativa % len(RESPOSTAS_FALLBACK)]