from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "diagramas"
OUT.mkdir(exist_ok=True)

FONT = ROOT / "fonts" / "Neuromax-Regular.otf"
FONT_SEM = ROOT / "fonts" / "Neuromax-SemiBold.otf"
font_manager.fontManager.addfont(str(FONT))
font_manager.fontManager.addfont(str(FONT_SEM))

INK = "#2B293D"
BODY = "#4F5361"
MUTED = "#7A8190"
ORANGE = "#F08A3C"
ORANGE_DARK = "#B45309"
PINK = "#E8386D"
BLUE = "#3B6FD4"
GREEN = "#2E8B57"
LINE = "#D9DEE8"
SOFT = "#F7F9FC"
WHITE = "#FFFFFF"

A_FILL = "#FDE7D6"
B_FILL = "#FCE0E9"
C_FILL = "#DDE9FB"
D_FILL = "#FFF3C4"

plt.rcParams.update({
    "font.family": "Neuromax",
    "font.size": 12,
    "text.color": INK,
    "axes.edgecolor": LINE,
    "axes.labelcolor": BODY,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "figure.facecolor": WHITE,
    "savefig.facecolor": WHITE,
    "axes.unicode_minus": False,
})


def clean(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def room(ax, x0, y0, x1, y1):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0,
                           facecolor=SOFT, edgecolor=LINE, linewidth=1.5, zorder=0))


def label_node(ax, x, y, value, color=ORANGE, size=0.26, fs=10):
    ax.add_patch(Circle((x, y), size, facecolor=color, edgecolor=WHITE,
                        linewidth=1.5, zorder=6))
    ax.text(x, y - 0.005, value, ha="center", va="center", color=WHITE,
            fontsize=fs, fontweight="bold", zorder=7)


