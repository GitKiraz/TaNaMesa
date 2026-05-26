"""Estado de sessão do usuário autenticado (em memória)."""

_usuario = None


def login(usuario_dict):
    global _usuario
    _usuario = usuario_dict


def logout():
    global _usuario
    _usuario = None


def atual():
    return _usuario


def autenticado():
    return _usuario is not None


def eh_professor():
    return _usuario is not None and _usuario.get("tipo_usuario") == "professor"
