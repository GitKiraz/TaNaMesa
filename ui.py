"""
Componentes visuais modernos baseados em Canvas — suportam cantos
arredondados, hover e estados visuais que o Tk padrão não oferece.
"""
import tkinter as tk
import tkinter.font as tkfont


# ---------------------------------------------------------------- fonte ----

_FONT_PREF = ["Inter", "SF Pro Display", "Segoe UI", "Cantarell",
              "Ubuntu", "Liberation Sans", "DejaVu Sans", "Helvetica"]
_family_cache = None


def family():
    """Devolve a melhor família de fonte disponível no sistema."""
    global _family_cache
    if _family_cache:
        return _family_cache
    try:
        disponivel = set(tkfont.families())
    except Exception:
        return "Helvetica"
    for f in _FONT_PREF:
        if f in disponivel:
            _family_cache = f
            return f
    _family_cache = "TkDefaultFont"
    return _family_cache


def font(size, weight="normal"):
    return (family(), size, weight)


# ------------------------------------------------------ geometria base ----

def rounded_points(x1, y1, x2, y2, r):
    """Polígono que aproxima um retângulo arredondado (raio `r`)."""
    return [
        x1 + r, y1, x2 - r, y1, x2, y1,
        x2, y1 + r, x2, y2 - r, x2, y2,
        x2 - r, y2, x1 + r, y2, x1, y2,
        x1, y2 - r, x1, y1 + r, x1, y1,
    ]


def _parent_bg(parent):
    try:
        return parent.cget("bg")
    except Exception:
        return "#ffffff"


# ----------------------------------------------------- RoundedButton ----

class RoundedButton(tk.Canvas):
    """
    Botão com cantos arredondados, hover, estados ativo/desabilitado.
    Auto-dimensionado pelo texto, ou com largura mínima opcional.
    """

    def __init__(self, parent, text, command=None, *,
                 bg="#dc2626", fg="#ffffff",
                 hover_bg=None, active_bg=None,
                 radius=10, padx=22, pady=11,
                 size=12, weight="bold",
                 min_width=None, parent_bg=None):
        if parent_bg is None:
            parent_bg = _parent_bg(parent)
        if hover_bg is None:
            hover_bg = _shade(bg, -0.10)
        if active_bg is None:
            active_bg = _shade(bg, -0.18)

        self._text = text
        self._command = command
        self._bg = bg
        self._fg = fg
        self._hover = hover_bg
        self._active = active_bg
        self._radius = radius
        self._padx = padx
        self._pady = pady
        self._font = font(size, weight)
        self._enabled = True
        self._current_bg = bg

        # Mede o texto para dimensionar o canvas
        f = tkfont.Font(family=family(), size=size, weight=weight)
        tw = f.measure(text)
        th = f.metrics("linespace")
        w = max(tw + 2 * padx, min_width or 0)
        h = th + 2 * pady

        super().__init__(parent, width=w, height=h,
                         highlightthickness=0, bd=0, bg=parent_bg)

        self._render(bg)

        self.bind("<Enter>",        lambda _e: self._on_enter())
        self.bind("<Leave>",        lambda _e: self._on_leave())
        self.bind("<ButtonPress-1>", lambda _e: self._on_press())
        self.bind("<ButtonRelease-1>", lambda _e: self._on_release())
        self.configure(cursor="hand2")

    def _render(self, fill):
        self._current_bg = fill
        self.delete("all")
        w = int(self.winfo_reqwidth())
        h = int(self.winfo_reqheight())
        pts = rounded_points(1, 1, w - 1, h - 1, self._radius)
        self.create_polygon(pts, smooth=True, fill=fill, outline=fill)
        fg = self._fg if self._enabled else "#9ca3af"
        self.create_text(w // 2, h // 2, text=self._text,
                         fill=fg, font=self._font)

    def _on_enter(self):
        if self._enabled:
            self._render(self._hover)

    def _on_leave(self):
        if self._enabled:
            self._render(self._bg)

    def _on_press(self):
        if self._enabled:
            self._render(self._active)

    def _on_release(self):
        if not self._enabled:
            return
        self._render(self._hover)
        if self._command:
            self._command()

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        self.configure(cursor="hand2" if enabled else "arrow")
        self._render(self._bg if enabled else _shade(self._bg, 0.30))


# -------------------------------------------------------- GhostButton ----

class GhostButton(RoundedButton):
    """Botão 'fantasma': fundo transparente, borda colorida."""

    def __init__(self, parent, text, command=None, *,
                 fg="#374151", border="#e5e7eb",
                 hover_bg="#f3f4f6", radius=10,
                 padx=20, pady=10, size=11, weight="bold",
                 parent_bg=None):
        self._border = border  # set ANTES do super().__init__ que chama _render
        super().__init__(parent, text, command,
                         bg=parent_bg or _parent_bg(parent),
                         fg=fg, hover_bg=hover_bg,
                         active_bg=_shade(hover_bg, -0.05),
                         radius=radius, padx=padx, pady=pady,
                         size=size, weight=weight, parent_bg=parent_bg)

    def _render(self, fill):
        self._current_bg = fill
        self.delete("all")
        w = int(self.winfo_reqwidth())
        h = int(self.winfo_reqheight())
        pts = rounded_points(1, 1, w - 1, h - 1, self._radius)
        self.create_polygon(pts, smooth=True, fill=fill,
                            outline=self._border)
        self.create_text(w // 2, h // 2, text=self._text,
                         fill=self._fg, font=self._font)


# -------------------------------------------------- Card (com sombra) ----

