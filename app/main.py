import logging
import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.core.config import settings
from app.database import init_db
from app.routers import auth, unidades_saude, casos_clinicos, cliniq, medical_chat
from app.core.limiter import limiter

# =========================
# LOGGING
# =========================

log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

logging.basicConfig(
    level=log_level,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("sundai.log", encoding="utf-8") if getattr(settings, 'LOG_TO_FILE', False) else None
    ]
)

logger = logging.getLogger("sundai")
logger.info(f"🚀 Iniciando SundAI v0.1.0")
logger.info(f"Ambiente: {settings.ENVIRONMENT.upper()}")
logger.info(f"Database: {'PostgreSQL' if 'postgres' in (settings.DATABASE_URL or '').lower() else 'SQLite'}")

# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="SundAI",
    description="Plataforma de Inteligência Clínica Aumentada — Salus Intellegens",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS (permite tudo durante desenvolvimento/produção inicial)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de Logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = f"req_{int(start_time * 1000)}"
    request.state.request_id = request_id

    logger.info(f"→ {request.method} {request.url.path} | ID: {request_id}")

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(f"← {request.method} {request.url.path} | Status: {response.status_code} | {process_time:.2f}ms | ID: {request_id}")
        return response
    except Exception as exc:
        logger.error(f"Erro na requisição {request.url.path} | ID: {request_id}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno no servidor", "request_id": request_id}
        )

# =========================
# INICIALIZAÇÃO
# =========================

init_db()

# ====================== ROUTERS ======================
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(unidades_saude.router, prefix="/unidades-saude", tags=["unidades"])
app.include_router(casos_clinicos.router, prefix="/casos-clinicos", tags=["casos"])
app.include_router(cliniq.router, prefix="/cliniq", tags=["cliniq"])
app.include_router(medical_chat.router, prefix="/medical-chat", tags=["chat"])

# Health & Info
@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "application": "SundAI",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "database": "PostgreSQL" if "postgres" in (settings.DATABASE_URL or "").lower() else "SQLite"
    }

@app.get("/info", tags=["health"])
async def app_info():
    return {
        "title": "SundAI",
        "version": "0.1.0",
        "description": "Salus Intellegens — Compreendendo cada vida para cuidar melhor",
        "environment": settings.ENVIRONMENT
    }

# =========================
# EXECUÇÃO
# =========================

if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor Uvicorn...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.is_development
    )