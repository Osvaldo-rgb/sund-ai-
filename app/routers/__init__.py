# app/routers/__init__.py

# app/routers/__init__.py

# Importamos diretamente os routers sem alias complicados
from .auth import router as auth_router
from .medical_chat import router as medical_chat_router

# Importa os outros apenas se existirem (para evitar erros)
try:
    from .casos_clinicos import router as casos_clinicos_router
except ImportError:
    casos_clinicos_router = None

try:
    from .cliniq import router as cliniq_router
except ImportError:
    cliniq_router = None

try:
    from .unidades_saude import router as unidades_saude_router
except ImportError:
    unidades_saude_router = None


__all__ = [
    "auth_router",
    "medical_chat_router",
    "casos_clinicos_router",
    "cliniq_router",
    "unidades_saude_router"
]