# ---------------------------------------------------------------- BSP problem
def bsp_problem():
    fig = plt.figure(figsize=(12.4, 6.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1, 1], wspace=0.18,
                          left=0.03, right=0.97, top=0.86, bottom=0.12)

    # map
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(-0.8, 5.4)
    ax.set_ylim(-2.9, 2.9)
    ax.set_aspect("equal")
    clean(ax)
    room(ax, -0.6, -2.6, 5.1, 2.6)
    ax.text(2.25, 2.9, "Mapa (vista desde arriba)", ha="center", va="bottom",
            fontsize=14, color=INK, fontweight="bold")

    # vision cone
    ax.add_patch(Polygon([[0.1, 0], [5.05, 1.9], [5.05, -1.9]],
                         closed=True, facecolor=ORANGE, alpha=0.10,
                         edgecolor="none", zorder=1))
    # walls
    ax.plot([2.35, 2.35], [0.15, 2.15], color=ORANGE, linewidth=9,
            solid_capstyle="round", zorder=4)
    ax.plot([4.55, 4.55], [-1.35, 1.35], color=BLUE, linewidth=9,
            solid_capstyle="round", zorder=3)
    ax.text(2.55, 1.55, "cercana", color=ORANGE_DARK, fontsize=11,
            fontweight="bold", zorder=5)
    ax.text(4.75, -0.4, "lejana", color=BLUE, fontsize=11,
            fontweight="bold", zorder=5)

    # sight lines
    for yy in (0.15, 2.15):
        ax.plot([0.1, 2.35], [0, yy], color=ORANGE, linewidth=1.0,
                linestyle=(0, (3, 3)), alpha=0.7, zorder=2)
    for yy in (-1.35, 1.35):
        ax.plot([0.1, 4.55], [0, yy], color=BLUE, linewidth=1.0,
                linestyle=(0, (3, 3)), alpha=0.6, zorder=2)

    # camera
    ax.add_patch(Circle((0.1, 0), 0.18, facecolor=INK, edgecolor=WHITE,
                        linewidth=2, zorder=8))
    ax.annotate("cámara", xy=(0.1, 0), xytext=(0.1, -2.35),
                ha="center", va="top", fontsize=10, color=BODY,
                arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=1))
    ax.annotate("", xy=(1.15, 0), xytext=(0.32, 0),
                arrowprops=dict(arrowstyle="-|>", color=INK, linewidth=1.4))
    ax.text(1.2, 0.12, "vista", fontsize=9, color=BODY)

    # screens
    def screen(ax_s, title, subtitle, wrong):
        ax_s.set_xlim(0, 6)
        ax_s.set_ylim(0, 7)
        clean(ax_s)
        ax_s.add_patch(FancyBboxPatch((0.35, 0.35), 5.3, 6.3,
                                      boxstyle="round,pad=0.02,rounding_size=0.18",
                                      facecolor=WHITE, edgecolor=LINE, linewidth=1.5))
        ax_s.text(3.0, 6.28, title, ha="center", va="top", fontsize=13.5,
                  color=INK, fontweight="bold")
        ax_s.text(3.0, 5.82, subtitle, ha="center", va="top", fontsize=9.5,
                  color=MUTED)
        ax_s.add_patch(Rectangle((1.05, 1.0), 3.9, 4.35, facecolor="#EEF2F7",
                                 edgecolor=LINE, linewidth=1.0))
        ax_s.text(3.0, 1.22, "pantalla", ha="center", va="bottom", fontsize=8.5,
                  color=MUTED)

        if wrong:
            # near first, far second: far wrongly covers near
            ax_s.add_patch(FancyBboxPatch((2.45, 3.65), 1.55, 1.75,
                                          boxstyle="round,pad=0,rounding_size=0.08",
                                          facecolor=ORANGE, edgecolor=WHITE, linewidth=2))
            ax_s.add_patch(FancyBboxPatch((2.15, 2.55), 1.25, 1.75,
                                          boxstyle="round,pad=0,rounding_size=0.08",
                                          facecolor=BLUE, edgecolor=WHITE, linewidth=2,
                                          alpha=0.98))
            ax_s.add_patch(Circle((4.75, 1.55), 0.36, facecolor=PINK,
                                  edgecolor=WHITE, linewidth=2))
            ax_s.plot([4.62, 4.88], [1.42, 1.68], color=WHITE, linewidth=3,
                      solid_capstyle="round", zorder=10)
            ax_s.plot([4.62, 4.88], [1.68, 1.42], color=WHITE, linewidth=3,
                      solid_capstyle="round", zorder=10)
            ax_s.text(3.0, 0.66, "cerca primero", ha="center", va="bottom",
                      fontsize=9.5, color=PINK, fontweight="bold")
        else:
            # far first, near second: near correctly covers far
            ax_s.add_patch(FancyBboxPatch((2.15, 2.55), 1.25, 1.75,
                                          boxstyle="round,pad=0,rounding_size=0.08",
                                          facecolor=BLUE, edgecolor=WHITE, linewidth=2))
            ax_s.add_patch(FancyBboxPatch((2.45, 3.65), 1.55, 1.75,
                                          boxstyle="round,pad=0,rounding_size=0.08",
                                          facecolor=ORANGE, edgecolor=WHITE, linewidth=2))
            ax_s.add_patch(Circle((4.75, 1.55), 0.36, facecolor=GREEN,
                                  edgecolor=WHITE, linewidth=2))
            ax_s.plot([4.58, 4.70, 4.90], [1.55, 1.43, 1.70], color=WHITE,
                      linewidth=3, solid_capstyle="round", zorder=10)
            ax_s.text(3.0, 0.66, "lejos primero", ha="center", va="bottom",
                      fontsize=9.5, color=GREEN, fontweight="bold")

    ax1 = fig.add_subplot(gs[0, 1])
    screen(ax1, "ORDEN INCORRECTO", "la pared lejana tapa a la cercana", True)
    ax2 = fig.add_subplot(gs[0, 2])
    screen(ax2, "ORDEN CORRECTO", "la pared cercana tapa a la lejana", False)

    fig.text(0.5, 0.035, "Sin z-buffer, el orden de dibujo decide qué pared se ve.",
             ha="center", va="bottom", fontsize=12.5, color=BODY)
    fig.savefig(OUT / "bsp_problema.png", dpi=170, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


# ---------------------------------------------------------------- BSP tree
def draw_bsp_map(ax, show_player=True, show_letters=True,
                 show_split_labels=True, caption=True):
    ax.set_xlim(-3.3, 3.3)
    ax.set_ylim(-3.3, 3.3)
    ax.set_aspect("equal")
    clean(ax)

    ax.add_patch(Polygon([[-3, 0], [0, 0], [0, 3], [-3, 3]], closed=True,
                         facecolor=A_FILL, edgecolor="none", zorder=1))
    ax.add_patch(Polygon([[-3, -3], [0, -3], [0, 0], [-3, 0]], closed=True,
                         facecolor=B_FILL, edgecolor="none", zorder=1))
    ax.add_patch(Polygon([[0, 0], [3, 0], [3, 3], [0, 3]], closed=True,
                         facecolor=C_FILL, edgecolor="none", zorder=1))
    ax.add_patch(Polygon([[0, -3], [3, -3], [3, 0], [0, 0]], closed=True,
                         facecolor=D_FILL, edgecolor="none", zorder=1))
    ax.add_patch(Rectangle((-3, -3), 6, 6, facecolor="none", edgecolor=INK,
                           linewidth=2.0, zorder=4))

    # splits
    ax.plot([0, 0], [-3, 3], color=INK, linewidth=3.2, zorder=3)
    ax.plot([-3, 0], [0, 0], color=INK, linewidth=3.2, zorder=3)
    ax.plot([0, 3], [0, 0], color=INK, linewidth=3.2, zorder=3)

    # labels
    if show_letters:
        ax.text(-1.5, 1.55, "A", ha="center", va="center", fontsize=24,
                color=INK, fontweight="bold", alpha=0.85, zorder=5)
        ax.text(-1.5, -1.55, "B", ha="center", va="center", fontsize=24,
                color=INK, fontweight="bold", alpha=0.85, zorder=5)
        ax.text(1.5, 1.55, "C", ha="center", va="center", fontsize=24,
                color=INK, fontweight="bold", alpha=0.85, zorder=5)
        ax.text(1.5, -1.55, "D", ha="center", va="center", fontsize=24,
                color=INK, fontweight="bold", alpha=0.85, zorder=5)

    if show_split_labels:
        label_node(ax, 0, 2.78, "L1", ORANGE, 0.24, 9)
        label_node(ax, -1.5, 0.0, "L2", PINK, 0.24, 9)
        label_node(ax, 1.5, 0.0, "L3", BLUE, 0.24, 9)

    if show_player:
        ax.add_patch(Polygon([[-1.95, -1.75], [-1.2, -1.05], [-1.95, -0.75]],
                             closed=True, facecolor=ORANGE, alpha=0.25,
                             edgecolor="none", zorder=5))
        ax.add_patch(Circle((-1.95, -1.25), 0.16, facecolor=INK,
                            edgecolor=WHITE, linewidth=2, zorder=7))
        ax.text(-2.55, -2.35, "cámara", ha="left", va="top", fontsize=9.5,
                color=BODY)

    if caption:
        ax.text(0, -3.22, "cada línea parte una zona en dos", ha="center",
                va="top", fontsize=10.5, color=MUTED)


def draw_tree(ax, order=None, show_question=True):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.4)
    clean(ax)

    pos = {
        "L1": (5.0, 7.2),
        "L2": (2.6, 4.6),
        "L3": (7.4, 4.6),
        "A": (1.15, 1.8),
        "B": (3.75, 1.8),
        "C": (6.25, 1.8),
        "D": (8.85, 1.8),
    }
    edges = [("L1", "L2"), ("L1", "L3"), ("L2", "A"), ("L2", "B"),
             ("L3", "C"), ("L3", "D")]
    for a, b in edges:
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1] - 0.32, pos[b][1] + 0.45],
                color=MUTED, linewidth=2.0, zorder=1, solid_capstyle="round")

    def box(name, color, fill=WHITE, fs=13):
        x, y = pos[name]
        ax.add_patch(FancyBboxPatch((x - 0.62, y - 0.32), 1.24, 0.64,
                                    boxstyle="round,pad=0.02,rounding_size=0.12",
                                    facecolor=fill, edgecolor=color, linewidth=2.4,
                                    zorder=4))
        ax.text(x, y, name, ha="center", va="center", fontsize=fs,
                color=INK, fontweight="bold", zorder=5)

    box("L1", ORANGE)
    box("L2", PINK)
    box("L3", BLUE)
    for name, fill in [("A", A_FILL), ("B", B_FILL), ("C", C_FILL), ("D", D_FILL)]:
        x, y = pos[name]
        ax.add_patch(Circle((x, y), 0.44, facecolor=fill, edgecolor=INK,
                            linewidth=1.8, zorder=4))
        ax.text(x, y, name, ha="center", va="center", fontsize=15,
                color=INK, fontweight="bold", zorder=5)

    if show_question:
        ax.text(5.0, 8.15, "¿delante o detrás?", ha="center", va="center",
                fontsize=12, color=ORANGE_DARK, style="italic")
        ax.text(5.0, 0.55, "nodos = cortes · hojas = zonas", ha="center",
                va="center", fontsize=9.5, color=MUTED)

    if order:
        for name, num in order.items():
            x, y = pos[name]
            ax.add_patch(Circle((x + 0.52, y + 0.36), 0.24, facecolor=INK,
                                edgecolor=WHITE, linewidth=1.4, zorder=7))
            ax.text(x + 0.52, y + 0.35, str(num), ha="center", va="center",
                    color=WHITE, fontsize=9, fontweight="bold", zorder=8)


