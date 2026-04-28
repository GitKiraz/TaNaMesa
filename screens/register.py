import tkinter as tk
from tkinter import messagebox
from constants import BG, CARD_BG, RED, LABEL_FG
from widgets import make_topbar, make_card, entry_field, tipo_usuario, action_button, link_label


class RegisterScreen(tk.Frame):
    def __init__(self, master, switch_to_login):
        super().__init__(master, bg=BG)
        self.switch = switch_to_login
        self._build()

    def _build(self):
        make_topbar(self, "Tela de cadastro")

        card = make_card(self)

        tk.Label(card, text="TáNaMesa", bg=CARD_BG, fg=RED,
                 font=("Georgia", 24, "bold")).pack(pady=(0, 6))

        self.nome     = entry_field(card, "Nome")
        self.nickname = entry_field(card, "Nickname")
        self.email    = entry_field(card, "Email")
        self.senha    = entry_field(card, "Senha", show="•")
        self.confirm  = entry_field(card, "Confirmar senha", show="•")

        self.tipo = tipo_usuario(card)

        action_button(card, "Cadastrar", self._cadastrar)

        tk.Frame(card, bg=CARD_BG, height=1).pack(fill="x", pady=6)

        tk.Label(card, text="Já possui cadastro?", bg=CARD_BG,
                 fg=LABEL_FG, font=("Georgia", 10)).pack()
        link_label(card, "Faça login", self.switch)

    def _cadastrar(self):
        campos = {
            "Nome":            self.nome.get().strip(),
            "Nickname":        self.nickname.get().strip(),
            "Email":           self.email.get().strip(),
            "Senha":           self.senha.get().strip(),
            "Confirmar senha": self.confirm.get().strip(),
        }
        for nome, val in campos.items():
            if not val:
                messagebox.showwarning("Atenção", f"Preencha o campo: {nome}")
                return
        if campos["Senha"] != campos["Confirmar senha"]:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return
        if not self.tipo.get():
            messagebox.showwarning("Atenção", "Selecione o tipo de usuário.")
            return
        messagebox.showinfo("Cadastro",
                            f"Cadastro realizado!\nBem-vindo, {campos['Nome']}!")
        self.switch()
