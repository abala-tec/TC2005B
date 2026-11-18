"""Diagramas de T8.8.3 con texto grande.

Cada figura declara su tamano minimo en figuras/manifest.json. El build
calcula el tamano efectivo en la diapositiva y falla si baja de 12 pt.
"""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figuras"
OUT.mkdir(exist_ok=True)

REG = str(ROOT / "fonts" / "Neuromax-Regular.otf")
SEM = str(ROOT / "fonts" / "Neuromax-SemiBold.otf")
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

INK = (19, 19, 21)
BODY = (79, 83, 97)
MUTED = (107, 114, 128)
ORANGE = (240, 138, 60)
ORANGE_D = (180, 83, 9)
PINK = (232, 56, 109)
GREEN = (46, 139, 87)
BLUE = (59, 111, 212)
WHITE = (255, 255, 255)
SOFT = (244, 247, 250)
LINE = (217, 222, 232)
DARK = (43, 41, 61)
RED = (200, 48, 48)
TEAL = (38, 166, 154)

S = 2
MIN_SIZE = [10 ** 9]
MANIFEST = {}


def F(path, size):
    MIN_SIZE[0] = min(MIN_SIZE[0], size)
    return ImageFont.truetype(path, size * S)


def canvas(w, h, color=WHITE):
    im = Image.new("RGB", (w * S, h * S), color)
    return im, ImageDraw.Draw(im)


def save(im, w, h, name):
    out = (int(w * 0.65), int(h * 0.65))
    im.resize(out, Image.LANCZOS).save(OUT / name)
    MANIFEST[name] = {"width": w, "height": h, "min_font": MIN_SIZE[0]}
    print(name, out, "min", MIN_SIZE[0])
    MIN_SIZE[0] = 10 ** 9


def box(d, x, y, w, h, fill=WHITE, outline=LINE, r=14, width=2):
    d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S],
                        radius=r * S, fill=fill, outline=outline,
                        width=width * S)


def circle(d, x, y, r, fill=ORANGE, outline=WHITE, width=3):
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S],
              fill=fill, outline=outline, width=width * S)


def txt(d, x, y, value, font, color=INK, anchor="la"):
    d.multiline_text((x * S, y * S), value, font=font, fill=color,
                     anchor=anchor, spacing=6 * S, align="left")


def arrow(d, x1, y1, x2, y2, color=INK, width=3, head=14):
    x1, y1, x2, y2 = x1 * S, y1 * S, x2 * S, y2 * S
    d.line([(x1, y1), (x2, y2)], fill=color, width=width * S)
    ang = math.atan2(y2 - y1, x2 - x1)
    pts = [(x2, y2),
           (x2 - head * S * math.cos(ang - 0.42),
            y2 - head * S * math.sin(ang - 0.42)),
           (x2 - head * S * math.cos(ang + 0.42),
            y2 - head * S * math.sin(ang + 0.42))]
    d.polygon(pts, fill=color)


def path_arrow(d, points, color=INK, width=3, head=14):
    for i in range(len(points) - 1):
        arrow(d, *points[i], *points[i + 1], color=color, width=width,
              head=head if i == len(points) - 2 else 1)


def chip(d, cx, cy, value, font, fg=INK, bg=WHITE, border=LINE):
    tw = d.textlength(value, font=font) / S
    th = font.size / S
    box(d, cx - tw / 2 - 8, cy - th / 2 - 4, tw + 16, th + 8,
        fill=bg, outline=border, r=6, width=1)
    txt(d, cx, cy, value, font, fg, anchor="mm")


def state(d, x, y, w, h, title, fill=WHITE, outline=LINE, accent=None,
          size=32):
    box(d, x, y, w, h, fill=fill, outline=outline, r=12, width=2)
    if accent:
        box(d, x, y, 7, h, fill=accent, outline=accent, r=3, width=1)
    txt(d, x + 16, y + h / 2, title, F(SEM, size), INK, anchor="lm")


