"""Componentes visuais reutilizáveis — layout / forms / sidebar."""
import tkinter as tk

import session
import ui
from constants import (BG, SURFACE, SOFT, TINT, RED, RED_DARK, RED_SOFT,
                       INK, TEXT, MUTED, SUBTLE, LINE,
                       LABEL_FG, LINK_FG)


# ---------------------------------------------------------- Top bar ----

def criar_barra_topo(parent, hint_text="", on_logout=None):
    """Barra superior usada nas telas sem sidebar (login/cadastro)."""
    bar = tk.Frame(parent, bg=BG)
    bar.pack(side="top", fill="x", padx=24, pady=16)

    logo = tk.Frame(bar, bg=BG)
    logo.pack(side="left")
    tk.Label(logo, text="Etec", bg=BG, fg=INK,
             font=ui.font(15, "bold")).pack(anchor="w")
    tk.Label(logo, text="Júlio de Mesquita  ·  Santo André",
             bg=BG, fg=MUTED, font=ui.font(9)).pack(anchor="w")

    right = tk.Frame(bar, bg=BG)
    right.pack(side="right")
    if hint_text:
        tk.Label(right, text=hint_text, bg=BG, fg=SUBTLE,
                 font=ui.font(10)).pack(side="right", padx=(0, 12))
    if on_logout:
        ui.GhostButton(right, "Sair", command=on_logout,
                       fg=TEXT, border=LINE,
                       padx=14, pady=8, size=10).pack(side="right")


# ----------------------------------------------------------- Form fields --

def campo_entrada(parent, label_text, show="", initial=""):
    """Label estilizado + ModernEntry."""
    tk.Label(parent, text=label_text, bg=parent.cget("bg"),
             fg=TEXT, font=ui.font(10, "bold")).pack(
        anchor="w", pady=(14, 4))
    e = ui.ModernEntry(parent, show=show)
    if initial:
        e.insert(0, initial)
    e.pack(fill="x")
    return e


def tipo_usuario(parent, initial=""):
    """Seleção Aluno / Professor estilizada (chip buttons)."""
    parent_bg = parent.cget("bg")
    tk.Label(parent, text="Tipo de usuário", bg=parent_bg, fg=TEXT,
             font=ui.font(10, "bold")).pack(anchor="w", pady=(16, 6))

    var = tk.StringVar(value=initial)
    row = tk.Frame(parent, bg=parent_bg)
    row.pack(anchor="w", fill="x")

    chips = {}

    def selecionar(valor):
        var.set(valor)
        for v, chip in chips.items():
            chip.definir_selecionado(v == valor)

    class Chip(ui.RoundedButton):
        def definir_selecionado(self, sel):
            self._bg     = RED if sel else "#ffffff"
            self._hover  = RED_DARK if sel else TINT
            self._active = ui._tonalizar(self._bg, -0.15)
            self._fg     = "#ffffff" if sel else TEXT
            self._renderizar(self._bg)

    for valor, rotulo in [("aluno", "Aluno"), ("professor", "Professor")]:
        chip = Chip(row, rotulo, command=lambda v=valor: selecionar(v),
                    bg="#ffffff", fg=TEXT, hover_bg=TINT,
                    radius=999, padx=22, pady=8, size=11,
                    parent_bg=parent_bg)
        chip.pack(side="left", padx=(0, 8))
        chips[valor] = chip

    if initial in chips:
        selecionar(initial)
    return var


def botao_acao(parent, text, command, bg=RED, fg="#ffffff"):
    """Botão de ação primário (cantos arredondados, full-width)."""
    btn = ui.RoundedButton(parent, text, command=command,
                           bg=bg, fg=fg, radius=10,
                           padx=28, pady=12, size=12)
    btn.pack(pady=(18, 4))
    return btn


def rotulo_link(parent, text, command):
    """Texto clicável estilo link."""
    lbl = tk.Label(parent, text=text, bg=parent.cget("bg"),
                   fg=LINK_FG, font=ui.font(10, "bold"),
                   cursor="hand2")
    lbl.pack(pady=(2, 0))
    lbl.bind("<Button-1>", lambda _e: command())
    return lbl


def titulo_secao(parent, text, sub=""):
    """Título grande de seção, com subtítulo opcional."""
    parent_bg = parent.cget("bg")
    tk.Label(parent, text=text, bg=parent_bg, fg=INK,
             font=ui.font(22, "bold")).pack(anchor="w")
    if sub:
        tk.Label(parent, text=sub, bg=parent_bg, fg=MUTED,
                 font=ui.font(11)).pack(anchor="w", pady=(2, 0))


