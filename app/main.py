from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.database import engine, Base
from app.routers import tickets, auth, chat, empresas
from app.core.limiter import limiter  # ✅ IMPORT CORRETO

# cria tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FridAI")

# liga limiter ao app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS (⚠️ em produção, restringir)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(auth.router)
app.include_router(empresas.router)
app.include_router(chat.router)
app.include_router(tickets.router)

