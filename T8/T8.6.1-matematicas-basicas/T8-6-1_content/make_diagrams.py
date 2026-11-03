"""Genera las figuras de T8.6.1: distancia, vectores, patrulla, ángulo y persecución."""

from pathlib import Path
from math import atan2, cos, sin, pi, sqrt, tan, radians

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figuras"
FONTS = ROOT / "fonts"
OUT.mkdir(exist_ok=True)

INK = (19, 19, 21)
BODY = (79, 83, 97)
MUTED = (107, 114, 128)
ORANGE = (240, 138, 60)
ORANGE_SOFT = (252, 232, 214)
PINK = (232, 56, 109)
GREEN = (46, 139, 87)
GREEN_SOFT = (223, 240, 230)
BLUE = (59, 111, 212)
LINE = (217, 222, 232)
SOFT = (244, 247, 250)
WHITE = (255, 255, 255)
DARK = (43, 41, 61)

REG = FONTS / "Neuromax-Regular.otf"
SEM = FONTS / "Neuromax-SemiBold.otf"


def font(path, size):
    return ImageFont.truetype(str(path), size)


def text(draw, xy, value, size=36, color=INK, sem=False, anchor="la"):
    draw.text(xy, value, font=font(SEM if sem else REG, size), fill=color, anchor=anchor)


def arrow(draw, p0, p1, color=ORANGE, width=6, head=18):
    x0, y0 = p0
    x1, y1 = p1
    draw.line([p0, p1], fill=color, width=width)
    ang = atan2(y1 - y0, x1 - x0)
    left = (x1 - head * cos(ang - pi / 6), y1 - head * sin(ang - pi / 6))
    right = (x1 - head * cos(ang + pi / 6), y1 - head * sin(ang + pi / 6))
    draw.polygon([p1, left, right], fill=color)


def dashed(draw, p0, p1, color=LINE, width=3, dash=14, gap=10):
    x0, y0 = p0
    x1, y1 = p1
    length = sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    if length == 0:
        return
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    t = 0
    while t < length:
        end = min(t + dash, length)
        draw.line([(x0 + ux * t, y0 + uy * t), (x0 + ux * end, y0 + uy * end)],
                  fill=color, width=width)
        t = end + gap


def dashed_circle(draw, center, radius, color=LINE, width=4, segments=72):
    cx, cy = center
    for i in range(segments):
        if i % 2 == 0:
            a0 = 2 * pi * i / segments
            a1 = 2 * pi * (i + 1) / segments
            draw.arc([cx - radius, cy - radius, cx + radius, cy + radius],
                     start=a0 * 180 / pi, end=a1 * 180 / pi, fill=color, width=width)


def dot(draw, p, r=12, color=ORANGE, outline=WHITE, outline_w=4):
    x, y = p
    draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=outline,
                 width=outline_w)


def background(w, h):
    image = Image.new("RGB", (w, h), SOFT)
    return image, ImageDraw.Draw(image)


def patrulla():
    image, draw = background(1600, 900)
    x0, y0, x1, y1 = 440, 70, 1200, 830
    draw.rectangle([x0, y0, x1, y1], fill=WHITE, outline=LINE, width=3)
    for i in range(1, 10):
        x = x0 + i * (x1 - x0) / 10
        y = y0 + i * (y1 - y0) / 10
        draw.line([(x, y0), (x, y1)], fill=(235, 239, 246), width=1)
        draw.line([(x0, y), (x1, y)], fill=(235, 239, 246), width=1)

    arrow(draw, (x0, y1), (x1 + 70, y1), BODY, 3, 14)
    arrow(draw, (x0, y1), (x0, y0 - 40), BODY, 3, 14)
    text(draw, (x1 + 82, y1 - 18), "X", 34, BODY, True)
    text(draw, (x0 - 36, y0 - 46), "Z", 34, BODY, True)

    inset = 38
    corners = {
        0: (x0 + inset, y1 - inset),
        1: (x1 - inset, y1 - inset),
        2: (x1 - inset, y0 + inset),
        3: (x0 + inset, y0 + inset),
    }
    for p in corners.values():
        dot(draw, p, 10, BLUE, WHITE, 3)

    sphere = corners[2]
    target = corners[0]
    dot(draw, sphere, 30, ORANGE, WHITE, 5)
    text(draw, (sphere[0] + 44, sphere[1] - 10), "esfera", 34, INK, True)
    draw.ellipse([target[0] - 26, target[1] - 26, target[0] + 26, target[1] + 26],
                 outline=PINK, width=5)
    arrow(draw, (sphere[0] - 32, sphere[1] + 28), (target[0] + 30, target[1] - 26),
          ORANGE, 5, 16)
    text(draw, (700, 470), "objetivo", 34, ORANGE, True, "ma")
    image.save(OUT / "patrulla.png")
    print("patrulla.png", image.size)


