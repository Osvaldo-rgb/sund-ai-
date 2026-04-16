import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    # =========================
    # AMBIENTE
    # =========================
    ENVIRONMENT: Literal["development", "production", "testing"] = "development"

    # =========================
    # BASE DE DADOS
    # =========================
    DATABASE_URL: str = "sqlite:///./sundai.db"   # fallback para desenvolvimento

    # =========================
    # SEGURANÇA
    # =========================
    SECRET_KEY: str = "sundai-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # =========================
    # IA (Groq)
    # =========================
    GROQ_API_KEY: str | None = None
    MODEL_NAME: str = "llama-3.1-8b-instant"

    # =========================
    # CORS
    # =========================
    ALLOWED_ORIGINS: list[str] = ["*"]   # Em produção, restringir

    # =========================
    # LOGGING
    # =========================
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = True

    # =========================
    # CONFIGURAÇÃO PYDANTIC
    # =========================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # =========================
    # PROPRIEDADES ÚTEIS
    # =========================
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"

    def get_cors_origins(self) -> list[str]:
        """Retorna origens permitidas conforme o ambiente"""
        if self.is_production:
            return [
                "https://sundai.ao",
                "https://app.sundai.ao",
                "http://localhost:3000",   # frontend local
                "http://127.0.0.1:3000"
            ]
        return self.ALLOWED_ORIGINS


# Instância global
settings = Settings()