def diamond(d, cx, cy, w, h, value, font, fill=SOFT, outline=LINE):
    pts = [(cx * S, (cy - h / 2) * S), ((cx + w / 2) * S, cy * S),
           (cx * S, (cy + h / 2) * S), ((cx - w / 2) * S, cy * S)]
    d.polygon(pts, fill=fill, outline=outline, width=2 * S)
    txt(d, cx, cy, value, font, INK, anchor="mm")


# --------------------------------------------------------- audio piezas
def fig_audio_piezas():
    W, H = 1200, 760
    im, d = canvas(W, H)

    box(d, 40, 20, 1120, 190, fill=SOFT, outline=LINE)
    txt(d, 65, 38, "AUDIOCLIP", F(SEM, 34), ORANGE_D)
    txt(d, 65, 82, "datos, no suena solo", F(REG, 31), BODY)
    files = [("jump-sound.mp3", 65, 130), ("classic_hurt.mp3", 65, 168),
             ("Moog City.mp3", 620, 130),
             ("kick-sound-effect.mp3", 620, 168)]
    for name, x, y in files:
        txt(d, x, y, name, F(MONO, 31), INK)

    arrow(d, 600, 210, 600, 245, ORANGE, width=4, head=16)
    txt(d, 620, 214, "reproduce", F(SEM, 31), ORANGE_D)

    box(d, 240, 245, 720, 260, fill=WHITE, outline=ORANGE, width=3)
    txt(d, 265, 262, "AUDIOSOURCE", F(SEM, 34), ORANGE_D)
    rows = ["Play On Awake: off", "Loop: off",
            "Spatial Blend: 2D", "Efectos: PlayOneShot"]
    for i, row in enumerate(rows):
        txt(d, 275, 310 + i * 42, row, F(REG, 31), BODY)

    arrow(d, 600, 505, 600, 540, BLUE, width=4, head=16)
    txt(d, 620, 512, "mezcla", F(SEM, 31), BLUE)

    box(d, 300, 540, 600, 160, fill=WHITE, outline=BLUE, width=3)
    txt(d, 325, 558, "AUDIO LISTENER", F(SEM, 34), BLUE)
    txt(d, 325, 610, "Main Camera", F(REG, 31), BODY)
    txt(d, 325, 648, "sin el no se oye", F(REG, 31), BODY)

    box(d, 920, 540, 240, 160, fill=SOFT, outline=LINE)
    txt(d, 942, 558, "2D", F(SEM, 34), INK)
    txt(d, 942, 610, "volumen", F(REG, 31), BODY)
    txt(d, 942, 648, "fijo", F(REG, 31), BODY)

    save(im, W, H, "fig_audio_piezas.png")


# --------------------------------------------------------- audio setup
def fig_audio_setup():
    W, H = 1000, 760
    im, d = canvas(W, H)

    box(d, 30, 20, 940, 130, fill=DARK, outline=DARK)
    txt(d, 55, 34, "GAMEOBJECT", F(SEM, 30), (190, 194, 206))
    txt(d, 55, 72, "Sonidos", F(SEM, 36), WHITE)

    box(d, 30, 160, 940, 240, fill=WHITE, outline=LINE)
    txt(d, 55, 176, "AUDIOSOURCE", F(SEM, 32), ORANGE_D)
    rows = [("Play On Awake", "off"), ("Loop", "off"),
            ("Spatial Blend", "2D"), ("Audio Clip", "none")]
    for i, (k, v) in enumerate(rows):
        y = 218 + i * 42
        txt(d, 55, y, k, F(REG, 30), BODY)
        txt(d, 650, y, v, F(SEM, 30), INK)

    box(d, 30, 420, 940, 320, fill=WHITE, outline=LINE)
    txt(d, 55, 436, "S8_SOUNDCONTROL", F(SEM, 32), BLUE)
    files = [("jump", "jump-sound.mp3"),
             ("hit", "classic_hurt.mp3"),
             ("won", "metal-slug-mission-complete.mp3"),
             ("kick", "kick-sound-effect.mp3"),
             ("airWush", "air-whoosh.mp3"),
             ("background", "Moog City.mp3")]
    for i, (field, file) in enumerate(files):
        y = 480 + i * 42
        txt(d, 55, y, field, F(MONO, 30), BLUE)
        txt(d, 280, y, file, F(MONO, 30), INK)

    save(im, W, H, "fig_audio_setup.png")