def vector_resta():
    image, draw = background(1400, 760)
    e = (200, 620)
    q = (1220, 160)
    dashed(draw, e, (q[0], e[1]), LINE, 3)
    dashed(draw, (q[0], e[1]), q, LINE, 3)
    arrow(draw, e, q, ORANGE, 6, 18)
    dot(draw, e, 13, BLUE, WHITE, 4)
    dot(draw, q, 13, PINK, WHITE, 4)

    text(draw, (e[0] - 10, e[1] + 28), "E: posición actual", 34, INK, True)
    text(draw, (q[0] - 12, q[1] - 50), "Q: objetivo", 34, INK, True, "ra")
    text(draw, (650, 300), "hacia = Q - E", 40, ORANGE, True, "ma")
    text(draw, (730, 650), "dx", 34, BODY, True, "ma")
    text(draw, (q[0] + 16, 400), "dz", 34, BODY, True, "la")

    image.save(OUT / "vector_resta.png")
    print("vector_resta.png", image.size)


def vector_suma():
    image, draw = background(1400, 760)
    p = (200, 620)
    q = (1220, 160)
    dashed(draw, p, (q[0], p[1]), LINE, 3)
    dashed(draw, (q[0], p[1]), q, LINE, 3)
    arrow(draw, p, q, ORANGE, 6, 18)
    dot(draw, p, 13, BLUE, WHITE, 4)
    dot(draw, q, 13, PINK, WHITE, 4)

    text(draw, (p[0] - 10, p[1] + 28), "P: posición actual", 34, INK, True)
    text(draw, (q[0] - 12, q[1] - 50), "P': posición nueva", 34, INK, True, "ra")
    text(draw, (620, 290), "dirección × paso", 38, ORANGE, True, "ma")

    image.save(OUT / "vector_suma.png")
    print("vector_suma.png", image.size)


def normalizacion():
    image, draw = background(1600, 950)
    text(draw, (80, 46), "Normalizar: misma dirección, longitud 1", 38, BODY, True)

    left = (120, 230, 720, 780)
    draw.rectangle(left, fill=WHITE, outline=LINE, width=3)
    text(draw, (140, 182), "Sin normalizar", 36, INK, True)
    origin = (180, 720)
    unit = 460
    dashed(draw, origin, (origin[0] + unit, origin[1]), LINE, 3)
    dashed(draw, (origin[0] + unit, origin[1]),
           (origin[0] + unit, origin[1] - unit), LINE, 3)
    arrow(draw, origin, (origin[0] + unit, origin[1] - unit), ORANGE, 6, 18)
    text(draw, (origin[0] + unit / 2, origin[1] + 22), "1", 32, BODY, True, "ma")
    text(draw, (origin[0] + unit + 16, origin[1] - unit / 2), "1", 32, BODY, True, "la")
    text(draw, (450, 500), "1.41", 40, ORANGE, True, "ma")

    right = (880, 230, 1480, 780)
    draw.rectangle(right, fill=WHITE, outline=LINE, width=3)
    text(draw, (900, 182), "Normalizado", 36, INK, True)
    origin2 = (940, 720)
    length = unit / sqrt(2)
    dashed(draw, origin2, (origin2[0] + length, origin2[1]), LINE, 3)
    dashed(draw, (origin2[0] + length, origin2[1]),
           (origin2[0] + length, origin2[1] - length), LINE, 3)
    arrow(draw, origin2, (origin2[0] + length, origin2[1] - length), BLUE, 6, 18)
    text(draw, (origin2[0] + length / 2, origin2[1] + 22), "0.707", 30, BODY, True, "ma")
    text(draw, (origin2[0] + length + 16, origin2[1] - length / 2), "0.707", 30, BODY, True, "la")
    text(draw, (1270, 600), "longitud = 1", 36, BLUE, True, "ma")

    text(draw, (120, 858), "Dividir cada componente entre la longitud conserva la dirección.", 30, BODY)
    image.save(OUT / "normalizacion.png")
    print("normalizacion.png", image.size)


