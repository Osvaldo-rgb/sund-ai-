import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers.auth import router as auth_router
from app.routers.medical_chat import router as medical_chat_router

app = FastAPI(title="SundAI", version="0.1.0", docs_url="/docs")

# CORS - Versão mais permissiva possível
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # permite qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

init_db()

# Só os routers que estamos a usar agora
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(medical_chat_router, prefix="/medical-chat", tags=["chat"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "SundAI está online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))