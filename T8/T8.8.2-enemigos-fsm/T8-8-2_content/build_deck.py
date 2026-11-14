#!/usr/bin/env python3
"""Construye T8.8.2 - Enemigos con máquina de estados finitos.

Sigue la plantilla FINAL-plantilla-videojuegos.pptx: fondo pixel art,
Neuromax, tarjetas blancas y acentos naranja/rosa. El código se muestra
como imagen y se copia en las notas de cada diapositiva.
"""

import os
import sys
import zipfile
from pathlib import Path

from lxml import etree
from PIL import Image
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
PPTX = Path(os.environ.get(
    "DECK_OUT", str(ROOT.parent / "T8.8.2-Enemigos-FSM.pptx")
))

REPO = ROOT.parents[2]
sys.path.insert(0, str(REPO / "video-juegos" / "template"))

from deck_style import (  # noqa: E402
    ROLE_STYLE,
    add_text,
    new_deck,
    role_for_size,
    set_role,
)
from validate_deck import validate  # noqa: E402
from snippets import SNIPPETS  # noqa: E402

# ---------------------------------------------------------------- palette
INK = RGBColor(0x13, 0x13, 0x15)
BODY = RGBColor(0x4F, 0x53, 0x61)
MUTED = RGBColor(0x6B, 0x72, 0x80)
ORANGE = RGBColor(0xF0, 0x8A, 0x3C)
ORANGE_TEXT = RGBColor(0xB4, 0x53, 0x09)
PINK = RGBColor(0xE8, 0x38, 0x6D)
YELLOW = RGBColor(0xFF, 0xC4, 0x00)
GREEN = RGBColor(0x2E, 0x8B, 0x57)
BLUE = RGBColor(0x3B, 0x6F, 0xD4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x2B, 0x29, 0x3D)
SOFT = RGBColor(0xF4, 0xF7, 0xFA)
LINE = RGBColor(0xD9, 0xDE, 0xE8)

REG = "Neuromax"
SEM = "Neuromax SemBd"

SW, SH = 13.333, 7.5


# ---------------------------------------------------------------- text
def _font(run, size, color=INK, font=REG, bold=False, italic=False):
    if color == ORANGE and size <= 16:
        color = ORANGE_TEXT
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color


def text(slide, x, y, w, h, value, size=None, color=INK, font=REG,
         bold=False, italic=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, line_spacing=1.0, space_after=0, role=None):
    if role is None:
        role = role_for_size(size, font, bold)
    elif (font == SEM or bold) and role in {"body", "note", "subtitle"}:
        role += "_strong"
    if color == ORANGE and ROLE_STYLE[role].size <= 16:
        color = ORANGE_TEXT
    return add_text(slide, x, y, w, h, value, role, color=color,
                    italic=italic, align=align, anchor=anchor,
                    line_spacing=line_spacing, space_after=space_after)


def rect(slide, x, y, w, h, fill=WHITE, line=None, line_w=1.0,
         shape=MSO_SHAPE.RECTANGLE):
    shp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(line_w)
    shp.shadow.inherit = False
    style = shp._element.find(qn("p:style"))
    if style is not None:
        shp._element.remove(style)
    return shp


def circle(slide, x, y, d, fill=ORANGE, line=WHITE, line_w=1.0):
    return rect(slide, x, y, d, d, fill, line, line_w, MSO_SHAPE.OVAL)


def picture_fit(slide, path, x, y, w, h, border=True, border_w=1.2,
                border_color=WHITE):
    im = Image.open(path)
    iw, ih = im.size
    scale = min(w / iw, h / ih)
    nw, nh = iw * scale, ih * scale
    left, top = x + (w - nw) / 2, y + (h - nh) / 2
    pic = slide.shapes.add_picture(str(path), Inches(left), Inches(top),
                                   Inches(nw), Inches(nh))
    if border:
        pic.line.color.rgb = border_color
        pic.line.width = Pt(border_w)
    return pic


def picture_fill(slide, path, x, y, w, h, border=True, border_w=1.2):
    im = Image.open(path)
    iw, ih = im.size
    ratio = iw / ih
    target = w / h
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y),
                                   Inches(w), Inches(h))
    if ratio > target:
        crop = (1 - target / ratio) / 2
        pic.crop_left = crop
        pic.crop_right = crop
    else:
        crop = (1 - ratio / target) / 2
        pic.crop_top = crop
        pic.crop_bottom = crop
    if border:
        pic.line.color.rgb = WHITE
        pic.line.width = Pt(border_w)
    return pic


def bg(slide):
    slide.shapes.add_picture(str(ROOT / "bg.png"), 0, 0,
                             Inches(SW), Inches(SH))


def header(slide, kicker, title, subtitle):
    rect(slide, 0.62, 0.30, 0.09, 0.09, ORANGE)
    text(slide, 0.81, 0.27, 10.5, 0.22, kicker, role="label", color=INK)
    text(slide, 0.62, 0.52, 11.95, 0.72, title, role="title", color=INK,
         line_spacing=0.95)
    text(slide, 0.62, 1.18, 11.95, 0.40, subtitle, role="body", color=BODY)


def footer(slide, value, y=6.18, h=0.50):
    rect(slide, 0.55, y, 11.80, h, WHITE)
    text(slide, 0.75, y + 0.12, 11.40, 0.28, value, role="footer", color=BODY)


def notes(slide, value):
    slide.notes_slide.notes_text_frame.text = value


def notes_code(slide, intro, blocks, extra=""):
    value = intro.strip()
    for path, code in blocks:
        value += "\n\nCÓDIGO DE LA DIAPOSITIVA (" + path + "):\n\n"
        value += code.strip("\n")
    if extra:
        value += "\n\n" + extra.strip()
    slide.notes_slide.notes_text_frame.text = value


def card(slide, x, y, w, h, accent=ORANGE, fill=WHITE, line=None):
    rect(slide, x, y, w, h, fill, line)
    rect(slide, x, y, 0.07, h, accent)


def label(slide, x, y, w, value, color=ORANGE_TEXT, size=None):
    text(slide, x, y, w, 0.22, value, role="label", color=color)


def pill(slide, x, y, w, value, color=BODY, fill=WHITE, size=None):
    rect(slide, x, y, w, 0.26, fill, LINE, 0.75, MSO_SHAPE.ROUNDED_RECTANGLE)
    text(slide, x, y + 0.04, w, 0.18, value, role="pill", color=color,
         align=PP_ALIGN.CENTER)


def shot(slide, name_or_path, x, y, w, h, pad=0.07):
    path = name_or_path if isinstance(name_or_path, Path) else ROOT / "img" / name_or_path
    rect(slide, x, y, w, h, WHITE, LINE, 0.8)
    return picture_fit(slide, path, x + pad, y + pad, w - 2 * pad, h - 2 * pad,
                       border=False)


def fig(slide, path, x, y, w, h):
    rect(slide, x, y, w, h, WHITE, LINE, 1.0)
    return picture_fit(slide, path, x + 0.08, y + 0.08, w - 0.16, h - 0.16,
                       border=False)


def code(slide, name, x, y, w, h, border=True):
    return picture_fit(slide, ROOT / "codigo" / name, x, y, w, h,
                       border=border, border_w=1.0)


def table(slide, x, y, w, h, rows, col_widths, font_size=None,
          header_size=None, row_h=None, align=PP_ALIGN.LEFT):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y),
                                   Inches(w), Inches(h))
    set_role(shape, "table")
    tbl = shape.table
    tbl.first_row = True
    tbl.horz_banding = False
    tblPr = tbl._tbl.tblPr
    for old in tblPr.findall(qn("a:tableStyleId")):
        tblPr.remove(old)
    style = tblPr.makeelement(qn("a:tableStyleId"), {})
    style.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"
    tblPr.append(style)

    for j, cw in enumerate(col_widths):
        tbl.columns[j].width = Inches(cw)
    if row_h:
        for i in range(len(rows)):
            tbl.rows[i].height = Inches(row_h[i] if isinstance(row_h, list) else row_h)

    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            cell = tbl.cell(i, j)
            cell.text = ""
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = align
            p.line_spacing = 0.95
            p.space_before = Pt(0)
            p.space_after = Pt(0)
            r = p.add_run()
            r.text = str(value)
            cell_role = "table_head" if i == 0 else "table_body"
            cell_style = ROLE_STYLE[cell_role]
            _font(r, cell_style.size,
                  WHITE if i == 0 else INK, cell_style.font, cell_style.bold)
            cell.fill.solid()
            cell.fill.fore_color.rgb = DARK if i == 0 else (WHITE if i % 2 == 1 else SOFT)
            cell.margin_left = Inches(0.09)
            cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.03)
            cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    return tbl


def bullets(slide, x, y, w, items, size=None, gap=0.66, color=BODY,
            bullet_color=ORANGE_TEXT):
    role = "body"
    for i, item in enumerate(items):
        text(slide, x, y + i * gap, 0.18, 0.3, "•", role="bullet",
             color=bullet_color)
        text(slide, x + 0.24, y + i * gap, w - 0.24, gap, item, role=role,
             color=color, line_spacing=1.02)


def steps(slide, x, y, w, items, size=None, gap=0.52, color=ORANGE):
    role = "body"
    for i, item in enumerate(items):
        yy = y + i * gap
        circle(slide, x, yy - 0.02, 0.30, color)
        text(slide, x, yy - 0.02, 0.30, 0.30, str(i + 1), role="step_number",
             color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(slide, x + 0.44, yy, w - 0.44, gap, item, role=role,
             color=BODY, line_spacing=1.0)


def section_slide(prs, number, title, subtitle, tags, color):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    text(s, 0.62, 0.98, 2.0, 1.0, number, role="section", color=color)
    text(s, 0.62, 1.92, 8.20, 1.60, title, role="section", color=INK,
         line_spacing=0.92)
    rect(s, 0.62, 3.85, 2.20, 0.07, color)
    text(s, 0.62, 4.12, 7.20, 0.90, subtitle, role="subtitle", color=INK,
         line_spacing=1.02)
    text(s, 0.62, 5.22, 8.00, 0.30, tags, role="label", color=BODY)
    picture_fit(s, ROOT / "decor" / "star.png", 9.56, 1.10, 1.10, 1.10, border=False)
    picture_fit(s, ROOT / "decor" / "mushroom.png", 11.35, 3.35, 0.95, 0.95, border=False)
    picture_fit(s, ROOT / "decor" / "cloud-low.png", 9.55, 4.95, 2.45, 1.40, border=False)
    picture_fit(s, ROOT / "decor" / "tree-small.png", 11.75, 4.75, 0.85, 1.55, border=False)
    return s



# ---------------------------------------------------------------- ayudas
CS = "Assets/Scripts/escena7_fsm/EnemigoFSM/EnemigoCilindro.cs"
CSE = "Assets/Scripts/escena7_fsm/S7_VelmaWalk_3D.cs"
FIG = ROOT / "figuras"


def snip(name):
    return SNIPPETS[name][0]


def nc(slide, intro, names, extra="", path=CS):
    notes_code(slide, intro, [(path, snip(n)) for n in names], extra)


def code_img(slide, name, x, y, w, h):
    path = ROOT / "codigo" / (name + ".png")
    iw, ih = Image.open(path).size
    sc = min(w / iw, h / ih)
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y),
                                    Inches(iw * sc), Inches(ih * sc))


def new_slide():
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    return s


def cap(slide, x, y, w, value):
    text(slide, x, y, w, 0.30, value, role="caption", color=MUTED)


def tip(slide, x, y, w, h, title, body, accent=ORANGE):
    card(slide, x, y, w, h, accent)
    text(slide, x + 0.24, y + 0.10, w - 0.40, 0.30, title, role="body",
         font=SEM, color=INK)
    text(slide, x + 0.24, y + 0.44, w - 0.40, h - 0.50, body, role="note",
         color=BODY, line_spacing=1.0)


def tbl(slide, x, y, w, rows, cols, row_h=0.46, head_h=0.46):
    h = head_h + row_h * (len(rows) - 1)
    return table(slide, x, y, w, h, rows, cols,
                 row_h=[head_h] + [row_h] * (len(rows) - 1))


def figure(slide, name, x, y, w, h):
    return fig(slide, FIG / name, x, y, w, h)


def fmt(c):
    return f"({c[0]},{c[1]})"



# ---------------------------------------------------------------- deck
prs = new_deck()
prs.core_properties.title = "T8.8.2 · Enemigos con máquina de estados finitos"
prs.core_properties.author = "TC2005B · Construcción de Software"
prs.core_properties.subject = "FSM, visión, patada y material sin fricción en Unity"
prs.core_properties.keywords = "Unity, C#, FSM, enemigos, visión, patada, física, TC2005B"
prs.core_properties.language = "es-MX"

# ---- portada
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
rect(s, 0.62, 0.32, 0.09, 0.09, ORANGE)
text(s, 0.81, 0.28, 10.0, 0.22, "8.8.2 · ENEMIGOS", role="label")
text(s, 0.62, 0.92, 6.00, 2.70, "UNA MÁQUINA\nDE ESTADOS\nPARA EL ENEMIGO", role="section", line_spacing=0.92)
text(s, 0.62, 3.64, 5.70, 0.80,
     "Patrullar, perseguir y morir: tres estados que cambian el comportamiento.",
     role="subtitle", line_spacing=1.02)
text(s, 0.62, 4.65, 5.55, 0.72,
     "La FSM organiza al enemigo. La visión y la patada la conectan con Velma.",
     role="note", color=BODY, line_spacing=1.02)
text(s, 0.62, 5.40, 5.40, 0.28, "TC2005B · Construcción de Software", role="note")
text(s, 0.62, 5.75, 5.40, 0.28, "Unity · C# · escena7_fsm", role="note", color=BODY)
rect(s, 6.55, 0.66, 6.18, 4.95, DARK)
picture_fit(s, ROOT / "img" / "vision_velma_frente.png", 6.75, 0.86, 5.78, 4.55, border=False)
pill(s, 6.95, 0.72, 1.55, "UNITY · C#", WHITE, DARK)
picture_fit(s, ROOT / "decor" / "star.png", 0.55, 6.30, 0.75, 0.75, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 11.55, 6.40, 0.85, 0.85, border=False)
notes(s,
      "Bienvenida al tema 8.8.2. En el tema anterior el enemigo perseguía a Velma con BFS. "
      "Ese comportamiento funcionaba, pero era el único: el enemigo no patrullaba, no moría y no "
      "reaccionaba a una patada.\n\n"
      "Hoy organizamos el comportamiento con una máquina de estados finitos, o FSM. Cada estado "
      "tiene su propio código y el enemigo está en un solo estado a la vez. La imagen de la derecha "
      "es una captura real de la vista Scene: el cono rojo indica que el enemigo ve a Velma.")

# ---- agenda
s = new_slide()
header(s, "HOY", "LO QUE VEREMOS",
       "Tres bloques explican la FSM, la visión y la patada, y cierran con la física de las paredes.")
rows = [
    ("01", "LA FSM DEL ENEMIGO", "La interfaz, la clase que cambia de estado y los estados Patrullar, Perseguir y Muerto.", ORANGE),
    ("02", "LA VISIÓN Y LA PATADA", "El cono de visión, la animación de Velma y la detección del golpe.", BLUE),
    ("03", "LA ESCENA SIN FRICCIÓN", "El material de las paredes y la solución al personaje que se atora.", GREEN),
]
for i, (num, title, desc, color) in enumerate(rows):
    y = 1.70 + i * 1.05
    card(s, 0.62, y, 12.09, 0.92, color)
    text(s, 0.82, y + 0.28, 0.45, 0.30, num, role="card_number", color=color)
    text(s, 1.42, y + 0.10, 10.8, 0.34, title, role="card_title_sm")
    text(s, 1.46, y + 0.50, 11.0, 0.30, desc, role="note", color=BODY)
text(s, 0.62, 4.95, 12.0, 0.40,
     "El bloque 01 es el más importante: ahí está la FSM que controla al enemigo.",
     role="body_strong")
footer(s, "El código se ve como imagen y se copia completo en las notas.")
notes(s,
      "Recorrido del tema.\n\n"
      "1. La FSM del enemigo: la interfaz IEnemyState, la clase EnemyStateMachine y los tres estados. "
      "Este es el bloque principal.\n"
      "2. La visión y la patada: cómo el enemigo detecta a Velma, cómo se anima la patada y cómo se "
      "detecta el golpe.\n"
      "3. La escena sin fricción: el material físico de las paredes y la solución al personaje que se "
      "atoraba.\n\n"
      "Todo el código sale de la carpeta Assets/Scripts/escena7_fsm. Los archivos completos están en "
      "la subcarpeta csharp de este tema.")

