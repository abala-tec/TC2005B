"""Dibuja las figuras de T8.7.2 con la simulación de codigo/simulacion_control_3d.py."""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "codigo"))
import simulacion_control_3d as sim  # noqa: E402

REG = str(ROOT / "fonts" / "Neuromax-Regular.otf")
SEM = str(ROOT / "fonts" / "Neuromax-SemiBold.otf")
INK, BODY, GRID = (19, 19, 21), (79, 83, 97), (217, 222, 232)
ORANGE, BLUE, PINK, GREEN = (240, 138, 60), (59, 111, 212), (232, 56, 109), (46, 139, 87)
S = 2


def f(path, size):
    return ImageFont.truetype(path, size * S)


def arrow(d, x0, y0, x1, y1, color, w=5):
    d.line([(x0, y0), (x1, y1)], fill=color, width=w * S)
    a = math.atan2(y1 - y0, x1 - x0)
    for da in (2.7, -2.7):
        d.line([(x1, y1), (x1 + 18 * S * math.cos(a + da), y1 + 18 * S * math.sin(a + da))],
               fill=color, width=w * S)


def fig_diagonal():
    W, H = 760 * S, 500 * S
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    ox, oy, u = 250 * S, 400 * S, 160 * S  # origen y 1 unidad en píxeles
    for i in range(-1, 5):  # cuadrícula
        d.line([(ox + i * u / 2, 40 * S), (ox + i * u / 2, oy + 20 * S)], fill=GRID, width=S)
    for j in range(0, 5):
        d.line([(60 * S, oy - j * u / 2), (W - 40 * S, oy - j * u / 2)], fill=GRID, width=S)
    d.arc([ox - u, oy - u, ox + u, oy + u], 180, 360, fill=BODY, width=2 * S)
    d.line([(ox, oy), (ox, 40 * S)], fill=INK, width=2 * S)
    d.line([(60 * S, oy), (W - 40 * S, oy)], fill=INK, width=2 * S)
    d.text((W - 40 * S, oy + 8 * S), "X", font=f(SEM, 20), fill=INK, anchor="rt")
    d.text((ox + 10 * S, 40 * S), "Z", font=f(SEM, 20), fill=INK, anchor="lt")
    arrow(d, ox, oy, ox + u, oy, GREEN)
    d.text((ox + u / 2, oy + 12 * S), "D: (1, 0)  largo 1", font=f(SEM, 17), fill=GREEN, anchor="mt")
    arrow(d, ox, oy, ox + 2 * u * 0.5, oy - 2 * u * 0.5, PINK)
    d.text((ox + u + 14 * S, oy - u - 10 * S), "W + D sin normalizar:\n(1, 1)  largo 1.41",
           font=f(SEM, 17), fill=PINK, anchor="lm")
    k = 1 / math.sqrt(2)
    arrow(d, ox, oy, ox + u * k, oy - u * k, BLUE)
    d.text((ox + u * k + 16 * S, oy - u * k + 24 * S), "normalizado:\n(0.71, 0.71)  largo 1",
           font=f(SEM, 17), fill=BLUE, anchor="lm")
    im.resize((W // S, H // S), Image.LANCZOS).save(ROOT / "figuras" / "fig_diagonal.png")


def fig_velocidad():
    W, H = 760 * S, 430 * S
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    l, r, t, b = 78 * S, W - 24 * S, 50 * S, H - 66 * S
    xmax, ymax = 1.5, 9

    def px(x):
        return l + (r - l) * x / xmax

    def py(y):
        return b - (b - t) * y / ymax

    for i in range(0, ymax + 1, 2):
        d.line([(l, py(i)), (r, py(i))], fill=GRID, width=S)
        d.text((l - 12 * S, py(i)), str(i), font=f(REG, 16), fill=BODY, anchor="rm")
    for x in (0, 0.5, 1, 1.5):
        d.text((px(x), b + 10 * S), f"{x:g}", font=f(REG, 16), fill=BODY, anchor="mt")
    d.line([(l, t), (l, b), (r, b)], fill=INK, width=2 * S)
    d.text(((l + r) / 2, H - 8 * S), "Tiempo (s)", font=f(SEM, 17), fill=INK, anchor="ms")
    d.text((8 * S, 8 * S), "Velocidad horizontal (u/s)", font=f(SEM, 17), fill=INK, anchor="lt")
    for norm, color in ((False, PINK), (True, BLUE)):
        tr = sim.correr(90, (1, 1), normalize=norm)
        d.line([(px(i * sim.DT), py(sim.length(v))) for i, v in enumerate(tr)],
               fill=color, width=4 * S, joint="curve")
    d.text((px(1.0), py(8.2)), "Sin normalizar: 7.95", font=f(SEM, 17), fill=PINK, anchor="ms")
    d.text((px(1.0), py(5.0)), "Normalizado: 5.625", font=f(SEM, 17), fill=BLUE, anchor="ms")
    im.resize((W // S, H // S), Image.LANCZOS).save(ROOT / "figuras" / "fig_velocidad_diag.png")


if __name__ == "__main__":
    fig_diagonal()
    fig_velocidad()
    print("figuras listas")
