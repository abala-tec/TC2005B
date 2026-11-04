"""Genera las figuras de T8.6.2: escala del plano, cámara y spawner."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)


def text(draw, xy, value, size=36, color=INK, sem=False, anchor="la"):
    draw.text(xy, value, font=font(SEM if sem else REG, size),
              fill=color, anchor=anchor)


def arrow(draw, p0, p1, color=ORANGE, width=6, head=18):
    draw.line([p0, p1], fill=color, width=width)
    import math
    angle = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for sign in (-0.5, 0.5):
        x = p1[0] - head * math.cos(angle + sign)
        y = p1[1] - head * math.sin(angle + sign)
        draw.line([p1, (x, y)], fill=color, width=width)


def dashed(draw, p0, p1, color=LINE, width=3, dash=14, gap=10):
    import math
    x0, y0 = p0
    x1, y1 = p1
    total = math.hypot(x1 - x0, y1 - y0)
    if total == 0:
        return
    ux, uy = (x1 - x0) / total, (y1 - y0) / total
    pos = 0
    while pos < total:
        end = min(pos + dash, total)
        draw.line([(x0 + ux * pos, y0 + uy * pos),
                   (x0 + ux * end, y0 + uy * end)], fill=color, width=width)
        pos = end + gap


def dot(draw, p, r=12, color=ORANGE, outline=WHITE, outline_w=4):
    draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r],
                 fill=color, outline=outline, width=outline_w)


def background(w, h):
    image = Image.new("RGB", (w, h), WHITE)
    draw = ImageDraw.Draw(image)
    for x in range(0, w, 60):
        draw.line([(x, 0), (x, h)], fill=(247, 249, 252))
    for y in range(0, h, 60):
        draw.line([(0, y), (w, y)], fill=(247, 249, 252))
    return image, draw


def plano_escala():
    w, h = 1800, 900
    image, draw = background(w, h)

    # Panel izquierdo: plano original
    text(draw, (60, 60), "ANTES", 34, MUTED, True)
    text(draw, (60, 110), "Plano de 10 × 10", 54, INK, True)
    text(draw, (60, 180), "El cubo nace cerca de una esquina.", 30, BODY)
    x0, y0, s = 120, 300, 420
    draw.rectangle([x0, y0, x0 + s, y0 + s], fill=GREEN_SOFT, outline=GREEN, width=5)
    # grid suave
    for i in range(1, 10):
        gx = x0 + s * i / 10
        gy = y0 + s * i / 10
        draw.line([(gx, y0), (gx, y0 + s)], fill=(203, 228, 214), width=2)
        draw.line([(x0, gy), (x0 + s, gy)], fill=(203, 228, 214), width=2)
    draw.rectangle([x0 + s - 70, y0 + 40, x0 + s - 10, y0 + 100],
                   fill=ORANGE, outline=WHITE, width=4)
    text(draw, (x0 + s - 40, y0 + 140), "Cube", 26, BODY, True, "ma")
    text(draw, (x0 + s / 2, y0 + s + 24), "10 unidades", 28, BODY, False, "ma")

    # Panel derecho: plano escalado
    text(draw, (960, 60), "DESPUÉS", 34, ORANGE, True)
    text(draw, (960, 110), "Plano de 100 × 100", 54, INK, True)
    text(draw, (960, 180), "El cubo conserva su posición.", 30, BODY)
    x1, y1, s2 = 1020, 300, 420
    draw.rectangle([x1, y1, x1 + s2, y1 + s2], fill=GREEN_SOFT, outline=GREEN, width=5)
    # 10 x 10 celdas
    for i in range(1, 10):
        gx = x1 + s2 * i / 10
        gy = y1 + s2 * i / 10
        draw.line([(gx, y1), (gx, y1 + s2)], fill=(203, 228, 214), width=2)
        draw.line([(x1, gy), (x1 + s2, gy)], fill=(203, 228, 214), width=2)
    draw.rectangle([x1 + s2 - 26, y1 + 12, x1 + s2 - 6, y1 + 32],
                   fill=ORANGE, outline=WHITE, width=2)
    text(draw, (x1 + s2 - 20, y1 + 50), "Cube", 26, BODY, True, "ra")
    text(draw, (x1 + s2 / 2, y1 + s2 + 24), "100 unidades", 28, BODY, False, "ma")

    # flecha entre paneles
    arrow(draw, (700, 510), (940, 510), ORANGE, 8, 22)
    text(draw, (820, 470), "Scale × 10", 32, ORANGE, True, "ma")

    # nota inferior
    draw.rectangle([60, 790, 1740, 850], fill=SOFT)
    text(draw, (90, 806), "El plano crece, pero el cubo no cambia de posición.", 30, BODY)
    image.save(OUT / "plano_escala.png")
    print("plano_escala.png", image.size)


def camara_lerp():
    w, h = 1800, 900
    image, draw = background(w, h)

    text(draw, (60, 50), "LA CÁMARA NO SALTA: SE ACERCA POCO A POCO", 44, INK, True)
    text(draw, (60, 115), "Lerp toma una parte del camino en cada fotograma.", 30, BODY)

    # línea de tiempo
    y = 360
    x0, x1 = 180, 1620
    draw.line([(x0, y), (x1, y)], fill=LINE, width=8)
    for x, label, color in ((x0, "posición actual", MUTED),
                            (x0 + (x1 - x0) * 0.2, "20 %", ORANGE),
                            (x1, "meta", GREEN)):
        dot(draw, (int(x), y), 18, color)
        text(draw, (int(x), y + 34), label, 30, color, True, "ma")

    arrow(draw, (x0 + 60, 290), (x1 - 60, 290), ORANGE, 5, 16)
    text(draw, ((x0 + x1) / 2, 250), "goalPosition", 32, ORANGE, True, "ma")

    # fórmula
    draw.rounded_rectangle([120, 500, 1680, 600], radius=18, fill=SOFT, outline=LINE, width=3)
    text(draw, (900, 550), "smoothedPosition = Lerp(actual, meta, 0.2)",
         36, INK, True, "mm")

    # explicación
    text(draw, (120, 660), "0.2 significa que la cámara recorre el 20 % de la distancia", 32, BODY)
    text(draw, (120, 710), "que le falta en ese fotograma. Por eso el movimiento se ve suave.", 32, BODY)

    draw.rectangle([120, 790, 1680, 850], fill=ORANGE_SOFT)
    text(draw, (150, 806), "La cámara nunca llega de golpe: persigue la meta.", 30, ORANGE, True)
    image.save(OUT / "camara_lerp.png")
    print("camara_lerp.png", image.size)


def spawner_radio():
    w, h = 1800, 900
    image, draw = background(w, h)

    text(draw, (60, 50), "EL SPAWNER REPARTE ENEMIGOS ALREDEDOR", 44, INK, True)
    text(draw, (60, 115), "Cada esfera recibe una posición aleatoria dentro del radio.", 30, BODY)

    # plano
    x0, y0, s = 160, 230, 560
    draw.rectangle([x0, y0, x0 + s, y0 + s], fill=GREEN_SOFT, outline=GREEN, width=6)
    import random
    random.seed(7)
    cx, cy = x0 + s / 2, y0 + s / 2
    radius = s * 0.42
    # círculo
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 outline=ORANGE, width=5)
    # puntos
    for _ in range(50):
        ang = random.random() * 6.283
        dist = radius * (random.random() ** 0.5)
        px = cx + dist * __import__("math").cos(ang)
        py = cy + dist * __import__("math").sin(ang)
        dot(draw, (px, py), 7, (120, 120, 130), WHITE, 2)
    # spawner
    draw.rectangle([cx - 14, cy - 14, cx + 14, cy + 14], fill=ORANGE, outline=WHITE, width=3)
    text(draw, (cx, cy + 34), "Spawner", 26, ORANGE, True, "ma")
    text(draw, (cx, cy - 34), "radio 45", 26, ORANGE, True, "mb")

    # cube corner
    draw.rectangle([x0 + s - 42, y0 + 18, x0 + s - 18, y0 + 42],
                   fill=BLUE, outline=WHITE, width=3)
    text(draw, (x0 + s - 30, y0 + 58), "Cube", 24, BLUE, True, "ma")

    # panel derecho
    px = 900
    text(draw, (px, 230), "CÓMO SE CALCULA", 30, ORANGE, True)
    text(draw, (px, 280), "x = spawn.x + aleatorio(-radio, radio)", 34, INK, True)
    text(draw, (px, 334), "z = spawn.z + aleatorio(-radio, radio)", 34, INK, True)
    text(draw, (px, 410), "La altura se fija en 0.5.", 30, BODY)
    text(draw, (px, 460), "Así la esfera queda apoyada en el plano.", 30, BODY)

    draw.rounded_rectangle([px, 540, 1720, 650], radius=18, fill=SOFT, outline=LINE, width=3)
    text(draw, (px + 30, 566), "50 enemigos · radio 45 · plano de 100 × 100", 30, INK, True)
    text(draw, (px + 30, 610), "Todos caben dentro del plano.", 28, BODY)

    draw.rectangle([px, 710, 1720, 830], fill=ORANGE_SOFT)
    text(draw, (px + 30, 730), "Si usas Random.Range(0, radio),", 30, ORANGE, True)
    text(draw, (px + 30, 774), "las esferas se acumulan en una sola esquina.", 30, BODY)
    image.save(OUT / "spawner_radio.png")
    print("spawner_radio.png", image.size)


if __name__ == "__main__":
    plano_escala()
    camara_lerp()
    spawner_radio()
