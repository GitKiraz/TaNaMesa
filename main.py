"""Entry point do TáNaMesa — Dominó Digital de Funções Inorgânicas."""
import tkinter as tk

import database as db
import session
from constants import BG
from screens import (LoginScreen, RegisterScreen, HomeScreen, OptionsScreen,
                     ProfileScreen, HelpScreen, AboutScreen, GameScreen,
                     ReportScreen)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TáNaMesa")
        self.geometry("1180x720")
        self.minsize(1000, 720)
        self.configure(bg=BG)

        db.init_db()

        self._current = None
        self._show("login")

    # ---------- router ---------------------------------------------------

    def _nav(self, screen, *args, **kwargs):
        """Retorna uma função que troca para `screen` quando chamada."""
        return lambda: self._show(screen, *args, **kwargs)

    def _logout(self):
        session.logout()
        self._show("login")

    def _show(self, screen, *args, **kwargs):
        if self._current is not None:
            self._current.place_forget()
            self._current.destroy()
            self._current = None

        nav = self._nav
        if screen == "login":
            frame = LoginScreen(self, switch_to_register=nav("register"),
                                on_success=nav("home"))
        elif screen == "register":
            frame = RegisterScreen(self, switch_to_login=nav("login"))
        elif screen == "home":
            frame = HomeScreen(self, nav=nav, on_logout=self._logout)
        elif screen == "options":
            frame = OptionsScreen(self, nav=nav, on_logout=self._logout)
        elif screen == "profile":
            frame = ProfileScreen(self, nav=nav, on_logout=self._logout)
        elif screen == "help":
            frame = HelpScreen(self, nav=nav, on_logout=self._logout)
        elif screen == "about":
            frame = AboutScreen(self, nav=nav, on_logout=self._logout)
        elif screen == "report":
            frame = ReportScreen(self, nav=nav, on_logout=self._logout)
        elif screen == "game":
            (nivel,) = args
            frame = GameScreen(self, nav=nav, on_logout=self._logout,
                               nivel=nivel)
        else:
            raise ValueError(f"Tela desconhecida: {screen}")

        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._current = frame


if __name__ == "__main__":
    App().mainloop()
