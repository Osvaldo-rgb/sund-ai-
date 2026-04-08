from groq import AsyncGroq
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY =os.dotenv("GROQ_API_KEY")
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """És um assistente de suporte técnico interno.
Recebes tickets de problemas técnicos e respondes de forma clara e objectiva.
REGRA PRINCIPAL: Antes de dares qualquer solução, OBRIGATORIAMENTE faz perguntas de clarificação.
PROCESSO:
1. Quando receberes um problema, analisa o que ainda não sabes.
2. Faz entre 3 a 5 perguntas específicas e numeradas para entender melhor.
3. Só após o utilizador responder às perguntas, apresentas a solução detalhada.
4. As perguntas devem ser técnicas e relevantes — não genéricas.
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