def bsp_tree():
    fig = plt.figure(figsize=(12.4, 6.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.08], wspace=0.12,
                          left=0.03, right=0.97, top=0.88, bottom=0.08)
    ax = fig.add_subplot(gs[0, 0])
    draw_bsp_map(ax)
    ax.set_title("El mapa se parte en zonas", fontsize=15, color=INK,
                 fontweight="bold", pad=10)
    ax2 = fig.add_subplot(gs[0, 1])
    draw_tree(ax2)
    ax2.set_title("El árbol guarda los cortes", fontsize=15, color=INK,
                  fontweight="bold", pad=10)
    fig.savefig(OUT / "bsp_arbol.png", dpi=170, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def bsp_recorrido():
    fig = plt.figure(figsize=(12.4, 6.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.08], wspace=0.12,
                          left=0.03, right=0.97, top=0.88, bottom=0.08)
    ax = fig.add_subplot(gs[0, 0])
    draw_bsp_map(ax, show_letters=False, show_split_labels=False, caption=False)
    ax.set_title("Orden de dibujo en el mapa", fontsize=15, color=INK,
                 fontweight="bold", pad=10)

    zones = [("B", 1, -1.5, -1.55), ("A", 3, -1.5, 1.55),
             ("D", 5, 1.5, -1.55), ("C", 7, 1.5, 1.55)]
    for _name, num, x, y in zones:
        ax.add_patch(Circle((x, y), 0.3, facecolor=INK, edgecolor=WHITE,
                            linewidth=1.8, zorder=9))
        ax.text(x, y - 0.01, str(num), ha="center", va="center", color=WHITE,
                fontsize=11, fontweight="bold", zorder=10)

    cuts = [(2, -1.5, 0.0), (4, 0.0, 2.45), (6, 1.5, 0.0)]
    for num, x, y in cuts:
        ax.add_patch(FancyBboxPatch((x - 0.24, y - 0.24), 0.48, 0.48,
                                    boxstyle="round,pad=0.01,rounding_size=0.08",
                                    facecolor=ORANGE, edgecolor=WHITE,
                                    linewidth=1.8, zorder=9))
        ax.text(x, y - 0.01, str(num), ha="center", va="center", color=WHITE,
                fontsize=10, fontweight="bold", zorder=10)



    ax2 = fig.add_subplot(gs[0, 1])
    draw_tree(ax2, order={"B": 1, "L2": 2, "A": 3, "L1": 4,
                          "D": 5, "L3": 6, "C": 7}, show_question=False)
    ax2.set_title("El árbol da el orden sin comparar píxeles", fontsize=15,
                  color=INK, fontweight="bold", pad=10)
    fig.savefig(OUT / "bsp_recorrido.png", dpi=170, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


# ---------------------------------------------------------------- rsqrt pipeline
def rsqrt_pipeline():
    fig, ax = plt.subplots(figsize=(13.2, 3.4))
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 3.4)
    clean(ax)

    boxes = [
        ("1", "LEER BITS", ["float y = 0.25"], "entrada"),
        ("2", "VER COMO ENTERO", ["i = 0x3e800000"], "bits del float"),
        ("3", "CONSTANTE MÁGICA", ["i = 0x5f3759df", "- (i >> 1)"], "primera pista"),
        ("4", "VOLVER A FLOAT", ["y ~ 1.9324"], "error 3.4 %"),
        ("5", "NEWTON", ["y = y * (1.5", "- 0.5*x*y*y)"], "error 0.17 %"),
    ]
    w, h = 2.35, 2.35
    gap = 0.25
    x0 = 0.35
    y0 = 0.45
    colors = [ORANGE, PINK, ORANGE, BLUE, GREEN]
    for idx, (num, title, code_lines, note) in enumerate(boxes):
        x = x0 + idx * (w + gap)
        color = colors[idx]
        ax.add_patch(FancyBboxPatch((x, y0), w, h,
                                    boxstyle="round,pad=0.02,rounding_size=0.16",
                                    facecolor=WHITE, edgecolor=color, linewidth=2.2))
        ax.add_patch(Circle((x + 0.26, y0 + h - 0.28), 0.19, facecolor=color,
                            edgecolor=WHITE, linewidth=1.5))
        ax.text(x + 0.26, y0 + h - 0.29, num, ha="center", va="center",
                color=WHITE, fontsize=9, fontweight="bold")
        ax.text(x + 0.53, y0 + h - 0.28, title, ha="left", va="center",
                fontsize=8.8, color=color, fontweight="bold")
        ax.text(x + w / 2, y0 + 1.22, "\n".join(code_lines), ha="center",
                va="center", fontsize=9.4, color=INK,
                family="DejaVu Sans Mono", linespacing=1.25)
        ax.text(x + w / 2, y0 + 0.46, note, ha="center", va="center",
                fontsize=9.5, color=MUTED, fontweight="bold")
        if idx < len(boxes) - 1:
            ax.annotate("", xy=(x + w + gap - 0.02, y0 + h / 2),
                        xytext=(x + w + 0.03, y0 + h / 2),
                        arrowprops=dict(arrowstyle="-|>", color=MUTED,
                                        linewidth=1.6, shrinkA=0, shrinkB=0))

    fig.savefig(OUT / "rsqrt_pipeline.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- rsqrt error
def fast_inv_sqrt(x):
    x = np.asarray(x, dtype=np.float32)
    i = x.view(np.int32)
    i = np.int32(0x5f3759df) - (i >> 1)
    y = i.view(np.float32)
    y = y * (np.float32(1.5) - np.float32(0.5) * x * y * y)
    return y.astype(np.float64)


def fast_inv_sqrt_raw(x):
    x = np.asarray(x, dtype=np.float32)
    i = x.view(np.int32)
    i = np.int32(0x5f3759df) - (i >> 1)
    return i.view(np.float32).astype(np.float64)


def rsqrt_error():
    x = np.logspace(-2, 2, 1400)
    exact = 1.0 / np.sqrt(x)
    raw = fast_inv_sqrt_raw(x)
    fast = fast_inv_sqrt(x)
    err_raw = np.abs(raw - exact) / exact * 100
    err_fast = np.abs(fast - exact) / exact * 100

    fig, ax = plt.subplots(figsize=(9.6, 5.4))
    ax.plot(x, err_raw, color=ORANGE, linewidth=1.6)
    ax.plot(x, err_fast, color=PINK, linewidth=2.0)
    ax.axhline(0.175, color=GREEN, linewidth=1.1, linestyle=(0, (4, 4)))
    ax.text(0.012, 0.25, "0.175 %", color=GREEN, fontsize=10, fontweight="bold")
    ax.text(0.012, 2.95, "sin Newton: 3.4 %", color=ORANGE_DARK, fontsize=10.5,
            fontweight="bold",
            bbox=dict(facecolor=WHITE, edgecolor="none", alpha=0.9, pad=2))
    ax.text(0.012, 0.62, "con Newton: 0.175 %", color=PINK, fontsize=10.5,
            fontweight="bold",
            bbox=dict(facecolor=WHITE, edgecolor="none", alpha=0.9, pad=2))
    ax.set_xscale("log")
    ax.set_xlim(0.01, 100)
    ax.set_ylim(0, 3.6)
    ax.set_xticks([0.01, 0.1, 1, 10, 100])
    ax.set_xticklabels(["0.01", "0.1", "1", "10", "100"])
    ax.set_xlabel("x (escala logarítmica)", fontsize=11)
    ax.set_ylabel("error relativo (%)", fontsize=11)
    ax.grid(True, which="major", color=LINE, linewidth=0.8)
    ax.grid(True, which="minor", color=LINE, linewidth=0.4, alpha=0.5)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.set_title("Error del truco frente al valor exacto", fontsize=14,
                 color=INK, fontweight="bold", loc="left", pad=10)
    fig.tight_layout()
    fig.savefig(OUT / "rsqrt_error.png", dpi=170)
    plt.close(fig)


# ---------------------------------------------------------------- vector
def vector_unitario():
    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    ax.set_xlim(-0.5, 4.2)
    ax.set_ylim(-0.5, 3.4)
    ax.set_aspect("equal")
    ax.grid(True, color=LINE, linewidth=0.8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.spines["bottom"].set_color(LINE)
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_yticks([0, 1, 2, 3])

    ax.annotate("", xy=(3, 2), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, linewidth=3,
                                shrinkA=0, shrinkB=0))
    ax.plot([3, 3], [0, 2], color=MUTED, linewidth=1.0, linestyle=(0, (3, 3)))
    ax.plot([0, 3], [2, 2], color=MUTED, linewidth=1.0, linestyle=(0, (3, 3)))
    ax.text(2.05, 1.15, "v = (3, 2)", fontsize=13, color=ORANGE_DARK,
            fontweight="bold", rotation=33)
    ax.text(3.08, 1.0, "2", fontsize=10, color=MUTED)
    ax.text(1.5, 2.08, "3", fontsize=10, color=MUTED)

    ax.annotate("", xy=(3 / np.sqrt(13), 2 / np.sqrt(13)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=PINK, linewidth=3,
                                shrinkA=0, shrinkB=0))
    ax.text(0.88, 0.83, "v / |v|", fontsize=12, color=PINK,
            fontweight="bold")
    ax.text(0.12, 2.9, r"$|v| = \sqrt{3^2 + 2^2} = \sqrt{13} \approx 3.61$",
            fontsize=12, color=BODY)
    ax.text(0.12, 2.55,
            r"normalizar $= v / |v| = v \cdot (1/\sqrt{13})$",
            fontsize=12, color=INK, fontweight="bold")
    ax.set_title(r"Normalizar un vector usa $1/\sqrt{x}$", fontsize=14,
                 color=INK, fontweight="bold", loc="left", pad=10)
    fig.tight_layout()
    fig.savefig(OUT / "vector_unitario.png", dpi=170)
    plt.close(fig)


# ---------------------------------------------------------------- rsqrt bars
def rsqrt_bars():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.4, 5.0),
                                   gridspec_kw={"width_ratios": [1, 1], "wspace": 0.45})
    fig.patch.set_facecolor(WHITE)

    labels = ["Solo\nconstante", "Con\nNewton"]
    vals = [3.4, 0.175]
    colors = [ORANGE, PINK]
    bars = ax1.bar(labels, vals, color=colors, width=0.55)
    ax1.set_ylim(0, 4.2)
    ax1.set_yticks([0, 1, 2, 3, 4])
    ax1.set_title("Error máximo (%)", fontsize=12, color=INK, fontweight="bold", pad=10)
    ax1.grid(axis="y", color=LINE, linewidth=0.8)
    ax1.set_axisbelow(True)
    for bar, value in zip(bars, vals):
        ax1.text(bar.get_x() + bar.get_width() / 2, value + 0.12,
                 f"{value} %", ha="center", va="bottom", fontsize=10.5,
                 color=INK, fontweight="bold")
    for spine in ["top", "right"]:
        ax1.spines[spine].set_visible(False)

    labels2 = ["1/sqrt\nexacto", "Q_rsqrt"]
    vals2 = [1, 4]
    colors2 = [MUTED, GREEN]
    bars2 = ax2.bar(labels2, vals2, color=colors2, width=0.55)
    ax2.set_ylim(0, 5)
    ax2.set_yticks([0, 1, 2, 3, 4])
    ax2.set_title("Velocidad relativa (2003)", fontsize=12, color=INK,
                  fontweight="bold", pad=10)
    ax2.grid(axis="y", color=LINE, linewidth=0.8)
    ax2.set_axisbelow(True)
    for bar, value in zip(bars2, vals2):
        label = "1x" if value == 1 else "~4x"
        ax2.text(bar.get_x() + bar.get_width() / 2, value + 0.16,
                 label, ha="center", va="bottom", fontsize=11,
                 color=INK, fontweight="bold")
    for spine in ["top", "right"]:
        ax2.spines[spine].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT / "rsqrt_bars.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    bsp_problem()
    bsp_tree()
    bsp_recorrido()
    rsqrt_pipeline()
    rsqrt_error()
    rsqrt_bars()
    vector_unitario()
    print("Diagramas generados en", OUT)
