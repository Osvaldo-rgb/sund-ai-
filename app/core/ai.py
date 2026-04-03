from groq import AsyncGroq
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY ="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"
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """És um assistente de suporte técnico interno.
Recebes tickets de problemas técnicos e respondes de forma clara e objectiva.
Fazes perguntas para ter uma ideia exacta sobre o problema.
Dás sempre passos concretos para resolver o problema.
Respondes em português."""

async def get_ai_response(historico: list[dict]) -> str:
    client = AsyncGroq(api_key=GROQ_API_KEY)
    mensagens = [{"role": "system", "content": SYSTEM_PROMPT}] + historico
    response = await client.chat.completions.create(
        model=MODEL,
        messages=mensagens,
        max_tokens=1024
    )
    return response.choices[0].message.content