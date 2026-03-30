from fastapi import FastAPI
from app.database import engine,Base
from app.routers import tickets,auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FridAI")
app.include_router(tickets.router)
app.include_router(auth.router)