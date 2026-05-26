import tkinter as tk
from tkinter import messagebox

import database as db
import session
import ui
from constants import BG, SURFACE, RED, INK, MUTED, TEXT, LINK
from widgets import (make_topbar, entry_field, tipo_usuario,
                     action_button, link_label)


class LoginScreen(tk.Frame):
    def __init__(self, master, switch_to_register, on_success):
        super().__init__(master, bg=BG)
        self.switch = switch_to_register
        self.on_success = on_success
        self._build()

    def _build(self):
        make_topbar(self)

        wrapper = tk.Frame(self, bg=BG)
        wrapper.pack(expand=True, fill="both")

        card = ui.Card(wrapper, padx=44, pady=36)
        card.pack(expand=True)
        body = card.body

        tk.Label(body, text="Bem-vindo de volta",
                 bg=SURFACE, fg=INK,
                 font=ui.font(22, "bold")).pack(anchor="w")
        tk.Label(body, text="Entre para continuar jogando.",
                 bg=SURFACE, fg=MUTED,
                 font=ui.font(11)).pack(anchor="w", pady=(0, 12))

        self.email = entry_field(body, "Email")
        self.senha = entry_field(body, "Senha", show="•")

        tk.Label(body, text="Esqueci minha senha", bg=SURFACE,
                 fg=LINK, font=ui.font(9, "bold"),
                 cursor="hand2").pack(anchor="e", pady=(6, 0))

        self.tipo = tipo_usuario(body)

        action_button(body, "Entrar", self._entrar)

        rodape = tk.Frame(body, bg=SURFACE)
        rodape.pack(pady=(14, 0))
        tk.Label(rodape, text="Não possui cadastro? ", bg=SURFACE,
                 fg=TEXT, font=ui.font(10)).pack(side="left")
        link_label(rodape, "Cadastre-se", self.switch)

    def _entrar(self):
        email = self.email.get().strip()
        senha = self.senha.get().strip()
        tipo  = self.tipo.get()
        if not email or not senha:
            messagebox.showwarning("Atenção", "Preencha todos os campos!")
            return
        if not tipo:
            messagebox.showwarning("Atenção", "Selecione o tipo de usuário.")
            return

        usuario = db.autenticar(email, senha, tipo)
        if not usuario:
            messagebox.showerror("Erro", "Erro ao efetuar login")
            self.senha.delete(0, tk.END)
            return

        session.login(usuario)
        self.email.delete(0, tk.END)
        self.senha.delete(0, tk.END)
        self.on_success()