# ---- problema
s = new_slide()
header(s, "EL PROBLEMA", "UN ENEMIGO QUE SOLO SABE PERSEGUIR",
       "Sin estados, el enemigo hace lo mismo todo el tiempo y no puede reaccionar.")
items = [
    ("¿Y SI NO VE A VELMA?", "Antes no existía un estado de patrulla. El enemigo se quedaba esperando o repetía el mismo movimiento.", ORANGE),
    ("¿Y SI LA VE?", "Perseguía con BFS, pero no había una transición explícita entre “no la veo” y “la veo”.", BLUE),
    ("¿Y SI LO PATEAN?", "No existía el estado muerto. El enemigo no podía dejar de perseguir ni acostarse en el suelo.", PINK),
]
for i, (title, body, color) in enumerate(items):
    x = 0.62 + i * 4.10
    card(s, x, 1.75, 3.89, 3.05, color)
    text(s, x + 0.24, 1.98, 3.35, 0.42, title, role="card_title_sm", color=color)
    text(s, x + 0.24, 2.55, 3.35, 1.95, body, role="note", color=BODY, line_spacing=1.05)
text(s, 0.62, 5.05, 12.09, 0.50,
     "La solución no es llenar el código de condicionales. La solución es separar cada comportamiento en un estado.",
     role="body_strong")
footer(s, "Una FSM hace explícitos los cambios y evita mezclar toda la lógica en Update().")
notes(s,
      "El problema se entiende con tres preguntas.\n\n"
      "Antes, el cilindro solo perseguía. Si no veía a Velma, seguía calculando el camino o se quedaba "
      "quieto. No tenía una forma clara de patrullar. Tampoco tenía una forma de morir: una patada no "
      "cambiaba su comportamiento.\n\n"
      "La solución no es agregar más if dentro de un solo método. La solución es separar cada "
      "comportamiento en una clase pequeña y dejar que una máquina decida cuál se ejecuta. Eso es una "
      "máquina de estados finitos.")

# ---- FSM
s = new_slide()
header(s, "LA IDEA", "UNA MÁQUINA DE ESTADOS FINITOS",
       "El objeto está en un estado a la vez y cambia cuando se cumple una condición.")
figure(s, "fsm_diagrama.png", 0.62, 1.65, 8.25, 4.45)
tip(s, 9.05, 1.70, 3.66, 1.30, "ESTADO",
    "Comportamiento y datos. Por ejemplo: Patrullar guarda el camino actual.", accent=ORANGE)
tip(s, 9.05, 3.15, 3.66, 1.30, "TRANSICIÓN",
    "Condición que cambia el estado. Por ejemplo: VeJugador() == true.", accent=BLUE)
tip(s, 9.05, 4.60, 3.66, 1.25, "EN CÓDIGO",
    "Enter() al entrar, Execute() en cada frame y Exit() al salir.", accent=GREEN)
footer(s, "La FSM no es un componente de Unity: es una clase de C# que organiza el comportamiento.")
notes(s,
      "Una máquina de estados finitos tiene un conjunto finito de estados y reglas para pasar de uno "
      "a otro. En nuestro caso hay tres estados: Patrullar, Perseguir y Muerto.\n\n"
      "El enemigo está en un solo estado a la vez. El estado actual recibe el control en cada frame. "
      "Cuando se cumple una condición, la máquina llama a Exit() del estado actual y a Enter() del "
      "nuevo. Así cada estado tiene su propio comportamiento y sus propios datos.\n\n"
      "La FSM no es un MonoBehaviour. Es una clase normal de C# que el componente EnemigoCilindro "
      "crea y actualiza. Eso la hace reutilizable y fácil de probar.")

# ---- tres estados
s = new_slide()
header(s, "EL DISEÑO", "PATRULLAR, PERSEGUIR Y MORIR",
       "Cada estado vive en su propio archivo y todos implementan la misma interfaz.")
states = [
    ("01", "PATRULLAR", "EPatrolState.cs",
     "Elige una celda libre al azar y camina con BFS. Si ve a Velma, cambia a Perseguir.", ORANGE),
    ("02", "PERSEGUIR", "EPerseguirState.cs",
     "Recalcula el camino a Velma cada 0.25 s. Si no hay camino, vuelve a Patrullar.", BLUE),
    ("03", "MUERTO", "EMuertoState.cs",
     "Se acuesta en el suelo y deja de ejecutar lógica. Solo se puede morir una vez.", PINK),
]
for i, (num, title, file, body, color) in enumerate(states):
    x = 0.62 + i * 4.10
    card(s, x, 1.70, 3.89, 3.20, color)
    text(s, x + 0.24, 1.92, 0.60, 0.32, num, role="card_number", color=color)
    text(s, x + 0.24, 2.35, 3.35, 0.42, title, role="card_title_sm", color=color)
    text(s, x + 0.24, 2.82, 3.35, 0.26, file, role="label", color=MUTED)
    text(s, x + 0.24, 3.22, 3.35, 1.55, body, role="note", color=BODY, line_spacing=1.05)
    text(s, x + 0.24, 4.35, 3.35, 0.26, ["SALIDA: VeJugador() == true",
         "SALIDA: camino == null o vacío", "ENTRADA: RecibirPatada()"][i], role="label", color=color)
text(s, 0.62, 5.15, 12.09, 0.30, "Las flechas del diagrama anterior son las transiciones que implementa la FSM.",
     role="body")
footer(s, "RecibirPatada() puede llevar a Muerto desde Patrullar o desde Perseguir.")
notes(s,
      "Los tres estados y sus archivos.\n\n"
      "Patrullar: el enemigo toma su celda actual como inicio y una celda libre al azar como destino. "
      "Usa BuscarCamino de S7_Grid, el mismo BFS del tema 8.8.1. Mientras camina, revisa si ve a Velma.\n\n"
      "Perseguir: recalcula el camino desde el enemigo hasta Velma cada 0.25 segundos. Si no hay camino, "
      "vuelve a Patrullar.\n\n"
      "Muerto: rota el cilindro 90 grados, lo baja al suelo y pone la bandera muerto en true. Execute() "
      "no hace nada. La muerte se dispara desde RecibirPatada(), no desde un Update.")

# ---- interfaz
s = new_slide()
header(s, "LA BASE", "TODOS LOS ESTADOS HABLAN EL MISMO IDIOMA",
       "La interfaz IEnemyState obliga a cada estado a implementar cuatro métodos.")
code_img(s, "code_iface", 0.62, 1.70, 6.55, 2.52)
steps(s, 7.55, 1.85, 5.16, [
    "Enter() se ejecuta una vez al entrar al estado.",
    "Execute() se ejecuta en cada frame, desde Update().",
    "Exit() se ejecuta una vez al salir del estado.",
    "DibujarGizmos() dibuja el cono y el camino en la vista Scene.",
], gap=0.92)
footer(s, "Si un estado no implementa los cuatro métodos, el compilador marca error.")
nc(s, "La interfaz IEnemyState define el contrato de todos los estados. No tiene código de "
      "comportamiento: solo declara los cuatro métodos que la máquina va a llamar.\n\n"
      "Enter() se usa para preparar el estado. Execute() contiene la lógica que antes estaba en "
      "Update(). Exit() limpia o avisa que el estado termina. DibujarGizmos() permite ver el cono de "
      "visión y el camino en la vista Scene.\n\n"
      "Como todos los estados implementan la misma interfaz, EnemyStateMachine puede guardarlos en "
      "una variable del tipo IEnemyState y llamarlos sin conocer la clase concreta.",
   ["code_iface"], path="Assets/Scripts/escena7_fsm/EnemigoFSM/IEnemyState.cs")

# ---- ESM
s = new_slide()
header(s, "EL NÚCLEO", "LA CLASE QUE CAMBIA DE ESTADO",
       "EnemyStateMachine guarda el estado actual y llama a sus métodos en el orden correcto.")
code_img(s, "code_esm", 0.62, 1.70, 6.05, 4.40)
steps(s, 7.05, 1.85, 5.66, [
    "Initialize() recibe el primer estado y llama a Enter().",
    "ChangeState() llama a Exit(), cambia el estado y llama a Enter().",
    "Update() llama a Execute() del estado actual.",
    "DibujarGizmos() delega el dibujo al estado actual.",
], gap=0.92)
footer(s, "ChangeState() hace la transición completa: Exit(), cambio de estado y Enter().")
nc(s, "EnemyStateMachine es el núcleo. Guarda una referencia al estado actual con el tipo "
      "IEnemyState.\n\n"
      "Initialize() se usa al empezar: guarda el primer estado y llama a Enter(). No llama a Exit() "
      "porque no hay estado anterior.\n\n"
      "ChangeState() hace la transición completa: Exit() del estado actual, cambia la referencia y "
      "Enter() del nuevo. Update() llama a Execute() si hay un estado válido. DibujarGizmos() hace lo "
      "mismo con el dibujo.\n\n"
      "Esta clase no sabe qué hace cada estado. Solo sabe que todos tienen Enter, Execute, Exit y "
      "DibujarGizmos.",
   ["code_esm"], path="Assets/Scripts/escena7_fsm/EnemigoFSM/EnemyStateMachine.cs")

