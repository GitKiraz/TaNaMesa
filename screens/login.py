import tkinter as tk
from tkinter import messagebox
from constants import BG, CARD_BG, RED, LABEL_FG, LINK_FG
from widgets import make_topbar, make_card, entry_field, tipo_usuario, action_button, link_label


class LoginScreen(tk.Frame):
    def __init__(self, master, switch_to_register):
        super().__init__(master, bg=BG)
        self.switch = switch_to_register
        self._build()

    def _build(self):
        make_topbar(self, "Tela de login")

        card = make_card(self)

        tk.Label(card, text="TáNaMesa", bg=CARD_BG, fg=RED,
                 font=("Georgia", 24, "bold")).pack(pady=(0, 6))

        self.email = entry_field(card, "Email")
        self.senha = entry_field(card, "Senha", show="•")

        tk.Label(card, text="Esqueci minha senha", bg=CARD_BG,
                 fg=LINK_FG, font=("Georgia", 8, "underline"),
                 cursor="hand2").pack(anchor="e", pady=(2, 0))

        self.tipo = tipo_usuario(card)

        action_button(card, "Entrar", self._entrar)

        tk.Frame(card, bg=CARD_BG, height=1).pack(fill="x", pady=6)

        tk.Label(card, text="Não possui cadastro?", bg=CARD_BG,
                 fg=LABEL_FG, font=("Georgia", 10)).pack()
        link_label(card, "Cadastre-se", self.switch)

    def _entrar(self):
        email = self.email.get().strip()
        senha = self.senha.get().strip()
        tipo  = self.tipo.get()
        if not email or not senha:
            messagebox.showwarning("Atenção", "Preencha email e senha.")
            return
        if not tipo:
            messagebox.showwarning("Atenção", "Selecione o tipo de usuário.")
            return
        messagebox.showinfo("Login", f"Bem-vindo!\nEmail: {email}\nTipo: {tipo}")
