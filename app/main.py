import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.database import init_db
from app.routers import auth, unidades_saude, casos_clinicos, cliniq,medical_chat
from app.core.limiter import limiter

# =========================
# CONFIGURAÇÃO DE LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),  # Console
        logging.FileHandler("sundai.log", encoding="utf-8")  # Arquivo de log
    ]
)

logger = logging.getLogger("sundai")

# =========================
# CRIAÇÃO DA APLICAÇÃO
# =========================

app = FastAPI(
    title="SundAI",
    description="Plataforma de Inteligência Clínica Aumentada para Profissionais de Saúde",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# =========================
# MIDDLEWARES DE SEGURANÇA E LOGGING
# =========================

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS (Mais seguro que antes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                    # TODO: Restringir em produção (ex: ["https://sundai.ao"])
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"]
)

# Middleware personalizado para Logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    start_time = time.time()
    
    # Gera um ID único para rastrear a requisição
    request_id = f"req_{int(start_time * 1000)}"
    request.state.request_id = request_id

    logger.info(f"→ {request.method} {request.url.path} | RequestID: {request_id} | Client: {request.client.host}")

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"← {request.method} {request.url.path} | Status: {response.status_code} | "
            f"Time: {process_time:.2f}ms | RequestID: {request_id}"
        )
        return response
    except Exception as exc:
        logger.error(f"✘ Erro na requisição {request.url.path} | RequestID: {request_id} | Erro: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno no servidor", "request_id": request_id}
        )


# =========================
# INICIALIZAÇÃO DA BASE DE DADOS
# =========================

init_db()

# =========================
# INCLUSÃO DOS ROUTERS
# =========================

app.include_router(auth.router)
app.include_router(unidades_saude.router)
app.include_router(casos_clinicos.router)
app.include_router(cliniq.router)
app.include_router(medical_chat.router)

# =========================
# HEALTH CHECK + INFO
# =========================

@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "application": "SundAI",
        "version": "0.1.0",
        "environment": "development"
    }


@app.get("/info", tags=["health"])
async def app_info():
    return {
        "title": "SundAI",
        "version": "0.1.0",
        "description": "Inteligência Clínica Aumentada",
        "logging_enabled": True,
        "rate_limiting_enabled": True
    }


# =========================
# EXECUÇÃO DIRETA (opcional)
# =========================

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando SundAI...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )