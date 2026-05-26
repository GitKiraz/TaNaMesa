import tkinter as tk

import database as db
import ui
from constants import BG, SURFACE, RED, INK, MUTED, TEXT
from screens._base import AuthScreen
from widgets import section_title


# Visual de cada nível
ESTILO = {
    1: dict(accent="#16a34a", emoji="●",
            descricao="Associação fórmula ↔ classificação. "
                      "Ideal para começar."),
    2: dict(accent="#f59e0b", emoji="●●",
            descricao="Associação nome ↔ fórmula. "
                      "Demanda memorização da nomenclatura."),
    3: dict(accent="#dc2626", emoji="●●●",
            descricao="Mistura nome, fórmula, propriedade e classificação. "
                      "Para os mais experientes."),
}


class OptionsScreen(AuthScreen):
    ativo_sidebar = "Opções"

    def _content(self, parent):
        wrapper = tk.Frame(parent, bg=BG)
        wrapper.pack(expand=True, fill="both", padx=48, pady=48)

        section_title(wrapper, "Escolha o nível",
                      "Cada nível tem uma forma diferente de associar "
                      "as peças.")

        grid = tk.Frame(wrapper, bg=BG)
        grid.pack(anchor="w", pady=(28, 0))

        for nv in db.listar_niveis():
            self._card_nivel(grid, nv).pack(side="left", padx=(0, 18),
                                            anchor="n")

    def _card_nivel(self, parent, nivel):
        est = ESTILO.get(nivel["ordem"], ESTILO[1])
        card = ui.Card(parent, padx=26, pady=22)

        # Faixa accent + emoji difficulty marker
        topo = tk.Frame(card.body, bg=SURFACE)
        topo.pack(anchor="w", fill="x", pady=(0, 14))
        tk.Frame(topo, bg=est["accent"], height=4).pack(fill="x")

        tk.Label(card.body, text=est["emoji"], bg=SURFACE,
                 fg=est["accent"],
                 font=ui.font(18, "bold")).pack(anchor="w")
        tk.Label(card.body, text=nivel["descricao"], bg=SURFACE, fg=INK,
                 font=ui.font(16, "bold")).pack(anchor="w", pady=(2, 6))
        tk.Label(card.body, text=est["descricao"], bg=SURFACE, fg=MUTED,
                 font=ui.font(10), wraplength=220,
                 justify="left").pack(anchor="w", pady=(0, 16))

        ui.RoundedButton(card.body, "Começar partida",
                         command=self.nav("game", nivel),
                         bg=est["accent"], fg="#ffffff",
                         radius=10, padx=20, pady=10, size=11
                         ).pack(anchor="w")

        return card
