"""Layout base de tela autenticada: sidebar + área de conteúdo."""
import tkinter as tk

import session
from constants import BG
from widgets import make_sidebar


def itens_sidebar(nav):
    """Itens padrão do menu lateral. Adapta para professor."""
    base = [
        ("Iniciar nova partida", nav("options")),
        ("Opções",               nav("options")),
        ("Perfil",               nav("profile")),
        ("Ajuda",                nav("help")),
        ("Sobre",                nav("about")),
    ]
    if session.eh_professor():
        base.insert(2, ("Relatórios", nav("report")))
    return base


class AuthScreen(tk.Frame):
    """
    Esqueleto de tela autenticada.
    Subclasses implementam _content(parent) que recebe o frame da
    área central (conteúdo principal à direita da sidebar).
    """
    ativo_sidebar = None

    def __init__(self, master, nav, on_logout):
        super().__init__(master, bg=BG)
        self.nav = nav
        self.on_logout = on_logout

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        make_sidebar(body, itens_sidebar(nav),
                     ativo=self.ativo_sidebar,
                     on_logout=on_logout)

        content = tk.Frame(body, bg=BG)
        content.pack(side="left", fill="both", expand=True)

        self._content(content)

    def _content(self, parent):
        raise NotImplementedError