# ---- enemigo
s = new_slide()
header(s, "EL ENEMIGO", "DONDE ARRANCA LA FSM",
       "EnemigoCilindro crea la máquina, le pasa el control y expone los datos al Inspector.")
code_img(s, "code_enemigo_start", 0.62, 1.70, 5.40, 4.07)
rows = [
    ("Campo", "Valor en la escena"),
    ("jugador", "velma_sprite_walk_3D"),
    ("chace_vel", "3"),
    ("chace_check_time", "0.25 s"),
    ("vision_rango", "8"),
    ("vision_angulo", "90°"),
]
tbl(s, 6.30, 1.72, 6.42, rows, [2.45, 3.97], row_h=0.48, head_h=0.48)
tip(s, 6.30, 4.72, 6.42, 1.15, "ARRANQUE",
    "Start() crea la FSM en Patrullar. Update() llama a esm.Update() en cada frame.", accent=GREEN)
footer(s, "Los valores del Inspector son los que usa la escena escena7_fsm.")
nc(s, "EnemigoCilindro es el MonoBehaviour que está en el GameObject del enemigo. En Start() crea "
      "la máquina y la inicializa con EPatrolState. En Update() llama a esm.Update(); en "
      "OnDrawGizmos() llama a esm.DibujarGizmos().\n\n"
      "Los campos públicos aparecen en el Inspector. jugador apunta a velma_sprite_walk_3D. "
      "chace_vel vale 3 en la escena, chace_check_time 0.25, vision_rango 8 y vision_angulo 90.\n\n"
      "La bandera muerto empieza en false y evita que el estado Muerto rote al enemigo más de una vez.",
   ["code_enemigo_start", "code_enemigo_campos"], path="Assets/Scripts/escena7_fsm/EnemigoFSM/EnemigoCilindro.cs")

# ---- patrullar
s = new_slide()
header(s, "ESTADO 01", "PATRULLAR: CAMINAR SIN RUMBO FIJO",
       "El estado elige una celda libre al azar y usa BFS para llegar sin chocar.")
code_img(s, "code_patrulla", 0.62, 1.70, 6.80, 4.01)
steps(s, 7.70, 1.85, 5.00, [
    "BuscarCamino toma la celda actual del enemigo como inicio.",
    "GetRandomCelda elige una celda libre del grid.",
    "BuscarCamino de S7_Grid calcula la ruta con BFS.",
    "El enemigo camina hacia camino[0] y lo borra al llegar.",
    "BuscarJugador revisa el cono antes de seguir patrullando.",
], gap=0.78)
footer(s, "La patrulla reutiliza el BFS y el grid del tema 8.8.1.")
nc(s, "EPatrolState implementa el estado de patrulla.\n\n"
      "Enter() llama a BuscarCamino(). Ese método toma la celda actual del enemigo y una celda libre "
      "al azar con GetRandomCelda(). Después llama a S7_Grid.BuscarCamino(), que devuelve la lista de "
      "casillas.\n\n"
      "Execute() primero llama a BuscarJugador(). Si el enemigo ve a Velma, cambia a EPerseguirState. "
      "Si el camino es null o está vacío, vuelve a buscar otro destino. Si hay camino, toma camino[0], "
      "convierte la celda a posición del mundo, gira al enemigo hacia esa casilla y avanza con "
      "Vector3.MoveTowards. Cuando llega, borra camino[0] con RemoveAt(0) y sigue con la siguiente.",
   ["code_patrulla"], path="Assets/Scripts/escena7_fsm/EnemigoFSM/EPatrolState.cs",
   extra="Método Execute() completo:\n\n"
         "public void Execute()\n"
         "{\n"
         "    S7_Grid grid = S7_Grid.Instancia;\n"
         "    BuscarJugador();\n"
         "    if (camino == null || camino.Count == 0) { BuscarCamino(); }\n"
         "    Vector3 objetivo = grid.CeldaAMundo(camino[0]);\n"
         "    objetivo.y = enemy.transform.position.y;\n"
         "    Vector3 haciaObjetivo = objetivo - enemy.transform.position;\n"
         "    if (haciaObjetivo.sqrMagnitude > 0.0001f) enemy.transform.rotation = Quaternion.LookRotation(haciaObjetivo);\n"
         "    enemy.transform.position = Vector3.MoveTowards(enemy.transform.position, objetivo, enemy.chace_vel * Time.deltaTime);\n"
         "    if (enemy.transform.position == objetivo) camino.RemoveAt(0);\n"
         "}")

# ---- perseguir
s = new_slide()
header(s, "ESTADO 02", "PERSEGUIR: EL CAMINO HACIA VELMA",
       "El estado recalcula la ruta cada 0.25 s y avanza hacia la primera casilla.")
code_img(s, "code_perseguir", 0.62, 1.70, 6.80, 4.01)
bullets(s, 7.70, 1.80, 5.00, [
    "Resta el tiempo transcurrido al temporizador.",
    "Cada 0.25 s vuelve a llamar a BuscarCamino.",
    "Si no hay camino, cambia a Patrullar.",
    "Avanza hacia camino[0] con MoveTowards.",
], gap=0.72)
tip(s, 7.70, 4.85, 5.00, 1.05, "DETALLE DEL CÓDIGO",
    "La línea que borra camino[0] está comentada. Por eso avanza una casilla por recálculo.", accent=PINK)
footer(s, "Perseguir no revisa si Velma sigue a la vista: solo cambia si no hay camino.")
nc(s, "EPerseguirState implementa el estado de persecución.\n\n"
      "Execute() resta Time.deltaTime al temporizador. Cuando llega a cero, lo reinicia con "
      "chace_check_time y llama a BuscarCamino() desde la celda del enemigo hasta la celda de Velma.\n\n"
      "Si el camino es null o está vacío, cambia a EPatrolState y termina. Si hay camino, toma "
      "camino[0], lo convierte a posición del mundo, gira al enemigo hacia esa casilla y avanza con "
      "Vector3.MoveTowards.\n\n"
      "Detalle importante: en este estado la línea camino.RemoveAt(0) está comentada. Eso hace que el "
      "enemigo avance una casilla por cada recálculo, en lugar de recorrer toda la lista. En Patrullar "
      "la línea sí está activa.",
   ["code_perseguir"], path="Assets/Scripts/escena7_fsm/EnemigoFSM/EPerseguirState.cs",
   extra="Método Execute() completo:\n\n"
         "public void Execute()\n"
         "{\n"
         "    S7_Grid grid = S7_Grid.Instancia;\n"
         "    tiempoRecalculo -= Time.deltaTime;\n"
         "    if (tiempoRecalculo <= 0f)\n"
         "    {\n"
         "        tiempoRecalculo = enemy.chace_check_time;\n"
         "        camino = grid.BuscarCamino(grid.MundoACelda(enemy.transform.position), grid.MundoACelda(enemy.jugador.position));\n"
         "    }\n"
         "    if (camino == null || camino.Count == 0)\n"
         "    {\n"
         "        esm.ChangeState(new EPatrolState(enemy, esm));\n"
         "        return;\n"
         "    }\n"
         "    Vector3 objetivo = grid.CeldaAMundo(camino[0]);\n"
         "    objetivo.y = enemy.transform.position.y;\n"
         "    Vector3 haciaObjetivo = objetivo - enemy.transform.position;\n"
         "    if (haciaObjetivo.sqrMagnitude > 0.0001f) enemy.transform.rotation = Quaternion.LookRotation(haciaObjetivo);\n"
         "    enemy.transform.position = Vector3.MoveTowards(enemy.transform.position, objetivo, enemy.chace_vel * Time.deltaTime);\n"
         "    // if (transform.position == objetivo) camino.RemoveAt(0);   // TODO REGALADO. esta linea arregla el avanze chopeado del enemigo\n"
         "}")

# ---- muerto
s = new_slide()
header(s, "ESTADO 03", "MORIR: UNA SOLA VEZ",
       "El enemigo se acuesta en el suelo y deja de ejecutar lógica.")
