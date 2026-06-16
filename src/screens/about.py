import tkinter as tk

import ui
from constants import BG, SURFACE, RED, INK, TEXT, MUTED, TINT
from screens._base import TelaAutenticada
from widgets import titulo_secao


TIME = [
    ("CA", "Caio Atzinger Pfeilsticker"),
    ("JP", "João Paulo de Lima Martins"),
]


class TelaSobre(TelaAutenticada):
    ativo_sidebar = "Sobre"

    def _conteudo(self, parent):
        wrapper = tk.Frame(parent, bg=BG)
        wrapper.pack(expand=True, fill="both", padx=48, pady=48)

        titulo_secao(wrapper, "Sobre o TáNaMesa",
                      "Projeto acadêmico sem fins lucrativos.")

        # Card de descrição
        card = ui.Card(wrapper, padx=28, pady=24)
        card.pack(fill="x", pady=(24, 16))

        tk.Label(card.body,
                 text=("Gamificação educacional desenvolvida em parceria "
                       "com a Etec Júlio de Mesquita por estudantes de "
                       "Ciência da Computação do Instituto Mauá de "
                       "Tecnologia."),
                 bg=SURFACE, fg=TEXT, font=ui.font(11),
                 wraplength=620, justify="left").pack(anchor="w")

        # Card do time
        time = ui.Card(wrapper, padx=28, pady=24)
        time.pack(fill="x")

        tk.Label(time.body, text="Equipe", bg=SURFACE, fg=INK,
                 font=ui.font(13, "bold")).pack(anchor="w", pady=(0, 12))

        for iniciais, nome in TIME:
            self._integrante(time.body, iniciais, nome).pack(
                anchor="w", pady=4)

    def _integrante(self, parent, iniciais, nome):
        row = tk.Frame(parent, bg=SURFACE)
        ui.Avatar(row, nome, size=38, bg=RED).pack(side="left")
        tk.Label(row, text=nome, bg=SURFACE, fg=TEXT,
                 font=ui.font(11)).pack(side="left", padx=12)
        return row
