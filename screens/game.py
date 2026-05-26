"""
Tela do jogo: dominó digital de funções inorgânicas.

Mecânica:
- O aluno recebe uma mão de peças (7) e uma peça inicial é posta no
  tabuleiro.
- Clicando em uma peça da mão e em "Encaixar à esquerda" ou
  "Encaixar à direita", o sistema valida por correspondência conceitual.
- Acertos somam pontos; erros contam. Tempo é cronometrado.
- A partida termina quando a mão esvazia, não há jogadas, ou o aluno sai.
"""
import random
import tkinter as tk
from tkinter import messagebox

import database as db
import session
import ui
from constants import (BG, SURFACE, RED, RED_DARK, INK, TEXT, MUTED,
                       LINE, TINT, HUD_BG, HUD_FG, HUD_ACCENT,
                       PIECE_VALID, PIECE_INVALID)
from screens._base import AuthScreen


PONTOS_ACERTO = 10
PONTOS_ERRO   = -2
TAMANHO_MAO   = 7
LARGURA_PECA  = ui.RoundedPiece.W + 12   # peça + margem entre peças


class GameScreen(AuthScreen):
    ativo_sidebar = None

    def __init__(self, master, nav, on_logout, nivel):
        self.nivel = nivel
        self._cadeia      = []     # lista de (esq_visivel, dir_visivel, id_peca)
        self._mao         = []     # peças dict do banco
        self._selecionada = None   # id da peça selecionada
        self._pontuacao   = 0
        self._acertos     = 0
        self._erros       = 0
        self._tempo_seg   = 0
        self._timer_job   = None
        self._partida_id  = None
        self._encerrada   = False
        self._resize_job  = None
        super().__init__(master, nav, on_logout)

    # ---------------------------------------------------------- layout ----

    def _content(self, parent):
        u = session.atual()
        self._partida_id = db.iniciar_partida(u["id_usuario"],
                                              self.nivel["id_nivel"])

        # Distribui peças
        todas = db.carregar_pecas(self.nivel["id_nivel"])
        random.shuffle(todas)
        inicial = todas.pop(0)
        self._cadeia.append((inicial["lado_a"], inicial["lado_b"],
                             inicial["id_peca"]))
        self._mao = todas[:TAMANHO_MAO]

        # --- HUD escuro com 3 métricas ---
        hud_wrap = tk.Frame(parent, bg=BG, padx=24, pady=18)
        hud_wrap.pack(fill="x")

        hud = tk.Frame(hud_wrap, bg=HUD_BG)
        hud.pack(fill="x", ipady=6)

        # Esquerda: rótulo do nível
        esq = tk.Frame(hud, bg=HUD_BG)
        esq.pack(side="left", padx=22, pady=10)
        tk.Label(esq, text="PARTIDA EM ANDAMENTO", bg=HUD_BG,
                 fg=HUD_ACCENT,
                 font=ui.font(9, "bold")).pack(anchor="w")
        tk.Label(esq, text=self.nivel["descricao"], bg=HUD_BG, fg=HUD_FG,
                 font=ui.font(14, "bold")).pack(anchor="w")

        # Direita: 3 boxes de métrica
        metr = tk.Frame(hud, bg=HUD_BG)
        metr.pack(side="right", padx=22, pady=10)
        self._lbl_tempo  = self._hud_box(metr, "TEMPO",     "00:00")
        self._lbl_pontos = self._hud_box(metr, "PONTUAÇÃO", "00")
        self._lbl_erros  = self._hud_box(metr, "ERROS",     "00")

        # --- Instrução ---
        info = tk.Label(parent,
                        text="Clique em uma peça da sua mão e escolha "
                             "uma extremidade do tabuleiro para encaixar.",
                        bg=BG, fg=MUTED, font=ui.font(10, "normal"))
        info.pack(pady=(2, 8))

        # --- Tabuleiro ---
        tab_wrap = ui.Card(parent, padx=18, pady=18)
        tab_wrap.pack(fill="x", padx=24)
        tk.Label(tab_wrap.body, text="TABULEIRO", bg=SURFACE, fg=MUTED,
                 font=ui.font(9, "bold")).pack(anchor="w", pady=(0, 6))
        self._tabuleiro_frame = tk.Frame(tab_wrap.body, bg=SURFACE)
        self._tabuleiro_frame.pack(fill="x")

        # --- Ações ---
        acoes = tk.Frame(parent, bg=BG)
        acoes.pack(pady=14)

        ui.RoundedButton(acoes, "← Encaixar à esquerda",
                         command=lambda: self._tentar("esq"),
                         bg=RED, hover_bg=RED_DARK, radius=999,
                         padx=18, pady=10, size=10).pack(side="left",
                                                         padx=6)
        ui.GhostButton(acoes, "Passar", command=self._passar,
                       fg=TEXT, border=LINE, radius=999,
                       padx=18, pady=10, size=10).pack(side="left", padx=6)
        ui.GhostButton(acoes, "Encerrar", command=self._sair,
                       fg=RED, border=RED, radius=999,
                       padx=18, pady=10, size=10).pack(side="left", padx=6)
        ui.RoundedButton(acoes, "Encaixar à direita →",
                         command=lambda: self._tentar("dir"),
                         bg=RED, hover_bg=RED_DARK, radius=999,
                         padx=18, pady=10, size=10).pack(side="left",
                                                         padx=6)

        # --- Mão ---
        mao_wrap = ui.Card(parent, padx=18, pady=14)
        mao_wrap.pack(fill="x", padx=24, pady=(0, 24))

        cab = tk.Frame(mao_wrap.body, bg=SURFACE)
        cab.pack(fill="x", pady=(0, 6))
        tk.Label(cab, text="SUA MÃO", bg=SURFACE, fg=MUTED,
                 font=ui.font(9, "bold")).pack(side="left")
        self._lbl_qtd = tk.Label(cab, text="", bg=SURFACE, fg=RED,
                                 font=ui.font(9, "bold"))
        self._lbl_qtd.pack(side="right")

        self._mao_frame = tk.Frame(mao_wrap.body, bg=SURFACE)
        self._mao_frame.pack(fill="x")

        # Re-layout no resize
        parent.bind("<Configure>", self._on_resize)

        self._render_tabuleiro()
        self._render_mao()
        self._tick()

    # ---------------------------------------------------------- HUD ----

    def _hud_box(self, parent, titulo, valor):
        box = tk.Frame(parent, bg=HUD_BG, padx=18)
        box.pack(side="left")
        tk.Label(box, text=titulo, bg=HUD_BG, fg=HUD_ACCENT,
                 font=ui.font(8, "bold")).pack()
        lbl = tk.Label(box, text=valor, bg=HUD_BG, fg=HUD_FG,
                       font=ui.font(20, "bold"))
        lbl.pack()
        return lbl

    # ---------------------------------------------------- render fluído --

    def _on_resize(self, _event=None):
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(80, self._relayout)

    def _relayout(self):
        self._resize_job = None
        if self._encerrada:
            return
        self._render_tabuleiro()
        self._render_mao()

    def _por_linha(self, container):
        container.update_idletasks()
        largura = container.winfo_width()
        if largura <= 1:
            largura = self.winfo_width() - 300
        return max(1, largura // LARGURA_PECA)

    def _render_grade(self, container, itens, draw_fn):
        for w in container.winfo_children():
            w.destroy()
        if not itens:
            return
        por_linha = self._por_linha(container)
        linha = None
        for i, item in enumerate(itens):
            if i % por_linha == 0:
                linha = tk.Frame(container, bg=container.cget("bg"))
                linha.pack(anchor="center", pady=4)
            draw_fn(linha, item)

    def _render_tabuleiro(self):
        def draw(parent, entrada):
            esq, dir_, _id = entrada
            ui.RoundedPiece(parent, esq, dir_,
                            parent_bg=parent.cget("bg")
                            ).pack(side="left", padx=6, pady=4)
        self._render_grade(self._tabuleiro_frame, self._cadeia, draw)

    def _render_mao(self):
        if hasattr(self, "_lbl_qtd"):
            self._lbl_qtd.config(text=f"{len(self._mao)} peça(s)")

        if not self._mao:
            for w in self._mao_frame.winfo_children():
                w.destroy()
            tk.Label(self._mao_frame, text="(sem peças na mão)",
                     bg=SURFACE, fg=MUTED,
                     font=ui.font(10, "normal")).pack(pady=10)
            return

        def draw(parent, peca):
            sel = (peca["id_peca"] == self._selecionada)
            ui.RoundedPiece(parent, peca["lado_a"], peca["lado_b"],
                            parent_bg=parent.cget("bg"),
                            selected=sel,
                            on_click=lambda i=peca["id_peca"]:
                                self._selecionar(i)
                            ).pack(side="left", padx=6, pady=4)
        self._render_grade(self._mao_frame, self._mao, draw)

    def _selecionar(self, id_peca):
        self._selecionada = id_peca if self._selecionada != id_peca else None
        self._render_mao()

    # ---------------------------------------------------------- regras ----

    def _peca_por_id(self, id_peca):
        for p in self._mao:
            if p["id_peca"] == id_peca:
                return p
        return None

    def _tentar(self, lado):
        if self._encerrada:
            return
        if self._selecionada is None:
            messagebox.showinfo("Atenção",
                                "Selecione uma peça da sua mão primeiro.")
            return
        peca = self._peca_por_id(self._selecionada)
        if not peca:
            return

        ok = self._encaixar(peca, lado)
        if ok:
            self._mao = [p for p in self._mao
                         if p["id_peca"] != self._selecionada]
            self._acertos   += 1
            self._pontuacao += PONTOS_ACERTO
            db.registrar_jogada(self._partida_id, peca["id_peca"],
                                True, "encaixe válido")
            self._flash(PIECE_VALID, "✓ Encaixe válido!  +10 pts")
        else:
            self._erros     += 1
            self._pontuacao += PONTOS_ERRO
            db.registrar_jogada(self._partida_id, peca["id_peca"],
                                False, "encaixe inválido")
            self._flash(PIECE_INVALID, "✗ Encaixe inválido")

        self._selecionada = None
        self._atualizar_hud()
        self._render_tabuleiro()
        self._render_mao()
        self._checar_fim()

    def _encaixar(self, peca, lado):
        a, b = peca["lado_a"], peca["lado_b"]
        if lado == "dir":
            exposto = self._cadeia[-1][1]
            if a == exposto:
                self._cadeia.append((a, b, peca["id_peca"]))
                return True
            if b == exposto:
                self._cadeia.append((b, a, peca["id_peca"]))
                return True
        else:
            exposto = self._cadeia[0][0]
            if a == exposto:
                self._cadeia.insert(0, (b, a, peca["id_peca"]))
                return True
            if b == exposto:
                self._cadeia.insert(0, (a, b, peca["id_peca"]))
                return True
        return False

    def _ha_jogada_possivel(self):
        if not self._cadeia or not self._mao:
            return False
        esq = self._cadeia[0][0]
        dir_ = self._cadeia[-1][1]
        for p in self._mao:
            if p["lado_a"] in (esq, dir_) or p["lado_b"] in (esq, dir_):
                return True
        return False

    def _passar(self):
        if not self._ha_jogada_possivel():
            messagebox.showinfo("Sem jogadas",
                                "Nenhuma peça da sua mão encaixa nas "
                                "extremidades. A partida será encerrada.")
            self._encerrar(motivo="sem jogadas")
        else:
            messagebox.showinfo("Atenção",
                                "Ainda existem jogadas possíveis na sua mão!")

    def _sair(self):
        if messagebox.askyesno("Encerrar partida",
                               "Deseja encerrar a partida agora?"):
            self._encerrar(motivo="saída do usuário")

    def _checar_fim(self):
        if not self._mao:
            self._encerrar(motivo="mão esvaziada")
        elif not self._ha_jogada_possivel():
            messagebox.showinfo("Fim de jogo",
                                "Nenhuma peça da sua mão encaixa mais. "
                                "Partida encerrada.")
            self._encerrar(motivo="sem jogadas")

    def _encerrar(self, motivo=""):
        if self._encerrada:
            return
        self._encerrada = True
        if self._timer_job:
            self.after_cancel(self._timer_job)
        db.encerrar_partida(self._partida_id,
                            self._pontuacao, self._acertos,
                            self._erros, self._tempo_seg)
        messagebox.showinfo(
            "Resultado",
            f"Partida encerrada ({motivo}).\n\n"
            f"Pontuação: {self._pontuacao}\n"
            f"Acertos:   {self._acertos}\n"
            f"Erros:     {self._erros}\n"
            f"Tempo:     {self._fmt_tempo(self._tempo_seg)}"
        )
        self.nav("home")()

    # ---------------------------------------------------------- timer ----

    def _tick(self):
        if self._encerrada:
            return
        self._tempo_seg += 1
        self._atualizar_hud()
        self._timer_job = self.after(1000, self._tick)

    def _atualizar_hud(self):
        self._lbl_tempo.config(text=self._fmt_tempo(self._tempo_seg))
        self._lbl_pontos.config(text=f"{max(self._pontuacao, 0):02d}")
        self._lbl_erros.config(text=f"{self._erros:02d}")

    @staticmethod
    def _fmt_tempo(seg):
        return f"{seg // 60:02d}:{seg % 60:02d}"

    # ---------------------------------------------------------- feedback -

    def _flash(self, cor, msg):
        bar = tk.Toplevel(self)
        bar.overrideredirect(True)
        bar.configure(bg=cor)
        tk.Label(bar, text=msg, bg=cor, fg=INK,
                 font=ui.font(11, "bold"),
                 padx=22, pady=10).pack()
        self.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() // 2 - 110
        y = self.winfo_rooty() + 110
        bar.geometry(f"+{x}+{y}")
        bar.after(900, bar.destroy)