code_img(s, "code_muerto", 0.62, 1.70, 5.20, 3.26)
shot(s, ROOT / "img" / "enemigo_muerto.png", 6.20, 1.70, 6.51, 4.15)
cap(s, 6.20, 5.88, 6.5, "El cilindro queda acostado y el cono desaparece.")
tip(s, 0.62, 5.15, 5.20, 0.95, "BANDERA muerto",
    "Evita que el cilindro se rote dos veces si se vuelve a llamar Enter().", accent=PINK)
footer(s, "El estado Muerto no actualiza nada: su Execute() solo hace return.")
nc(s, "EMuertoState implementa el estado de muerte.\n\n"
      "Enter() escribe el mensaje “Estado: Bien Muerto” en la consola. Si la bandera muerto es "
      "false, rota el Transform 90 grados sobre su eje derecho, lo baja al suelo con Vector3.down y "
      "pone muerto en true. Esa bandera evita que una segunda llamada a Enter() vuelva a rotar el "
      "cilindro.\n\n"
      "Execute(), Exit() y DibujarGizmos() están vacíos. Un enemigo muerto no se mueve, no persigue y "
      "no dibuja el cono.",
   ["code_muerto"], path="Assets/Scripts/escena7_fsm/EnemigoFSM/EMuertoState.cs")

# ---- consola
s = new_slide()
header(s, "EN ACCIÓN", "LA FSM DEJA UN RASTRO EN LA CONSOLA",
       "Cada Enter() y Exit() escribe un mensaje; así se ve el cambio de estado.")
shot(s, ROOT / "img" / "consola_estados_crop4.png", 0.62, 1.70, 7.20, 4.06)
text(s, 8.05, 1.80, 4.66, 0.30, "SECUENCIA DE LA PRUEBA", role="label", color=ORANGE_TEXT)
secuencia = [
    ("1", "Comienza patrulla", "Start() entra a Patrullar."),
    ("2", "Ya no patrullo más", "Exit() de Patrullar."),
    ("3", "Perseguir a Velma", "El cono detectó a Velma."),
    ("4", "Bien Muerto", "La patada llegó de fuera del cono."),
]
for i, (num, title, body) in enumerate(secuencia):
    y = 2.22 + i * 0.90
    circle(s, 8.05, y, 0.30, ORANGE if i < 3 else PINK)
    text(s, 8.05, y, 0.30, 0.30, num, role="step_number", color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 8.47, y - 0.02, 4.20, 0.28, title, role="body_strong", color=INK)
    text(s, 8.47, y + 0.28, 4.20, 0.44, body, role="note", color=BODY)
footer(s, "La consola se limpió antes de la prueba para ver solo los mensajes de la FSM.")
notes(s,
      "Esta captura es de una prueba real en Play. Antes de entrar se limpió la consola para que "
      "solo aparecieran los mensajes de la FSM.\n\n"
      "La secuencia muestra el ciclo completo: Start() entra a Patrullar y escribe “Estado: Comienza "
      "patrulla”. Cuando el enemigo ve a Velma, Exit() de Patrullar escribe “Ya NO patrullo mas” y "
      "Enter() de Perseguir escribe “Estado: Perseguir a Velma”. Después, cuando la patada llega por "
      "la espalda, Enter() de Muerto escribe “Estado: Bien Muerto”.\n\n"
      "Los mensajes salen de Debug.Log dentro de Enter() y Exit(). Son una herramienta de depuración "
      "muy útil para comprobar que las transiciones ocurren en el orden esperado.")

# ---- cono
s = new_slide()
header(s, "LA VISIÓN", "UN CONO DE 8 UNIDADES Y 90 GRADOS",
       "El enemigo solo ve lo que está cerca y dentro de su campo de visión.")
figure(s, "vision_cono.png", 0.62, 1.65, 5.30, 4.10)
tip(s, 6.25, 1.70, 6.46, 1.35, "RANGO",
    "vision_rango = 8. La distancia se mide en 3D desde los ojos del enemigo hasta los ojos de Velma.", accent=ORANGE)
tip(s, 6.25, 3.20, 6.46, 1.35, "ÁNGULO",
    "vision_angulo = 90°. El cono tiene 45° a cada lado del vector forward.", accent=BLUE)
tip(s, 6.25, 4.70, 6.46, 1.25, "PARED",
    "El rayo debe llegar a Velma sin chocar con una pared. Si choca, no hay visión.", accent=PINK)
footer(s, "El ángulo se mide en el plano XZ; el rango usa la distancia real en 3D.")
notes(s,
      "El cono de visión tiene dos parámetros: rango y ángulo.\n\n"
      "vision_rango vale 8. Es la distancia máxima entre los ojos del enemigo y los ojos de Velma. "
      "En el código se usa dir.magnitude, que incluye la altura.\n\n"
      "vision_angulo vale 90 grados. Es la apertura total del cono, así que hay 45 grados a cada lado "
      "del vector transform.forward. El ángulo se calcula con la dirección proyectada en el plano XZ, "
      "no con la dirección 3D.\n\n"
      "El tercer filtro es la pared: aunque Velma esté dentro del rango y del ángulo, el rayo debe "
      "llegar sin obstáculos. Eso se comprueba con Physics.Raycast.")

# ---- vision code
s = new_slide()
header(s, "LA VISIÓN", "CÓMO SE DECIDE SI VELMA ESTÁ ENFRENTE",
       "VeJugador() aplica tres filtros: rango, ángulo y raycast.")
code_img(s, "code_vision", 0.62, 1.70, 7.15, 4.40)
steps(s, 8.00, 1.85, 4.70, [
    "Calcula la dirección desde los ojos del enemigo hasta los ojos de Velma.",
    "Proyecta la dirección en el plano XZ y compara el ángulo con forward.",
    "Lanza un rayo hasta Velma. Si el primer choque no es Velma, hay una pared.",
], gap=1.35)
footer(s, "El raycast usa dir.magnitude, la misma distancia que se comparó con el rango.")
nc(s, "VeJugador() está en EnemigoCilindro.cs.\n\n"
      "Primero revisa que el campo jugador no sea null; esa línea no cabe en la imagen, pero está "
      "en el archivo completo. Después calcula origen, que es la posición "
      "del enemigo más Vector3.up; así los ojos quedan un metro arriba del centro del enemigo. "
      "Calcula dir desde ese origen hasta los ojos de Velma.\n\n"
      "Luego crea plano, que es la misma dirección pero con y = 0. Con Vector3.Angle compara el "
      "forward del enemigo con plano. Si la distancia es mayor que vision_rango o el ángulo es mayor "
      "que vision_angulo / 2, regresa false.\n\n"
      "Al final lanza un Physics.Raycast desde los ojos hasta Velma. Si el rayo no choca con nada, "
      "regresa true. Si choca, revisa si el objeto golpeado es Velma o un hijo de Velma. Si no lo es, "
      "hay una pared en medio y regresa false.",
   ["code_vision"], path="Assets/Scripts/escena7_fsm/EnemigoFSM/EnemigoCilindro.cs",
   extra="ConoVisionGizmo() dibuja el cono en la vista Scene. El color cambia con VeJugador():\n\n"
         + snip("code_cono"))

# ---- vision red
s = new_slide()
header(s, "LA VISIÓN EN UNITY", "VELMA ESTÁ ENFRENTE: CONO ROJO",
       "La vista Scene dibuja el cono con OnDrawGizmos y lo pinta de rojo cuando detecta a Velma.")
shot(s, ROOT / "img" / "vision_velma_frente.png", 0.62, 1.68, 5.20, 4.25)
cap(s, 0.62, 5.96, 5.2, "El cilindro es el enemigo; el sprite es Velma.")
tip(s, 6.10, 1.70, 6.61, 1.40, "ROJO",
    "VeJugador() devolvió true. Velma está dentro del rango y del ángulo, y el rayo llegó sin pared.", accent=PINK)
tip(s, 6.10, 3.30, 6.61, 1.30, "CONO",
    "Las tres líneas son el borde del cono: izquierda, derecha y el fondo del arco.", accent=ORANGE)
tip(s, 6.10, 4.80, 6.61, 1.15, "CONSECUENCIA",
    "En Patrullar, BuscarJugador() cambia a EPerseguirState en ese mismo frame.", accent=BLUE)