# --------------------------------------------------------- audio mezcla
def fig_audio_mezcla():
    W, H = 1200, 520
    im, d = canvas(W, H)

    txt(d, 40, 18, "UNA FUENTE, VARIAS VOCES", F(SEM, 34), BODY)

    box(d, 40, 60, 1120, 80, fill=(255, 240, 224), outline=ORANGE, width=2)
    txt(d, 65, 82, "Moog City  ·  loop", F(SEM, 34), ORANGE_D)

    events = [(150, "jump", ORANGE), (400, "air", BLUE),
              (650, "kick", PINK), (900, "hit", GREEN)]
    for x, name, color in events:
        box(d, x, 195, 130, 65, fill=color, outline=color)
        txt(d, x + 65, 227, name, F(SEM, 34), WHITE, anchor="mm")
        d.line([(x + 65) * S, 165 * S, (x + 65) * S, 192 * S],
               fill=color, width=2 * S)

    txt(d, 600, 286, "PlayOneShot", F(SEM, 34), MUTED, anchor="ma")
    arrow(d, 40, 360, 1160, 360, BODY, width=2, head=12)
    txt(d, 40, 374, "0 s", F(REG, 34), MUTED)
    txt(d, 1160, 374, "12 s", F(REG, 34), MUTED, anchor="ra")

    box(d, 40, 420, 1120, 80, fill=SOFT, outline=LINE)
    txt(d, 65, 438, "no corta lo que ya suena", F(SEM, 34), INK)

    save(im, W, H, "fig_audio_mezcla.png")


# --------------------------------------------------------- rock raycast
def fig_rock_raycast():
    W, H = 1200, 700
    im, d = canvas(W, H)

    txt(d, 30, 18, "CLICK EN UNA PIEDRA", F(SEM, 34), ORANGE_D)

    box(d, 900, 170, 190, 130, fill=SOFT, outline=INK, width=3)
    box(d, 868, 205, 36, 70, fill=INK, outline=INK)
    txt(d, 995, 222, "CAMARA", F(SEM, 32), INK, anchor="ma")

    box(d, 680, 140, 70, 310, fill=DARK, outline=DARK)
    txt(d, 715, 470, "PANTALLA", F(SEM, 32), MUTED, anchor="ma")
    d.polygon([(715 * S, 300 * S), (733 * S, 332 * S),
               (722 * S, 330 * S), (718 * S, 342 * S)],
              fill=WHITE, outline=INK)

    box(d, 150, 300, 190, 190, fill=(210, 205, 200), outline=INK, width=3)
    txt(d, 245, 385, "PIEDRA", F(SEM, 32), INK, anchor="mm")

    arrow(d, 880, 235, 350, 385, ORANGE, width=5, head=18)
    txt(d, 430, 170, "ScreenPointToRay", F(MONO, 32), ORANGE_D)
    txt(d, 480, 540, "Physics.Raycast", F(MONO, 32), BODY)
    txt(d, 760, 600, "hit == transform", F(MONO, 32), INK)

    save(im, W, H, "fig_rock_raycast.png")


