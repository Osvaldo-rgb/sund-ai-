import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db

# Importações diretas (mais estáveis)
from app.routers.auth import router as auth_router
from app.routers.medical_chat import router as medical_chat_router
from app.routers.cliniq import router as cliniq_router
from app.routers.casos_clinicos import router as casos_clinicos_router
from app.routers.unidades_saude import router as unidades_saude_router

app = FastAPI(title="SundAI", version="0.1.0", docs_url="/docs")

# CORS ultra-permissivo (resolve o erro que tinhas no frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# Routers

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(medical_chat_router, prefix="/medical-chat", tags=["chat"])
app.include_router(casos_clinicos_router, prefix="/casos-clinicos", tags=["casos"])
app.include_router(cliniq_router, prefix="/cliniq", tags=["cliniq"])
app.include_router(unidades_saude_router, prefix="/unidades-saude", tags=["unidades"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))