# ----------------------------------------------------------- Sidebar ----

def criar_barra_lateral(parent, items, ativo=None, on_logout=None):
    """
    Sidebar moderna: logo + menu rolável + perfil/sair no rodapé.
    items: lista de (label, callback)
    """
    side = tk.Frame(parent, bg=SOFT, width=240)
    side.pack(side="left", fill="y")
    side.pack_propagate(False)

    # --- Cabeçalho (logo) ---
    header = tk.Frame(side, bg=SOFT)
    header.pack(fill="x", pady=(28, 18), padx=22)
    tk.Label(header, text="TáNaMesa", bg=SOFT, fg=RED,
             font=ui.font(20, "bold")).pack(anchor="w")
    tk.Label(header, text="Dominó digital  ·  Etec", bg=SOFT, fg=MUTED,
             font=ui.font(9)).pack(anchor="w")

    # --- Separador ---
    tk.Frame(side, bg=LINE, height=1).pack(fill="x", padx=22, pady=(0, 12))

    # --- Itens do menu ---
    menu = tk.Frame(side, bg=SOFT)
    menu.pack(fill="x", padx=14)

    for label, cmd in items:
        ativo_item = (label == ativo)
        _SidebarItem(menu, label, cmd, ativo=ativo_item).pack(fill="x", pady=2)

    # --- Rodapé com usuário + sair ---
    rodape = tk.Frame(side, bg=SOFT)
    rodape.pack(side="bottom", fill="x", padx=14, pady=14)

    u = session.atual() or {}
    perfil = tk.Frame(rodape, bg=SOFT)
    perfil.pack(fill="x", pady=(0, 8))
    ui.Avatar(perfil, u.get("nome", "?"), size=38, bg=RED).pack(side="left")
    txt = tk.Frame(perfil, bg=SOFT)
    txt.pack(side="left", padx=10)
    tk.Label(txt, text=u.get("nome", "Convidado"), bg=SOFT, fg=INK,
             font=ui.font(10, "bold"), anchor="w").pack(anchor="w")
    tk.Label(txt, text=u.get("tipo_usuario", "").capitalize() or "—",
             bg=SOFT, fg=MUTED, font=ui.font(9), anchor="w").pack(anchor="w")

    if on_logout:
        ui.GhostButton(rodape, "Sair da conta", command=on_logout,
                       fg=TEXT, border=LINE, padx=14, pady=10,
                       size=10, parent_bg=SOFT).pack(fill="x")

    return side


class _SidebarItem(tk.Frame):
    """Item do menu lateral: pill arredondada, hover, estado ativo."""

    def __init__(self, parent, label, cmd, ativo=False):
        super().__init__(parent, bg=SOFT)
        self._label = label
        self._cmd = cmd
        self._ativo = ativo

        self._bg_normal = SOFT
        self._bg_hover  = RED_SOFT
        self._bg_ativo  = RED
        self._fg_normal = TEXT
        self._fg_hover  = RED_DARK
        self._fg_ativo  = "#ffffff"
        self._current_bg = self._bg_ativo if ativo else self._bg_normal

        self._btn = tk.Canvas(self, width=200, height=40,
                              highlightthickness=0, bd=0, bg=SOFT)
        self._btn.pack(fill="x")

        self._renderizar(self._current_bg)

        self._btn.bind("<Enter>", self._ao_entrar)
        self._btn.bind("<Leave>", self._ao_sair)
        self._btn.bind("<Button-1>", self._ao_clicar)
        self._btn.bind("<Configure>", lambda _e: self._renderizar(self._current_bg))
        self._btn.configure(cursor="hand2")

    def _renderizar(self, bg):
        self._current_bg = bg
        self._btn.delete("all")
        w = self._btn.winfo_width()
        if w <= 1:                      # ainda não dimensionado pelo layout
            w = int(self._btn.winfo_reqwidth())
        h = 40
        pts = ui.pontos_arredondados(2, 2, w - 2, h - 2, 10)
        self._btn.create_polygon(pts, smooth=True, fill=bg, outline=bg)
        if self._ativo:
            fg = self._fg_ativo
        elif bg == self._bg_hover:
            fg = self._fg_hover
        else:
            fg = self._fg_normal
        self._btn.create_text(18, h // 2, text=self._label,
                              fill=fg, anchor="w",
                              font=ui.font(11, "bold"))

    def _ao_entrar(self, _):
        if not self._ativo:
            self._renderizar(self._bg_hover)

    def _ao_sair(self, _):
        self._renderizar(self._bg_ativo if self._ativo else self._bg_normal)

    def _ao_clicar(self, _):
        if self._cmd:
            self._cmd()