# --------------------------------------------------------- rock estados
def fig_rock_estados():
    W, H = 1200, 700
    im, d = canvas(W, H)

    state(d, 40, 300, 300, 150, "REPOSO", outline=LINE, accent=GREEN,
          size=35)
    state(d, 450, 60, 310, 150, "ARRASTRANDO", fill=(255, 247, 238),
          outline=ORANGE, accent=ORANGE, size=35)
    state(d, 850, 300, 300, 150, "CAYENDO", outline=LINE, accent=BLUE,
          size=35)

    path_arrow(d, [(340, 345), (390, 345), (390, 135), (446, 135)],
               ORANGE, width=5, head=16)
    chip(d, 390, 232, "click", F(SEM, 35), ORANGE_D)

    path_arrow(d, [(760, 135), (805, 135), (805, 345), (846, 345)],
               BLUE, width=5, head=16)
    chip(d, 805, 232, "soltar", F(SEM, 35), BLUE)

    path_arrow(d, [(985, 440), (985, 600), (190, 600), (190, 444)],
               GREEN, width=5, head=16)
    chip(d, 590, 600, "colision + grid", F(SEM, 35), GREEN)

    save(im, W, H, "fig_rock_estados.png")


# --------------------------------------------------------- rock grid
def fig_rock_grid():
    W, H = 1200, 680
    im, d = canvas(W, H)

    cols, rows, cell = 8, 7, 44

    def draw_grid(ox, oy, blocked, rock, path, title, subtitle, color):
        txt(d, ox, oy - 62, title, F(SEM, 31), INK)
        txt(d, ox, oy - 30, subtitle, F(REG, 27), BODY)
        for r in range(rows):
            for c in range(cols):
                x = ox + c * cell
                y = oy + r * cell
                fill = WHITE
                if (c, r) in blocked:
                    fill = (90, 92, 104)
                elif (c, r) in rock:
                    fill = (244, 180, 160)
                d.rectangle([x * S, y * S, (x + cell) * S, (y + cell) * S],
                            fill=fill, outline=LINE, width=1 * S)
        pts = [(ox + (c + 0.5) * cell, oy + (r + 0.5) * cell)
               for c, r in path]
        for i in range(len(pts) - 1):
            d.line([(pts[i][0] * S, pts[i][1] * S),
                    (pts[i + 1][0] * S, pts[i + 1][1] * S)],
                   fill=color, width=7 * S, joint="curve")
        for i in range(len(pts) - 1):
            arrow(d, *pts[i], *pts[i + 1], color=color, width=7, head=9)
        ex, ey = ox + 1.5 * cell, oy + 1.5 * cell
        circle(d, ex, ey, 15, fill=(130, 80, 160), outline=WHITE, width=3)
        txt(d, ex, ey, "E", F(SEM, 27), WHITE, anchor="mm")
        vx, vy = ox + 6.5 * cell, oy + 5.5 * cell
        circle(d, vx, vy, 15, fill=ORANGE, outline=WHITE, width=3)
        txt(d, vx, vy, "V", F(SEM, 27), WHITE, anchor="mm")

    blocked = {(3, 0), (3, 1), (3, 2), (3, 3),
               (3, 3), (4, 3), (5, 3)}
    before = [(1, 1), (2, 1), (2, 4), (6, 4), (6, 5)]
    after = [(1, 1), (2, 1), (2, 6), (6, 6), (6, 5)]

    draw_grid(40, 110, blocked, set(), before, "ANTES",
              "cruza bajo la pared", BLUE)
    draw_grid(620, 110, blocked, {(4, 4), (5, 4), (4, 5), (5, 5)},
              after, "DESPUES", "rodea la piedra", ORANGE)

    box(d, 40, 500, 1120, 140, fill=SOFT, outline=LINE)
    legend = [((90, 92, 104), "pared o piedra"),
              ((244, 180, 160), "piedra suelta"),
              (BLUE, "camino antes"), (ORANGE, "camino despues")]
    for i, (color, text) in enumerate(legend):
        x = 65 + (i % 2) * 540
        y = 535 + (i // 2) * 45
        d.rectangle([x * S, y * S, (x + 28) * S, (y + 22) * S],
                    fill=color, outline=LINE, width=1 * S)
        txt(d, x + 42, y - 4, text, F(REG, 27), BODY)

    save(im, W, H, "fig_rock_grid.png")


# --------------------------------------------------------- anim concepto
def fig_anim_concepto():
    W, H = 1200, 700
    im, d = canvas(W, H)

    state(d, 40, 300, 170, 90, "Entry", outline=GREEN, accent=GREEN, size=29)
    state(d, 300, 280, 240, 130, "Caminar", fill=(255, 247, 238),
          outline=ORANGE, accent=ORANGE, size=32)
    state(d, 760, 280, 240, 130, "Correr", outline=LINE, accent=BLUE,
          size=32)
    state(d, 180, 80, 240, 90, "Any State", outline=TEAL, accent=TEAL,
          size=29)
    state(d, 760, 80, 240, 90, "Hit", outline=LINE, accent=PINK, size=29)

    arrow(d, 210, 345, 296, 345, GREEN, width=3, head=13)
    arrow(d, 540, 330, 756, 330, INK, width=3, head=13)
    arrow(d, 756, 380, 540, 380, BLUE, width=3, head=13)
    arrow(d, 420, 170, 756, 140, PINK, width=3, head=13)

    chip(d, 648, 302, "run=true", F(MONO, 29), INK)
    chip(d, 648, 410, "run=false", F(MONO, 29), BLUE)
    chip(d, 560, 160, "trigger hit", F(MONO, 29), PINK)

    box(d, 40, 480, 1120, 190, fill=SOFT, outline=LINE)
    lines = ["Estado: un clip activo.",
             "Transicion: flecha con condiciones.",
             "Parametro: lo escribe C#.",
             "Any State: entra desde cualquier estado."]
    for i, line in enumerate(lines):
        txt(d, 65, 505 + i * 40, line, F(REG, 29), BODY)

    save(im, W, H, "fig_anim_concepto.png")


# --------------------------------------------------------- anim velma
def fig_anim_velma():
    W, H = 1600, 800
    im, d = canvas(W, H)

    entry = (40, 430, 180, 80)
    any_s = (40, 220, 220, 80)
    kick = (300, 70, 240, 90)
    drop = (300, 270, 240, 90)
    walk = (650, 390, 260, 100)
    run = (1100, 390, 220, 90)
    jump = (1100, 120, 220, 90)
    duck = (650, 660, 220, 90)

    arrow(d, 220, 470, 646, 440, GREEN, width=3, head=14)
    arrow(d, 260, 260, 296, 130, TEAL, width=3, head=14)
    chip(d, 258, 170, "kick", F(MONO, 31), PINK)
    arrow(d, 260, 280, 296, 320, TEAL, width=3, head=14)
    chip(d, 245, 370, "push", F(MONO, 31), RED)
    arrow(d, 540, 130, 646, 420, PINK, width=3, head=14)
    arrow(d, 540, 320, 646, 460, RED, width=3, head=14)
    arrow(d, 910, 425, 1096, 425, BLUE, width=3, head=14)
    chip(d, 1003, 395, "run=true", F(MONO, 31), BLUE)
    arrow(d, 1100, 465, 914, 465, BLUE, width=3, head=14)
    chip(d, 1003, 495, "run=false", F(MONO, 31), BLUE)
    arrow(d, 830, 390, 1096, 215, BLUE, width=3, head=14)
    chip(d, 965, 280, "jump=true", F(MONO, 31), BLUE)
    arrow(d, 1170, 390, 1170, 215, BLUE, width=3, head=14)
    chip(d, 1290, 300, "jump=true", F(MONO, 31), BLUE)
    path_arrow(d, [(1210, 120), (1210, 60), (780, 60), (780, 386)],
               TEAL, width=3, head=14)
    chip(d, 995, 60, "jump=false", F(MONO, 31), TEAL)
    arrow(d, 760, 490, 760, 656, GREEN, width=3, head=14)
    chip(d, 870, 575, "duck=true", F(MONO, 31), GREEN)
    arrow(d, 720, 660, 720, 494, GREEN, width=3, head=14)
    chip(d, 585, 575, "duck=false", F(MONO, 31), GREEN)

    state(d, *entry, "Entry", outline=GREEN, accent=GREEN, size=32)
    state(d, *any_s, "Any State", outline=TEAL, accent=TEAL, size=31)
    state(d, *kick, "VelmaKick", outline=PINK, accent=PINK, size=32)
    state(d, *drop, "VelmaDrop", outline=RED, accent=RED, size=32)
    state(d, *walk, "VelmaWalking", fill=(255, 240, 224), outline=ORANGE,
          accent=ORANGE, size=32)
    state(d, *run, "VelmaRun", outline=BLUE, accent=BLUE, size=32)
    state(d, *jump, "VelmaJump", outline=BLUE, accent=BLUE, size=32)
    state(d, *duck, "VelmaDuck", outline=GREEN, accent=GREEN, size=32)

    save(im, W, H, "fig_anim_velma.png")


# --------------------------------------------------------- anim exit
def fig_anim_exit():
    W, H = 1200, 500
    im, d = canvas(W, H)

    txt(d, 40, 18, "CLIP VELMAKICK", F(SEM, 34), PINK)

    x0, x1, y = 60, 930, 130
    box(d, x0, y, x1 - x0, 100, fill=(255, 232, 238), outline=PINK, width=3)
    txt(d, (x0 + x1) / 2, y + 32, "VelmaKick", F(SEM, 36), PINK, anchor="ma")
    for i in range(7):
        x = x0 + (x1 - x0) * i / 6
        d.line([(x * S, y * S), (x * S, (y + 100) * S)], fill=PINK,
               width=1 * S)

    d.line([(x1 * S, (y - 20) * S), (x1 * S, (y + 130) * S)],
           fill=RED, width=3 * S)
    chip(d, x1, y - 42, "Exit Time = 1", F(SEM, 34), RED)
    arrow(d, x1 + 8, y + 50, 1020, y + 50, GREEN, width=4, head=16)
    state(d, 1020, 110, 160, 90, "Walking", outline=GREEN, accent=GREEN,
          size=34)

    by = 330
    d.line([(x0 * S, by * S), (x1 * S, by * S)], fill=TEAL, width=3 * S)
    d.line([(x0 * S, (by - 12) * S), (x0 * S, (by + 12) * S)],
           fill=TEAL, width=3 * S)
    d.line([(x1 * S, (by - 12) * S), (x1 * S, (by + 12) * S)],
           fill=TEAL, width=3 * S)
    chip(d, (x0 + x1) / 2, by, "IsName = true", F(MONO, 34), TEAL)

    save(im, W, H, "fig_anim_exit.png")


# --------------------------------------------------------- anim code map
def fig_anim_code_map():
    W, H = 1500, 520
    im, d = canvas(W, H)

    txt(d, 40, 14, "CODIGO C#", F(SEM, 24), BLUE)
    txt(d, 900, 14, "ANIMATOR", F(SEM, 24), ORANGE_D)

    rows = [
        ('SetBool("isRunning", runHeld && input != Vector2.zero)',
         "Walking <-> Run", BLUE),
        ('SetBool("isJumping", !grounded)', "VelmaJump", BLUE),
        ('SetBool("isDucking", value)', "VelmaDuck", GREEN),
        ('SetTrigger("kick")', "Any State -> Kick", PINK),
        ('SetTrigger("push")', "Any State -> Drop", RED),
    ]
    for i, (code, state_name, color) in enumerate(rows):
        y = 58 + i * 88
        box(d, 40, y, 820, 68, fill=DARK, outline=DARK)
        txt(d, 58, y + 20, code, F(MONO, 22), (237, 237, 242))
        arrow(d, 870, y + 34, 900, y + 34, color, width=3, head=13)
        box(d, 910, y, 550, 68, fill=WHITE, outline=color, width=2)
        txt(d, 930, y + 20, state_name, F(SEM, 24), INK)

    save(im, W, H, "fig_anim_code_map.png")


# --------------------------------------------------------- kickback flujo
def fig_kickback_flujo():
    W, H = 1200, 800
    im, d = canvas(W, H)

    def node(x, y, w, h, title, fill=WHITE, outline=LINE):
        box(d, x, y, w, h, fill=fill, outline=outline)
        txt(d, x + w / 2, y + h / 2, title, F(SEM, 32), INK, anchor="mm")

    box(d, 350, 20, 500, 70, fill=DARK, outline=DARK)
    txt(d, 600, 55, "OnCollisionEnter", F(SEM, 32), WHITE, anchor="mm")
    arrow(d, 600, 90, 600, 118, BODY, width=3, head=13)

    node(350, 120, 500, 70, "CheckEnemyHit")
    arrow(d, 600, 190, 600, 218, BODY, width=3, head=13)
    diamond(d, 600, 260, 440, 84, "layer Enemigos?", F(SEM, 32))

    arrow(d, 820, 260, 890, 260, RED, width=3, head=13)
    node(890, 225, 280, 70, "return false", (255, 240, 240), RED)

    arrow(d, 600, 302, 600, 330, BODY, width=3, head=13)
    node(350, 330, 500, 70, "GolpeVelma")
    arrow(d, 600, 400, 600, 428, BODY, width=3, head=13)
    diamond(d, 600, 470, 440, 84, "dentro del cono?", F(SEM, 32))

    arrow(d, 820, 470, 890, 470, RED, width=3, head=13)
    node(890, 435, 280, 70, "return false", (255, 240, 240), RED)

    arrow(d, 600, 512, 600, 540, GREEN, width=3, head=13)
    node(350, 540, 500, 70, "away + normalize", (240, 255, 246), GREEN)
    arrow(d, 600, 610, 600, 638, GREEN, width=3, head=13)
    node(350, 638, 500, 70, "return true", (240, 255, 246), GREEN)

    save(im, W, H, "fig_kickback_flujo.png")


# --------------------------------------------------------- kickback vector
def fig_kickback_vector():
    W, H = 1200, 650
    im, d = canvas(W, H)

    ex, ey = 400, 380
    vx, vy = 700, 520

    d.polygon([(ex * S, ey * S),
               ((ex + 380) * S, (ey - 380) * S),
               ((ex + 380) * S, (ey + 380) * S)],
              fill=(255, 249, 226), outline=(240, 210, 120))

    circle(d, ex, ey, 58, fill=(120, 74, 150), outline=WHITE, width=4)
    txt(d, ex, ey, "E", F(SEM, 33), WHITE, anchor="mm")
    txt(d, ex - 70, ey - 90, "ENEMIGO", F(SEM, 33), INK)

    circle(d, vx, vy, 38, fill=ORANGE, outline=WHITE, width=4)
    txt(d, vx, vy, "V", F(SEM, 33), WHITE, anchor="mm")
    txt(d, vx + 50, vy - 10, "VELMA", F(SEM, 33), ORANGE_D)

    arrow(d, ex, ey, vx, vy, BLUE, width=5, head=17)
    chip(d, (ex + vx) / 2, (ey + vy) / 2 - 34, "away", F(MONO, 33), BLUE)

    ux = (vx - ex) / math.hypot(vx - ex, vy - ey)
    uy = (vy - ey) / math.hypot(vx - ex, vy - ey)
    arrow(d, vx + 38 * ux, vy + 38 * uy,
          vx + 38 * ux + 180 * ux, vy + 38 * uy + 180 * uy,
          GREEN, width=5, head=17)
    txt(d, vx + 235 * ux, vy + 235 * uy, "empuje", F(MONO, 33), GREEN)

    arrow(d, 70, 590, 220, 590, BODY, width=2, head=11)
    arrow(d, 70, 590, 70, 460, BODY, width=2, head=11)
    txt(d, 230, 580, "X", F(SEM, 33), BODY)
    txt(d, 52, 440, "Z", F(SEM, 33), BODY)

    box(d, 520, 30, 650, 210, fill=SOFT, outline=LINE)
    txt(d, 545, 50, "DE CONTACTO A VECTOR", F(SEM, 33), ORANGE_D)
    txt(d, 545, 95, "away = Velma - Enemigo", F(MONO, 33), INK)
    txt(d, 545, 140, "away.y = 0", F(MONO, 33), INK)
    txt(d, 545, 185, "empuje = normalize(away.xz)", F(MONO, 33), GREEN)

    box(d, 40, 650, 1120, 40, fill=(255, 248, 235), outline=ORANGE, width=2)
    txt(d, 60, 657, "si estan juntos: no hay empuje", F(SEM, 33), ORANGE_D)

    save(im, W, H, "fig_kickback_vector.png")


# --------------------------------------------------------- kickback tiempo
def fig_kickback_timeline():
    W, H = 1400, 700
    im, d = canvas(W, H)

    txt(d, 40, 16, "DESPUES DEL CONTACTO", F(SEM, 31), ORANGE_D)

    x0, x1 = 420, 1360
    t0 = 500
    lanes = [("FISICA", 110, BODY), ("UPDATE", 265, BLUE),
             ("ANIMATOR", 455, PINK), ("AUDIO", 620, GREEN)]
    for name, y, color in lanes:
        txt(d, 40, y - 10, name, F(SEM, 31), color)
        d.line([(x0 * S, y * S), (x1 * S, y * S)], fill=LINE, width=1 * S)

    d.line([(t0 * S, 60 * S), (t0 * S, 675 * S)], fill=RED, width=2 * S)
    box(d, t0 - 75, 78, 150, 64, fill=DARK, outline=DARK)
    txt(d, t0, 110, "contacto", F(SEM, 31), WHITE, anchor="mm")
    txt(d, t0 + 8, 42, "t = 0", F(MONO, 31), RED)

    txt(d, 700, 92, "hubo golpe", F(SEM, 31), BODY)
    txt(d, 700, 130, "guarda away", F(REG, 31), BODY)

    box(d, 430, 238, 150, 54, fill=WHITE, outline=BLUE, width=2)
    txt(d, 505, 265, "Update", F(SEM, 31), BLUE, anchor="mm")
    txt(d, 650, 240, "push + impulso", F(MONO, 31), PINK)
    txt(d, 650, 290, "play_hit()", F(MONO, 31), GREEN)

    box(d, 430, 425, 210, 60, fill=(255, 240, 224), outline=ORANGE, width=2)
    txt(d, 535, 455, "Walking", F(SEM, 31), ORANGE_D, anchor="mm")
    box(d, 700, 425, 210, 60, fill=(255, 232, 238), outline=PINK, width=2)
    txt(d, 805, 455, "Drop", F(SEM, 31), PINK, anchor="mm")
    box(d, 970, 425, 210, 60, fill=(255, 240, 224), outline=ORANGE, width=2)
    txt(d, 1075, 455, "Walking", F(SEM, 31), ORANGE_D, anchor="mm")
    arrow(d, 645, 455, 696, 455, PINK, width=2, head=10)
    arrow(d, 914, 455, 966, 455, PINK, width=2, head=10)

    box(d, 585, 595, 150, 50, fill=(240, 255, 246), outline=GREEN, width=2)
    txt(d, 660, 620, "hit", F(SEM, 31), GREEN, anchor="mm")

    box(d, 1000, 220, 360, 110, fill=(255, 248, 235), outline=ORANGE, width=2)
    txt(d, 1020, 240, "en el aire", F(SEM, 31), ORANGE_D)
    txt(d, 1020, 285, "espera", F(REG, 31), BODY)

    save(im, W, H, "fig_kickback_timeline.png")


if __name__ == "__main__":
    fig_audio_piezas()
    fig_audio_setup()
    fig_audio_mezcla()
    fig_rock_raycast()
    fig_rock_estados()
    fig_rock_grid()
    fig_anim_concepto()
    fig_anim_velma()
    fig_anim_exit()
    fig_anim_code_map()
    fig_kickback_flujo()
    fig_kickback_vector()
    fig_kickback_timeline()
    (OUT / "manifest.json").write_text(
        json.dumps(MANIFEST, indent=2, sort_keys=True), encoding="utf-8"
    )
