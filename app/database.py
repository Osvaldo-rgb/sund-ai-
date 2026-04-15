import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

# =========================
# CONFIGURAÇÃO DA BASE DE DADOS
# =========================

DATABASE_URL = os.getenv("DATABASE_URL")

# Configuração para desenvolvimento (SQLite) ou produção (PostgreSQL, etc.)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./sundai.db"
    
    # Configurações específicas para SQLite
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},   # Necessário para SQLite + FastAPI
        poolclass=StaticPool,                        # Melhor performance em dev
        echo=False                                   # Muda para True se quiseres ver as queries SQL
    )
else:
    # Para bases de dados como PostgreSQL/MySQL em produção
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,          # Evita conexões mortas
        pool_size=10,
        max_overflow=20,
        echo=False
    )

# =========================
# SESSION FACTORY
# =========================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False   # Recomendado quando se usa Pydantic + SQLAlchemy
)

# =========================
# BASE PARA MODELOS ORM
# =========================

class Base(DeclarativeBase):
    """Base comum para todos os modelos SQLAlchemy"""
    pass


# =========================
# DEPENDENCY PARA FASTAPI
# =========================

def get_db():
    """
    Dependency para injetar sessão de base de dados nos endpoints.
    Garante que a sessão é sempre fechada após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Função auxiliar útil durante desenvolvimento
def init_db():
    """Cria todas as tabelas (útil para reset durante dev)"""
    from app.models.db_models import Base  # Import aqui para evitar circular imports
    Base.metadata.create_all(bind=engine)
    print("✅ Base de dados inicializada com sucesso!")


# Opcional: Função para dropar todas as tabelas (cuidado em produção!)
def drop_db():
    from app.models.db_models import Base
    Base.metadata.drop_all(bind=engine)
    print("🗑️  Todas as tabelas foram removidas.")