class Card(tk.Frame):
    """
    Cartão visual: fundo claro + borda fina + sombra sutil simulada.
    Use `card.body` como container para o conteúdo.
    """

    def __init__(self, parent, *, bg="#ffffff", border="#e5e7eb",
                 padx=28, pady=24, shadow="#eceae6"):
        parent_bg = _parent_bg(parent)
        super().__init__(parent, bg=parent_bg)

        # "Sombra": faixa 3px na base que cria sensação de profundidade.
        # Empacotada PRIMEIRO em side=bottom para reservar o espaço.
        tk.Frame(self, bg=shadow, height=3).pack(side="bottom", fill="x")

        # Borda fina (1px) ao redor do corpo
        wrapper = tk.Frame(self, bg=border)
        wrapper.pack(side="top", fill="both", expand=True)

        # Corpo branco (onde o usuário coloca conteúdo)
        self.body = tk.Frame(wrapper, bg=bg, padx=padx, pady=pady)
        self.body.pack(fill="both", expand=True, padx=1, pady=1)


# -------------------------------------------------------- RoundedPiece ----

class RoundedPiece(tk.Canvas):
    """
    Peça de dominó: dois lados, divisor central e cantos arredondados.
    Estados: normal, selecionada (borda vermelha), válida, inválida.
    """

    W = 210
    H = 86

    def __init__(self, parent, lado_a, lado_b, *,
                 on_click=None, selected=False, parent_bg=None,
                 bg="#ffffff", ink="#111827", border="#e5e7eb",
                 selected_border="#dc2626", radius=14):
        if parent_bg is None:
            parent_bg = _parent_bg(parent)

        super().__init__(parent, width=self.W, height=self.H,
                         highlightthickness=0, bd=0, bg=parent_bg)
        self._lado_a = lado_a
        self._lado_b = lado_b
        self._on_click = on_click
        self._bg = bg
        self._ink = ink
        self._border = border
        self._sel_border = selected_border
        self._radius = radius
        self._selected = selected
        self._render()

        if on_click is not None:
            self.bind("<Button-1>", lambda _e: on_click())
            self.bind("<Enter>", lambda _e: self._render(hover=True))
            self.bind("<Leave>", lambda _e: self._render())
            self.configure(cursor="hand2")

    def _render(self, hover=False):
        self.delete("all")
        w, h = self.W, self.H

        # Borda externa (mais grossa se selecionada)
        border_w = 3 if self._selected else 1
        border_color = self._sel_border if self._selected else self._border
        pts = rounded_points(1, 1, w - 1, h - 1, self._radius)
        self.create_polygon(pts, smooth=True, fill=self._bg,
                            outline=border_color, width=border_w)

        # Levíssimo highlight no hover
        if hover and not self._selected:
            self.create_polygon(pts, smooth=True, fill="",
                                outline="#fca5a5", width=2)

        # Divisor central
        cx = w // 2
        self.create_line(cx, 10, cx, h - 10,
                         fill=self._border, width=1)

        # Textos (com quebra automática)
        text_font = font(10, "bold")
        max_w = (w // 2) - 14
        self.create_text(w // 4, h // 2, text=self._lado_a, fill=self._ink,
                         font=text_font, width=max_w, justify="center")
        self.create_text(3 * w // 4, h // 2, text=self._lado_b, fill=self._ink,
                         font=text_font, width=max_w, justify="center")

    def set_selected(self, sel: bool):
        self._selected = sel
        self._render()


# --------------------------------------------------------------- Avatar --

class Avatar(tk.Canvas):
    """Círculo colorido com as iniciais do usuário."""

    def __init__(self, parent, nome, *, size=44,
                 bg="#dc2626", fg="#ffffff", parent_bg=None):
        if parent_bg is None:
            parent_bg = _parent_bg(parent)
        super().__init__(parent, width=size, height=size,
                         highlightthickness=0, bd=0, bg=parent_bg)
        iniciais = "".join(p[0] for p in (nome or "?").split()[:2]).upper() or "?"
        self.create_oval(2, 2, size - 2, size - 2, fill=bg, outline=bg)
        self.create_text(size // 2, size // 2, text=iniciais,
                         fill=fg, font=font(size // 3, "bold"))


# ------------------------------------------------------------- Entry --

class ModernEntry(tk.Frame):
    """
    Entry com visual moderno: container com borda 1px arredondada
    (simulada por fundo claro), bg branco, padding interno.
    """

    def __init__(self, parent, *, show="", placeholder="", width=28,
                 bg_inner="#ffffff", border="#e5e7eb",
                 focus_border="#dc2626", parent_bg=None):
        if parent_bg is None:
            parent_bg = _parent_bg(parent)
        super().__init__(parent, bg=border, padx=1, pady=1)
        self._border = border
        self._focus_border = focus_border

        inner = tk.Frame(self, bg=bg_inner, padx=12, pady=8)
        inner.pack(fill="both", expand=True)

        self.entry = tk.Entry(inner, bg=bg_inner, relief="flat", bd=0,
                              font=font(11), show=show, width=width,
                              insertbackground="#111827")
        self.entry.pack(fill="x")

        self.entry.bind("<FocusIn>",  lambda _e: self.configure(bg=focus_border))
        self.entry.bind("<FocusOut>", lambda _e: self.configure(bg=border))

    # Proxy mínimo para parecer um Entry
    def get(self):        return self.entry.get()
    def set(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
    def delete(self, *a, **kw): self.entry.delete(*a, **kw)
    def insert(self, *a, **kw): self.entry.insert(*a, **kw)
    def focus_set(self):  self.entry.focus_set()
    def config_state(self, state):
        self.entry.configure(state=state)


# -------------------------------------------------------------- utils --

def _shade(hex_color, factor):
    """Clareia (factor>0) ou escurece (factor<0) uma cor hex."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    if factor >= 0:
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
    else:
        f = 1 + factor
        r, g, b = int(r * f), int(g * f), int(b * f)
    return f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"
