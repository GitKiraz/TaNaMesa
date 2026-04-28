import tkinter as tk
from constants import BG
from screens import LoginScreen, RegisterScreen


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TáNaMesa")

        self.resizable(True, True)


        self.state("normal")

        self.geometry("1180x720")
        self.minsize(1000, 720)

        self.configure(bg=BG)

        self._login = LoginScreen(self, self._show_register)
        self._register = RegisterScreen(self, self._show_login)

        self._show_login()

    def _show_login(self):
        self._register.place_forget()
        self._login.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _show_register(self):
        self._login.place_forget()
        self._register.place(relx=0, rely=0, relwidth=1, relheight=1)


if __name__ == "__main__":
    App().mainloop()