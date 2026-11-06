"""Dibuja las figuras de T8.7.1 con la simulación de codigo/simulacion_control.py."""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "codigo"))
import simulacion_control as sim  # noqa: E402

REG = str(ROOT / "fonts" / "Neuromax-Regular.otf")
SEM = str(ROOT / "fonts" / "Neuromax-SemiBold.otf")
INK, BODY, GRID = (19, 19, 21), (79, 83, 97), (217, 222, 232)
ORANGE, BLUE, PINK, GREEN = (240, 138, 60), (59, 111, 212), (232, 56, 109), (46, 139, 87)
S = 2  # factor de resolución


def f(path, size):
    return ImageFont.truetype(path, size * S)


def chart(name, series, xmax, ymax, xlabel, ylabel, notes=(), size=(760, 430)):
    W, H = size[0] * S, size[1] * S
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    l, r, t, b = 78 * S, W - 24 * S, 50 * S, H - 66 * S

    def px(x):
        return l + (r - l) * x / xmax

    def py(y):
        return b - (b - t) * y / ymax

    for i in range(0, int(ymax) + 1):
        if i % (2 if ymax > 6 else 1) == 0:
            d.line([(l, py(i)), (r, py(i))], fill=GRID, width=S)
            d.text((l - 12 * S, py(i)), str(i), font=f(REG, 16), fill=BODY, anchor="rm")
    xs = [0, .5, 1, 1.5, 2]
    for x in xs:
        if x <= xmax:
            d.text((px(x), b + 10 * S), f"{x:g}", font=f(REG, 16), fill=BODY, anchor="mt")
    d.line([(l, t), (l, b), (r, b)], fill=INK, width=2 * S)
    d.text(((l + r) / 2, H - 8 * S), xlabel, font=f(SEM, 17), fill=INK, anchor="ms")
    d.text((8 * S, 8 * S), ylabel, font=f(SEM, 17), fill=INK, anchor="lt")
    for label, pts, color in series:
        d.line([(px(x), py(y)) for x, y in pts], fill=color, width=4 * S, joint="curve")
    for text, x, y, color in notes:
        d.text((px(x), py(y)), text, font=f(SEM, 17), fill=color, anchor="lm")
    im = im.resize((W // S, H // S), Image.LANCZOS) if False else im
    im.save(ROOT / "figuras" / name)
    print(name, im.size)


def speed_fig():
    def caso(run):
        tr = sim.correr_caso(120, lambda i: (1 if i < 60 else 0, run, False, False))
        return [(i * sim.DT, s["vx"]) for i, s in enumerate(tr)]
    walk, run = caso(False), caso(True)
    chart("fig_velocidad.png",
          [("caminar", walk, BLUE), ("correr", run, ORANGE)], 2, 10,
          "Tiempo (s). Se suelta la tecla en 1 s.", "vx (u/s)",
          [("Correr: 9.375", 1.35, 9.0, ORANGE), ("Caminar: 5.625", 0.58, 4.7, BLUE)])


def jump_fig():
    def caso(held):
        tr = sim.correr_caso(60, lambda i: (0, False, i == 0, held))
        return [(i * sim.DT, s["y"]) for i, s in enumerate(tr)]
    chart("fig_salto.png",
          [("toque", caso(False), BLUE), ("mantener", caso(True), ORANGE)], 1, 5,
          "Tiempo (s)", "Altura (tiles)",
          [("Mantener: 4.4 tiles", .50, 4.7, ORANGE), ("Toque: 1.1 tiles", .30, 1.5, BLUE)])


def normals_fig():
    W, H = 760 * S, 400 * S
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)

    def arrow(x0, y0, x1, y1, color):
        d.line([(x0, y0), (x1, y1)], fill=color, width=5 * S)
        import math
        a = math.atan2(y1 - y0, x1 - x0)
        for da in (2.6, -2.6):
            d.line([(x1, y1), (x1 + 18 * S * math.cos(a + da), y1 + 18 * S * math.sin(a + da))],
                   fill=color, width=5 * S)

    # personaje sobre el suelo
    d.rectangle([40 * S, 300 * S, 360 * S, 360 * S], fill=(120, 120, 140))
    d.rectangle([160 * S, 190 * S, 240 * S, 300 * S], fill=ORANGE)
    arrow(200 * S, 300 * S, 200 * S, 200 * S, GREEN)
    d.text((200 * S, 40 * S), "Suelo", font=f(SEM, 22), fill=INK, anchor="mt")
    d.text((200 * S, 90 * S), "normal.y = 1", font=f(REG, 20), fill=GREEN, anchor="mt")
    d.text((200 * S, 125 * S), "grounded = true", font=f(SEM, 20), fill=GREEN, anchor="mt")
    # personaje contra una pared
    d.rectangle([560 * S, 120 * S, 640 * S, 360 * S], fill=(120, 120, 140))
    d.rectangle([450 * S, 190 * S, 530 * S, 300 * S], fill=ORANGE)
    arrow(560 * S, 245 * S, 462 * S, 245 * S, PINK)
    d.text((540 * S, 40 * S), "Pared", font=f(SEM, 22), fill=INK, anchor="mt")
    d.text((540 * S, 70 * S), "normal.y = 0", font=f(REG, 20), fill=PINK, anchor="mt")
    d.text((540 * S, 100 * S), "no es suelo", font=f(SEM, 20), fill=PINK, anchor="mt")
    im.save(ROOT / "figuras" / "fig_normales.png")
    print("fig_normales.png", im.size)


if __name__ == "__main__":
    (ROOT / "figuras").mkdir(exist_ok=True)
    speed_fig(); jump_fig(); normals_fig()
