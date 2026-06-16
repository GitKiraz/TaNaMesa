import tkinter as tk

import ui
from constants import BG, SURFACE, RED, INK, TEXT, MUTED, TINT
from screens._base import TelaAutenticada
from widgets import titulo_secao


REGRAS = [
    ("Encaixe correto",
     "Encaixe peças fazendo associações químicas corretas — "
     "fórmula, nome, propriedade ou classificação."),
    ("Jogadas válidas",
     "Jogadas inválidas não são permitidas pelo sistema."),
    ("Fim da partida",
     "O jogo termina quando todas as peças são utilizadas ou "
     "quando não há mais jogadas possíveis."),
    ("Pontuação",
     "São registrados tempo, acertos e erros — visíveis no HUD "
     "durante a partida."),
]


class TelaAjuda(TelaAutenticada):
    ativo_sidebar = "Ajuda"

    def _conteudo(self, parent):
        wrapper = tk.Frame(parent, bg=BG)
        wrapper.pack(expand=True, fill="both", padx=48, pady=48)

        titulo_secao(wrapper, "Ajuda",
                      "Como funciona o TáNaMesa.")

        # Lista de regras como mini-cards
        lista = tk.Frame(wrapper, bg=BG)
        lista.pack(fill="x", pady=(24, 0))

        for i, (titulo, corpo) in enumerate(REGRAS):
            self._cartao_regra(lista, i + 1, titulo, corpo).pack(
                fill="x", pady=(0, 10))

        # Suporte
        suporte = ui.Card(wrapper, padx=24, pady=20)
        suporte.pack(fill="x", pady=(18, 0))
        tk.Label(suporte.body, text="Precisa de mais ajuda?",
                 bg=SURFACE, fg=INK,
                 font=ui.font(12, "bold")).pack(anchor="w")
        tk.Label(suporte.body,
                 text="Entre em contato pelo e-mail "
                      "suporte@tanamesa.com.",
                 bg=SURFACE, fg=MUTED,
                 font=ui.font(10)).pack(anchor="w", pady=(4, 0))

    def _cartao_regra(self, parent, n, titulo, corpo):
        card = ui.Card(parent, padx=20, pady=16)
        row = tk.Frame(card.body, bg=SURFACE)
        row.pack(fill="x")

        # Número em badge
        badge = tk.Label(row, text=str(n), bg=TINT, fg=RED,
                         font=ui.font(13, "bold"),
                         width=2, height=1)
        badge.pack(side="left", padx=(0, 14))

        col = tk.Frame(row, bg=SURFACE)
        col.pack(side="left", fill="x", expand=True)
        tk.Label(col, text=titulo, bg=SURFACE, fg=INK,
                 font=ui.font(12, "bold"),
                 anchor="w").pack(anchor="w")
        tk.Label(col, text=corpo, bg=SURFACE, fg=TEXT,
                 font=ui.font(10), wraplength=620,
                 justify="left", anchor="w").pack(anchor="w", pady=(2, 0))

        return card
