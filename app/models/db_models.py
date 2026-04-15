from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from datetime import datetime, timezone
from app.database import Base

# ==================== UNIDADES DE SAÚDE ====================
class UnidadeSaude(Base):
    __tablename__ = "unidades_saude"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)          # hospital, clinica, posto_saude, farmacia, etc.
    dominio = Column(String, unique=True, nullable=False)
    provincia = Column(String, nullable=False)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# ==================== PROFISSIONAIS DE SAÚDE ====================
class ProfissionalSaude(Base):
    __tablename__ = "profissionais_saude"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nome_completo = Column(String, nullable=False)
    especialidade = Column(String, nullable=True)
    numero_licenca = Column(String, unique=True, nullable=True)
    role = Column(String, default="medico")        # medico, enfermeiro, admin_clinica, superadmin
    unidade_saude_id = Column(Integer, ForeignKey("unidades_saude.id"), nullable=True)

# ==================== PACIENTES (anonimizados) ====================
class Paciente(Base):
    __tablename__ = "pacientes"
    id = Column(Integer, primary_key=True, index=True)
    codigo_anonimo = Column(String, unique=True, nullable=False)   # ex: PAT-20260414-78392
    idade = Column(Integer, nullable=True)
    sexo = Column(String(10), nullable=True)                       # M, F, Outro
    unidade_saude_id = Column(Integer, ForeignKey("unidades_saude.id"), nullable=True)

# ==================== CASOS CLÍNICOS ====================
class CasoClinico(Base):
    __tablename__ = "casos_clinicos"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text, nullable=False)
    prioridade = Column(String, default="normal")      # baixa, normal, urgente, emergencia
    unidade_saude_id = Column(Integer, ForeignKey("unidades_saude.id"), nullable=False)
    criado_por = Column(Integer, ForeignKey("profissionais_saude.id"), nullable=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=True)
    diagnostico_sugerido = Column(String, nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

# ==================== MENSAGENS CLÍNICAS ====================
class MensagemClinica(Base):
    __tablename__ = "mensagens_clinicas"
    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos_clinicos.id"), nullable=False)
    role = Column(String, nullable=False)              # user, assistant, system
    content = Column(Text, nullable=False)
    citacoes = Column(JSON, nullable=True)             # fontes do RAG
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# ==================== TOKEN BLACKLIST (mantido) ====================
class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))