from fastapi import HTTPException

# Permissões adaptadas ao contexto clínico
PERMISSOES = {
    "superadmin": [
        "ver_tudo",
        "gerir_unidades",
        "gerir_profissionais",
        "ver_casos",
        "criar_casos",
        "gerir_casos"
    ],
    "admin_clinica": [
        "gerir_profissionais",
        "ver_casos",
        "criar_casos",
        "gerir_casos",
        "ver_relatorios"
    ],
    "medico": [
        "ver_casos",
        "criar_casos"
    ],
    "enfermeiro": [
        "ver_casos",
        "criar_casos"
    ]
}

def verificar_permissao(user: dict, permissao: str):
    role = user.get("role", "medico")
    if permissao not in PERMISSOES.get(role, []):
        raise HTTPException(
            status_code=403,
            detail=f"Sem permissão — precisas de '{permissao}' para esta ação"
        )

def verificar_unidade_saude(user: dict, unidade_id: int):
    """Verifica se o utilizador tem acesso à unidade de saúde"""
    if user.get("role") == "superadmin":
        return True
    
    if user.get("unidade_saude_id") != unidade_id:
        raise HTTPException(
            status_code=403,
            detail="Sem acesso a esta unidade de saúde"
        )
    return True

def verificar_unidade_obrigatoria(user: dict):
    """Verifica se o utilizador tem uma unidade associada (exceto superadmin)"""
    if user.get("unidade_saude_id") is None and user.get("role") != "superadmin":
        raise HTTPException(
            status_code=403,
            detail="Conta sem unidade de saúde associada — contacta o administrador"
        )