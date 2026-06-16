"""Layout base de tela autenticada: sidebar + área de conteúdo."""
import tkinter as tk

import session
from constants import BG
from widgets import criar_barra_lateral


def itens_barra_lateral(nav):
    """Itens padrão do menu lateral. Adapta para professor."""
    base = [
        ("Iniciar nova partida", nav("home")),
        ("Opções",               nav("options")),
        ("Perfil",               nav("profile")),
        ("Ajuda",                nav("help")),
        ("Sobre",                nav("about")),
    ]
    if session.eh_professor():
        base.insert(2, ("Relatórios", nav("report")))
    return base


class TelaAutenticada(tk.Frame):
    """
    Esqueleto de tela autenticada.
    Subclasses implementam _conteudo(parent) que recebe o frame da
    área central (conteúdo principal à direita da sidebar).
    """
    ativo_sidebar = None

    def __init__(self, master, nav, on_logout):
        super().__init__(master, bg=BG)
        self.nav = nav
        self.on_logout = on_logout

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        criar_barra_lateral(body, itens_barra_lateral(nav),
                     ativo=self.ativo_sidebar,
                     on_logout=on_logout)

        content = tk.Frame(body, bg=BG)
        content.pack(side="left", fill="both", expand=True)

        self._conteudo(content)

    def _conteudo(self, parent):
        raise NotImplementedError