def distancia():
    image, draw = background(1600, 900)
    text(draw, (60, 36), "Distancia en el plano XZ", 36, BODY, True)

    x0, y0, x1, y1 = 180, 110, 1380, 810
    draw.rectangle([x0, y0, x1, y1], fill=WHITE, outline=LINE, width=3)
    for i in range(1, 10):
        x = x0 + i * (x1 - x0) / 10
        y = y0 + i * (y1 - y0) / 10
        draw.line([(x, y0), (x, y1)], fill=(235, 239, 246), width=1)
        draw.line([(x0, y), (x1, y)], fill=(235, 239, 246), width=1)

    e = (300, 700)
    q = (1250, 200)
    dashed(draw, e, (q[0], e[1]), LINE, 3)
    dashed(draw, (q[0], e[1]), q, LINE, 3)
    arrow(draw, e, q, ORANGE, 6, 18)
    dot(draw, e, 13, ORANGE, WHITE, 4)
    dot(draw, q, 13, PINK, WHITE, 4)

    text(draw, (e[0] - 10, e[1] + 26), "E (esfera)", 34, INK, True)
    text(draw, (q[0] - 16, q[1] - 50), "Q (esquina)", 34, INK, True, "ra")
    text(draw, (720, 330), "d = 12.73", 40, ORANGE, True, "ma")
    text(draw, (760, 730), "dx = 9", 30, BODY, True, "ma")
    text(draw, (q[0] + 14, 430), "dz = 9", 30, BODY, True, "la")
    text(draw, (60, 842), "d = raíz(dx*dx + dz*dz)", 32, INK, True)

    image.save(OUT / "distancia.png")
    print("distancia.png", image.size)


def angulo_pisoton():
    image, draw = background(1800, 950)
    text(draw, (50, 30), "1. Ángulo de elevación", 34, BODY, True)
    text(draw, (930, 30), "2. Zona de pisotón", 34, BODY, True)

    # Panel izquierdo: vista lateral
    e = (190, 720)
    arrow(draw, e, (830, 720), BODY, 3, 14)
    arrow(draw, e, (190, 160), BODY, 3, 14)
    text(draw, (845, 700), "horizontal", 26, BODY)
    text(draw, (150, 130), "Y", 28, BODY, True)

    cube = (190 + 396, 720 - 450)
    dashed(draw, cube, (cube[0], 720), (200, 206, 218), 3)
    dashed(draw, (190, cube[1]), cube, (200, 206, 218), 3)
    arrow(draw, e, cube, ORANGE, 5, 16)
    draw.rectangle([cube[0] - 42, cube[1] - 42, cube[0] + 42, cube[1] + 42],
                   outline=ORANGE, width=4)
    text(draw, (cube[0] + 54, cube[1] - 20), "C (cubo)", 28, ORANGE, True)

    draw.arc([e[0] - 110, e[1] - 110, e[0] + 110, e[1] + 110],
             start=-48.7, end=0, fill=GREEN, width=4)
    text(draw, (300, 650), "48.7°", 28, GREEN, True)
    text(draw, (440, 742), "horizontal = 2.2", 26, BODY)
    text(draw, (600, 520), "dy = 2.5", 26, PINK)

    # Panel derecho: cono y cilindro
    e2 = (1330, 760)
    draw.line([(940, 760), (1740, 760)], fill=BODY, width=3)
    draw.line([(e2[0], 760), (e2[0], 180)], fill=BODY, width=3)
    text(draw, (1290, 150), "Y", 28, BODY, True)

    # Cono grande y zona verde
    draw.polygon([e2, (900, 180), (1760, 180)], fill=ORANGE_SOFT)
    draw.polygon([e2, (1030, 240), (1630, 240)], fill=GREEN_SOFT)
    draw.line([e2, (900, 180)], fill=ORANGE, width=4)
    draw.line([e2, (1760, 180)], fill=ORANGE, width=4)
    draw.line([(1030, 240), (1030, 760)], fill=BLUE, width=3)
    draw.line([(1630, 240), (1630, 760)], fill=BLUE, width=3)
    text(draw, (1010, 730), "1.5", 26, BLUE, True, "ra")
    text(draw, (1650, 730), "1.5", 26, BLUE, True)
    text(draw, (1330, 300), "PISOTÓN", 34, GREEN, True, "ma")
    text(draw, (1330, 342), "ángulo >= 60° y horizontal <= 1.5", 24, GREEN, True, "ma")
    text(draw, (1110, 540), "60°", 26, ORANGE, True, "ma")

    cube2 = (1330, 470)
    draw.rectangle([cube2[0] - 30, cube2[1] - 30, cube2[0] + 30, cube2[1] + 30],
                   outline=ORANGE, width=3)
    text(draw, (1330, 520), "cubo", 24, BODY, True, "ma")

    outside = (1540, 620)
    dashed(draw, (outside[0] - 34, outside[1] - 34),
           (outside[0] + 34, outside[1] + 34), PINK, 3, 8, 6)
    dashed(draw, (outside[0] - 34, outside[1] + 34),
           (outside[0] + 34, outside[1] - 34), PINK, 3, 8, 6)
    text(draw, (1580, 600), "no pisotón", 24, PINK, True)

    text(draw, (60, 862), "ángulo = atan2(dy, horizontal) × 180 / PI", 28, INK, True)
    text(draw, (930, 862), "if (ángulo >= 60 && horizontal <= 1.5)", 26, INK, True)

    image.save(OUT / "angulo-pisoton.png")
    print("angulo-pisoton.png", image.size)


