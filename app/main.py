import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.core.config import settings
from app.database import init_db

# Imports diretos (mais confiável)
from app.routers.auth import router as auth_router
from app.routers.medical_chat import router as medical_chat_router

logger = logging.getLogger("sundai")

app = FastAPI(
    title="SundAI",
    description="Plataforma de Inteligência Clínica Aumentada",
    version="0.1.0",
    docs_url="/docs",
)

# CORS forte (resolve o erro que estás a ver)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Temporariamente aberto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Inicializa banco
init_db()

# ====================== ROUTERS ======================
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(medical_chat_router, prefix="/medical-chat", tags=["chat"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": "SundAI",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )