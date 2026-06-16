"""Entry point do TáNaMesa — Dominó Digital de Funções Inorgânicas."""
import tkinter as tk

import database as db
import session
from constants import BG
from screens import (TelaLogin, TelaCadastro, TelaInicio, TelaOpcoes,
                     TelaPerfil, TelaAjuda, TelaSobre, TelaJogo,
                     TelaRelatorios)


class Aplicativo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TáNaMesa")
        self.geometry("1180x720")
        self.minsize(1000, 720)
        self.configure(bg=BG)

        db.init_db()

        self._current = None
        self._mostrar("login")

    # ---------- router ---------------------------------------------------

    def _navegar(self, screen, *args, **kwargs):
        """Retorna uma função que troca para `screen` quando chamada."""
        return lambda: self._mostrar(screen, *args, **kwargs)

    def _logout(self):
        session.logout()
        self._mostrar("login")

    def _mostrar(self, screen, *args, **kwargs):
        if self._current is not None:
            self._current.place_forget()
            self._current.destroy()
            self._current = None

        nav = self._navegar
        if screen == "login":
            frame = TelaLogin(self, switch_to_register=nav("register"),
                                on_success=nav("home"))
        elif screen == "register":
            frame = TelaCadastro(self, switch_to_login=nav("login"))
        elif screen == "home":
            frame = TelaInicio(self, nav=nav, on_logout=self._logout)
        elif screen == "options":
            frame = TelaOpcoes(self, nav=nav, on_logout=self._logout)
        elif screen == "profile":
            frame = TelaPerfil(self, nav=nav, on_logout=self._logout)
        elif screen == "help":
            frame = TelaAjuda(self, nav=nav, on_logout=self._logout)
        elif screen == "about":
            frame = TelaSobre(self, nav=nav, on_logout=self._logout)
        elif screen == "report":
            frame = TelaRelatorios(self, nav=nav, on_logout=self._logout)
        elif screen == "game":
            (nivel,) = args
            frame = TelaJogo(self, nav=nav, on_logout=self._logout,
                               nivel=nivel)
        else:
            raise ValueError(f"Tela desconhecida: {screen}")

        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._current = frame


if __name__ == "__main__":
    Aplicativo().mainloop()
