"""Tela de relatórios — visível apenas para professores."""
import tkinter as tk
from tkinter import ttk, messagebox

import database as db
import session
import ui
from constants import (BG, SURFACE, RED, RED_DARK, INK, TEXT, MUTED,
                       LINE, LINE_SOFT, HUD_BG)
from screens._base import AuthScreen
from widgets import section_title


class ReportScreen(AuthScreen):
    ativo_sidebar = "Relatórios"

    def _content(self, parent):
        if not session.eh_professor():
            tk.Label(parent, text="Acesso restrito a professores.",
                     bg=BG, fg=INK,
                     font=ui.font(13, "bold")).pack(expand=True)
            return

        wrapper = tk.Frame(parent, bg=BG)
        wrapper.pack(expand=True, fill="both", padx=48, pady=48)

        topo = tk.Frame(wrapper, bg=BG)
        topo.pack(fill="x")

        col_t = tk.Frame(topo, bg=BG)
        col_t.pack(side="left", fill="x", expand=True)
        section_title(col_t, "Relatórios",
                      "Acompanhe o desempenho dos alunos.")

        ui.RoundedButton(topo, "Atualizar dados",
                         command=self._gerar,
                         bg=RED, hover_bg=RED_DARK,
                         padx=22, pady=10, size=11).pack(side="right",
                                                         anchor="ne")

        # Card resumo
        self._resumo = tk.Frame(wrapper, bg=BG)
        self._resumo.pack(fill="x", pady=(20, 16))

        # Tabela
        tab_card = ui.Card(wrapper, padx=0, pady=0)
        tab_card.pack(fill="both", expand=True)

        # Estilo moderno do ttk
        self._setup_treeview_style()

        cols = ("aluno", "nickname", "nivel", "pontos",
                "acertos", "erros", "tempo", "data")
        self.tree = ttk.Treeview(tab_card.body, columns=cols,
                                 show="headings", height=14,
                                 style="Modern.Treeview")
        headers = {
            "aluno":    ("Aluno",        180),
            "nickname": ("Nickname",     120),
            "nivel":    ("Nível",        120),
            "pontos":   ("Pontuação",     90),
            "acertos":  ("Acertos",       80),
            "erros":    ("Erros",         70),
            "tempo":    ("Tempo (s)",     90),
            "data":     ("Encerrada em", 180),
        }
        for k, (titulo, w) in headers.items():
            self.tree.heading(k, text=titulo)
            self.tree.column(k, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Linhas zebradas
        self.tree.tag_configure("odd",  background=LINE_SOFT)
        self.tree.tag_configure("even", background=SURFACE)

        self._carregar()

    def _setup_treeview_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Modern.Treeview",
                        background=SURFACE,
                        fieldbackground=SURFACE,
                        foreground=TEXT,
                        rowheight=34,
                        bordercolor=LINE,
                        borderwidth=0,
                        font=ui.font(10))
        style.configure("Modern.Treeview.Heading",
                        background=HUD_BG,
                        foreground="#ffffff",
                        font=ui.font(10, "bold"),
                        padding=8,
                        relief="flat")
        style.map("Modern.Treeview.Heading",
                  background=[("active", HUD_BG)])
        style.map("Modern.Treeview",
                  background=[("selected", RED)],
                  foreground=[("selected", "#ffffff")])

    def _stat(self, parent, titulo, valor):
        card = ui.Card(parent, padx=20, pady=16)
        tk.Label(card.body, text=titulo, bg=SURFACE, fg=MUTED,
                 font=ui.font(9, "bold")).pack(anchor="w")
        tk.Label(card.body, text=str(valor), bg=SURFACE, fg=INK,
                 font=ui.font(20, "bold")).pack(anchor="w",
                                                pady=(2, 0))
        return card

    def _carregar(self):
        dados = db.gerar_relatorio(session.atual()["id_usuario"])

        # Resumo agregado
        for w in self._resumo.winfo_children():
            w.destroy()
        total = len(dados)
        soma_pts = sum(d["pontuacao"] for d in dados)
        soma_ace = sum(d["acertos"]   for d in dados)
        soma_err = sum(d["erros"]     for d in dados)

        self._stat(self._resumo, "Partidas",       total).pack(
            side="left", padx=(0, 12))
        self._stat(self._resumo, "Pontos totais",  soma_pts).pack(
            side="left", padx=(0, 12))
        self._stat(self._resumo, "Acertos totais", soma_ace).pack(
            side="left", padx=(0, 12))
        self._stat(self._resumo, "Erros totais",   soma_err).pack(
            side="left")

        # Tabela
        for i in self.tree.get_children():
            self.tree.delete(i)
        for idx, r in enumerate(dados):
            tag = "odd" if idx % 2 else "even"
            self.tree.insert("", "end", tags=(tag,), values=(
                r["nome"], r["nickname"], r["nivel"],
                r["pontuacao"], r["acertos"], r["erros"],
                r["tempo_segundos"], r["encerrada_em"],
            ))

    def _gerar(self):
        self._carregar()
        messagebox.showinfo("Relatório", "Relatório atualizado.")
