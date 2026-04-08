from fastapi import HTTPException

PERMISSOES = {
    "superadmin": ["ver_tudo", "gerir_empresas", "gerir_users", "ver_tickets", "criar_tickets"],
    "admin":      ["gerir_users", "ver_tickets", "criar_tickets", "ver_relatorios"],
    "agente":     ["ver_tickets", "criar_tickets"],
}

def verificar_permissao(user: dict, permissao: str):
    role = user.get("role", "agente")
    if permissao not in PERMISSOES.get(role, []):
        raise HTTPException(
            status_code=403,
            detail=f"Sem permissão — precisas de '{permissao}'"
        )

def verificar_empresa(user: dict, empresa_id: int):
    role = user.get("role")
    user_empresa = user.get("empresa_id")

    # superadmin vê tudo
    if role == "superadmin":
        return

    # outros só vêem a sua empresa
    if user_empresa != empresa_id:
        raise HTTPException(
            status_code=403,
            detail="Sem acesso a esta empresa"
        )