import tkinter as tk
from constants import (
    BG, CARD_BG, SHADOW, RED, DARK,
    LABEL_FG, ENTRY_BG, BTN_BG, BTN_FG, LINK_FG, HINT_FG
)


def make_topbar(parent, hint_text):
    """Barra superior: logo à esquerda, dica de tela à direita."""
    bar = tk.Frame(parent, bg=BG, pady=10)
    bar.pack(side="top", fill="x", padx=16)

    # Logo (esquerda)
    logo = tk.Frame(bar, bg=BG)
    logo.pack(side="left")
    tk.Label(logo, text="Etec", bg=BG, fg=DARK,
             font=("Georgia", 16, "bold")).pack(anchor="w")
    tk.Label(logo, text="Júlio de Mesquita", bg=BG, fg=RED,
             font=("Georgia", 8)).pack(anchor="w")
    tk.Label(logo, text="Santo André", bg=BG, fg=DARK,
             font=("Georgia", 7)).pack(anchor="w")

    # Dica de tela (direita)
    tk.Label(bar, text=hint_text, bg=BG, fg=HINT_FG,
             font=("Georgia", 9)).pack(side="right", anchor="ne")


def make_card(parent):
    """Card branco centralizado com sombra simulada."""
    wrapper = tk.Frame(parent, bg=BG)
    wrapper.pack(expand=True)

    shadow = tk.Frame(wrapper, bg=SHADOW)
    shadow.pack()

    card = tk.Frame(shadow, bg=CARD_BG, padx=36, pady=24)
    card.pack(padx=2, pady=2)

    return card


def entry_field(parent, label_text, show=""):
    """Label + Entry empilhados."""
    tk.Label(parent, text=label_text, bg=CARD_BG, fg=LABEL_FG,
             font=("Georgia", 10)).pack(anchor="w", pady=(10, 2))
    e = tk.Entry(parent, bg=ENTRY_BG, relief="flat", bd=4,
                 font=("Georgia", 10), show=show, width=30)
    e.pack(fill="x", ipady=4)
    return e


def tipo_usuario(parent):
    """Radio buttons Aluno / Professor."""
    tk.Label(parent, text="Tipo de usuário:", bg=CARD_BG, fg=LABEL_FG,
             font=("Georgia", 10)).pack(anchor="w", pady=(12, 4))
    var = tk.StringVar(value="")
    row = tk.Frame(parent, bg=CARD_BG)
    row.pack(anchor="w")
    tk.Radiobutton(row, text="Aluno",     variable=var, value="aluno",
                   bg=CARD_BG, font=("Georgia", 10)).pack(side="left", padx=(0, 12))
    tk.Radiobutton(row, text="Professor", variable=var, value="professor",
                   bg=CARD_BG, font=("Georgia", 10)).pack(side="left")
    return var


def action_button(parent, text, command):
    """Botão principal escuro."""
    btn = tk.Button(parent, text=text, command=command,
                    bg=BTN_BG, fg=BTN_FG, relief="flat",
                    font=("Georgia", 11, "bold"), width=16,
                    cursor="hand2", activebackground="#444444",
                    activeforeground=BTN_FG, bd=0, pady=7)
    btn.pack(pady=(16, 4), fill="x")
    return btn


def link_label(parent, text, command):
    """Texto clicável estilo link."""
    lbl = tk.Label(parent, text=text, bg=CARD_BG, fg=LINK_FG,
                   font=("Georgia", 10, "underline"), cursor="hand2")
    lbl.pack()
    lbl.bind("<Button-1>", lambda e: command())
    return lbl
