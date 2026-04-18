import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.core.config import settings
from app.database import init_db
from app.routers import (
    auth_router,
    medical_chat_router,
    casos_clinicos_router,
    cliniq_router,
    unidades_saude_router
)
from app.core.limiter import limiter

logger = logging.getLogger("sundai")

app = FastAPI(
    title="SundAI",
    description="Plataforma de Inteligência Clínica Aumentada",
    version="0.1.0",
    docs_url="/docs",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Inicializa DB
init_db()

# ====================== ROUTERS ======================
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(medical_chat_router, prefix="/medical-chat", tags=["chat"])
app.include_router(casos_clinicos_router, prefix="/casos-clinicos", tags=["casos"])
app.include_router(cliniq_router, prefix="/cliniq", tags=["cliniq"])
app.include_router(unidades_saude_router, prefix="/unidades-saude", tags=["unidades"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": "SundAI",
        "version": "0.1.0",
        "environment": "production",
        "database": "PostgreSQL"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.is_development
    )