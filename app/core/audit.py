from sqlalchemy.orm import Session
from app.models.db_models import AuditLog

def registar(
    db: Session,
    acao: str,
    user_email: str = None,
    empresa_id: int = None,
    detalhe: str = None,
    ip: str = None
):
    log = AuditLog(
        acao=acao,
        user_email=user_email,
        empresa_id=empresa_id,
        detalhe=detalhe,
        ip=ip
    )
    db.add(log)
    db.commit()