def persecucion():
    image, draw = background(1300, 700)

    panels = [
        (30, "Fuera del radio", "va a la esquina", False),
        (680, "Dentro del radio", "va al cubo", True),
    ]
    for x0, title, subtitle, inside in panels:
        x1 = x0 + 590
        draw.rounded_rectangle([x0, 80, x1, 640], radius=18, fill=WHITE,
                               outline=LINE, width=3)
        cx, cy = x0 + 295, 350
        radius = 180
        dashed_circle(draw, (cx, cy), radius, (210, 216, 228), 4)
        text(draw, (x0 + 22, 98), title, 30, INK, True)
        text(draw, (x0 + 22, 138), subtitle, 24, MUTED, True)

        draw.rounded_rectangle([cx - 27, cy - 27, cx + 27, cy + 27], radius=5,
                               fill=BLUE, outline=WHITE, width=3)
        text(draw, (cx + 38, cy - 12), "cubo", 24, BLUE, True)
        text(draw, (cx + 40, cy + 195), "radio = 3.0", 23, MUTED)

        if inside:
            sphere = (cx - 130, cy + 110)
            arrow(draw, sphere, (cx - 36, cy + 32), ORANGE, 5, 14)
        else:
            sphere = (x0 + 75, 560)
            corner = (x0 + 75, 170)
            arrow(draw, sphere, corner, GREEN, 5, 14)
            dot(draw, corner, 7, GREEN, WHITE, 3)
            text(draw, (corner[0] + 14, corner[1] - 10), "esquina", 23, GREEN, True)

        dot(draw, sphere, 22, ORANGE, WHITE, 4)
        text(draw, (sphere[0] - 4, sphere[1] + 30), "esfera", 23, INK, True, "ma")

    image.save(OUT / "persecucion.png")
    print("persecucion.png", image.size)


def autocrop(name, margin=40):
    path = OUT / name
    im = Image.open(path).convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((0, 0)))
    bbox = ImageChops.difference(im, bg).getbbox()
    if bbox:
        left = max(0, bbox[0] - margin)
        top = max(0, bbox[1] - margin)
        right = min(im.width, bbox[2] + margin)
        bottom = min(im.height, bbox[3] + margin)
        im.crop((left, top, right, bottom)).save(path)
        print("recortada", name, (right - left, bottom - top))


if __name__ == "__main__":
    patrulla()
    vector_resta()
    vector_suma()
    normalizacion()
    distancia()
    angulo_pisoton()
    persecucion()
    for name in ("patrulla.png", "vector_resta.png", "vector_suma.png",
                 "normalizacion.png", "distancia.png", "angulo-pisoton.png",
                 "persecucion.png"):
        autocrop(name)
