import sqlite3
import tkinter as tk
from tkinter import messagebox

import database as db
import ui
from constants import BG, SURFACE, INK, MUTED, TEXT
from widgets import (criar_barra_topo, campo_entrada, tipo_usuario,
                     botao_acao, rotulo_link)


class TelaCadastro(tk.Frame):
    def __init__(self, master, switch_to_login):
        super().__init__(master, bg=BG)
        self.switch = switch_to_login
        self._construir()

    def _construir(self):
        criar_barra_topo(self)

        wrapper = tk.Frame(self, bg=BG)
        wrapper.pack(expand=True, fill="both")

        card = ui.Card(wrapper, padx=44, pady=32)
        card.pack(expand=True)
        body = card.body

        tk.Label(body, text="Crie sua conta", bg=SURFACE, fg=INK,
                 font=ui.font(22, "bold")).pack(anchor="w")
        tk.Label(body, text="Comece a jogar TáNaMesa em segundos.",
                 bg=SURFACE, fg=MUTED,
                 font=ui.font(11)).pack(anchor="w", pady=(0, 6))

        self.nome     = campo_entrada(body, "Nome")
        self.nickname = campo_entrada(body, "Nickname")
        self.email    = campo_entrada(body, "Email")
        self.senha    = campo_entrada(body, "Senha (mín. 8 caracteres)",
                                    show="•")
        self.confirm  = campo_entrada(body, "Confirmar senha", show="•")

        self.tipo = tipo_usuario(body)

        botao_acao(body, "Cadastrar", self._cadastrar)

        rodape = tk.Frame(body, bg=SURFACE)
        rodape.pack(pady=(14, 0))
        tk.Label(rodape, text="Já possui cadastro? ", bg=SURFACE,
                 fg=TEXT, font=ui.font(10)).pack(side="left")
        rotulo_link(rodape, "Faça login", self.switch)

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
        if len(campos["Senha"]) < 8:
            messagebox.showwarning("Atenção",
                                   "A senha deve possuir no mínimo 8 dígitos.")
            return
        if not self.tipo.get():
            messagebox.showwarning("Atenção", "Selecione o tipo de usuário.")
            return

        try:
            db.criar_usuario(
                nome=campos["Nome"],
                email=campos["Email"],
                senha=campos["Senha"],
                nickname=campos["Nickname"],
                tipo_usuario=self.tipo.get(),
            )
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro ao cadastrar",
                                 "Já existe um usuário com este e-mail.")
            return
        except Exception:
            messagebox.showerror("Erro ao cadastrar",
                                 "Não foi possível concluir o cadastro.")
            return

        messagebox.showinfo("Cadastro",
                            f"Cadastro realizado!\nBem-vindo, {campos['Nome']}!")
        for w in (self.nome, self.nickname, self.email,
                  self.senha, self.confirm):
            w.delete(0, tk.END)
        self.switch()
