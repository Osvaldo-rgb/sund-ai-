import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings

# ===================== DATABASE ENGINE =====================
if settings.DATABASE_URL.startswith("sqlite"):
    # Configuração para SQLite (desenvolvimento)
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
        echo=False
    )
else:
    # Configuração para PostgreSQL (produção)
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,        # evita conexões mortas
        pool_size=10,
        max_overflow=20,
        echo=False                 # muda para True se quiseres ver as queries
    )

# ===================== SESSION =====================
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# ===================== BASE =====================
class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Cria todas as tabelas"""
    from app.models.db_models import Base
    Base.metadata.create_all(bind=engine)
    print("Base de dados inicializada com sucesso!")


def drop_db():
    """Apaga todas as tabelas (cuidado!)"""
    from app.models.db_models import Base
    Base.metadata.drop_all(bind=engine)
    print(" Todas as tabelas foram removidas.")