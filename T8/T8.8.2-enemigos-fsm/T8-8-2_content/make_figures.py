"""Dibuja las figuras de T8.8.2 con el estilo de la plantilla."""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figuras"
OUT.mkdir(exist_ok=True)

REG = str(ROOT / "fonts" / "Neuromax-Regular.otf")
SEM = str(ROOT / "fonts" / "Neuromax-SemiBold.otf")
INK = (19, 19, 21)
BODY = (79, 83, 97)
MUTED = (107, 114, 128)
ORANGE = (240, 138, 60)
ORANGE_D = (180, 83, 9)
BLUE = (59, 111, 212)
PINK = (232, 56, 109)
GREEN = (46, 139, 87)
LINE = (217, 222, 232)
SOFT = (244, 247, 250)
WALL = (190, 194, 205)
S = 2


def F(path, size):
    return ImageFont.truetype(path, int(size * S))


def canvas(w, h):
    im = Image.new("RGB", (w * S, h * S), "white")
    return im, ImageDraw.Draw(im)


def save(im, name):
    im.resize((im.width // S, im.height // S), Image.LANCZOS).save(OUT / name)


def rrect(d, box, r, fill, outline=None, width=1):
    d.rounded_rectangle([v * S for v in box], radius=r * S, fill=fill,
                        outline=outline, width=width * S)


def text(d, xy, value, font, color=INK, anchor="la", spacing=4):
    d.multiline_text((xy[0] * S, xy[1] * S), value, font=font, fill=color,
                     anchor=anchor, spacing=spacing * S)


def arrow(d, p0, p1, color, w=3, head=13):
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    p0 = (p0[0] + math.cos(a) * 2, p0[1] + math.sin(a) * 2)
    p1 = (p1[0] - math.cos(a) * 4, p1[1] - math.sin(a) * 4)
    d.line([(p0[0] * S, p0[1] * S), (p1[0] * S, p1[1] * S)],
           fill=color, width=w * S)
    pts = [(p1[0] * S, p1[1] * S)]
    for s in (0.48, -0.48):
        pts.append(((p1[0] - head * math.cos(a + s)) * S,
                    (p1[1] - head * math.sin(a + s)) * S))
    d.polygon(pts, fill=color)


# ---------------------------------------------------------------- FSM
def fig_fsm():
    im, d = canvas(1200, 600)
    text(d, (40, 26), "La FSM del enemigo", F(SEM, 34), INK)

    box_w, box_h = 300, 150
    pat = (150, 100, 150 + box_w, 100 + box_h)
    per = (690, 100, 690 + box_w, 100 + box_h)
    mue = (420, 390, 420 + box_w, 390 + box_h)

    def state(box, title, sub, accent, dark):
        rrect(d, box, 18, "white", LINE, 2)
        d.rounded_rectangle([box[0] * S, box[1] * S, (box[0] + 10) * S,
                             box[3] * S], radius=6 * S, fill=accent)
        text(d, (box[0] + 32, box[1] + 20), title, F(SEM, 30), dark)
        text(d, (box[0] + 32, box[1] + 64), sub, F(REG, 18), BODY, spacing=6)

    state(pat, "Patrullar", "elige una celda libre\ny camina con BFS", ORANGE, ORANGE_D)
    state(per, "Perseguir", "recalcula el camino\na Velma cada 0.25 s", BLUE, BLUE)
    state(mue, "Muerto", "se acuesta en el suelo\ny ya no se mueve", PINK, PINK)

    text(d, (34, 160), "Start()", F(SEM, 20), MUTED)
    arrow(d, (90, 175), (145, 175), MUTED, 3, 12)

    arrow(d, (455, 145), (685, 145), GREEN, 4, 14)
    text(d, (570, 112), "VeJugador() == true", F(SEM, 19), GREEN, anchor="ma")

    arrow(d, (685, 210), (455, 210), BLUE, 4, 14)
    text(d, (570, 222), "camino == null", F(SEM, 19), BLUE, anchor="ma")

    arrow(d, (330, 255), (450, 385), PINK, 4, 14)
    arrow(d, (850, 255), (735, 385), PINK, 4, 14)
    text(d, (570, 325), "RecibirPatada()\ndesde fuera del cono", F(SEM, 18), PINK,
         anchor="ma", spacing=5)

    rrect(d, (150, 540, 1050, 585), 12, SOFT, LINE, 1)
    text(d, (172, 550),
         "ChangeState(): Exit() del estado actual, luego Enter() del nuevo.",
         F(REG, 18), BODY)

    save(im, "fsm_diagrama.png")


# ---------------------------------------------------------------- cono
def fig_cono():
    im, d = canvas(820, 620)
    ox, oy = 190, 330
    r = 270
    scale = r / 8.0

    for i in range(-8, 9):
        x = ox + i * scale
        d.line([(x * S, 40 * S), (x * S, 580 * S)], fill=(238, 241, 246), width=1 * S)
        y = oy + i * scale
        d.line([(20 * S, y * S), (800 * S, y * S)], fill=(238, 241, 246), width=1 * S)

    a1 = math.radians(-45)
    a2 = math.radians(45)
    p1 = (ox + r * math.cos(a1), oy + r * math.sin(a1))
    p2 = (ox + r * math.cos(a2), oy + r * math.sin(a2))
    d.polygon([(ox * S, oy * S), (p1[0] * S, p1[1] * S), (p2[0] * S, p2[1] * S)],
              fill=(209, 236, 218))
    d.line([(ox * S, oy * S), (p1[0] * S, p1[1] * S)], fill=GREEN, width=3 * S)
    d.line([(ox * S, oy * S), (p2[0] * S, p2[1] * S)], fill=GREEN, width=3 * S)
    d.arc([(ox - r) * S, (oy - r) * S, (ox + r) * S, (oy + r) * S],
          -45, 45, fill=GREEN, width=3 * S)

    d.ellipse([(ox - 16) * S, (oy - 16) * S, (ox + 16) * S, (oy + 16) * S],
              fill=ORANGE, outline=ORANGE_D, width=2 * S)
    text(d, (ox, oy + 1), "E", F(SEM, 18), "white", anchor="mm")

    arrow(d, (ox + 20, oy), (ox + 210, oy), ORANGE_D, 4, 14)
    text(d, (ox + 112, oy - 42), "forward", F(SEM, 28), ORANGE_D, anchor="ma")

    vx = ox + math.cos(math.radians(-24)) * 6.4 * scale
    vy = oy + math.sin(math.radians(-24)) * 6.4 * scale
    d.rounded_rectangle([(vx - 20) * S, (vy - 34) * S, (vx + 20) * S, (vy + 34) * S],
                        radius=8 * S, fill=PINK, outline=(150, 20, 70), width=2 * S)
    text(d, (vx, vy), "V", F(SEM, 22), "white", anchor="mm")
    d.line([(ox * S, oy * S), (vx * S, vy * S)], fill=PINK, width=3 * S)

    text(d, (ox + 250, oy + 48), "rango = 8", F(SEM, 26), BODY)
    text(d, (ox + 92, oy - 122), "45°", F(SEM, 28), GREEN)
    d.arc([(ox - 110) * S, (oy - 110) * S, (ox + 110) * S, (oy + 110) * S],
          -45, 0, fill=GREEN, width=2 * S)
    text(d, (vx + 34, vy - 34), "Velma", F(SEM, 26), PINK)

    save(im, "vision_cono.png")


# ---------------------------------------------------------------- frames
def fig_frames():
    sheet = Image.open(ROOT.parent.parent / "Unity_Sample" / "Sample_Game" /
                       "Assets" / "Images" / "velma_sprite_kick2.png").convert("RGBA")
    rects = [(32, 0, 56, 101), (100, 0, 61, 101), (178, 0, 53, 101),
             (247, 0, 70, 101), (327, 0, 65, 101), (406, 0, 58, 101)]
    times = ["0.00 s", "0.08 s", "0.17 s", "0.25 s", "0.33 s", "0.42 s"]

    im, d = canvas(1200, 360)
    text(d, (30, 18), "VelmaKick: 6 sprites a 12 fps", F(SEM, 30), INK)
    text(d, (30, 60), "El clip dura 0.5 segundos y no se repite.", F(REG, 18), BODY)

    x0, y0 = 64, 100
    step = 178
    for i, (rect, t) in enumerate(zip(rects, times)):
        x = x0 + i * step
        rrect(d, (x - 34, y0 - 18, x + 100, y0 + 220), 12, SOFT, LINE, 1)
        sprite = sheet.crop((rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]))
        bbox = sprite.getbbox()
        if bbox:
            sprite = sprite.crop(bbox)
        scale = 180 / sprite.height
        sprite = sprite.resize((max(1, int(sprite.width * scale)), 180),
                               Image.Resampling.BILINEAR)
        px = int((x + 33 - sprite.width / 2) * S)
        im.paste(sprite, (px, int((y0 + 8) * S)), sprite)
        text(d, (x + 36, y0 - 12), f"Frame {i}", F(SEM, 17), MUTED, anchor="ma")
        text(d, (x + 36, y0 + 214), t, F(SEM, 19), INK, anchor="ma")

    text(d, (600, 342), "cada 1/12 s cambia el sprite", F(REG, 17), MUTED, anchor="ma")
    save(im, "frames_patada.png")


# ---------------------------------------------------------------- fricción
def fig_friccion():
    im, d = canvas(1100, 520)
    text(d, (36, 24), "El problema de la fricción", F(SEM, 32), INK)

    panels = [(36, "CON FRICCIÓN", PINK, "se atora"),
              (566, "SIN FRICCIÓN", GREEN, "se desliza")]

    for x0, title, color, result in panels:
        rrect(d, (x0, 92, x0 + 498, 470), 18, "white", LINE, 2)
        text(d, (x0 + 24, 108), title, F(SEM, 22), color)

        d.rectangle([(x0 + 380) * S, 160 * S, (x0 + 450) * S, 400 * S],
                    fill=WALL, outline=(140, 145, 160), width=2 * S)
        text(d, (x0 + 415, 420), "pared", F(REG, 16), MUTED, anchor="ma")

        px, py = x0 + 300, 255
        d.rounded_rectangle([(px - 34) * S, (py - 34) * S, (px + 34) * S, (py + 34) * S],
                            radius=8 * S, fill=(255, 214, 232), outline=PINK, width=2 * S)
        text(d, (px, py), "V", F(SEM, 22), PINK, anchor="mm")

        arrow(d, (px - 60, py + 70), (px + 52, py - 30), BLUE, 4, 12)
        text(d, (px - 66, py + 78), "input", F(SEM, 16), BLUE)

        if color == PINK:
            arrow(d, (px + 50, py - 78), (px + 50, py + 2), PINK, 4, 12)
            text(d, (px + 66, py - 92), "fricción", F(SEM, 16), PINK)
            text(d, (x0 + 250, 348), "la pared frena el movimiento", F(REG, 16), BODY,
                 anchor="ma")
        else:
            arrow(d, (px + 48, py + 10), (px + 48, py - 90), GREEN, 4, 12)
            text(d, (px + 66, py - 112), "velocidad", F(SEM, 16), GREEN)
            text(d, (x0 + 250, 348), "la velocidad no se frena", F(REG, 16), BODY,
                 anchor="ma")

        rrect(d, (x0 + 148, 398, x0 + 350, 438), 10, color, None, 0)
        text(d, (x0 + 249, 418), result, F(SEM, 20), "white", anchor="mm")

    text(d, (36, 486),
         "Friction Combine = Minimum: Unity toma el valor más bajo de los dos colliders.",
         F(REG, 17), BODY)
    save(im, "friccion.png")


if __name__ == "__main__":
    fig_fsm()
    fig_cono()
    fig_frames()
    fig_friccion()
    print("figuras listas")
