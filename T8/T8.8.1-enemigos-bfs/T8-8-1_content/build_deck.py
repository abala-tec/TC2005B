#!/usr/bin/env python3
"""Construye T8.7.2 - Controles 3D estilo Mario.

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
    "DECK_OUT", str(ROOT.parent / "T8.8.1-Enemigos-BFS.pptx")
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
import sim_bfs  # noqa: E402

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
CS = "Assets/Scripts/escena6_enemigos/S6_Grid.cs"
CSE = "Assets/Scripts/escena6_enemigos/S6_EnemigoCilindro.cs"
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
prs.core_properties.title = "T8.8.1 · Enemigos que persiguen con BFS"
prs.core_properties.author = "TC2005B · Construcción de Software"
prs.core_properties.subject = "Búsqueda de caminos con BFS en una cuadrícula de Unity"
prs.core_properties.keywords = "Unity, C#, BFS, pathfinding, enemigos, cuadrícula, TC2005B"
prs.core_properties.language = "es-MX"

# ---- portada
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
rect(s, 0.62, 0.32, 0.09, 0.09, ORANGE)
text(s, 0.81, 0.28, 10.0, 0.22, "8.8.1 · ENEMIGOS", role="label")
text(s, 0.62, 0.92, 6.00, 2.70, "ENEMIGOS\nQUE\nPERSIGUEN", role="section", line_spacing=0.92)
text(s, 0.62, 3.64, 5.70, 0.80,
     "Cómo usar BFS para que un enemigo rodee las paredes y llegue al jugador.",
     role="subtitle", line_spacing=1.02)
text(s, 0.62, 4.75, 5.55, 0.72,
     "Convertimos el piso en una cuadrícula y buscamos el camino más corto.",
     role="note", color=BODY, line_spacing=1.02)
text(s, 0.62, 5.20, 5.40, 0.28, "TC2005B · Construcción de Software", role="note")
text(s, 0.62, 5.55, 5.40, 0.28, "Unity · C# · S6_Grid", role="note", color=BODY)
rect(s, 6.55, 0.66, 6.18, 4.95, DARK)
picture_fit(s, FIG / "real_camino.png", 6.75, 0.86, 5.78, 4.55, border=False)
pill(s, 6.95, 0.72, 1.55, "UNITY · C#", WHITE, DARK)
picture_fit(s, ROOT / "decor" / "star.png", 0.55, 6.30, 0.75, 0.75, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 11.55, 6.40, 0.85, 0.85, border=False)
notes(s,
      "Bienvenida al tema 8.8.1. Hasta ahora nuestros enemigos se movían en línea recta hacia el "
      "jugador. Eso funciona en un campo vacío, pero falla en cuanto hay paredes: el enemigo "
      "se queda pegado a ellas.\n\n"
      "Hoy resolvemos ese problema con una idea muy sencilla: convertir el piso en una cuadrícula "
      "y usar el algoritmo BFS (búsqueda en anchura) para encontrar el camino más corto.\n\n"
      "La imagen de la derecha es el resultado real de nuestro código en la escena escena6_enemigos: "
      "el cuadro rosa es el jugador, el círculo naranja es el enemigo y la línea amarilla es el "
      "camino que calcula BFS.")

# ---- agenda
s = new_slide()
header(s, "HOY", "LO QUE VEREMOS HOY",
       "Tres bloques llevan al enemigo de la línea recta al camino inteligente.")
rows = [
    ("01", "EL PISO EN CASILLAS", "Un grid de 50 por 50 casillas y las paredes marcadas.", ORANGE),
    ("02", "BFS PASO A PASO", "La cola, el diccionario, un ejemplo pequeño y el código.", BLUE),
    ("03", "EL ENEMIGO QUE PERSIGUE", "Recalcular el camino y caminar casilla por casilla.", GREEN),
]
for i, (num, title, desc, color) in enumerate(rows):
    y = 1.70 + i * 1.05
    card(s, 0.62, y, 12.09, 0.92, color)
    text(s, 0.82, y + 0.28, 0.45, 0.30, num, role="card_number", color=color)
    text(s, 1.42, y + 0.10, 10.8, 0.34, title, role="card_title_sm")
    text(s, 1.46, y + 0.50, 11.0, 0.30, desc, role="note", color=BODY)
text(s, 0.62, 4.95, 12.0, 0.40,
     "El bloque 02 es el más importante: ahí entendemos BFS con dibujos.", role="body_strong")
footer(s, "El código se ve como imagen y se copia completo en las notas.")
notes(s,
      "Recorrido del tema.\n\n"
      "1. El piso en casillas: dividimos el Plane en una cuadrícula y marcamos las casillas que "
      "tienen pared.\n"
      "2. BFS paso a paso: es el corazón del tema. Lo explicamos con un mapa pequeño de 6 por 4 "
      "casillas, con dibujos, y después con el código real.\n"
      "3. El enemigo: cómo usa el camino para perseguir al jugador.\n\n"
      "Todo el código sale de dos archivos: S6_Grid.cs y S6_EnemigoCilindro.cs. Las figuras con la "
      "escena real se generaron con una réplica en Python del mismo algoritmo (sim_bfs.py).")

K1 = "BLOQUE 01 · EL PISO EN CASILLAS"
# 3 ------------------------------------------------------------ problema
s = new_slide()
header(s, K1, "EL PROBLEMA: LAS PAREDES",
       "Una línea recta no sabe rodear obstáculos.")
figure(s, "real_sin_bfs.png", 0.62, 1.70, 4.00, 4.00)
cap(s, 0.62, 5.78, 4.4, "Línea recta: choca con la pared.")
figure(s, "real_camino.png", 5.22, 1.70, 4.00, 4.00)
cap(s, 5.22, 5.78, 4.4, "Con BFS: rodea las paredes.")
tip(s, 9.82, 1.70, 2.89, 2.10, "SIN BFS",
    "El enemigo avanza derecho y se queda pegado a la pared.", accent=PINK)
tip(s, 9.82, 4.00, 2.89, 2.10, "CON BFS",
    "El enemigo sigue casillas libres hasta llegar al jugador.", accent=GREEN)
notes(s,
      "Vista desde arriba de la escena escena6_enemigos. El plano mide 25 por 25 unidades y tiene "
      "seis paredes. El círculo naranja es el EnemigoCilindro, en la posición (22, 22). El cuadro "
      "rosa es el jugador, cerca de (0.5, 0.4).\n\n"
      "A la izquierda, la línea rosa es lo que hace un enemigo que solo avanza hacia el jugador. "
      "Cruza una pared, así que en el juego el enemigo se atoraría. El círculo rojo marca el punto "
      "donde la línea toca la pared.\n\n"
      "A la derecha, la línea amarilla es el camino que calcula BFS. Rodea todas las paredes. "
      "Estas imágenes se dibujaron con los datos reales de la escena.")

# 4 ------------------------------------------------------------ grid
s = new_slide()
header(s, K1, "EL GRID: UNA CASILLA ES (X, Z)",
       "Cada casilla se nombra con dos números enteros.")
figure(s, "toy_inicial.png", 0.62, 1.70, 5.60, 3.95)
cap(s, 0.62, 5.72, 5.6, "Ejemplo pequeño: 6 columnas por 4 filas.")
code_img(s, "code_campos", 6.55, 1.70, 6.16, 2.40)
bullets(s, 6.55, 4.35, 6.16, [
    "El Plane mide 25 por 25; cada casilla mide 0.5.",
    "Entonces el grid tiene 50 por 50 casillas.",
], gap=0.72)
footer(s, "bloqueada[x, z] vale true cuando esa casilla tiene una pared.")
nc(s, "El grid es solo una tabla de verdad. En S6_Grid.cs lo guardamos en bool[,] bloqueada: "
      "bloqueada[x, z] es true si hay pared y false si la casilla está libre.\n\n"
      "Las casillas se nombran con dos enteros (x, z). En el dibujo, x crece hacia la derecha y z "
      "hacia arriba, igual que en el piso de Unity visto desde arriba. La casilla (0, 0) es la "
      "esquina inferior izquierda.\n\n"
      "El Plane base de Unity mide 10 unidades; con escala 2.5 mide 25. Con casillas de 0.5 "
      "caben 50 casillas por lado, es decir 2,500 casillas en total. Si quisieras un grid más "
      "pequeño, solo cambias ancho, alto o celda.", ["code_campos"])

# 5 ------------------------------------------------------------ conversion
s = new_slide()
header(s, K1, "DEL MUNDO A LA CASILLA",
       "Dos fórmulas convierten metros en casillas y casillas en metros.")
figure(s, "conversion.png", 0.62, 1.70, 6.50, 4.40)
tip(s, 7.45, 1.70, 5.26, 1.30, "MUNDO A CASILLA",
    "casilla = piso( (posición − origen) / celda )")
tip(s, 7.45, 3.20, 5.26, 1.30, "CASILLA A MUNDO",
    "centro = origen + (casilla + 0.5) por celda", accent=BLUE)
tip(s, 7.45, 4.70, 5.26, 1.40, "EJEMPLO",
    "x = 1.8 → piso(1.8 / 0.5) = 3.\nz = 1.3 → piso(2.6) = 2. Casilla (3, 2).", accent=GREEN)
notes(s,
      "El mundo usa decimales y el grid usa enteros, así que necesitamos dos funciones que "
      "conviertan en los dos sentidos.\n\n"
      "Mundo a casilla: se resta el origen (la esquina inferior izquierda del Plane) y se divide "
      "entre el tamaño de la casilla. Después se redondea hacia abajo con piso (FloorToInt).\n\n"
      "Casilla a mundo: es la operación inversa. Se suma 0.5 para llegar al centro de la casilla.\n\n"
      "Ejemplo del dibujo: el jugador está en x = 1.8 y z = 1.3. Con casillas de 0.5, 1.8 / 0.5 = 3.6 "
      "y el piso es 3; 1.3 / 0.5 = 2.6 y el piso es 2. Está en la casilla (3, 2), cuyo centro es "
      "(1.75, 1.25). En esta escena el origen es (0, 0) porque el Plane está en (12.5, 12.5) y mide 25.")

# 6 ------------------------------------------------------------ codigo conversiones
s = new_slide()
header(s, K1, "LAS CONVERSIONES EN CÓDIGO",
       "Son dos funciones cortas que se pueden probar con Debug.Log.")
code_img(s, "code_conversiones", 0.62, 1.70, 7.10, 4.40)
tip(s, 8.05, 1.70, 4.66, 2.05, "FLOORTOINT",
    "Redondea hacia abajo. Así 3.6 y 3.2 caen en la misma casilla.")
tip(s, 8.05, 3.95, 4.66, 2.15, "EL + 0.5", "Lleva el punto al centro de la casilla, no a su esquina.",
    accent=BLUE)
nc(s, "Estas son las dos funciones de S6_Grid.cs. MundoACelda recibe una posición del mundo y "
      "devuelve un Vector2Int. Ojo: el campo y del Vector2Int guarda la fila en Z del mundo, no "
      "la altura.\n\n"
      "CeldaAMundo hace lo contrario y devuelve el centro de la casilla, con altura 0.5 para que "
      "el enemigo camine sobre el piso.\n\n"
      "Para comprobar que son inversas puedes poner un Debug.Log con la posición del jugador "
      "convertida a casilla.", ["code_conversiones"])

# 7 ------------------------------------------------------------ paredes
s = new_slide()
header(s, K1, "MARCAR LAS CASILLAS CON PARED",
       "Al iniciar, preguntamos a la física casilla por casilla.")
code_img(s, "code_awake", 0.62, 1.70, 6.70, 4.40)
steps(s, 7.70, 1.85, 5.0, [
    "Calcula el origen del grid.",
    "Recorre las 2,500 casillas.",
    "CheckBox pregunta: ¿hay una pared en esta caja?",
    "Guarda la respuesta en bloqueada.",
], gap=0.82)
footer(s, "La capa Pared evita que otros objetos cuenten como paredes.")
nc(s, "Awake se ejecuta una sola vez al empezar. Primero centra el grid sobre el Plane: el origen "
      "es el centro del plano menos la mitad del grid.\n\n"
      "Después recorre todas las casillas. Para cada una crea una caja del tamaño de la casilla más "
      "un margen (celda / 2 + margen) y usa Physics.CheckBox para preguntar si algún collider de "
      "la capa Pared está dentro. Funciona aunque la pared esté girada, y por eso no marcamos las "
      "paredes a mano.\n\n"
      "Antes de usarlo se crea la capa Pared, se asigna al objeto paredes (con sus hijos) y se "
      "elige en el campo capaParedes del script.", ["code_awake"])

# 8 ------------------------------------------------------------ mapa real
s = new_slide()
header(s, K1, "EL MAPA QUE VE EL ENEMIGO",
       "Las casillas rosas son las paredes. BFS nunca entra en ellas.")
figure(s, "real_cuadricula.png", 0.62, 1.70, 4.00, 4.00)
cap(s, 0.62, 5.78, 4.4, "332 casillas bloqueadas de 2,500.")
figure(s, "checkbox.png", 5.22, 1.70, 4.00, 4.00)
cap(s, 5.22, 5.78, 4.4, "Zoom: una pared girada.")
tip(s, 9.82, 1.70, 2.89, 2.30, "MARGEN",
    "Engorda las paredes 0.1 para que el enemigo no roce las orillas.", accent=PINK)
tip(s, 9.82, 4.20, 2.89, 1.90, "COMPRUEBA",
    "En Play, mira la vista Scene: lo rosa debe cubrir las paredes.", accent=GREEN)
notes(s,
      "Resultado de marcar las paredes, dibujado con la misma lógica de CheckBox y los valores de "
      "la escena: celda 0.5, margen 0.1 y seis paredes. Salen 332 casillas bloqueadas de 2,500.\n\n"
      "A la derecha hay un zoom a pared_6, que está girada unos 56 grados. Las casillas rosas la "
      "cubren como escalones y un poco más: ese poco más es el margen.\n\n"
      "En Unity, el método OnDrawGizmos de S6_Grid dibuja estas mismas casillas en la vista Scene. "
      "Antes de seguir, verifica que las casillas rojas de Unity coinciden con tus paredes. Si no "
      "aparecen, revisa que capaParedes esté asignada y que paredes tenga la capa Pared.")

K2 = "BLOQUE 02 · BFS PASO A PASO"
# 10 ----------------------------------------------------------- onda
s = new_slide()
header(s, K2, "BFS: UNA ONDA EN EL AGUA",
       "BFS significa Breadth-First Search, o búsqueda en anchura.")
figure(s, "onda_abierta.png", 0.62, 1.70, 4.40, 4.40)
cap(s, 0.62, 6.12, 4.4, "Los números dicen cuántos pasos hay desde el centro.")
bullets(s, 5.45, 1.80, 7.26, [
    "Primero visita las casillas a 1 paso.",
    "Después las que están a 2 pasos, luego a 3, y así.",
    "Siempre avanza en las cuatro direcciones.",
    "La primera vez que toca la meta, ya encontró el camino más corto.",
], gap=0.88)
footer(s, "Como tirar una piedra al agua: la onda crece de manera pareja.")
notes(s,
      "La idea de BFS se entiende con una onda en el agua. Desde la casilla de inicio (el 0 del "
      "dibujo) la onda llega primero a las cuatro casillas vecinas, que están a 1 paso. Después "
      "llega a las casillas a 2 pasos, luego a 3, y así sucesivamente.\n\n"
      "Como la onda crece por distancias, la primera vez que toca una casilla es por el camino "
      "más corto. Por eso, cuando toca la meta, ya no hace falta buscar más.\n\n"
      "En una cuadrícula con movimientos arriba, abajo, izquierda y derecha, la onda tiene forma "
      "de rombo, como se ve en la figura. Este algoritmo se conoce desde hace décadas y se ha usado "
      "para resolver laberintos y mapas de juegos.")

# 11 ----------------------------------------------------------- cola y diccionario
s = new_slide()
header(s, K2, "DOS HERRAMIENTAS: COLA Y DICCIONARIO",
       "Con estas dos estructuras BFS no se pierde ni repite casillas.")
figure(s, "cola.png", 0.62, 1.70, 7.30, 2.40)
figure(s, "diccionario.png", 8.30, 1.70, 4.41, 2.80)
tip(s, 0.62, 4.40, 7.30, 1.70, "LA COLA",
    "Guarda las casillas que faltan por explorar. Sale primero la que entró primero, así la onda crece en orden.")
tip(s, 8.30, 4.70, 4.41, 1.40, "EL DICCIONARIO",
    "Anota de dónde vino cada casilla.", accent=BLUE)
notes(s,
      "BFS necesita solo dos estructuras.\n\n"
      "La cola (Queue en C#) es una fila de espera. Las casillas nuevas entran por un lado con "
      "Enqueue y la siguiente por explorar sale por el otro lado con Dequeue. Como el primero que "
      "entra es el primero que sale, las casillas más cercanas se exploran antes que las lejanas. "
      "Eso es lo que hace que la búsqueda avance como una onda.\n\n"
      "El diccionario (Dictionary) se llama vinoDe. Para cada casilla guarda desde cuál casilla "
      "llegamos a ella. Sirve para dos cosas: saber si una casilla ya fue visitada (si está en el "
      "diccionario, ya la visitamos) y reconstruir el camino al final.\n\n"
      "La tabla del dibujo es un ejemplo con el mapa pequeño que veremos enseguida: la casilla "
      "(1,1) vino de (0,1), igual que (0,0), y (1,2) vino de (1,1).")

# 12 ----------------------------------------------------------- 5 pasos
s = new_slide()
header(s, K2, "EL ALGORITMO EN 5 PASOS",
       "Es corto: cinco ideas que se repiten.")
steps(s, 0.62, 1.85, 6.90, [
    "Mete el inicio en la cola.",
    "Saca la primera casilla de la cola: es actual.",
    "Revisa sus vecinos. Si no son pared ni visitados, anota de dónde vinieron y mételos a la cola.",
    "Repite hasta llegar a la meta. Si la cola se vacía, no hay camino.",
    "Reconstruye el camino hacia atrás y voltea la lista.",
], gap=0.88)
figure(s, "vecinos.png", 7.90, 1.70, 4.81, 2.30)
tip(s, 7.90, 4.20, 4.81, 1.90, "VECINOS",
    "El código revisa 4 vecinos: derecha, izquierda, arriba y abajo. No usa diagonales.", accent=GREEN)
notes(s,
      "Resumen del algoritmo. Los pasos 2 y 3 se repiten dentro de un ciclo while.\n\n"
      "1. Se mete el inicio a la cola y se anota en vinoDe.\n"
      "2. Se saca la primera casilla de la cola.\n"
      "3. Para cada vecino (derecha, izquierda, arriba y abajo): si es libre y no se ha visitado, "
      "se anota vinoDe[vecino] = actual y se mete a la cola.\n"
      "4. Se repite hasta llegar a la meta. Si la cola se vacía sin llegar, no existe camino y el "
      "método regresa null.\n"
      "5. Para reconstruir se parte de la meta y se sigue vinoDe hacia atrás hasta el inicio; al "
      "final se voltea la lista para que quede en orden.\n\n"
      "En la extensión del tema veremos cómo agregar las diagonales.")

# 13 ----------------------------------------------------------- olas
s = new_slide()
header(s, K2, "EJEMPLO: LA ONDA RODEA LA PARED",
       "S es el enemigo, M es el jugador y las casillas rosas son pared.")
figure(s, "toy_olas.png", 0.62, 1.65, 12.09, 3.20)
bullets(s, 0.62, 5.00, 12.09, [
    "Paso 0: solo existe S. Paso 1: sus vecinos libres reciben un 1.",
    "Paso 2: los vecinos de esos reciben un 2. La pared no deja pasar la onda.",
], gap=0.55)
footer(s, "Cada número indica cuántos pasos hay desde S.")
notes(s,
      "Usamos un mapa pequeño de 6 columnas por 4 filas para ver el algoritmo completo. S está en "
      "la casilla (0,1), M en (4,1) y las casillas (2,0), (2,1) y (2,2) son pared. El único hueco "
      "está arriba, en (2,3).\n\n"
      "Primer panel: después de 0 pasos solo conocemos S.\n"
      "Segundo panel: los vecinos de S (arriba, abajo y a la derecha) reciben un 1. La izquierda "
      "queda fuera del mapa.\n"
      "Tercer panel: los vecinos de esas casillas reciben un 2. Fíjate que la onda llega a la pared "
      "y no pasa; solo sigue por las casillas libres.")

# 14 ----------------------------------------------------------- completa
s = new_slide()
header(s, K2, "LA ONDA LLEGA A M",
       "La onda sube, pasa por el hueco y baja hasta el jugador.")
figure(s, "toy_completo.png", 0.62, 1.70, 6.90, 4.40)
tip(s, 7.85, 1.70, 4.86, 1.40, "M TIENE UN 8", "El camino más corto mide 8 pasos.",
    accent=PINK)
tip(s, 7.85, 3.30, 4.86, 1.40, "EL HUECO", "La única salida de la pared es la casilla (2,3).",
    accent=BLUE)
tip(s, 7.85, 4.90, 4.86, 1.20, "SE DETIENE", "BFS se detiene al sacar a M. Las casillas en blanco nunca se visitan.", accent=GREEN)
notes(s,
      "Así queda el mapa cuando la onda cubre todas las casillas alcanzables. El jugador M recibe "
      "el número 8: hacen falta 8 pasos para llegar desde S rodeando la pared por el hueco de "
      "arriba.\n\n"
      "BFS se detiene en cuanto saca a M de la cola (if (actual == meta) break). Por eso en el "
      "dibujo no aparecen números en las casillas de abajo a la derecha: BFS nunca las visitó. "
      "Todavía aparecen un 8 junto a M y un 9, porque esas casillas ya habían entrado a la cola "
      "cuando M llegó al frente. Las casillas que están más lejos, como la 10, no se tocan.")

# 15 ----------------------------------------------------------- tabla cola
TOY_W = {(2, 0), (2, 1), (2, 2)}
q = [(0, 1)]
seen = {(0, 1)}
rows = [("Paso", "Sale de la cola", "Entran", "Cola después")]
for paso in range(1, 7):
    a = q.pop(0)
    nuevos = []
    for d in sim_bfs.DIRECCIONES:
        v = (a[0] + d[0], a[1] + d[1])
        if 0 <= v[0] < 6 and 0 <= v[1] < 4 and v not in TOY_W and v not in seen:
            seen.add(v)
            q.append(v)
            nuevos.append(v)
    rows.append((str(paso), fmt(a), " ".join(map(fmt, nuevos)) or "nada",
                 " ".join(map(fmt, q))))
s = new_slide()
header(s, K2, "LA COLA EN ACCIÓN",
       "Estos son los primeros 6 pasos del ejemplo, en el orden de las cuatro direcciones.")
tbl(s, 0.62, 1.70, 12.09, rows, [0.9, 2.4, 3.6, 5.19], row_h=0.50, head_h=0.50)
footer(s, "Orden de vecinos del código: derecha, izquierda, arriba, abajo.", y=5.78)
TABLA_NOTA = "\n".join(" | ".join(r) for r in rows)
notes(s,
      "Tabla de lo que pasa dentro de la cola con el mapa pequeño. Se generó con el mismo "
      "algoritmo del código, revisando los vecinos en el orden derecha, izquierda, arriba y abajo.\n\n"
      + TABLA_NOTA + "\n\n"
      "Observa dos cosas. Primero, la cola siempre saca por el frente y agrega por el final. "
      "Segundo, ninguna casilla entra dos veces: una casilla ya visitada ya no se vuelve a agregar.")

# 16 ----------------------------------------------------------- vinoDe
s = new_slide()
header(s, K2, "EL DICCIONARIO: DE DÓNDE VINO CADA CASILLA",
       "Cada flecha apunta a la casilla anterior.")
figure(s, "toy_vinode.png", 0.62, 1.70, 6.90, 4.40)
bullets(s, 7.85, 1.80, 4.86, [
    "Al entrar a la cola, cada casilla anota su origen.",
    "Las flechas forman un camino de regreso hasta S.",
    "Sin este diccionario solo sabríamos la distancia, no el camino.",
], gap=1.30)
footer(s, "vinoDe[vecino] = actual guarda la flecha.")
notes(s,
      "Cada vez que BFS descubre una casilla nueva guarda de dónde vino: vinoDe[vecino] = actual. "
      "En el dibujo, esa información son las flechas pequeñas. Todas las flechas terminan, tarde o "
      "temprano, en S.\n\n"
      "Esto es importante: la cola y los números solo dicen qué tan lejos está cada casilla. Para "
      "caminar necesitamos saber por dónde ir, y eso lo da el diccionario. Con él podemos empezar "
      "en M y seguir las flechas hacia atrás.")

# 17 ----------------------------------------------------------- reconstruir
CAM = sim_bfs.buscar_camino((0, 1), (4, 1), [[(x, z) in TOY_W for z in range(4)] for x in range(6)])
s = new_slide()
header(s, K2, "RECONSTRUIR EL CAMINO",
       "Se sigue vinoDe desde M hasta S, y luego se voltea la lista.")
figure(s, "toy_camino.png", 0.62, 1.70, 6.90, 4.40)
steps(s, 7.85, 1.85, 4.86, [
    "Empieza en M.",
    "Pasa a la casilla de donde vino.",
    "Repite hasta llegar a S.",
    "Voltea la lista (Reverse).",
], gap=0.74)
tip(s, 7.85, 4.95, 4.86, 1.15, "CAMINO FINAL",
    " ".join(map(fmt, CAM[:4])) + "\n" + " ".join(map(fmt, CAM[4:])), accent=GREEN)
nc(s, "Para reconstruir el camino, partimos de la meta y avanzamos hacia atrás con vinoDe hasta "
      "llegar al inicio. Los números amarillos del dibujo van en ese orden, del 1 al 7, empezando "
      "por la casilla anterior a M. La lista queda al revés, por eso se llama Reverse().\n\n"
      "Camino final del ejemplo (sin incluir S): " + " ".join(map(fmt, CAM)) + ".\n\n"
      "Detalle importante: la lista no incluye la casilla donde está el enemigo, así que el primer "
      "elemento siempre es la siguiente casilla por visitar.", ["code_bfs_b"])

# 19 ----------------------------------------------------------- codigo A
s = new_slide()
header(s, K2, "EL CÓDIGO: PREPARACIÓN",
       "Primero revisamos que haya camino posible y creamos las dos estructuras.")
code_img(s, "code_bfs_a", 0.62, 1.70, 7.50, 4.40)
steps(s, 8.45, 1.85, 4.26, [
    "Si inicio o meta es pared, regresa null.",
    "Crea la cola y el diccionario.",
    "Mete el inicio a la cola.",
    "Anota el inicio en vinoDe.",
], gap=0.86)
nc(s, "Primera parte de BuscarCamino en S6_Grid.cs.\n\n"
      "Devuelve una lista de casillas (List<Vector2Int>) o null si no hay camino. Primero revisa "
      "que el inicio y la meta no sean paredes ni estén fuera del plano.\n\n"
      "Después crea la cola y el diccionario vinoDe. Mete el inicio en la cola y también en "
      "vinoDe apuntando a sí mismo: así el inicio cuenta como visitado y sirve como señal de "
      "parada al reconstruir.", ["code_bfs_a"])

# 20 ----------------------------------------------------------- codigo loop
s = new_slide()
header(s, K2, "EL CÓDIGO: EL CICLO DE LA ONDA",
       "Aquí está la onda: sacar una casilla y meter a sus vecinos.")
code_img(s, "code_bfs_loop", 0.62, 1.70, 6.30, 4.40)
tip(s, 7.25, 1.70, 5.46, 1.30, "1 · SALE", "Dequeue saca a actual. Si es la meta, break.")
tip(s, 7.25, 3.15, 5.46, 1.45, "2 · FILTRA",
    "Se salta al vecino si es pared, está fuera del plano o ya fue visitado.", accent=BLUE)
tip(s, 7.25, 4.75, 5.46, 1.35, "3 · ENTRA", "Anota vinoDe y mete al vecino a la cola.",
    accent=GREEN)
nc(s, "Este es el ciclo de BFS dentro de BuscarCamino.\n\n"
      "Mientras la cola tenga casillas: se saca la primera (actual). Si es la meta, termina el "
      "ciclo con break porque ya encontramos el camino.\n\n"
      "Para cada una de las cuatro direcciones se calcula el vecino (actual + d). Si no es libre "
      "(pared o fuera del plano) o ya está en vinoDe, se salta con continue. Si pasa los filtros, "
      "se anota vinoDe[vecino] = actual y se mete a la cola.\n\n"
      "Las dos llamadas continue son lo que evita que la onda regrese por donde ya pasó.",
   ["code_bfs_loop"])

# 21 ----------------------------------------------------------- codigo B
s = new_slide()
header(s, K2, "EL CÓDIGO: RECONSTRUIR",
       "Después del ciclo, seguimos las flechas de vinoDe hacia atrás.")
code_img(s, "code_bfs_b", 0.62, 1.70, 7.20, 4.40)
steps(s, 8.15, 1.85, 4.56, [
    "Si la meta nunca entró a vinoDe, no hay camino: null.",
    "Parte de la meta.",
    "Agrega la casilla y retrocede con vinoDe.",
    "Reverse() la deja en orden.",
], gap=0.95)
nc(s, "Segunda parte de BuscarCamino.\n\n"
      "Si la meta no está en vinoDe, la onda nunca la alcanzó (por ejemplo, está encerrada por "
      "paredes) y el método regresa null.\n\n"
      "Si la alcanzó, se recorre vinoDe desde la meta hasta el inicio, agregando cada casilla a "
      "la lista. El inicio no se agrega, por eso camino[0] será siempre la siguiente casilla. "
      "Como se agregó de la meta hacia el inicio, se voltea con Reverse().", ["code_bfs_b"])

# 22 ----------------------------------------------------------- real
ENE, JUG = sim_bfs.mundo_a_celda(22, 22), sim_bfs.mundo_a_celda(0.54, 0.44)
CAM_REAL = sim_bfs.buscar_camino(ENE, JUG)
s = new_slide()
header(s, K2, "BFS EN LA ESCENA REAL",
       f"El enemigo en {fmt(ENE)} llega al jugador en {fmt(JUG)} con {len(CAM_REAL)} pasos.")
figure(s, "real_onda.png", 0.62, 1.70, 4.00, 4.00)
cap(s, 0.62, 5.78, 4.4, "Onda: naranja cerca, azul lejos.")
figure(s, "real_camino.png", 5.22, 1.70, 4.00, 4.00)
cap(s, 5.22, 5.78, 4.4, "Camino que sigue el enemigo.")
tip(s, 9.82, 1.70, 2.89, 2.30, "UN CAMINO",
    "Hay varios caminos igual de cortos. BFS elige uno.", accent=BLUE)
tip(s, 9.82, 4.20, 2.89, 1.90, "EN UNITY", "La línea amarilla sale de OnDrawGizmos.", accent=GREEN)
notes(s,
      "Aquí aplicamos BFS al mapa real. A la izquierda se ve la onda desde el enemigo: los colores "
      "van de naranja (cerca) a azul (lejos). Se ve cómo rodea las paredes en lugar de cruzarlas.\n\n"
      f"A la derecha está el camino que devuelve BuscarCamino: {len(CAM_REAL)} casillas desde "
      f"{fmt(ENE)} hasta {fmt(JUG)}. Como todos los pasos cuestan lo mismo, hay muchos caminos "
      "igual de cortos; BFS devuelve el primero que encuentra según el orden de las direcciones "
      "(derecha, izquierda, arriba y abajo). Por eso el camino parece una L.\n\n"
      "En Unity esta misma línea amarilla se ve en la vista Scene gracias a OnDrawGizmos del "
      "enemigo. Las figuras se calcularon con la réplica en Python sim_bfs.py, que incluye "
      "pruebas con assert.")

K3 = "BLOQUE 03 · EL ENEMIGO"
# 24 ----------------------------------------------------------- campos
s = new_slide()
header(s, K3, "LOS CAMPOS DEL ENEMIGO",
       "S6_EnemigoCilindro necesita el jugador, el camino y un temporizador.")
code_img(s, "code_campos_enemigo", 0.62, 1.70, 7.60, 3.00)
tip(s, 8.50, 1.70, 4.21, 1.50, "cubo", "El Transform del jugador (velma_sprite_walk_3D).")
tip(s, 8.50, 3.40, 4.21, 1.50, "camino", "Lista de casillas por recorrer.", accent=BLUE)
tip(s, 8.50, 5.10, 4.21, 1.00, "cadaCuanto", "Segundos entre cálculos (0.25).", accent=GREEN)
bullets(s, 0.62, 5.00, 7.60, ["Update llama a Perseguir() en cada cuadro, sin radio de detección."], gap=0.7)
nc(s, "Campos de S6_EnemigoCilindro.cs. cubo es el Transform del jugador, que se arrastra en el "
      "Inspector. camino es la lista de casillas que devuelve BFS. tiempoRecalculo cuenta hacia "
      "atrás y cadaCuanto dice cada cuántos segundos se vuelve a calcular el camino (0.25 s).\n\n"
      "Update solo llama a Perseguir() en cada cuadro: el cilindro persigue siempre, no tiene radio de detección. En la escena, velocidad vale 30 y cubo apunta a velma_sprite_walk_3D. Hace falta using System.Collections.Generic "
      "para usar List.", ["code_campos_enemigo"], path=CSE)

# 25 ----------------------------------------------------------- perseguir
s = new_slide()
header(s, K3, "PERSEGUIR(): BFS Y MOVIMIENTO",
       "Calcula el camino de vez en cuando y camina hacia la siguiente casilla.")
code_img(s, "code_perseguir", 0.62, 1.70, 5.20, 4.40)
steps(s, 6.20, 1.85, 6.51, [
    "Resta el tiempo transcurrido al temporizador.",
    "Si llegó a 0, vuelve a llamar a BuscarCamino.",
    "Si no hay camino, se queda quieto.",
    "Toma camino[0] como objetivo.",
    "Camina hacia él con MoveTowards (y espera ahí).",
], gap=0.84)
nc(s, "Perseguir() hace dos cosas.\n\n"
      "1. Cada cadaCuanto segundos llama a grid.BuscarCamino con la casilla actual del enemigo y la "
      "casilla del jugador (convertidas con MundoACelda). No lo hace en cada cuadro porque no hace "
      "falta y gastaría tiempo.\n"
      "2. Si hay camino, toma la primera casilla (camino[0]), la convierte a posición del mundo con "
      "CeldaAMundo y se mueve hacia ella con Vector3.MoveTowards. La altura no cambia.\n\n"
      "Si el camino es null (no hay ruta) o está vacío, el enemigo se queda quieto. Ojo: camino[0] no se borra al llegar; la diapositiva siguiente explica qué consecuencia tiene.",
   ["code_perseguir"], path=CSE)

# 26 ----------------------------------------------------------- camino[0] y tiempo
s = new_slide()
header(s, K3, "UNA CASILLA CADA 0.25 SEGUNDOS",
       "Con este código, el enemigo avanza solo hasta camino[0] y espera al siguiente cálculo.")
figure(s, "tiempo.png", 0.62, 1.70, 8.00, 2.30)
card(s, 8.95, 1.70, 3.76, 2.30, ORANGE)
text(s, 9.25, 1.85, 3.3, 0.8, "2 u/s", role="stat_sm", color=ORANGE_TEXT)
text(s, 9.25, 2.75, 3.3, 1.1, "velocidad máxima: 0.5 de casilla entre 0.25 s.", role="note", color=BODY)
tip(s, 0.62, 4.20, 5.90, 1.90, "CAMINO[0]",
    "BuscarCamino no incluye la casilla actual. camino[0] es la siguiente y nunca se borra de la lista.")
tip(s, 6.81, 4.20, 5.90, 1.90, "LA VELOCIDAD NO AYUDA",
    "Al llegar a camino[0] el enemigo se queda quieto. Subir velocidad no lo hace más rápido.",
    accent=PINK)
notes(s,
      "Esta diapositiva explica un detalle importante de nuestro código actual.\n\n"
      "BuscarCamino no incluye la casilla donde ya está el enemigo, así que camino[0] siempre es la "
      "siguiente casilla. Perseguir() mueve al enemigo hacia camino[0] con MoveTowards, pero nunca "
      "quita esa casilla de la lista. Cuando el enemigo llega a ella, sigue apuntando a la misma "
      "casilla y se queda quieto hasta que pasen 0.25 s y se recalcule el camino. Entonces camino[0] "
      "es la casilla siguiente.\n\n"
      "Resultado: el enemigo avanza una casilla (0.5 unidades) por cada cálculo. Eso da 0.5 / 0.25 = "
      "2 unidades por segundo, sin importar el valor de velocidad (en la escena está en 30, pero ya "
      "no cambia nada). Con el camino real de 87 casillas tardaría unos 22 segundos. Se ve como "
      "pasos cortos y rápidos con una pausa.\n\n"
      "Dos formas de arreglarlo, que se ven al final: borrar camino[0] al llegar a la casilla, o "
      "bajar cadaCuanto.")

# 28 ----------------------------------------------------------- errores
s = new_slide()
header(s, K3, "ERRORES COMUNES",
       "Casi todos se resuelven mirando la Scene y la Consola.")
tbl(s, 0.62, 1.70, 12.09, [
    ("Síntoma", "Causa probable"),
    ("NullReferenceException", "Falta el objeto Grid en la escena, o cubo sin asignar."),
    ("El enemigo no se mueve", "Él o el jugador está fuera del grid o dentro de una pared."),
    ("No hay casillas rosas", "capaParedes sin asignar o paredes sin la capa Pared."),
    ("Casillas desfasadas", "El campo plano no apunta al Plane o el tamaño no coincide."),
    ("Avanza muy lento", "Solo da una casilla por cálculo. Subir velocidad no sirve."),
], [3.6, 8.49], row_h=0.62)
footer(s, "En todos los casos: primero verifica el grid, después el enemigo.")
notes(s,
      "Errores frecuentes al probar la escena con S6_EnemigoCilindro.\n\n"
      "- NullReferenceException: Perseguir() usa S6_Grid.Instancia, que se crea en Awake. Si no hay un "
      "objeto Grid con el script, Instancia es null. También pasa si el campo cubo no se arrastró "
      "en el Inspector.\n"
      "- Si el enemigo no se mueve, BuscarCamino devolvió null: el enemigo o el jugador está fuera del "
      "grid o sobre una casilla de pared.\n"
      "- Si no hay casillas rosas, falta asignar capaParedes o la capa Pared.\n"
      "- Si las casillas están desfasadas, plano no apunta al Plane o ancho y alto por celda no "
      "coinciden con el tamaño del Plane.\n"
      "- Si avanza lento, es porque solo avanza hasta camino[0] y espera al siguiente cálculo.")

# 29 ----------------------------------------------------------- limites
s = new_slide()
header(s, K3, "LÍMITES Y MEJORAS",
       "Nuestro código funciona, pero se puede mejorar.")
tip(s, 0.62, 1.70, 3.90, 2.50, "AVANZAR MEJOR",
    "Borra camino[0] al llegar a la casilla (RemoveAt) para seguir con la siguiente.", accent=PINK)
tip(s, 4.72, 1.70, 3.90, 2.50, "RADIO DE DETECCIÓN",
    "Hoy el cilindro persigue siempre. Persigue solo si el jugador está cerca.", accent=ORANGE)
tip(s, 8.82, 1.70, 3.89, 2.50, "DIAGONALES",
    "Agrega 4 direcciones más. Los giros se ven más naturales.", accent=BLUE)
bullets(s, 0.62, 4.45, 12.09, [
    "Muchos enemigos: un solo BFS desde el jugador (flow field). Con costos: Dijkstra o A*.",
    "El camino sigue las líneas del grid y no suaviza las esquinas.",
], gap=0.70)
footer(s, "BFS es el primer paso: A* es el mismo esquema con una heurística.")
notes(s,
      "Mejoras al código actual.\n\n"
      "- Avanzar mejor: en Perseguir(), cuando la distancia a camino[0] sea muy pequeña, llama a "
      "camino.RemoveAt(0) para pasar a la siguiente casilla sin esperar el recálculo.\n"
      "- Radio de detección: S6_EnemigoCilindro persigue siempre, sin importar la distancia. Se puede "
      "agregar una condición como la de la esfera: solo buscar camino si el jugador está a menos de "
      "radioDeteccion.\n"
      "- Diagonales: agrega (1,1), (1,-1), (-1,1) y (-1,-1) al arreglo direcciones. Una diagonal mide "
      "más que un paso recto, así que BFS ya no garantiza el camino más corto en distancia real.\n"
      "- Muchos enemigos: en vez de un BFS por enemigo, se hace un solo BFS desde el jugador y se "
      "guarda para cada casilla la dirección hacia el jugador. Eso se llama flow field.\n"
      "- Costos distintos: Dijkstra y A* resuelven este caso. A* es como BFS pero con una "
      "heurística que lo guía hacia la meta.")

# ---- cierre
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
text(s, 0.0, 1.55, 13.33, 1.35, "¿PREGUNTAS?", role="closing", align=PP_ALIGN.CENTER)
text(s, 0.0, 3.18, 13.33, 0.38, "Un enemigo que rodea paredes con solo una cola y un diccionario.",
     role="subtitle", align=PP_ALIGN.CENTER)
text(s, 0.0, 3.72, 13.33, 0.38, "Grid, BFS y camino[0]: tres ideas que se pueden probar en Unity.",
     role="note", color=BODY, align=PP_ALIGN.CENTER)
picture_fit(s, ROOT / "decor" / "star.png", 1.55, 2.30, 0.85, 0.85, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 3.60, 4.15, 0.75, 0.75, border=False)
picture_fit(s, ROOT / "decor" / "tree-small.png", 1.10, 4.36, 1.15, 2.06, border=False)
picture_fit(s, ROOT / "decor" / "cloud-low.png", 9.85, 4.68, 2.65, 1.42, border=False)
notes(s, "Cierre del tema 8.8.1. Resumen: convertimos el piso en un grid, marcamos las paredes con "
         "CheckBox, usamos BFS con una cola y un diccionario para encontrar el camino más corto, y "
         "el enemigo camina casilla por casilla recalculando cada 0.25 segundos.")


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
