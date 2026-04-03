import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "phi"

SYSTEM_PROMPT = """És um assistente de suporte técnico interno.
Recebes tickets de problemas técnicos e respondes de forma clara e objectiva.
Fases perguntas para ter uma ideia exata sobre o problema.
Dás sempre passos concretos para resolver o problema.
Respondes em português."""

import httpx

xai_URL = "http://localhost:11434/api/chat"
MODEL = "phi"

SYSTEM_PROMPT = """És um assistente de suporte técnico interno.
Recebes tickets de problemas técnicos e respondes de forma clara e objectiva.
Fazes perguntas para ter uma ideia exata sobre o problema.
Dás sempre passos concretos para resolver o problema.
Respondes em português."""

async def get_ai_response(historico: list[dict]) -> str:
    mensagens = [{"role": "system", "content": SYSTEM_PROMPT}] + historico

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(OLLAMA_URL, json={
            "model": MODEL,
            "messages": mensagens,
            "stream": False
        })

        data = response.json()
        print("OLLAMA:", data)

        # 👇 lógica correta
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"]
        elif "response" in data:
            return data["response"]
        elif "error" in data:
            return f"Erro do Ollama: {data['error']}"
        else:
            return f"Resposta inesperada: {data}"