footer(s, "El gizmo se dibuja en la vista Scene, no en el Game. Se activa con Gizmos.")
notes(s,
      "Esta captura es de la vista Scene en Play. El cilindro blanco es el enemigo y el sprite es "
      "Velma. El cono se dibuja con OnDrawGizmos y el método ConoVisionGizmo().\n\n"
      "El color rojo significa que VeJugador() devolvió true. Velma está dentro del rango de 8 "
      "unidades, dentro del ángulo de 90 grados y el rayo llegó hasta ella sin chocar con una pared.\n\n"
      "En el estado Patrullar, BuscarJugador() llama a VeJugador() en cada Execute(). Si el resultado "
      "es true, cambia a EPerseguirState. En la captura ya se ve el cono rojo porque la posición se "
      "acomodó para mostrar la detección.")

# ---- vision wall
s = new_slide()
header(s, "LA VISIÓN EN UNITY", "LA PARED TAPA A VELMA: CONO VERDE",
       "Aunque Velma esté cerca, el rayo choca con la pared y el enemigo no la ve.")
shot(s, ROOT / "img" / "vision_pared_en_medio.png", 0.62, 1.68, 5.20, 4.25)
cap(s, 0.62, 5.96, 5.2, "La pared está entre el enemigo y Velma.")
tip(s, 6.10, 1.70, 6.61, 1.40, "VERDE",
    "VeJugador() devolvió false. El rayo encontró la pared antes que a Velma.", accent=GREEN)
tip(s, 6.10, 3.30, 6.61, 1.30, "RAYCAST",
    "Physics.Raycast devuelve el primer collider que toca. Si no es Velma, hay un obstáculo.", accent=ORANGE)
tip(s, 6.10, 4.80, 6.61, 1.15, "CONSECUENCIA",
    "El enemigo sigue en Patrullar y no cambia a Perseguir.", accent=BLUE)
footer(s, "Sin línea de visión no hay transición, aunque la distancia sea corta.")
notes(s,
      "La segunda captura muestra el mismo cono, pero de color verde. Velma está cerca, dentro del "
      "rango y dentro del ángulo, pero hay una pared entre los dos.\n\n"
      "El raycast sale de los ojos del enemigo y avanza hacia Velma. El primer collider que encuentra "
      "es la pared, no Velma. Por eso la condición hit.transform.IsChildOf(jugador) es falsa y "
      "VeJugador() regresa false.\n\n"
      "El cono verde no significa que el enemigo esté ciego: significa que en ese frame no tiene "
      "línea de visión. Si Velma rodea la pared y entra al cono, el estado cambia a Perseguir.")

# ---- animator
s = new_slide()
header(s, "LA PATADA", "UN TRIGGER LLAMADO KICK",
       "Velma tiene un estado VelmaKick al que entra desde Any State.")
shot(s, ROOT / "img" / "animator_velma.png", 0.62, 1.68, 5.20, 4.45)
tip(s, 6.10, 1.70, 6.61, 1.40, "PARÁMETRO kick",
    "Es un trigger. Se dispara una vez con SetTrigger(\"kick\") y no se repite solo.", accent=PINK)
tip(s, 6.10, 3.30, 6.61, 1.30, "TRANSICIÓN",
    "Any State → VelmaKick. Cualquier estado puede entrar a la patada cuando el trigger se activa.", accent=ORANGE)
tip(s, 6.10, 4.80, 6.61, 1.15, "REGRESO",
    "VelmaKick → VelmaWalking con Exit Time. El clip dura 0.5 s y no se repite.", accent=BLUE)
footer(s, "El Animator de Velma usa los parámetros isRunning, isJumping, isDucking y kick.")
notes(s,
      "La captura es de la ventana Animator con Velma seleccionada. El controlador se llama "
      "velma_sprite_walk_2_0.\n\n"
      "El parámetro kick es un trigger. Un trigger se activa una vez y el Animator lo consume; no se "
      "queda encendido como un bool. Por eso la patada no se repite sola.\n\n"
      "La transición sale de Any State hacia VelmaKick. Eso permite patear desde VelmaWalking, "
      "VelmaRun o VelmaJump. La transición de regreso va de VelmaKick a VelmaWalking con Exit Time: "
      "cuando el clip termina, Velma vuelve a caminar.\n\n"
      "Los otros parámetros son isRunning, isJumping e isDucking. En la captura también se ven los "
      "estados VelmaWalking, VelmaRun, VelmaJump y VelmaDuck.")

# ---- frames
s = new_slide()
header(s, "LA PATADA", "SEIS DIBUJOS EN MEDIO SEGUNDO",
       "El clip VelmaKick cambia el sprite seis veces a 12 fotogramas por segundo.")
figure(s, "frames_patada.png", 0.62, 1.62, 12.09, 3.55)
cards = [
    ("12 fps", "Cada sprite dura 1/12 s."),
    ("0.5 s", "Duración total del clip."),
    ("SIN LOOP", "El clip no se repite."),
]
for i, (title, body) in enumerate(cards):
    x = 0.62 + i * 4.10
    card(s, x, 5.35, 3.89, 0.72, ORANGE if i == 0 else (BLUE if i == 1 else PINK))
    text(s, x + 0.20, 5.42, 3.50, 0.25, title, role="body_strong", color=INK)
    text(s, x + 0.20, 5.70, 3.50, 0.25, body, role="note", color=BODY)
footer(s, "El sprite sheet tiene seis sprites de 101 píxeles de alto; el ancho cambia en cada uno.")
notes(s,
      "La figura muestra los seis sprites del clip VelmaKick, en orden. Cada uno dura 1/12 de "
      "segundo, así que el clip completo dura 0.5 segundos.\n\n"
      "El clip no tiene loop. Cuando termina, el Animator regresa a VelmaWalking por la transición "
      "con Exit Time. Si el clip tuviera loop, Velma se quedaría pateando para siempre.\n\n"
      "Los sprites salen de velma_sprite_kick2.png. Cada sprite mide 101 píxeles de alto y el ancho "
      "cambia según la pose. El PNG completo mide 573 por 101. El sprite sheet se cortó con Sprite "
      "Mode = Multiple y seis rectángulos.")

# ---- animation window + sprite editor
s = new_slide()
header(s, "LA PATADA", "CÓMO SE ARMÓ EL CLIP",
       "El Animation window muestra las seis llaves; el Sprite Editor muestra los seis cortes.")
shot(s, ROOT / "img" / "animation_kick.png", 0.62, 1.68, 6.00, 3.60)
cap(s, 0.62, 5.38, 6.0, "Animation window: clip VelmaKick con seis llaves.")
shot(s, ROOT / "img" / "sprite_editor_kick.png", 6.95, 1.68, 5.76, 2.90)
cap(s, 6.95, 4.63, 5.76, "Sprite Editor: seis cortes en el PNG.")
tip(s, 6.95, 5.05, 5.76, 1.05, "PROCESO",
    "Texture Type = Sprite; Sprite Mode = Multiple; Slice = 6; Apply; luego se crean las seis llaves del clip.",
    accent=GREEN)
notes(s,
      "La captura de la izquierda es la ventana Animation con el clip VelmaKick abierto. Se ven seis "
      "llaves, una por sprite, sobre la línea de tiempo. La captura de la derecha es el Sprite Editor "
      "con los seis cortes del PNG.\n\n"
      "El proceso fue: seleccionar velma_sprite_kick2.png, poner Texture Type = Sprite (2D and UI), "
      "Sprite Mode = Multiple, abrir el Sprite Editor, cortar los seis sprites y aplicar. Después se "
      "creó el clip VelmaKick y se agregaron las seis llaves de sprite en orden, a 12 fps.\n\n"
      "El clip se asigna al estado VelmaKick del Animator. El Animator lo reproduce cuando el trigger "
      "kick se activa.")

# ---- trigger
s = new_slide()
header(s, "LA PATADA", "EL BOTÓN F DISPARA EL KICK",
       "Solo se puede patear en el suelo; el impulso se suma a la velocidad horizontal.")
code_img(s, "code_patada_trigger", 0.62, 1.70, 6.20, 2.74)
steps(s, 7.10, 1.85, 5.60, [
    "Comprueba que Velma esté en el suelo y que F se haya presionado en este frame.",
    "Activa el trigger kick del Animator.",
    "Calcula la dirección: el input actual o el lado hacia donde mira el sprite.",
    "Suma kickImpulse a la velocidad horizontal.",
], gap=0.90)
tip(s, 0.62, 4.95, 6.20, 1.00, "¿POR QUÉ EN EL SUELO?",
    "La patada es una acción terrestre. En el aire, el impulso se sumaría al salto.", accent=BLUE)
footer(s, "kickImpulse vale 6; el frenado del personaje se encarga de detener el impulso.")
nc(s, "Este bloque está dentro de Update() de S7_VelmaWalk_3D.cs.\n\n"
      "La condición pide dos cosas: grounded y kb.fKey.wasPressedThisFrame. grounded se actualiza "
      "con las colisiones del Rigidbody; wasPressedThisFrame garantiza que la patada se dispare una "
      "sola vez por pulsación.\n\n"
      "SetTrigger(\"kick\") activa el trigger del Animator. Después se calcula la dirección: si hay "
      "input, se usa input.normalized; si no hay input, se usa el lado hacia donde mira el sprite "
      "(flipX). Finalmente se suma dir * kickImpulse a horizontal.\n\n"
      "El impulso no teletransporta a Velma: se suma a la velocidad y el frenado lo reduce con el "
      "tiempo.",
   ["code_patada_trigger"], path="Assets/Scripts/escena7_fsm/S7_VelmaWalk_3D.cs")

# ---- hit
s = new_slide()
header(s, "LA PATADA", "COLISIÓN + ANIMACIÓN = GOLPE",
       "Velma revisa si el objeto es enemigo y si está en el estado VelmaKick.")
code_img(s, "code_check_hit", 0.62, 1.70, 6.20, 3.12)
steps(s, 7.10, 1.85, 5.60, [
    "OnCollisionEnter y OnCollisionStay llaman a CheckEnemyHit.",
    "Si la capa del objeto no es Enemigos, termina.",
    "Si el Animator está en el estado VelmaKick, hay patada.",
    "Llama a RecibirPatada con la posición de Velma.",
], gap=0.92)
tip(s, 0.62, 5.15, 6.20, 0.75, "CAPA Enemigos",
    "Evita que el golpe se dispare contra paredes, piso o el HUD.", accent=ORANGE)
footer(s, "La animación es la que decide si hay golpe; la colisión es la que lo detecta.")
nc(s, "CheckEnemyHit() está en S7_VelmaWalk_3D.cs.\n\n"
      "Primero compara la capa del objeto con la capa Enemigos. Si no coincide, termina. Después "
      "consulta el Animator: GetCurrentAnimatorStateInfo(0).IsName(\"VelmaKick\") devuelve true "
      "mientras la animación de patada está activa.\n\n"
      "Si las dos condiciones se cumplen, llama a RecibirPatada() del EnemigoCilindro y le pasa la "
      "posición de Velma. El enemigo decide si la patada viene de frente o por la espalda.\n\n"
      "OnCollisionEnter y OnCollisionStay llaman a CheckEnemyHit. Enter detecta el primer contacto; "
      "Stay mantiene la detección mientras los colliders siguen tocándose.",
   ["code_check_hit", "code_oncollision"], path="Assets/Scripts/escena7_fsm/S7_VelmaWalk_3D.cs")

# ---- recibir patada
s = new_slide()
header(s, "LA PATADA", "LA PATADA MATA SI VIENE POR LA ESPALDA",
       "El enemigo compara el origen del golpe con su propio frente.")
code_img(s, "code_recibir_patada", 0.62, 1.70, 6.20, 2.45)
tip(s, 7.10, 1.70, 5.60, 1.45, "DE FRENTE: NO MUERE",
    "Si el ángulo es menor o igual a 45°, el golpe viene de frente, dentro del cono. La patada no lo mata.", accent=GREEN)
tip(s, 7.10, 3.35, 5.60, 1.45, "FUERA DEL CONO: MUERE",
    "Si el ángulo es mayor a 45°, el golpe viene de fuera del cono. La FSM entra a EMuertoState.", accent=PINK)
tip(s, 7.10, 5.00, 5.60, 0.95, "Initialize, NO ChangeState",
    "RecibirPatada usa esm.Initialize(new EMuertoState(...)).", accent=ORANGE)
tip(s, 0.62, 4.35, 6.20, 1.35, "MISMO CONO",
    "RecibirPatada reutiliza vision_angulo / 2. No hay un ángulo nuevo: el mismo cono decide si la patada es sorpresa.",
    accent=BLUE)
footer(s, "Es una decisión de diseño: solo una patada sorpresa mata al enemigo.")
nc(s, "RecibirPatada() está en EnemigoCilindro.cs.\n\n"
      "Calcula haciaVelma como el vector desde el enemigo hasta el origen de la patada. Pone y = 0 "
      "para medir solo en el plano. Después compara el forward del enemigo con ese vector usando "
      "Vector3.Angle.\n\n"
      "Si el ángulo es mayor que vision_angulo / 2, la patada viene de fuera del cono de visión. En "
      "ese caso llama a esm.Initialize(new EMuertoState(this, esm)). Si viene de frente, no hace nada: "
      "el enemigo la ve y la patada no lo mata.\n\n"
      "Se usa Initialize en lugar de ChangeState porque se quiere entrar directo al estado muerto, "
      "sin llamar a Exit() del estado actual. Es una decisión del código original.",
   ["code_recibir_patada"], path="Assets/Scripts/escena7_fsm/EnemigoFSM/EnemigoCilindro.cs")

# ---- fricción
s = new_slide()
header(s, "LA ESCENA", "EL PERSONAJE SE ATORABA EN LAS PAREDES",
       "Al empujar contra una pared, la fricción frenaba el movimiento y el personaje se quedaba pegado.")
figure(s, "friccion.png", 0.62, 1.65, 7.10, 3.35)
tip(s, 7.95, 1.70, 4.76, 1.35, "COLISIÓN",
    "El BoxCollider de Velma toca el BoxCollider de la pared. Unity calcula una fuerza de fricción.", accent=ORANGE)
tip(s, 7.95, 3.20, 4.76, 1.35, "SÍNTOMA",
    "Si mantienes la dirección contra la pared, el personaje avanza muy lento o se detiene.", accent=PINK)
tip(s, 7.95, 4.70, 4.76, 1.20, "SOLUCIÓN",
    "Un Physics Material con fricción 0 en las paredes. Así el personaje se desliza.", accent=GREEN)
footer(s, "La fricción no se quitó al personaje: se quitó a las paredes.")
notes(s,
      "El problema era físico. El personaje tiene un Rigidbody y un BoxCollider. Las paredes tienen "
      "BoxCollider. Cuando Velma empuja contra una pared, Unity genera una fuerza de fricción que se "
      "opone al movimiento.\n\n"
      "Si el jugador mantiene la dirección contra la pared, la fricción frena el deslizamiento. El "
      "personaje parece atorarse: avanza muy lento o se queda pegado. No era un error de los controles; "
      "era la combinación de fricción entre los dos colliders.\n\n"
      "La solución fue crear un Physics Material sin fricción y asignarlo a las paredes. El material "
      "del personaje no se tocó. Así las paredes dejan de frenar el deslizamiento.\n\n"
      "CÓDIGO DEL JUGADOR (S7_VelmaWalk_3D.cs, Start):\n\n"
      + snip("code_player_start"))

# ---- material
s = new_slide()
header(s, "LA ESCENA", "PAREDES CON FRICCIÓN CERO",
       "ParedesMaterial tiene fricción dinámica y estática en 0, y se asigna al BoxCollider de cada pared.")
label(s, 0.62, 1.45, 5.2, "MATERIAL", color=ORANGE_TEXT)
shot(s, ROOT / "img" / "material_sin_friccion_crop2.png", 0.62, 1.68, 5.20, 1.76)
label(s, 6.95, 1.45, 5.2, "BOX COLLIDER DE LA PARED", color=BLUE)
shot(s, ROOT / "img" / "pared_collider_material.png", 6.95, 1.68, 5.76, 2.90)
card(s, 0.62, 3.58, 5.20, 0.95, GREEN)
text(s, 0.86, 3.66, 4.70, 0.26, "VALORES DEL MATERIAL", role="body_strong", color=INK)
text(s, 0.86, 3.98, 4.70, 0.44, "Dynamic 0 · Static 0 · Combine Minimum", role="body", color=BODY)
steps(s, 0.62, 4.70, 5.20, [
    "Crea el material desde Assets > Create.",
    "Pon Dynamic Friction = 0 y Static Friction = 0.",
    "Elige Friction Combine = Minimum.",
], gap=0.40)
steps(s, 6.95, 4.70, 5.76, [
    "Arrastra el material al campo Material del BoxCollider.",
    "Repite en todas las paredes y prueba en Play.",
], gap=0.40)
footer(s, "Friction Combine = Minimum toma el valor más bajo entre el material de la pared y el de Velma.")
notes(s,
      "La captura de arriba a la izquierda es el Inspector del asset ParedesMaterial. Dynamic "
      "Friction y Static Friction valen 0; Bounciness vale 0; Friction Combine está en Minimum.\n\n"
      "La captura de la derecha es el Inspector del BoxCollider de pared_1. El campo Material apunta "
      "a ParedesMaterial. El mismo material se asignó a las seis paredes.\n\n"
      "Friction Combine = Minimum es importante. Unity combina la fricción de los dos colliders que "
      "se tocan. Si la pared tiene 0 y Velma tiene el valor por defecto, Minimum elige 0. Por eso el "
      "personaje se desliza aunque su collider tenga fricción.\n\n"
      "Los pasos para aplicarlo: crear el material, poner las dos fricciones en 0, elegir Minimum, "
      "arrastrarlo al campo Material de cada BoxCollider y probar en Play.")

# ---- errores
s = new_slide()
header(s, "CIERRE", "QUÉ REVISAR SI NO FUNCIONA",
       "Casi todos los problemas se ven en la Consola o en la vista Scene.")
rows = [
    ("Síntoma", "Causa probable"),
    ("El enemigo no se mueve", "Falta el objeto Grid en la escena o el jugador está fuera del grid."),
    ("No cambia a Perseguir", "El jugador no está en el cono, hay una pared en medio o vision_rango es muy bajo."),
    ("La patada no lo mata", "La patada llega de frente, la capa no es Enemigos o el Animator no está en VelmaKick."),
    ("El personaje se atora", "Las paredes no tienen ParedesMaterial o Friction Combine no está en Minimum."),
    ("La animación no se ve", "El trigger kick no se activa o el estado VelmaKick no tiene el clip asignado."),
]
tbl(s, 0.62, 1.70, 12.09, rows, [4.0, 8.09], row_h=0.62, head_h=0.50)
tip(s, 0.62, 5.42, 12.09, 0.72, "PRUEBA RÁPIDA",
    "Entra a Play, mira el cono en la vista Scene y revisa la Consola. Los tres estados escriben un mensaje.",
    accent=GREEN)
notes(s,
      "Lista de comprobación.\n\n"
      "Si el enemigo no se mueve, revisa que exista el objeto Grid con S7_Grid y que el jugador esté "
      "dentro del grid. Si no cambia a Perseguir, revisa el cono: verde significa que no hay línea de "
      "visión o que Velma está fuera del rango o del ángulo. Si la patada no lo mata, revisa que llegue "
      "por la espalda, que la capa del enemigo sea Enemigos y que el Animator esté en VelmaKick. Si el "
      "personaje se atora, revisa el material de las paredes y Friction Combine. Si la animación no se "
      "ve, revisa el trigger kick y el clip del estado VelmaKick.\n\n"
      "La prueba más rápida es entrar a Play y mirar la vista Scene con los Gizmos activados. El cono "
      "cambia de color y la Consola muestra los mensajes de los estados.")

# ---- cierre
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
text(s, 0.0, 1.55, 13.33, 1.35, "¿PREGUNTAS?", role="closing", align=PP_ALIGN.CENTER)
text(s, 0.0, 3.18, 13.33, 0.38, "Tres estados, un cono y una patada.",
     role="subtitle", align=PP_ALIGN.CENTER)
text(s, 0.0, 3.72, 13.33, 0.38, "La FSM separa el comportamiento; la visión y la patada la conectan con Velma.",
     role="note", color=BODY, align=PP_ALIGN.CENTER)
picture_fit(s, ROOT / "decor" / "star.png", 1.55, 2.30, 0.85, 0.85, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 3.60, 4.15, 0.75, 0.75, border=False)
picture_fit(s, ROOT / "decor" / "tree-small.png", 1.10, 4.36, 1.15, 2.06, border=False)
picture_fit(s, ROOT / "decor" / "cloud-low.png", 9.85, 4.68, 2.65, 1.42, border=False)
notes(s,
      "Cierre del tema 8.8.2. Resumen: el enemigo tiene una FSM con tres estados. Patrullar elige una "
      "celda al azar y camina con BFS. Perseguir recalcula el camino a Velma cada 0.25 segundos. "
      "Muerto se acuesta en el suelo y deja de ejecutar lógica.\n\n"
      "La visión usa un cono de 8 unidades y 90 grados, más un raycast para comprobar que no haya "
      "paredes. La patada se anima con un trigger y seis sprites, y se detecta con una colisión y el "
      "estado VelmaKick del Animator. La escena usa un material sin fricción en las paredes para que "
      "el personaje no se atore.")


def embed_fonts(path):
    """Incrusta Neuromax y Neuromax SemBd en el .pptx."""
    font1 = (ROOT / "fonts" / "Neuromax-Regular.fntdata").read_bytes()
    font2 = (ROOT / "fonts" / "Neuromax-SemiBold.fntdata").read_bytes()

    rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    ct_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
    tmp = path.with_name(path.name + ".tmp")

    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(
            tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        pres = etree.fromstring(zin.read("ppt/presentation.xml"))
        pres.attrib.pop("saveSubsetFonts", None)
        pres.set("embedTrueTypeFonts", "1")
        rels = etree.fromstring(zin.read("ppt/_rels/presentation.xml.rels"))
        ctypes = etree.fromstring(zin.read("[Content_Types].xml"))

        for rel in list(rels):
            if rel.get("Type", "").endswith("/font"):
                rels.remove(rel)
        for old in pres.findall(qn("p:embeddedFontLst")):
            pres.remove(old)

        used = [r.get("Id", "") for r in rels]
        nums = [int(r[3:]) for r in used if r.startswith("rId") and r[3:].isdigit()]
        rid1 = "rId" + str(max(nums, default=0) + 1)
        rid2 = "rId" + str(max(nums, default=0) + 2)

        for rid, target in ((rid1, "fonts/font1.fntdata"),
                            (rid2, "fonts/font2.fntdata")):
            etree.SubElement(rels, "{%s}Relationship" % rel_ns,
                             Id=rid,
                             Type="http://schemas.openxmlformats.org/"
                                  "officeDocument/2006/relationships/font",
                             Target=target)

        lst = etree.Element(qn("p:embeddedFontLst"))
        for typeface, rid, panose in (
                ("Neuromax", rid1, "020B0604020202020204"),
                ("Neuromax SemBd", rid2, None)):
            ef = etree.SubElement(lst, qn("p:embeddedFont"))
            f = etree.SubElement(ef, qn("p:font"))
            f.set("typeface", typeface)
            if panose:
                f.set("panose", panose)
            f.set("charset", "0")
            reg = etree.SubElement(ef, qn("p:regular"))
            reg.set(qn("r:id"), rid)

        default = pres.find(qn("p:defaultTextStyle"))
        if default is not None:
            default.addprevious(lst)
        else:
            pres.append(lst)

        if not any(d.get("Extension") == "fntdata" for d in ctypes):
            etree.SubElement(ctypes, "{%s}Default" % ct_ns,
                             Extension="fntdata",
                             ContentType="application/x-fontdata")

        for item in zin.infolist():
            if item.filename in ("ppt/fonts/font1.fntdata",
                                 "ppt/fonts/font2.fntdata"):
                continue
            data = zin.read(item.filename)
            if item.filename == "ppt/presentation.xml":
                data = etree.tostring(pres, xml_declaration=True,
                                      encoding="UTF-8", standalone=True)
            elif item.filename == "ppt/_rels/presentation.xml.rels":
                data = etree.tostring(rels, xml_declaration=True,
                                      encoding="UTF-8", standalone=True)
            elif item.filename == "[Content_Types].xml":
                data = etree.tostring(ctypes, xml_declaration=True,
                                      encoding="UTF-8", standalone=True)
            zout.writestr(item, data)

        zout.writestr("ppt/fonts/font1.fntdata", font1)
        zout.writestr("ppt/fonts/font2.fntdata", font2)

    tmp.replace(path)


TMP = PPTX.with_name(PPTX.stem + ".draft.pptx")
prs.save(TMP)
embed_fonts(TMP)

report = validate(TMP, strict=True)
print(report.format())
if report.errors:
    print("Build abortado: corrige los errores y vuelve a intentar.")
    TMP.unlink(missing_ok=True)
    raise SystemExit(1)

TMP.replace(PPTX)
print("Guardado:", PPTX)
print("Diapositivas:", len(prs.slides))
