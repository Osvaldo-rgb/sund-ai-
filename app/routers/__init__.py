# app/routers/__init__.py

from .auth import router as auth_router
from .medical_chat import router as medical_chat_router
from .casos_clinicos import router as casos_clinicos_router
from .cliniq import router as cliniq_router
from .unidades_saude import router as unidades_saude_router

__all__ = [
    "auth_router",
    "medical_chat_router",
    "casos_clinicos_router",
    "cliniq_router",
    "unidades_saude_router"
]