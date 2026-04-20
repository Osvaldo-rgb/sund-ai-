from groq import AsyncGroq
from dotenv import load_dotenv
import os
import asyncio
from typing import List, Dict, Optional

from app.models.db_models import CasoClinico

load_dotenv()

# ===================== CONFIGURAÇÃO =====================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print(" AVISO: GROQ_API_KEY não encontrada no .env")

# Usa um modelo bom e equilibrado (podes mudar se quiseres)
MODEL = "llama-3.1-8b-instant"      # Bom para raciocínio clínico
# MODEL = "llama-3.1-8b-instant"       # Mais rápido e barato (para testes)

SYSTEM_PROMPT_CLINICO = """
Você é um assistente clínico experiente, direto e prático.
Responda de forma clara, concisa e natural, como um médico experiente faria numa conversa rápida.
- Seja objetivo e vá direto ao ponto.
- Use linguagem simples e profissional.
- Evite listas longas, asteriscos, negrito ou formatação.
- Responda em português de Angola (português africano natural).
- Máximo 3-4 frases por resposta, a menos que seja realmente necessário mais.
- Nunca use ** ou * no texto.

Regras importantes que deves SEMPRE seguir:
- Responde sempre em português correto, claro, profissional e empático.
- Faz perguntas relevantes para esclarecer o quadro clínico (sintomas, duração, sinais vitais, antecedentes, etc.).
- Sugere diagnósticos diferenciais ordenados por probabilidade aproximada.
- Fornece passos concretos de investigação, manejo inicial e critérios de referenciação.
- Dá especial atenção a doenças comuns em Angola: malária, tuberculose, cólera, HIV, anemias, desnutrição, infeções respiratórias e tropicais.
- Nunca dás um diagnóstico definitivo — reforça sempre que é uma sugestão de apoio ao clínico responsável.
- Prioriza a segurança do paciente e boas práticas baseadas em evidência.
- Mantém um tom colaborativo e respeitoso.

Responde de forma estruturada quando possível (ex: Avaliação, Perguntas, Recomendações)."""

RESPOSTAS_FALLBACK = [
    "Estou com dificuldades técnicas neste momento. Por favor, tenta novamente em alguns minutos.",
    "O serviço de apoio clínico está temporariamente indisponível. Tenta novamente brevemente.",
    "Erro temporário — a tua mensagem foi registada e será respondida em breve."
]


async def call_groq(mensagens: List[Dict]) -> str:
    """Chama a API da Groq"""
    if not GROQ_API_KEY:
        return "Erro: Chave da API Groq não configurada (GROQ_API_KEY)."

    client = AsyncGroq(api_key=GROQ_API_KEY)
    
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=mensagens,
            max_tokens=1024,
            temperature=0.3,      # Mais determinístico para contexto médico
            top_p=0.95,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro na chamada Groq: {e}")
        raise


async def get_cliniq_response(
    historico: List[Dict],
    caso: Optional[CasoClinico] = None
) -> str:
    """
    Motor principal do SundAI CliniqCore.
    
    Args:
        historico: Lista de mensagens no formato [{"role": "user"|"assistant", "content": "..."}]
        caso: Objeto CasoClinico (opcional, para contexto futuro)
    """
    try:
        # Monta as mensagens para a IA
        mensagens = [
            {"role": "system", "content": SYSTEM_PROMPT_CLINICO}
        ] + historico

        # Chama a Groq
        resposta = await call_groq(mensagens)
        return resposta

    except Exception as e:
        print(f"[CliniqCore] Erro geral: {e}")

        # Tentativa de recuperação em caso de rate limit
        if "rate_limit" in str(e).lower() or "429" in str(e):
            print("Rate limit detectado. Aguardando 8 segundos...")
            await asyncio.sleep(8)
            try:
                return await call_groq(mensagens)
            except:
                pass

        # Retorna mensagem de fallback
        return RESPOSTAS_FALLBACK[0]


# Função auxiliar para ingestão (desativada por enquanto)
async def ingestir_documento_medico(texto: str, fonte: str, **kwargs):
    """Mantida para compatibilidade futura com RAG"""
    print(f"⚠️  Ingestão de documentos desativada. Texto recebido de: {fonte}")
    return None