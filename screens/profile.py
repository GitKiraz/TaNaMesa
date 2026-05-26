import tkinter as tk
from tkinter import messagebox

import database as db
import session
import ui
from constants import (BG, SURFACE, RED, RED_DARK, INK, TEXT, MUTED,
                       LINE)
from screens._base import AuthScreen
from widgets import section_title


class ProfileScreen(AuthScreen):
    ativo_sidebar = "Perfil"

    def _content(self, parent):
        u = session.atual() or {}
        self._editando = False

        wrapper = tk.Frame(parent, bg=BG)
        wrapper.pack(expand=True, fill="both", padx=48, pady=48)

        section_title(wrapper, "Meu perfil",
                      "Visualize e edite suas informações de cadastro.")

        # Card principal com avatar + dados
        card = ui.Card(wrapper, padx=32, pady=28)
        card.pack(anchor="w", pady=(24, 0))

        # Cabeçalho do card: avatar grande + nome
        topo = tk.Frame(card.body, bg=SURFACE)
        topo.pack(fill="x", pady=(0, 18))
        ui.Avatar(topo, u.get("nome", "?"), size=64,
                  bg=RED).pack(side="left")
        info = tk.Frame(topo, bg=SURFACE)
        info.pack(side="left", padx=16)
        tk.Label(info, text=u.get("nome", ""), bg=SURFACE, fg=INK,
                 font=ui.font(18, "bold"), anchor="w").pack(anchor="w")
        tk.Label(info, text=u.get("email", ""), bg=SURFACE, fg=MUTED,
                 font=ui.font(10), anchor="w").pack(anchor="w")
        tk.Label(info, text=u.get("tipo_usuario", "").capitalize(),
                 bg=SURFACE, fg=RED,
                 font=ui.font(10, "bold"), anchor="w").pack(anchor="w",
                                                            pady=(4, 0))

        tk.Frame(card.body, bg=LINE, height=1).pack(fill="x", pady=(0, 12))

        # Form
        self.campos = {}
        self._linha(card.body, "Nickname", "nickname",
                    u.get("nickname", ""))
        self._linha(card.body, "Nome", "nome", u.get("nome", ""))
        self._linha(card.body, "E-mail", "email", u.get("email", ""))
        self._linha(card.body, "Senha", "senha", "", show="•")

        # Botões
        botoes = tk.Frame(card.body, bg=SURFACE)
        botoes.pack(anchor="w", pady=(18, 0))

        self.btn_editar = ui.GhostButton(botoes, "Editar",
                                         command=self._editar,
                                         fg=TEXT, border=LINE,
                                         padx=22, pady=10, size=11)
        self.btn_editar.pack(side="left", padx=(0, 8))

        self.btn_salvar = ui.RoundedButton(botoes, "Salvar alterações",
                                           command=self._salvar,
                                           bg=RED, hover_bg=RED_DARK,
                                           padx=22, pady=10, size=11)
        self.btn_salvar.pack(side="left")
        self._aplicar_modo()

    def _linha(self, parent, label, key, valor, show=""):
        row = tk.Frame(parent, bg=SURFACE)
        row.pack(fill="x", pady=6)
        tk.Label(row, text=label, bg=SURFACE, fg=TEXT,
                 font=ui.font(10, "bold"), width=14, anchor="w"
                 ).pack(side="left", padx=(0, 12))
        e = ui.ModernEntry(row, show=show, width=32)
        if valor:
            e.insert(0, valor)
        e.pack(side="left", fill="x", expand=True)
        self.campos[key] = e

    def _aplicar_modo(self):
        for key, entry in self.campos.items():
            entry.config_state("normal" if self._editando else "readonly")

    def _editar(self):
        self._editando = True
        self._aplicar_modo()
        self.campos["nickname"].focus_set()

    def _salvar(self):
        if not self._editando:
            messagebox.showinfo("Perfil",
                                "Clique em 'Editar' para alterar seus dados.")
            return
        u = session.atual()
        nome     = self.campos["nome"].get().strip()
        email    = self.campos["email"].get().strip()
        nickname = self.campos["nickname"].get().strip()
        senha    = self.campos["senha"].get().strip()

        if not nome or not email or not nickname:
            messagebox.showwarning("Atenção",
                                   "Nome, e-mail e nickname não podem "
                                   "estar vazios.")
            return
        if senha and len(senha) < 8:
            messagebox.showwarning("Atenção",
                                   "A senha deve possuir no mínimo 8 dígitos.")
            return

        try:
            db.atualizar_usuario(
                id_usuario=u["id_usuario"],
                nome=nome, email=email, nickname=nickname,
                senha=senha or None,
            )
        except Exception:
            messagebox.showerror("Erro",
                                 "Não foi possível salvar as alterações.")
            return

        session.login(db.buscar_usuario(u["id_usuario"]))
        self._editando = False
        self.campos["senha"].delete(0, tk.END)
        self._aplicar_modo()
        messagebox.showinfo("Perfil", "Alterações salvas com sucesso!")
