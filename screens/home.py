import tkinter as tk

import session
import ui
from constants import BG, SURFACE, RED, INK, MUTED, TEXT
from screens._base import AuthScreen


class HomeScreen(AuthScreen):
    ativo_sidebar = "Iniciar nova partida"

    def _content(self, parent):
        u = session.atual() or {}

        wrapper = tk.Frame(parent, bg=BG)
        wrapper.pack(expand=True, fill="both", padx=48, pady=48)

        # Saudação
        nome = (u.get("nome") or u.get("nickname") or "").split()[0]
        tk.Label(wrapper,
                 text=f"Olá, {nome}!" if nome else "Olá!",
                 bg=BG, fg=INK,
                 font=ui.font(26, "bold")).pack(anchor="w")
        tk.Label(wrapper,
                 text="Pronto para revisar funções inorgânicas?",
                 bg=BG, fg=MUTED,
                 font=ui.font(12)).pack(anchor="w", pady=(2, 32))

        # Grid de cards de ação
        grid = tk.Frame(wrapper, bg=BG)
        grid.pack(anchor="w")

        self._action_card(grid, "Iniciar nova partida",
                          "Escolha um nível e comece a jogar dominó "
                          "de funções inorgânicas.",
                          accent=RED, cta="Jogar agora",
                          on_click=self.nav("options")).pack(
            side="left", padx=(0, 18))

        self._action_card(grid, "Meu perfil",
                          "Veja e edite suas informações de cadastro.",
                          accent="#1f2937", cta="Abrir perfil",
                          on_click=self.nav("profile")).pack(side="left")

        # Tip do dia
        tip = ui.Card(wrapper, padx=22, pady=18)
        tip.pack(fill="x", pady=(28, 0))
        tk.Label(tip.body, text="DICA",
                 bg=SURFACE, fg=RED,
                 font=ui.font(9, "bold")).pack(anchor="w")
        tk.Label(tip.body,
                 text=("Comece pelo nível fácil para se ambientar com a "
                       "associação fórmula ↔ classificação. "
                       "Depois, evolua para nome e propriedades."),
                 bg=SURFACE, fg=TEXT, font=ui.font(11),
                 wraplength=560, justify="left").pack(anchor="w", pady=(4, 0))

    def _action_card(self, parent, titulo, descricao,
                     accent, cta, on_click):
        card = ui.Card(parent, padx=28, pady=24)

        # Faixa de cor superior (accent)
        tk.Frame(card.body, bg=accent, height=4).pack(fill="x",
                                                      pady=(0, 16))

        tk.Label(card.body, text=titulo, bg=SURFACE, fg=INK,
                 font=ui.font(16, "bold"),
                 wraplength=240, justify="left").pack(anchor="w")
        tk.Label(card.body, text=descricao, bg=SURFACE, fg=MUTED,
                 font=ui.font(10), wraplength=240,
                 justify="left").pack(anchor="w", pady=(6, 18))

        ui.RoundedButton(card.body, cta, command=on_click,
                         bg=accent, fg="#ffffff", radius=10,
                         padx=24, pady=10, size=11).pack(anchor="w")
        return card
