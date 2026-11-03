#!/usr/bin/env python3
"""Construye T8.6.1 - Matemáticas para enemigos.

Sigue la plantilla FINAL-plantilla-videojuegos.pptx: fondo pixel art,
Neuromax, tarjetas blancas y acentos naranja/rosa. El código se muestra
como imagen y se copia en las notas de cada diapositiva.
"""

import zipfile
from pathlib import Path

from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
PPTX = ROOT.parent / "T8.6.1-Matematicas-para-enemigos.pptx"

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


def text(slide, x, y, w, h, value, size, color=INK, font=REG,
         bold=False, italic=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, line_spacing=1.0, space_after=0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, line in enumerate(value.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_before = Pt(0)
        p.space_after = Pt(space_after)
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        _font(r, size, color, font, bold, italic)
    return box


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


def picture_fit(slide, path, x, y, w, h, border=True, border_w=1.2):
    im = Image.open(path)
    iw, ih = im.size
    scale = min(w / iw, h / ih)
    nw, nh = iw * scale, ih * scale
    left, top = x + (w - nw) / 2, y + (h - nh) / 2
    pic = slide.shapes.add_picture(str(path), Inches(left), Inches(top),
                                   Inches(nw), Inches(nh))
    if border:
        pic.line.color.rgb = WHITE
        pic.line.width = Pt(border_w)
    return pic


def picture_fill(slide, path, x, y, w, h, border=True, border_w=1.2):
    im = Image.open(path)
    iw, ih = im.size
    ratio = iw / ih
    target = w / h
    left = top = 0
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
    text(slide, 0.81, 0.27, 10.5, 0.22, kicker, 9.5, INK, SEM)
    text(slide, 0.62, 0.52, 11.95, 0.72, title, 36, INK, SEM,
         line_spacing=0.95)
    text(slide, 0.62, 1.18, 11.95, 0.40, subtitle, 16, BODY, REG)


def footer(slide, value, y=6.18, h=0.50):
    rect(slide, 0.55, y, 11.17, h, WHITE)
    text(slide, 0.75, y + 0.12, 10.80, 0.28, value, 12.2, BODY, REG)


def notes(slide, value):
    slide.notes_slide.notes_text_frame.text = value


def notes_code(slide, intro, path, code, extra=""):
    value = intro.strip()
    value += "\n\nCÓDIGO DE LA DIAPOSITIVA (" + path + "):\n\n"
    value += code.strip("\n")
    if extra:
        value += "\n\n" + extra.strip()
    slide.notes_slide.notes_text_frame.text = value


def card(slide, x, y, w, h, accent=ORANGE, fill=WHITE, line=None):
    rect(slide, x, y, w, h, fill, line)
    rect(slide, x, y, 0.07, h, accent)


def label(slide, x, y, w, value, color=ORANGE_TEXT):
    text(slide, x, y, w, 0.22, value, 9.5, color, SEM)


def pill(slide, x, y, w, value, color=BODY, fill=WHITE):
    rect(slide, x, y, w, 0.26, fill, LINE, 0.75, MSO_SHAPE.ROUNDED_RECTANGLE)
    text(slide, x, y + 0.04, w, 0.18, value, 7.5, color, SEM,
         align=PP_ALIGN.CENTER)


def shot(slide, path, x, y, w, h, pad=0.08):
    rect(slide, x, y, w, h, WHITE)
    return picture_fit(slide, path, x + pad, y + pad, w - 2 * pad, h - 2 * pad,
                       border=False)


def fig(slide, path, x, y, w, h):
    rect(slide, x, y, w, h, WHITE, LINE, 1.0)
    return picture_fit(slide, path, x + 0.08, y + 0.08, w - 0.16, h - 0.16,
                       border=False)


def code(slide, name, x, y, w, h):
    return picture_fit(slide, ROOT / "codigo" / name, x, y, w, h,
                       border=True, border_w=1.0)


def table(slide, x, y, w, h, rows, col_widths, font_size=12,
          header_size=12, row_h=None, align=PP_ALIGN.LEFT):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y),
                                   Inches(w), Inches(h))
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
            _font(r, header_size if i == 0 else font_size,
                  WHITE if i == 0 else INK, SEM if i == 0 else REG)
            cell.fill.solid()
            cell.fill.fore_color.rgb = DARK if i == 0 else (WHITE if i % 2 == 1 else SOFT)
            cell.margin_left = Inches(0.09)
            cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.03)
            cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    return tbl


def bullets(slide, x, y, w, items, size=13, gap=0.78, color=BODY,
            bullet_color=ORANGE_TEXT):
    for i, item in enumerate(items):
        text(slide, x, y + i * gap, 0.18, 0.3, "•", size + 1, bullet_color, SEM)
        text(slide, x + 0.24, y + i * gap, w - 0.24, gap, item, size, color, REG,
             line_spacing=1.02)


# ---------------------------------------------------------------- deck
prs = Presentation()
prs.slide_width = Inches(SW)
prs.slide_height = Inches(SH)
prs.core_properties.title = "T8.6.1 · Matemáticas para enemigos"
prs.core_properties.author = "TC2005B · Construcción de Software"
prs.core_properties.subject = "Distancia, vectores, patrulla, pisotón y persecución"
prs.core_properties.keywords = "Unity, C#, atan2, vectores, enemigos, TC2005B"
prs.core_properties.language = "es-MX"

# 0 ---------------------------------------------------------------- portada
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
rect(s, 0.62, 0.32, 0.09, 0.09, ORANGE)
text(s, 0.81, 0.28, 9.5, 0.22, "8.6.1 · MATEMÁTICAS PARA ENEMIGOS", 9.5, INK, SEM)
text(s, 0.62, 0.92, 6.00, 2.70, "DISTANCIA,\nÁNGULOS\nY VECTORES", 48, INK, SEM,
     line_spacing=0.92)
text(s, 0.62, 3.64, 5.55, 0.80,
     "Cómo un enemigo decide a dónde moverse y cuándo el jugador lo pisa.",
     20, INK, REG, line_spacing=1.02)
text(s, 0.62, 4.48, 5.45, 0.72,
     "Patrulla entre cuatro esquinas, detecta al jugador y reacciona a un pisotón.",
     14, BODY, REG, line_spacing=1.02)
text(s, 0.62, 5.62, 5.40, 0.28, "TC2005B · Construcción de Software", 12.5, INK, REG)
text(s, 0.62, 5.96, 5.40, 0.28, "Unity · C# · Sample_Game", 11, MUTED, REG)

rect(s, 6.55, 0.66, 6.18, 4.95, DARK)
shot(s, ROOT / "img" / "escena-esfera.png", 6.75, 0.86, 5.78, 4.55, pad=0.0)
rect(s, 6.75, 0.86, 5.78, 4.55, None, WHITE, 1.2)
pill(s, 6.95, 0.72, 1.35, "UNITY · C#", WHITE, DARK)
picture_fit(s, ROOT / "decor" / "star.png", 0.55, 6.30, 0.75, 0.75, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 11.55, 6.10, 0.95, 0.95, border=False)
notes(s,
      "Bienvenida al tema 8.6.1. Hoy construimos el enemigo esfera del proyecto "
      "Sample_Game.\n\n"
      "El recorrido es: medir distancias, restar y normalizar vectores, patrullar "
      "entre cuatro esquinas, detectar un pisotón con atan2 y perseguir al cubo "
      "cuando entra en un radio de detección.\n\n"
      "La meta no es memorizar fórmulas: es entender qué operación resuelve cada "
      "decisión del enemigo. Todo el código se muestra en imágenes y se copia en "
      "las notas de cada diapositiva.")

# 1 ---------------------------------------------------------------- agenda
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "HOY", "LO QUE VEREMOS HOY",
       "Cuatro ideas matemáticas construyen una mecánica completa.")
rows = [
    ("01", "DISTANCIA", "Medir con raíz(dx*dx + dz*dz) y separar la altura cuando hace falta.", ORANGE_TEXT),
    ("02", "VECTORES", "Restar, normalizar y sumar para mover al enemigo a velocidad constante.", PINK),
    ("03", "PATRULLA", "Cuatro esquinas, un objetivo aleatorio y un cambio cada cinco segundos.", BLUE),
    ("04", "PISOTÓN Y PERSECUCIÓN", "Dos condiciones para el pisotón y un radio para perseguir al jugador.", GREEN),
]
for i, (num, title, desc, color) in enumerate(rows):
    y = 1.64 + i * 0.80
    card(s, 0.62, y, 12.09, 0.72, color)
    text(s, 0.82, y + 0.16, 0.45, 0.30, num, 13, color, SEM)
    text(s, 1.42, y + 0.10, 8.60, 0.30, title, 18, INK, SEM)
    text(s, 1.46, y + 0.43, 10.40, 0.25, desc, 12, BODY, REG)
text(s, 0.62, 5.15, 12.09, 0.62,
     "Cada bloque agrega una decisión al enemigo. Al final, las cuatro trabajan juntas.",
     15, INK, SEM, line_spacing=1.02)
text(s, 0.62, 5.78, 11.6, 0.30,
     "El taller se hace en Unity con C# y se apoya en el proyecto de T8.5.2.", 12, BODY, REG)
notes(s,
      "Recorrido en cuatro bloques.\n\n"
      "1. Distancia: medir cuánto falta para llegar y cuándo el cubo está cerca.\n"
      "2. Vectores: restar para obtener la dirección, normalizar para no acelerar "
      "en diagonal y sumar para avanzar.\n"
      "3. Patrulla: cuatro esquinas, un índice objetivo y un temporizador.\n"
      "4. Pisotón y persecución: ángulo con atan2, radio horizontal y cambio de "
      "objetivo cuando el cubo entra en el radio de detección.\n\n"
      "La base es el proyecto de T8.5.2: el cubo ya se mueve y salta.")

# 2 ---------------------------------------------------------------- seccion 01
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
text(s, 0.62, 0.98, 2.0, 1.0, "01", 48, ORANGE_TEXT, SEM)
text(s, 0.62, 1.92, 7.40, 1.60, "DISTANCIA", 48, INK, SEM, line_spacing=0.92)
rect(s, 0.62, 3.85, 2.20, 0.07, ORANGE)
text(s, 0.62, 4.12, 6.60, 0.90,
     "Todo empieza por medir cuánto falta para llegar.", 20, INK, REG, line_spacing=1.02)
text(s, 0.62, 5.22, 7.40, 0.30,
     "DISTANCIA · VECTORES · ATAN2 · PERSECUCIÓN", 9.5, BODY, SEM)
picture_fit(s, ROOT / "decor" / "star.png", 9.56, 1.10, 1.10, 1.10, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 11.35, 3.35, 0.95, 0.95, border=False)
picture_fit(s, ROOT / "decor" / "cloud-low.png", 9.55, 4.95, 2.45, 1.40, border=False)
picture_fit(s, ROOT / "decor" / "tree-small.png", 11.75, 4.75, 0.85, 1.55, border=False)
notes(s,
      "Bloque 1. Antes de mover un enemigo hay que responder dos preguntas: "
      "¿cuánto falta para llegar? y ¿qué tan cerca está el jugador?\n\n"
      "La distancia es la longitud del vector que une dos puntos. En el plano "
      "XZ se calcula con las componentes x y z. La altura se usa después, en el "
      "ángulo del pisotón.")

# 3 ---------------------------------------------------------------- distancia
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · DISTANCIA", "MEDIR LA DISTANCIA ENTRE DOS PUNTOS",
       "La distancia es la longitud del vector que une los dos centros.")
label(s, 0.62, 1.65, 4.6, "LA FÓRMULA")
text(s, 0.62, 1.96, 5.10, 0.92,
     "d = raíz(dx*dx + dy*dy + dz*dz)", 22, INK, SEM, line_spacing=1.0)
for i, (name, value) in enumerate([
    ("dx", "x2 - x1"),
    ("dy", "y2 - y1"),
    ("dz", "z2 - z1"),
]):
    y = 2.92 + i * 0.46
    pill(s, 0.62, y, 0.55, name, INK, SOFT)
    text(s, 1.30, y + 0.02, 3.8, 0.28, "= " + value, 14, BODY, REG)
card(s, 0.62, 4.55, 4.95, 1.18)
text(s, 0.86, 4.68, 4.40, 0.24, "EN EL PLANO", 9.5, ORANGE_TEXT, SEM)
text(s, 0.86, 4.98, 4.50, 0.58,
     "horizontal = raíz(dx*dx + dz*dz)", 18, INK, SEM)
text(s, 0.86, 5.34, 4.45, 0.24,
     "La altura dy se trata aparte, en el ángulo.", 11, BODY, REG)
fig(s, ROOT / "figuras" / "distancia.png", 5.80, 1.62, 6.90, 3.48)
text(s, 5.92, 5.20, 6.65, 0.55,
     "Figura 1. La esfera E y la esquina Q están a la misma altura. La distancia "
     "es la hipotenusa en el plano XZ.", 10, MUTED, REG, line_spacing=1.0)
footer(s, "Si los dos puntos están a la misma altura, dy = 0 y la distancia 3D coincide con la horizontal.")
notes(s,
      "La distancia completa entre dos puntos usa las tres componentes: "
      "d = raíz(dx*dx + dy*dy + dz*dz).\n\n"
      "dx, dy y dz son las diferencias entre las coordenadas de los dos puntos. "
      "Si la esfera y la esquina están a la misma altura, dy = 0. Entonces la "
      "fórmula se reduce a raíz(dx*dx + dz*dz), que es la distancia horizontal.\n\n"
      "En el pisotón se usa la distancia horizontal porque la altura se analiza "
      "por separado con el ángulo. En la patrulla se usa la distancia completa, "
      "pero como la esfera y las esquinas están a y = 0.5, el resultado coincide.")

# 4 ---------------------------------------------------------------- ejemplo distancia
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · DISTANCIA", "UN EJEMPLO CON NÚMEROS",
       "La fórmula produce un resultado que se puede comprobar a mano.")
table(s, 0.62, 1.68, 7.55, 2.55, [
    ["Punto", "x", "y", "z"],
    ["E (esfera)", "4.5", "0.5", "4.5"],
    ["Q (esquina)", "-4.5", "0.5", "-4.5"],
    ["diferencia", "-9", "0", "-9"],
], [2.80, 1.55, 1.60, 1.60], font_size=14, header_size=13, row_h=0.50)
card(s, 8.42, 1.68, 4.25, 2.55)
text(s, 8.66, 1.82, 3.80, 0.24, "CÁLCULO", 9.5, ORANGE_TEXT, SEM)
text(s, 8.66, 2.12, 3.80, 0.36, "d = raíz(81 + 0 + 81)", 17, INK, SEM)
text(s, 8.66, 2.62, 3.80, 0.36, "d = raíz(162)", 17, INK, SEM)
text(s, 8.66, 3.12, 3.80, 0.60, "d = 12.73", 24, ORANGE_TEXT, SEM)
card(s, 0.62, 4.52, 12.05, 1.08, BLUE)
text(s, 0.88, 4.68, 11.45, 0.30, "La misma fórmula se usa para la esquina y para el cubo.",
     15, INK, SEM)
text(s, 0.88, 5.06, 11.45, 0.28,
     "Solo cambia el punto que se resta: primero la esquina, después la posición del cubo.",
     11.5, BODY, REG)
footer(s, "La distancia está en unidades de la escena: 12.73 unidades separan las dos esquinas opuestas.")
notes(s,
      "Ejemplo con la esfera en una esquina y la esquina opuesta.\n\n"
      "E = (4.5, 0.5, 4.5) y Q = (-4.5, 0.5, -4.5).\n"
      "dx = -9, dy = 0, dz = -9.\n"
      "d = raíz(81 + 0 + 81) = raíz(162) = 12.73.\n\n"
      "La misma operación se repite con el cubo: se resta su posición y se mide "
      "el vector. En el pisotón, la distancia horizontal se calcula aparte porque "
      "la altura se usa en el ángulo.")

# 5 ---------------------------------------------------------------- seccion 02
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
text(s, 0.62, 0.98, 2.0, 1.0, "02", 48, PINK, SEM)
text(s, 0.62, 1.92, 8.20, 1.60, "VECTORES", 48, INK, SEM, line_spacing=0.92)
rect(s, 0.62, 3.85, 2.20, 0.07, PINK)
text(s, 0.62, 4.12, 7.20, 0.90,
     "Restar, normalizar y sumar: tres operaciones para mover al enemigo.",
     20, INK, REG, line_spacing=1.02)
text(s, 0.62, 5.22, 7.40, 0.30,
     "RESTA · LONGITUD · NORMALIZACIÓN · SUMA", 9.5, BODY, SEM)
picture_fit(s, ROOT / "decor" / "star.png", 9.56, 1.10, 1.10, 1.10, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 11.35, 3.35, 0.95, 0.95, border=False)
picture_fit(s, ROOT / "decor" / "cloud-low.png", 9.55, 4.95, 2.45, 1.40, border=False)
picture_fit(s, ROOT / "decor" / "tree-small.png", 11.75, 4.75, 0.85, 1.55, border=False)
notes(s,
      "Bloque 2. Un vector tiene dirección y longitud. Para mover al enemigo se "
      "usan tres operaciones: restar para saber hacia dónde ir, normalizar para "
      "que la diagonal no sea más rápida y sumar para dar el siguiente paso.\n\n"
      "Todas las operaciones se hacen componente por componente.")

# 6 ---------------------------------------------------------------- resta
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · VECTORES", "RESTAR VECTORES: ¿HACIA DÓNDE VOY?",
       "La resta entre el objetivo y la posición actual produce el vector que falta recorrer.")
fig(s, ROOT / "figuras" / "vector_resta.png", 0.62, 1.64, 6.45, 3.63)
text(s, 7.30, 1.70, 5.40, 0.70,
     "hacia = objetivo - posición", 22, INK, SEM, line_spacing=1.0)
bullets(s, 7.30, 2.62, 5.30, [
    "La resta se hace componente por componente.",
    "El vector apunta del enemigo al objetivo.",
    "Su longitud es la distancia que falta.",
    "El signo importa: al revés, apunta en contra.",
], size=12.5, gap=0.66)
code(s, "code_resta.png", 7.30, 5.06, 5.30, 0.76)
footer(s, "El vector hacia guarda la dirección y la distancia en un solo valor de tipo Vector3.")
notes_code(s,
           "La resta de vectores se hace coordenada por coordenada: "
           "(x2 - x1, y2 - y1, z2 - z1). El resultado apunta del punto inicial al "
           "punto final.\n\n"
           "En el script, hacia = objetivo - transform.position. Ese vector se "
           "usa para medir la distancia y, después de normalizarlo, para mover.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """Vector3 hacia = objetivo - transform.position;
float distancia = Longitud(hacia);""")

# 7 ---------------------------------------------------------------- suma
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · VECTORES", "SUMAR VECTORES: DAR EL SIGUIENTE PASO",
       "La posición nueva es la posición actual más la dirección multiplicada por el paso.")
fig(s, ROOT / "figuras" / "vector_suma.png", 0.62, 1.64, 6.40, 3.60)
text(s, 7.25, 1.70, 5.45, 0.80,
     "posición nueva = posición actual + dirección × paso", 19, INK, SEM,
     line_spacing=1.0)
bullets(s, 7.25, 2.74, 5.35, [
    "dirección: vector de longitud 1.",
    "paso: distancia que se recorre en un fotograma.",
    "La altura y no cambia: la esfera no se eleva.",
], size=12.5, gap=0.66)
code(s, "code_suma.png", 7.25, 4.50, 5.40, 1.50)
footer(s, "La suma se aplica a x y a z. La y se copia tal cual para conservar la altura.")
notes_code(s,
           "La posición nueva se construye con un Vector3 nuevo. Se suma a x y a z; "
           "la y se conserva.\n\n"
           "El paso es la distancia recorrida en este fotograma. Sin él, la esfera "
           "se teletransportaría al objetivo.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """transform.position = new Vector3(
    transform.position.x + direccion.x * paso,
    transform.position.y,                       // la altura no cambia
    transform.position.z + direccion.z * paso
);""")

# 8 ---------------------------------------------------------------- longitud
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · VECTORES", "MEDIR LA LONGITUD DE UN VECTOR",
       "La longitud es la raíz de la suma de los cuadrados de sus componentes.")
code(s, "code_longitud.png", 0.62, 1.74, 6.15, 1.86)
text(s, 7.05, 1.72, 5.60, 0.50,
     "longitud = raíz(x*x + y*y + z*z)", 20, INK, SEM)
bullets(s, 7.05, 2.42, 5.55, [
    "Math.Sqrt recibe la suma y devuelve un double.",
    "El resultado se convierte a float con (float).",
    "Usa Math.Sqrt, no Vector3.Distance.",
], size=12.5, gap=0.62)
card(s, 0.62, 4.12, 6.15, 1.45, GREEN)
text(s, 0.86, 4.25, 5.55, 0.24, "EJEMPLO", 9.5, GREEN, SEM)
text(s, 0.86, 4.55, 5.60, 0.34, "v = (3, 0, 4)", 18, INK, SEM)
text(s, 0.86, 4.96, 5.60, 0.34, "raíz(9 + 0 + 16) = raíz(25) = 5", 17, INK, SEM)
text(s, 7.05, 4.40, 5.55, 0.80,
     "La longitud siempre es positiva o cero. Solo es cero cuando el vector es (0, 0, 0).",
     12.5, BODY, REG, line_spacing=1.03)
footer(s, "El archivo necesita using System; para poder usar Math.Sqrt.")
notes_code(s,
           "Longitud aplica la fórmula de la distancia al vector. System.Math.Sqrt "
           "trabaja con double; por eso el resultado se convierte a float.\n\n"
           "El script usa esta función en la patrulla, en el pisotón y en la "
           "persecución. No usa Vector3.Distance ni Vector3.magnitude: la idea es "
           "ver la fórmula escrita una vez.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """static float Longitud(Vector3 v)
{
    return (float)Math.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}""")

# 9 ---------------------------------------------------------------- normalizar
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · VECTORES", "NORMALIZAR: DIRECCIÓN Y VELOCIDAD",
       "Un vector normalizado mide 1 y conserva la dirección del vector original.")
fig(s, ROOT / "figuras" / "normalizacion.png", 0.62, 1.64, 5.70, 3.38)
code(s, "code_normalizar.png", 6.58, 1.64, 6.00, 2.61)
bullets(s, 6.58, 4.42, 5.95, [
    "Divide cada componente entre la longitud.",
    "El resultado mide 1 y mantiene la dirección.",
    "Si la longitud es casi cero, devuelve (0, 0, 0).",
], size=12.5, gap=0.58)
footer(s, "Sin normalizar, una diagonal de 45° avanza 1.41 veces más rápido que un movimiento recto.")
notes_code(s,
           "Normalizar convierte un vector en una dirección de longitud 1. Se divide "
           "cada componente entre la longitud.\n\n"
           "La comprobación longitud < 0.0001f evita dividir entre cero cuando el "
           "enemigo ya está en el objetivo.\n\n"
           "Sin normalizar, la diagonal (1, 0, 1) avanza raíz(2) = 1.41 unidades "
           "por cada unidad de un movimiento recto. La esfera parecería más rápida "
           "en las diagonales.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """static Vector3 Normalizar(Vector3 v)
{
    float longitud = Longitud(v);
    if (longitud < 0.0001f) { 
        return new Vector3(0f, 0f, 0f);
    }
    return new Vector3(v.x / longitud, v.y / longitud, v.z / longitud);
}""")

# 10 --------------------------------------------------------------- seccion 03
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
text(s, 0.62, 0.98, 2.0, 1.0, "03", 48, BLUE, SEM)
text(s, 0.62, 1.92, 11.20, 1.60, "PATRULLA ENTRE ESQUINAS", 48, INK, SEM, line_spacing=0.92)
rect(s, 0.62, 3.85, 2.20, 0.07, BLUE)
text(s, 0.62, 4.12, 7.20, 0.90,
     "La esfera recorre el plano sin perseguir todavía al jugador.",
     20, INK, REG, line_spacing=1.02)
text(s, 0.62, 5.22, 7.40, 0.30,
     "ESCENA · ARREGLO · ÍNDICE · TEMPORIZADOR", 9.5, BODY, SEM)
picture_fit(s, ROOT / "decor" / "star.png", 9.56, 1.10, 1.10, 1.10, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 11.35, 3.35, 0.95, 0.95, border=False)
picture_fit(s, ROOT / "decor" / "cloud-low.png", 9.55, 4.95, 2.45, 1.40, border=False)
picture_fit(s, ROOT / "decor" / "tree-small.png", 11.75, 4.75, 0.85, 1.55, border=False)
notes(s,
      "Bloque 3. La esfera patrulla entre cuatro esquinas. Todavía no mira al "
      "jugador: elige una esquina, camina hacia ella y cambia de objetivo cada "
      "cinco segundos.\n\n"
      "Aquí aparecen el arreglo de Vector3, el índice objetivo y Time.deltaTime.")

# 11 --------------------------------------------------------------- escena
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · PATRULLA", "PREPARAR LA ESCENA",
       "Un plano de 10 × 10 y una esfera de 1 unidad de diámetro.")
shot(s, ROOT / "img" / "escena-esfera.png", 0.62, 1.64, 6.45, 3.92)
text(s, 0.74, 5.66, 6.25, 0.28, "La esfera aparece en una esquina del plano.", 10, MUTED, REG)
rows = [
    ("Plane", "10 × 10 en (0, 0, 0)"),
    ("Esquinas reales", "de -5 a 5 en X y Z"),
    ("Esfera", "radio 0.5, centro en y = 0.5"),
    ("Esquinas de patrulla", "de -4.5 a 4.5"),
]
for i, (name, value) in enumerate(rows):
    y = 1.70 + i * 0.82
    text(s, 7.30, y, 5.30, 0.26, name.upper(), 9.5, ORANGE_TEXT, SEM)
    text(s, 7.30, y + 0.28, 5.30, 0.36, value, 15, INK, SEM)
card(s, 7.30, 5.02, 5.35, 1.00, ORANGE)
text(s, 7.54, 5.14, 4.90, 0.28, "¿Por qué 4.5 y no 5?", 12.5, INK, SEM)
text(s, 7.54, 5.44, 4.90, 0.48,
     "El centro de la esfera debe quedar dentro del plano. Por eso las esquinas se meten 0.5.",
     11.5, BODY, REG, line_spacing=1.0)
footer(s, "La esfera mide 1 de diámetro: su radio es 0.5. El centro no puede quedar en el borde.")
notes(s,
      "El plano primitivo de Unity mide 10 × 10 y está centrado en (0, 0, 0). Sus "
      "esquinas reales están en (5, 0, 5), (5, 0, -5), (-5, 0, 5) y (-5, 0, -5).\n\n"
      "La esfera primitiva mide 1 de diámetro, así que su radio es 0.5. Para que "
      "su centro no salga del plano, las esquinas de patrulla se colocan en 4.5, "
      "no en 5.\n\n"
      "En la escena, la esfera está en (4.5, 0.5, 4.5). La altura 0.5 es la mitad "
      "de su diámetro: así queda apoyada sobre el plano.")

# 12 --------------------------------------------------------------- crear esfera
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · PATRULLA", "CREAR LA ESFERA Y EL RIGIDBODY",
       "La esfera necesita un collider y un Rigidbody que no caiga.")
shot(s, ROOT / "img" / "crear-esfera.png", 0.62, 1.64, 4.35, 3.28)
text(s, 0.74, 5.02, 4.10, 0.26, "GameObject > 3D Object > Sphere.", 10, MUTED, REG)
text(s, 5.32, 1.74, 7.30, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps = [
    "1. Crea la esfera y renómbrala Enemigo.",
    "2. Ajusta SphereCollider: radio 0.5.",
    "3. Agrega Rigidbody y activa Is Kinematic.",
    "4. Comprueba en Play que la esfera no se cae.",
]
for i, step in enumerate(steps):
    text(s, 5.32, 2.06 + i * 0.44, 7.15, 0.30, step, 12.5, BODY, REG)
shot(s, ROOT / "img" / "is-kinematic.png", 5.32, 3.76, 3.62, 2.38)
notes(s,
      "La esfera se crea con GameObject > 3D Object > Sphere. Se renombra Enemigo "
      "para encontrarla en la jerarquía.\n\n"
      "El SphereCollider tiene radio 0.5, que coincide con la esfera primitiva. "
      "El Rigidbody se marca como Is Kinematic: así la gravedad no la mueve y el "
      "script puede cambiar su posición.\n\n"
      "No se usa OnCollisionEnter para el pisotón. El contacto físico existe, pero "
      "la detección del pisotón es matemática.")

# 13 --------------------------------------------------------------- asignar script
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · PATRULLA", "CREAR Y ASIGNAR EL SCRIPT",
       "Crea el script, agrégalo a la esfera y asigna el cubo desde el Inspector.")
shot(s, ROOT / "img" / "collider-script.png", 0.72, 1.64, 3.45, 4.20)
text(s, 0.84, 5.88, 3.25, 0.24, "Add Component > EnemigoEsfera.", 10, MUTED, REG)
shot(s, ROOT / "img" / "asignar-cubo.png", 4.62, 1.64, 5.90, 3.03)
text(s, 4.74, 4.74, 5.70, 0.26, "El campo Cubo apunta al GameObject Cube.", 10, MUTED, REG)
bullets(s, 4.62, 5.02, 7.95, [
    "Crea el script con Assets > Create > C# Script.",
    "Agrega EnemigoEsfera y asigna el Cube.",
    "Ajusta Velocidad y Distancia Contacto.",
], size=11.5, gap=0.38)
footer(s, "Si el campo Cubo queda vacío, cubo.position lanza NullReferenceException.")
notes(s,
      "Para crear el script: clic derecho en Assets, Create > C# Script, y escribe "
      "EnemigoEsfera. El nombre del archivo y el nombre de la clase deben coincidir.\n\n"
      "Selecciona Enemigo y agrega el componente EnemigoEsfera con Add Component. "
      "Luego arrastra el GameObject Cube desde la jerarquía al campo Cubo.\n\n"
      "Ese campo es un Transform: el script solo necesita leer cubo.position. No "
      "necesita una referencia al script CubeMoveMath.\n\n"
      "En la captura, los valores del Inspector son Velocidad = 5 y Distancia "
      "Contacto = 1.1. En la escena final, Distancia Contacto se ajustó a 1.5.")

# 14 --------------------------------------------------------------- campos
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · PATRULLA", "LOS CAMPOS DEL SCRIPT",
       "El Inspector permite ajustar la mecánica sin tocar el código.")
code(s, "code_campos.png", 0.62, 1.64, 5.95, 3.05)
shot(s, ROOT / "img" / "campos-inspector.png", 0.62, 4.92, 5.95, 1.02)
text(s, 0.74, 5.98, 5.75, 0.22, "Inspector: Velocidad y Distancia Contacto.", 9.5, MUTED, REG)
fields = [
    ("cubo", "Transform del jugador."),
    ("esquinas", "Los cuatro puntos de patrulla."),
    ("indiceObjetivo", "Esquina que se persigue."),
    ("velocidad", "Unidades por segundo."),
    ("distanciaContacto", "Radio horizontal del pisotón."),
    ("anguloPisoton", "Ángulo mínimo, en grados."),
    ("radioDeteccion", "Radio para perseguir al cubo."),
]
for i, (name, desc) in enumerate(fields):
    y = 1.68 + i * 0.59
    text(s, 6.85, y, 2.15, 0.26, name, 12, INK, SEM)
    text(s, 9.00, y - 0.01, 3.80, 0.28, desc, 11.5, BODY, REG)
text(s, 6.85, 5.95, 5.90, 0.24, "Los valores del Inspector mandan sobre los del script.", 10, MUTED, REG)
footer(s, "distanciaContacto vale 1.1 en el script y 1.5 en la escena: el Inspector tiene la última palabra.")
notes_code(s,
           "Los campos públicos aparecen en el Inspector. Los privados no, pero "
           "igual se usan dentro del script.\n\n"
           "cubo es la referencia al jugador. esquinas guarda los cuatro puntos. "
           "indiceObjetivo dice cuál se persigue. velocidad se mide en unidades por "
           "segundo. distanciaContacto y anguloPisoton definen el pisotón. "
           "radioDeteccion define cuándo empieza la persecución.\n\n"
           "El valor del Inspector manda: si el script dice 1.1 y la escena dice "
           "1.5, se usa 1.5.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """public Transform cubo;
private Vector3[] esquinas;  // arreglo de Vector3 para guardar las esquinas
public int indiceObjetivo;
public float velocidad = 5.0f;
public float distanciaContacto = 1.1f;  // distancia para saber si el cubo tocó la esfera
public float anguloPisoton = 60f;
// radio de detección para empezar a perseguir al jugador
public float radioDeteccion = 3.0f;  """)

# 15 --------------------------------------------------------------- start
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · PATRULLA", "GUARDAR LAS CUATRO ESQUINAS",
       "El arreglo guarda los puntos y elige uno al azar al iniciar.")
code(s, "code_start.png", 0.62, 1.64, 6.25, 3.83)
text(s, 7.12, 1.72, 5.55, 0.28, "PASO A PASO", 9.5, ORANGE_TEXT, SEM)
steps = [
    ("1", "Crea un arreglo de cuatro Vector3."),
    ("2", "Guarda las esquinas de -4.5 a 4.5."),
    ("3", "Llama a NewRandom para elegir una esquina."),
    ("4", "Coloca la esfera con transform.position."),
    ("5", "Repite el cambio con InvokeRepeating."),
]
for i, (num, step) in enumerate(steps):
    y = 2.06 + i * 0.58
    pill(s, 7.12, y, 0.34, num, WHITE, ORANGE)
    text(s, 7.58, y + 0.02, 5.05, 0.28, step, 12, BODY, REG)
card(s, 7.12, 5.12, 5.35, 0.90, ORANGE)
text(s, 7.36, 5.24, 4.90, 0.26, "La posición del Inspector se sobrescribe.", 11.5, INK, SEM)
text(s, 7.36, 5.52, 4.90, 0.26, "Start siempre coloca la esfera en una esquina.", 10.5, BODY, REG)
footer(s, "El índice 0 es la primera esquina; el índice 3 es la última. El arreglo tiene cuatro posiciones.")
notes_code(s,
           "Start se ejecuta una vez, antes del primer Update. Crea el arreglo de "
           "cuatro Vector3, guarda las esquinas y elige una al azar.\n\n"
           "La posición inicial del Inspector se sobrescribe con transform.position. "
           "Después, InvokeRepeating cambia el índice cada cinco segundos.\n\n"
           "Las esquinas están en y = 0.5 para que el centro de la esfera quede a "
           "la altura del plano.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """void Start()
{
    esquinas = new Vector3[4];
    esquinas[0] = new Vector3(-4.5f, 0.5f, -4.5f);
    esquinas[1] = new Vector3( 4.5f, 0.5f, -4.5f);
    esquinas[2] = new Vector3( 4.5f, 0.5f,  4.5f);
    esquinas[3] = new Vector3(-4.5f, 0.5f,  4.5f);

    // configuración de la primera esquina
    NewRandom();
    transform.position = esquinas[indiceObjetivo];

    InvokeRepeating("NewRandom", 0f, 5f);  // cambiar de esquina cada 5 segundos
}""")

# 16 --------------------------------------------------------------- newrandom
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · PATRULLA", "ELEGIR ESQUINA Y REPETIR",
       "NewRandom elige un índice y InvokeRepeating repite la elección cada cinco segundos.")
code(s, "code_newrandom.png", 0.62, 1.64, 6.25, 1.40)
code(s, "code_invoke.png", 0.62, 3.18, 6.25, 0.80)
bullets(s, 7.15, 1.72, 5.50, [
    "Random.Range(0, 4) devuelve 0, 1, 2 o 3.",
    "El límite superior no se incluye.",
    "UnityEngine.Random evita la ambigüedad con System.Random.",
    "El nombre del método va como texto.",
    "Puede repetir la misma esquina.",
], size=12, gap=0.64)
card(s, 0.62, 4.18, 6.25, 1.05, PINK)
text(s, 0.86, 4.30, 5.80, 0.26, "El primer disparo ocurre casi de inmediato.", 11.5, INK, SEM)
text(s, 0.86, 4.60, 5.80, 0.48,
     "NewRandom ya se llamó antes; el objetivo puede cambiar otra vez al inicio.",
     10.5, BODY, REG, line_spacing=1.0)
footer(s, "InvokeRepeating no necesita un contador: Unity llama al método por su nombre cada cinco segundos.")
notes_code(s,
           "NewRandom elige un índice entre 0 y 3. Random.Range con enteros no "
           "incluye el límite superior, así que 4 nunca sale.\n\n"
           "Se escribe UnityEngine.Random porque using System; también trae "
           "System.Random y el compilador se confunde.\n\n"
           "InvokeRepeating recibe el nombre del método como string, el retardo "
           "inicial y el intervalo. Si renombras NewRandom, actualiza el string.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """void NewRandom()
{
    indiceObjetivo = UnityEngine.Random.Range(0, 4); 
}""",
           "Invocación en Start:\nInvokeRepeating(\"NewRandom\", 0f, 5f);")

# 17 --------------------------------------------------------------- mover objetivo
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · PATRULLA", "CALCULAR EL VECTOR Y LA DISTANCIA",
       "Primero se obtiene el vector que falta y se mide su longitud.")
code(s, "code_mover_objetivo.png", 0.62, 1.64, 6.35, 3.63)
text(s, 7.22, 1.72, 5.50, 0.50, "hacia = objetivo - posición", 19, INK, SEM)
bullets(s, 7.22, 2.38, 5.45, [
    "Longitud(hacia) mide el vector.",
    "Si la distancia es menor a 0.1, ya llegó.",
    "Elige otra esquina con un salto de 1, 2 o 3.",
    "El operador % 4 da la vuelta al arreglo.",
], size=12, gap=0.66)
card(s, 7.22, 5.06, 5.50, 0.92, ORANGE)
text(s, 7.46, 5.18, 5.05, 0.26, "El return evita mover la esfera en ese fotograma.", 11.5, INK, SEM)
text(s, 7.46, 5.47, 5.05, 0.26, "Después de elegir, el método termina.", 10.5, BODY, REG)
footer(s, "El desplazamiento nunca es 0: la esquina nueva siempre es distinta de la actual.")
notes_code(s,
           "Este es el primer paso de MoverEsfera. Se toma la esquina objetivo y se "
           "resta la posición actual.\n\n"
           "Si la distancia es menor a 0.1, la esfera ya llegó. Entonces se elige "
           "otra esquina con un desplazamiento de 1, 2 o 3. El operador % 4 hace "
           "que el índice dé la vuelta: 3 + 1 = 0, por ejemplo. El return impide "
           "mover la esfera en ese fotograma.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """void MoverEsfera()
{
    Vector3 objetivo = esquinas[indiceObjetivo];
    Vector3 hacia = objetivo - transform.position;
    float distancia = Longitud(hacia);

    if (distancia < 0.1f)
    {
        // Elige otra esquina distinta: suma 1, 2 o 3 y da la vuelta
        indiceObjetivo = (indiceObjetivo + UnityEngine.Random.Range(1, 4)) % 4;
        return;
    }""")

# 18 --------------------------------------------------------------- mover paso
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · PATRULLA", "AVANZAR UN PASO HACIA EL OBJETIVO",
       "La dirección se normaliza y se multiplica por la velocidad y por el tiempo.")
code(s, "code_mover_paso.png", 0.62, 1.64, 6.35, 2.80)
card(s, 0.62, 4.62, 6.35, 1.05, BLUE)
text(s, 0.86, 4.74, 5.95, 0.26,
     "Time.deltaTime: misma velocidad, distinto hardware.", 11.5, INK, SEM)
text(s, 0.86, 5.05, 5.95, 0.45,
     "60 FPS: 0.083 por fotograma · 30 FPS: 0.167 · 144 FPS: 0.035",
     10.5, BODY, REG)
text(s, 7.22, 1.72, 5.55, 0.50, "paso = velocidad × Time.deltaTime", 19, INK, SEM)
bullets(s, 7.22, 2.40, 5.45, [
    "Normalizar deja la dirección en longitud 1.",
    "El paso depende del tiempo, no de los FPS.",
    "La posición nueva suma dirección × paso.",
    "La y se conserva: la esfera no se eleva.",
], size=12, gap=0.64)
text(s, 7.22, 5.12, 5.45, 0.62,
     "La esfera se traslada sin rodar. El giro visual no está implementado.",
     11.5, BODY, REG, line_spacing=1.02)
footer(s, "La velocidad es 5 unidades por segundo. El paso convierte esa velocidad en distancia por fotograma.")
notes_code(s,
           "Normalizar(hacia) convierte el vector en dirección unitaria. Sin eso, "
           "la diagonal avanzaría más rápido.\n\n"
           "El paso es velocidad * Time.deltaTime. La posición nueva se construye "
           "componente por componente y conserva la y.\n\n"
           "El script no usa transform.Rotate: la esfera se traslada, no rueda.\n\n"
           "Time.deltaTime es el tiempo del último fotograma. A 60 FPS vale 0.0167 s; "
           "a 30 FPS, 0.0333. Sin deltaTime, la velocidad cambia con los FPS. En un "
           "segundo, la esfera recorre 5 unidades.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """    Vector3 direccion = Normalizar(hacia);
    float paso = velocidad * Time.deltaTime;

    transform.position = new Vector3(
        transform.position.x + direccion.x * paso,
        transform.position.y,                       // la altura no cambia
        transform.position.z + direccion.z * paso
    );
}""")

# 20 --------------------------------------------------------------- seccion 04
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
text(s, 0.62, 0.98, 2.0, 1.0, "04", 48, GREEN, SEM)
text(s, 0.62, 1.92, 11.40, 1.60, "PISOTÓN Y PERSECUCIÓN", 48, INK, SEM, line_spacing=0.92)
rect(s, 0.62, 3.85, 2.20, 0.07, GREEN)
text(s, 0.62, 4.12, 7.20, 0.90,
     "Detectar una caída sobre la esfera y decidir cuándo perseguir.",
     20, INK, REG, line_spacing=1.02)
text(s, 0.62, 5.22, 8.00, 0.30,
     "ATAN2 · ÁNGULO · RADIO · RESET · RADIO DE DETECCIÓN", 9.5, BODY, SEM)
picture_fit(s, ROOT / "decor" / "star.png", 9.56, 1.10, 1.10, 1.10, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 11.35, 3.35, 0.95, 0.95, border=False)
picture_fit(s, ROOT / "decor" / "cloud-low.png", 9.55, 4.95, 2.45, 1.40, border=False)
picture_fit(s, ROOT / "decor" / "tree-small.png", 11.75, 4.75, 0.85, 1.55, border=False)
notes(s,
      "Bloque 4. La esfera ya patrulla. Ahora debe reaccionar cuando el cubo cae "
      "encima y cuando el jugador se acerca.\n\n"
      "El pisotón se detecta con dos condiciones: un ángulo mínimo y un radio "
      "horizontal. La persecución se detecta con una distancia y cambia el objetivo.")

# 21 --------------------------------------------------------------- cubo salta
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · PISOTÓN", "EL CUBO YA SABE SALTAR",
       "La base viene de T8.5.2: el salto no se modifica para este ejercicio.")
code(s, "code_jump.png", 0.62, 1.64, 5.55, 2.36)
text(s, 0.74, 4.12, 5.30, 0.26, "SALTO CON LA BARRA ESPACIADORA", 9.5, ORANGE_TEXT, SEM)
code(s, "code_suelo.png", 6.55, 1.64, 5.55, 2.44)
text(s, 6.67, 4.20, 5.30, 0.26, "DETECCIÓN DEL SUELO", 9.5, ORANGE_TEXT, SEM)
card(s, 0.62, 4.72, 12.05, 1.02, GREEN)
text(s, 0.86, 4.84, 11.50, 0.28, "jumpForce = 5.0 y estaEnSuelo = true al inicio.",
     14, INK, SEM)
text(s, 0.86, 5.18, 11.50, 0.28,
     "El impulso solo se aplica cuando el cubo toca el plano y la barra espaciadora se presiona en ese fotograma.",
     11, BODY, REG)
footer(s, "El pisotón usa la altura que produce este salto. El enemigo solo lee cubo.position.")
notes_code(s,
           "El cubo viene de T8.5.2. Su Rigidbody no es kinematic: la gravedad y el "
           "impulso funcionan. El salto se aplica con AddForce y ForceMode.Impulse "
           "cuando se presiona Space y estaEnSuelo es true.\n\n"
           "OnCollisionEnter marca estaEnSuelo cuando el cubo choca con el objeto "
           "llamado Plane. Si el cubo queda sobre la esfera, no recupera el salto "
           "hasta tocar el piso.\n\n"
           "El enemigo no modifica este script: solo lee la posición del cubo.",
           "Assets/Scripts/escena3_math/CubeMoveMath.cs",
           """if (keyboard.spaceKey.wasPressedThisFrame && estaEnSuelo == true)
{
    rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
    estaEnSuelo = false;
}

private void OnCollisionEnter(Collision collision)
{
    if (collision.gameObject.name == "Plane")  // Si el cubo está chocando con el suelo 
    {
        estaEnSuelo = true;
    }
}""")

# 22 --------------------------------------------------------------- contacto
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · PISOTÓN", "PRIMERA IDEA: MEDIR SOLO LA DISTANCIA",
       "La función Contacto detecta cualquier acercamiento entre los centros.")
code(s, "code_contacto.png", 0.62, 1.64, 6.05, 2.73)
text(s, 0.74, 4.52, 5.80, 0.26, "Versión descartada; en el archivo final está comentada.", 9.5, MUTED, REG)
card(s, 7.05, 1.68, 5.60, 1.40, GREEN)
text(s, 7.29, 1.80, 5.10, 0.26, "Qué funciona", 12.5, INK, SEM)
text(s, 7.29, 2.10, 5.10, 0.72,
     "Detecta que el cubo está cerca, sin importar la dirección.",
     11.5, BODY, REG, line_spacing=1.0)
card(s, 7.05, 3.24, 5.60, 1.78, PINK)
text(s, 7.29, 3.36, 5.10, 0.26, "Qué falla", 12.5, INK, SEM)
text(s, 7.29, 3.66, 5.10, 1.20,
     "No distingue si el cubo está arriba, al lado o abajo. Un golpe lateral también entra en el umbral.",
     11.5, BODY, REG, line_spacing=1.03)
card(s, 0.62, 4.90, 6.05, 0.82, ORANGE)
text(s, 0.86, 5.03, 5.60, 0.26, "Se conserva como paso didáctico.", 11.5, INK, SEM)
text(s, 0.86, 5.32, 5.60, 0.26, "Después se reemplaza por Pisoton.", 10.5, BODY, REG)
footer(s, "Contacto solo mide distancias. El pisotón necesita además saber desde qué dirección llega el cubo.")
notes_code(s,
           "La primera versión medía la distancia 3D entre los centros. Si era menor "
           "o igual a distanciaContacto, devolvía true.\n\n"
           "El problema es que no distingue arriba de abajo. Un golpe lateral, un "
           "cubo que pasa al lado o un cubo debajo también entran en el umbral.\n\n"
           "Por eso la función quedó comentada y se reemplazó por Pisoton, que "
           "agrega el ángulo de elevación.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """// bool Contacto()
// {
//     Vector3 haciaCubo = cubo.position - transform.position;
//     float distanciaCubo = Longitud(haciaCubo);
//
//     if (distanciaCubo <= distanciaContacto)
//     {
//         return true;
//     }
//     return false;
// }""")

# 23 --------------------------------------------------------------- dos condiciones
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · PISOTÓN", "PISOTÓN: DOS CONDICIONES A LA VEZ",
       "El cubo debe estar arriba y cerca en el plano horizontal.")
card(s, 0.62, 1.68, 4.55, 1.18, ORANGE)
text(s, 0.86, 1.80, 4.10, 0.24, "ÁNGULO", 9.5, ORANGE_TEXT, SEM)
text(s, 0.86, 2.10, 4.10, 0.42, "60° o más", 24, INK, SEM)
text(s, 0.86, 2.50, 4.10, 0.24, "medido desde la horizontal", 10.5, BODY, REG)
card(s, 0.62, 3.04, 4.55, 1.18, PINK)
text(s, 0.86, 3.16, 4.10, 0.24, "DISTANCIA HORIZONTAL", 9.5, PINK, SEM)
text(s, 0.86, 3.46, 4.10, 0.42, "1.5 o menos", 24, INK, SEM)
text(s, 0.86, 3.86, 4.10, 0.24, "valor usado en la escena", 10.5, BODY, REG)
card(s, 0.62, 4.42, 4.55, 0.90, GREEN)
text(s, 0.86, 4.54, 4.10, 0.26, "Las dos se cumplen", 13, INK, SEM)
text(s, 0.86, 4.84, 4.10, 0.26, "Si falta una, no hay pisotón.", 10.5, BODY, REG)
fig(s, ROOT / "figuras" / "angulo-pisoton.png", 5.42, 1.64, 7.28, 3.64)
text(s, 5.54, 5.34, 7.05, 0.55,
     "Figura 2. El ángulo sale de atan2(dy, horizontal). La zona verde cumple las dos condiciones.",
     10, MUTED, REG, line_spacing=1.0)
footer(s, "No es una esfera de contacto: es un cono de 60° recortado por un cilindro de radio 1.5.")
notes(s,
      "El pisotón exige dos condiciones al mismo tiempo.\n\n"
      "1. El ángulo de elevación debe ser de 60° o más. Se mide desde la horizontal, "
      "así que el cubo debe estar dentro de los 30° alrededor de la vertical.\n\n"
      "2. La distancia horizontal debe ser de 1.5 o menos. Es el valor ajustado en "
      "la escena; el script trae 1.1 por defecto.\n\n"
      "La zona válida es un cono recortado por un cilindro. No es una esfera: un "
      "cubo lejano y alto puede cumplir el ángulo pero fallar el radio.")

# 24 --------------------------------------------------------------- atan2
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · PISOTÓN", "CALCULAR EL ÁNGULO CON ATAN2",
       "atan2 recibe la altura y la distancia horizontal, en ese orden.")
code(s, "code_pisoton.png", 0.62, 1.64, 5.35, 4.18)
text(s, 6.25, 1.72, 6.45, 0.80,
     "ángulo = atan2(dy, horizontal) × 180 / PI", 18, INK, SEM, line_spacing=1.0)
bullets(s, 6.25, 2.66, 6.35, [
    "Primero dy; luego horizontal.",
    "Devuelve radianes; se convierte a grados.",
    "Si horizontal = 0 y dy no es 0, devuelve 90° o -90°.",
    "La condición exige ángulo y radio.",
], size=12, gap=0.64)
card(s, 6.25, 5.06, 6.35, 0.85, ORANGE)
text(s, 6.49, 5.18, 5.90, 0.26, "60° desde la horizontal = 30° desde la vertical.", 11.5, INK, SEM)
text(s, 6.49, 5.47, 5.90, 0.26, "El orden de los argumentos cambia el ángulo.", 10.5, BODY, REG)
footer(s, "Si intercambias dy y horizontal, obtienes el ángulo complementario: 90° menos el correcto.")
notes_code(s,
           "Pisoton resta la posición de la esfera a la del cubo. dx, dy y dz son "
           "las componentes del vector.\n\n"
           "horizontal = raíz(dx*dx + dz*dz) elimina la altura. El ángulo sale de "
           "Math.Atan2(dy, horizontal), que recibe primero la altura y luego la "
           "distancia horizontal. Devuelve radianes; se multiplica por 180 / PI para "
           "convertirlo a grados.\n\n"
           "La condición usa &&: se deben cumplir el ángulo y el radio. Si se cumple, "
           "escribe PISOTON, llama a Reset y devuelve true.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """bool Pisoton()
{
    Vector3 haciaCubo = cubo.position - transform.position;
    float dx = haciaCubo.x;
    float dy = haciaCubo.y;
    float dz = haciaCubo.z;

    float horizontal = (float) Math.Sqrt(dx*dx + dz*dz);  // distancia horizontal
    float angulo = (float)(Math.Atan2(dy, horizontal) * 180.0 / Math.PI); // ángulo vertical

    if (angulo >= anguloPisoton && horizontal <= distanciaContacto){
        Debug.Log("PISOTON");
        Reset();
        return true;
    }
    return false;

}""")

# 25 --------------------------------------------------------------- ejemplos
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · PISOTÓN", "¿CUÁNDO HAY PISOTÓN?",
       "La tabla aplica las dos condiciones con ángulo 60 y distancia 1.5.")
table(s, 0.62, 1.66, 7.70, 4.10, [
    ["Caso", "horizontal", "dy", "ángulo", "¿Pisotón?"],
    ["Justo encima", "0", "1.0", "90°", "Sí"],
    ["Arriba y cerca", "0.5", "1.0", "63.4°", "Sí"],
    ["Arriba y lejos", "1.0", "1.0", "45°", "No: falta ángulo"],
    ["Al lado", "1.0", "0", "0°", "No"],
    ["Abajo", "0", "-1.0", "-90°", "No"],
    ["Borde del radio", "1.5", "2.6", "60°", "Sí, en el límite"],
], [2.15, 1.15, 0.85, 1.00, 2.55], font_size=12, header_size=11.5,
   row_h=[0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.60])
card(s, 8.55, 1.66, 4.10, 3.10, BLUE)
text(s, 8.79, 1.80, 3.65, 0.26, "OBSERVA EL TERCER CASO", 9.5, BLUE, SEM)
text(s, 8.79, 2.14, 3.65, 1.40,
     "horizontal = 1.0 sí está dentro del radio, pero el ángulo de 45° no alcanza el umbral.",
     13, INK, REG, line_spacing=1.04)
text(s, 8.79, 3.55, 3.65, 0.90,
     "No basta con la distancia: el cubo también debe estar suficientemente alto.",
     12, BODY, SEM, line_spacing=1.02)
text(s, 8.79, 4.35, 3.65, 0.28, "La condición se evalúa en cada fotograma.", 10, MUTED, REG)
text(s, 0.62, 5.92, 12.05, 0.28,
     "La tabla evalúa la condición matemática del código, no el contacto físico entre colliders.",
     10.5, MUTED, REG)
footer(s, "Un cubo lejano y alto puede cumplir el ángulo pero fallar el radio. Las dos condiciones son necesarias.")
notes(s,
      "La tabla usa anguloPisoton = 60 y distanciaContacto = 1.5.\n\n"
      "Justo encima: horizontal 0, dy 1.0, ángulo 90°, pisotón.\n"
      "Arriba y cerca: horizontal 0.5, dy 1.0, ángulo 63.4°, pisotón.\n"
      "Arriba y lejos: horizontal 1.0, dy 1.0, ángulo 45°, no alcanza el ángulo.\n"
      "Al lado: horizontal 1.0, dy 0, ángulo 0°, no.\n"
      "Abajo: horizontal 0, dy -1.0, ángulo -90°, no.\n"
      "Borde del radio: horizontal 1.5, dy 2.6, ángulo 60°, pisotón en el límite.\n\n"
      "El tercer caso es el más importante: estar dentro del radio no basta.")

# 26 --------------------------------------------------------------- calibrar
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · PISOTÓN", "CALIBRAR EL UMBRAL DEL PISOTÓN",
       "Cuanto más lejos del centro, más alto debe estar el cubo.")
card(s, 0.62, 1.68, 5.55, 1.12, ORANGE)
text(s, 0.86, 1.80, 5.10, 0.24, "ALTURA MÍNIMA", 9.5, ORANGE_TEXT, SEM)
text(s, 0.86, 2.10, 5.10, 0.38, "dy mínimo = horizontal × tan(60°)", 20, INK, SEM)
table(s, 0.62, 3.02, 5.55, 2.05, [
    ["horizontal", "dy mínimo", "centro del cubo en y"],
    ["0.5", "0.87", "1.37"],
    ["1.0", "1.73", "2.23"],
    ["1.5", "2.60", "3.10"],
], [1.55, 1.55, 2.45], font_size=12, header_size=10.5, row_h=0.44)
text(s, 6.72, 1.72, 5.90, 0.28, "QUÉ SIGNIFICA", 9.5, ORANGE_TEXT, SEM)
bullets(s, 6.72, 2.08, 5.95, [
    "Cuanto más lejos, más alto debe estar el cubo.",
    "El salto real limita la altura alcanzable.",
    "distanciaContacto = 1.5 es un margen didáctico.",
    "El contacto físico ocurre a 1.0 entre centros.",
], size=12, gap=0.78)
card(s, 6.72, 5.10, 5.95, 0.88, GREEN)
text(s, 6.96, 5.22, 5.50, 0.26, "Calibra en el Inspector con el salto real.", 11.5, INK, SEM)
text(s, 6.96, 5.50, 5.50, 0.26, "El valor 1.5 no significa que todo el cilindro sea alcanzable.", 10, BODY, REG)
footer(s, "La esfera está en y = 0.5. La columna 'centro del cubo en y' suma ese 0.5 al dy mínimo.")
notes(s,
      "Para que el ángulo llegue a 60°, la altura mínima crece con la distancia "
      "horizontal: dy mínimo = horizontal * tan(60°).\n\n"
      "A 0.5 de distancia horizontal, el cubo necesita 0.87 de altura sobre la "
      "esfera; su centro queda en y = 1.37. A 1.5, necesita 2.60; su centro queda "
      "en y = 3.10.\n\n"
      "Con un salto normal, el radio efectivo es menor que 1.5. Calibra "
      "distanciaContacto y anguloPisoton en el Inspector con el salto real del cubo.")

# 27 --------------------------------------------------------------- reset
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · PISOTÓN", "DESPUÉS DEL PISOTÓN: RESET",
       "La esfera no desaparece: elige otra esquina y se teletransporta.")
code(s, "code_reset.png", 0.62, 1.72, 5.55, 1.43)
text(s, 0.74, 3.30, 5.30, 0.26, "La esfera vuelve a una esquina aleatoria.", 10, MUTED, REG)
bullets(s, 6.55, 1.72, 6.10, [
    "NewRandom elige otra esquina.",
    "transform.position teletransporta la esfera.",
    "Puede repetir la misma esquina.",
    "Si se repite, el log puede salir en cada fotograma.",
    "Reset también es un mensaje del Editor de Unity.",
], size=12, gap=0.70)
card(s, 0.62, 3.55, 5.55, 1.05, BLUE)
text(s, 0.86, 3.67, 5.10, 0.26, "La única señal es el log PISOTON.", 12, INK, SEM)
text(s, 0.86, 3.98, 5.10, 0.48, "Aparece en la Console de Unity cada vez que se cumple la condición.", 10.5, BODY, REG)
card(s, 6.55, 5.12, 6.10, 0.92, PINK)
text(s, 6.79, 5.24, 5.65, 0.26, "Si aparece un error al agregar el componente,", 11.5, INK, SEM)
text(s, 6.79, 5.53, 5.65, 0.26, "renombra el método a Reubicar.", 11.5, INK, SEM)
footer(s, "No hay pantalla de victoria ni derrota: solo el log PISOTON y el teletransporte de la esfera.")
notes_code(s,
           "Reset elige una esquina nueva y coloca la esfera ahí. No termina el "
           "juego ni oculta la esfera.\n\n"
           "NewRandom puede devolver la misma esquina. En ese caso la esfera no se "
           "mueve y, si el cubo sigue cumpliendo las condiciones, el log PISOTON "
           "puede repetirse en cada fotograma. No hay una bandera resuelto que lo "
           "impida.\n\n"
           "Reset también es el nombre de un mensaje del Editor de Unity. Si Unity "
           "lo llama antes de Start, esquinas todavía es null. Si aparece ese error, "
           "renombra el método a Reubicar.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """void Reset()
{
    NewRandom();
    transform.position = esquinas[indiceObjetivo];
}""")

# 28 --------------------------------------------------------------- detectar
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · PERSECUCIÓN", "DETECTAR AL JUGADOR",
       "La esfera compara la distancia al cubo con radioDeteccion.")
code(s, "code_persigue_detecta.png", 0.62, 1.64, 5.55, 1.70)
bullets(s, 0.62, 3.60, 5.65, [
    "radioDeteccion = 3.0 en el Inspector.",
    "La distancia se mide en 3D.",
    "Si el cubo salta, la altura cuenta.",
], size=12, gap=0.64)
card(s, 0.62, 5.20, 5.65, 0.80, ORANGE)
text(s, 0.86, 5.32, 5.20, 0.26, "El radio horizontal efectivo se reduce", 11.5, INK, SEM)
text(s, 0.86, 5.61, 5.20, 0.26, "cuando el cubo está alto.", 11.5, INK, SEM)
fig(s, ROOT / "figuras" / "persecucion.png", 6.45, 1.64, 6.25, 3.30)
text(s, 6.57, 5.12, 6.00, 0.55,
     "Figura 3. Fuera del radio, la esfera va a la esquina. Dentro, va al cubo.",
     10, MUTED, REG, line_spacing=1.0)
footer(s, "La comparación devuelve verdadero o falso y se guarda en una variable bool.")
notes_code(s,
           "La persecución empieza con una comparación. Se mide la distancia entre "
           "el cubo y la esfera con Longitud y se compara con radioDeteccion.\n\n"
           "La distancia es 3D: incluye la altura. Si el cubo está en el piso, su "
           "centro está en y = 0.5, igual que la esfera. Si salta, dy crece y la "
           "distancia también. Por eso el radio horizontal efectivo se reduce "
           "cuando el cubo está alto.\n\n"
           "El resultado se guarda en la variable bool persiguiendo.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """void MoverEsfera()
{
    // si la longitud de la esfera al cubo es menor a radioDeteccion, persiguiendo es true
    bool persiguiendo = Longitud(cubo.position - transform.position) <= radioDeteccion;""")

# 29 --------------------------------------------------------------- elegir objetivo
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · PERSECUCIÓN", "CAMBIAR EL OBJETIVO",
       "La misma variable objetivo apunta al cubo o a la esquina.")
code(s, "code_persigue_objetivo.png", 0.62, 1.64, 6.25, 3.57)
bullets(s, 7.18, 1.72, 5.50, [
    "persiguiendo == true: objetivo = cubo.position.",
    "persiguiendo == false: objetivo = esquinas[indiceObjetivo].",
    "La llegada solo elige otra esquina cuando no persigue.",
    "El temporizador sigue cambiando el índice.",
], size=12, gap=0.70)
card(s, 7.18, 5.08, 5.45, 0.92, GREEN)
text(s, 7.42, 5.20, 5.00, 0.26, "Perseguir es cambiar el objetivo,", 11.5, INK, SEM)
text(s, 7.42, 5.49, 5.00, 0.26, "no escribir otro algoritmo.", 11.5, INK, SEM)
footer(s, "Cuando el cubo sale del radio, el objetivo vuelve a la esquina que marque el temporizador.")
notes_code(s,
           "Si persiguiendo es true, el objetivo es la posición del cubo. Si es false, "
           "el objetivo es la esquina actual.\n\n"
           "A partir de ahí, el código sigue igual: se resta el objetivo, se mide la "
           "distancia, se normaliza y se suma el paso. La persecución reutiliza el "
           "mismo movimiento de la patrulla.\n\n"
           "La condición de llegada incluye !persiguiendo: la esfera solo elige otra "
           "esquina cuando no está persiguiendo.\n\n"
           "El temporizador sigue activo: aunque la esfera persiga, indiceObjetivo "
           "puede cambiar cada cinco segundos. Cuando termine la persecución, irá a "
           "la esquina que esté marcada en ese momento.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """    Vector3 objetivo;
    if (persiguiendo)
    {
        objetivo = cubo.position;
    }
    else
    {
        objetivo = esquinas[indiceObjetivo];
    }
    
    Vector3 hacia = objetivo - transform.position;
    float distancia = Longitud(hacia);""")

# 30 --------------------------------------------------------------- mover igual
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · PERSECUCIÓN", "EL MOVIMIENTO ES EL MISMO",
       "La esfera resta, mide, normaliza y suma con el nuevo objetivo.")
code(s, "code_mover_paso.png", 0.62, 1.64, 6.20, 2.73)
text(s, 7.12, 1.72, 5.55, 0.50, "paso = velocidad × Time.deltaTime", 19, INK, SEM)
bullets(s, 7.12, 2.40, 5.50, [
    "La dirección se calcula con el nuevo objetivo.",
    "La altura no cambia.",
    "Cuando persigue, no elige otra esquina.",
    "El movimiento es directo, sin rodeos.",
], size=12, gap=0.64)
card(s, 7.12, 5.10, 5.55, 0.82, ORANGE)
text(s, 7.36, 5.22, 5.10, 0.26, "El bloque es idéntico al de la patrulla.", 11.5, INK, SEM)
text(s, 7.36, 5.51, 5.10, 0.26, "Solo cambia el valor de objetivo.", 10.5, BODY, REG)
footer(s, "La persecución reutiliza las cuatro operaciones: restar, medir, normalizar y sumar.")
notes_code(s,
           "Este bloque es el mismo que se usa en la patrulla. La diferencia está "
           "en el objetivo: cuando persigue, apunta al cubo; cuando no, apunta a la "
           "esquina.\n\n"
           "La condición de llegada tiene && !persiguiendo. Eso significa que la "
           "esfera solo cambia de esquina cuando no está persiguiendo. Si persigue, "
           "sigue avanzando hacia el cubo.\n\n"
           "La altura se conserva: la esfera no sube aunque el cubo esté en el aire.",
           "Assets/Scripts/escena3_math/EnemigoEsfera.cs",
           """    Vector3 direccion = Normalizar(hacia);
    float paso = velocidad * Time.deltaTime;

    transform.position = new Vector3(
        transform.position.x + direccion.x * paso,
        transform.position.y,                       // la altura no cambia
        transform.position.z + direccion.z * paso
    );""")

# 31 --------------------------------------------------------------- limites
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · PERSECUCIÓN", "QUÉ HACE Y QUÉ NO HACE",
       "Es una persecución directa, sin búsqueda de caminos.")
card(s, 0.62, 1.68, 5.85, 3.20, GREEN)
text(s, 0.86, 1.82, 5.35, 0.28, "SÍ HACE", 9.5, GREEN, SEM)
bullets(s, 0.86, 2.18, 5.35, [
    "Cambia el objetivo al cubo.",
    "Mantiene la altura de la esfera.",
    "Vuelve a la esquina cuando el cubo sale del radio.",
    "Usa la misma matemática de la patrulla.",
], size=12, gap=0.70)
card(s, 6.70, 1.68, 5.85, 3.20, PINK)
text(s, 6.94, 1.82, 5.35, 0.28, "NO HACE", 9.5, PINK, SEM)
bullets(s, 6.94, 2.18, 5.35, [
    "No evita obstáculos.",
    "No rodea paredes.",
    "No acelera ni gira visualmente.",
    "No limita la persecución al plano.",
], size=12, gap=0.70)
card(s, 0.62, 5.18, 11.93, 0.82, BLUE)
text(s, 0.86, 5.30, 11.40, 0.26,
     "Si el cubo se aleja, el objetivo vuelve a la esquina que el temporizador haya elegido.",
     11.5, INK, SEM)
text(s, 0.86, 5.58, 11.40, 0.26,
     "Para un juego con obstáculos haría falta un algoritmo de búsqueda de caminos.",
     10.5, BODY, REG)
footer(s, "La persecución es una línea recta hacia el cubo. La escena no tiene obstáculos, así que funciona.")
notes(s,
      "La persecución directa funciona porque la escena es un plano abierto. La "
      "esfera va en línea recta hacia el cubo.\n\n"
      "No hay pathfinding, no hay detección de obstáculos y no hay límites del "
      "plano. Si el cubo camina fuera del plano, la esfera también puede salir "
      "persiguiéndolo.\n\n"
      "Tampoco hay giro visual: la esfera se traslada sin rodar. Si se quisiera un "
      "juego con paredes, haría falta un algoritmo de búsqueda de caminos, como A* "
      "o una malla de navegación.")

# 32 --------------------------------------------------------------- pruebas
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · PRUEBAS", "PROBAR LA MECÁNICA",
       "Primero las matemáticas aisladas; después, la mecánica completa.")
table(s, 0.62, 1.64, 8.05, 4.35, [
    ["Prueba", "Cómo", "Resultado esperado"],
    ["Matemáticas", "Mide el vector (3, 0, 4)", "5"],
    ["Normalización", "Normaliza y vuelve a medir", "1"],
    ["Patrulla", "Comenta Pisoton()", "Va de esquina a esquina"],
    ["Contacto lateral", "Camina contra la esfera", "No aparece PISOTON"],
    ["Pisotón", "Salta y cae encima", "PISOTON y teletransporte"],
    ["Borde", "Salta cerca del borde", "No hay pisotón"],
    ["Calibración", "Ajusta el Inspector", "Más fácil o más estricto"],
], [1.90, 3.20, 2.95], font_size=11.5, header_size=11, row_h=0.48)
shot(s, ROOT / "img" / "consola-ok.png", 8.95, 1.64, 3.70, 4.40)
footer(s, "No hay pantalla de victoria ni derrota: la señal del pisotón es el log y el teletransporte.")
notes(s,
      "Orden de pruebas:\n\n"
      "1. Matemáticas: dentro del script, Debug.Log(Longitud(new Vector3(3, 0, 4))) "
      "debe escribir 5.\n"
      "2. Normalización: Longitud(Normalizar(new Vector3(3, 0, 4))) debe escribir 1.\n"
      "3. Patrulla: comenta Pisoton() en Update. La esfera debe ir de esquina a "
      "esquina y cambiar de objetivo cada 5 segundos.\n"
      "4. Contacto lateral: camina contra la esfera a nivel del piso. No debe "
      "aparecer PISOTON.\n"
      "5. Pisotón: salta y cae encima. Debe aparecer PISOTON y la esfera se "
      "reubica.\n"
      "6. Borde: salta cerca del borde. El ángulo no alcanza 60°.\n"
      "7. Calibración: ajusta distanciaContacto y anguloPisoton en el Inspector.")

# 33 --------------------------------------------------------------- errores
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · CIERRE", "ERRORES COMUNES",
       "Seis detalles que rompen la mecánica.")
errors = [
    ("Random ambiguo", "Usa UnityEngine.Random.Range.",
     "El compilador no sabe cuál de los dos Random usar.", ORANGE),
    ("atan2 en radianes", "Multiplica por 180 / PI.",
     "El ángulo se vería 57 veces más pequeño.", PINK),
    ("Orden de atan2", "Primero dy, luego horizontal.",
     "Al revés obtienes 90° menos el ángulo correcto.", BLUE),
    ("Sin Time.deltaTime", "La velocidad depende de los FPS.",
     "La esfera se movería distinto en cada computadora.", GREEN),
    ("Rigidbody no kinematic", "La esfera se cae por la gravedad.",
     "Activa Is Kinematic en el Rigidbody.", ORANGE),
    ("Cubo sin asignar", "cubo.position lanza NullReferenceException.",
     "Arrastra el Cube al campo Cubo del Inspector.", PINK),
]
for i, (title, desc, detail, color) in enumerate(errors):
    x = 0.62 + (i % 3) * 4.05
    y = 1.68 + (i // 3) * 1.92
    card(s, x, y, 3.85, 1.64, color)
    text(s, x + 0.24, y + 0.14, 3.40, 0.28, title, 12.5, INK, SEM)
    text(s, x + 0.24, y + 0.54, 3.40, 0.38, desc, 10.5, BODY, REG, line_spacing=1.0)
    text(s, x + 0.24, y + 1.00, 3.40, 0.50, detail, 10, MUTED, REG, line_spacing=1.0)
footer(s, "La mayoría de los errores viene de confundir la distancia horizontal con la distancia completa.")
notes(s,
      "Errores frecuentes:\n\n"
      "- Random ambiguo: using System; también trae System.Random. Escribe "
      "UnityEngine.Random.Range.\n"
      "- atan2 devuelve radianes; hay que multiplicar por 180 / PI.\n"
      "- El orden es Atan2(dy, horizontal). Al revés se calcula el ángulo "
      "complementario.\n"
      "- Sin Time.deltaTime, la velocidad cambia con los FPS.\n"
      "- Si el Rigidbody no es kinematic, la gravedad mueve la esfera.\n"
      "- Si el campo cubo está vacío, cubo.position lanza NullReferenceException.")

# 34 --------------------------------------------------------------- resumen
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "CIERRE", "LO QUE APRENDISTE",
       "Cuatro operaciones construyen toda la mecánica.")
summary = [
    ("01", "DISTANCIA", "raíz(dx*dx + dz*dz) para decidir si llegó o si el cubo está cerca.", ORANGE),
    ("02", "VECTORES", "Restar, normalizar y sumar para avanzar a velocidad constante.", PINK),
    ("03", "PATRULLA", "Cuatro esquinas y un objetivo nuevo cada cinco segundos.", BLUE),
    ("04", "PISOTÓN Y PERSECUCIÓN", "Ángulo, radio y un objetivo que cambia al jugador.", GREEN),
]
for i, (num, title, desc, color) in enumerate(summary):
    x = 0.62 if i % 2 == 0 else 6.44
    y = 1.62 if i < 2 else 3.14
    card(s, x, y, 5.55, 1.34, color)
    text(s, x + 0.26, y + 0.16, 0.40, 0.22, num, 13, color, SEM)
    text(s, x + 0.76, y + 0.13, 4.50, 0.28, title, 18, INK, SEM)
    text(s, x + 0.89, y + 0.56, 4.45, 0.58, desc, 11.5, BODY, REG, line_spacing=1.0)
card(s, 0.62, 4.75, 11.37, 0.95, ORANGE)
text(s, 0.86, 4.89, 10.80, 0.30,
     "La base es siempre la misma: restar, medir, normalizar y sumar.", 15, INK, SEM)
text(s, 0.86, 5.25, 10.80, 0.26,
     "Para practicar: agrega una bandera para que el pisotón ocurra una sola vez.",
     10.5, BODY, REG)
footer(s, "El enemigo ya patrulla, persigue y reacciona al pisotón. La siguiente práctica es agregar victoria y derrota.")
notes(s,
      "Resumen:\n\n"
      "1. Distancia: la fórmula raíz(dx*dx + dy*dy + dz*dz); en el plano se usa "
      "raíz(dx*dx + dz*dz).\n"
      "2. Vectores: restar para obtener hacia, normalizar para que la diagonal no "
      "sea más rápida y sumar para avanzar.\n"
      "3. Patrulla: cuatro esquinas, un índice y InvokeRepeating cada cinco "
      "segundos.\n"
      "4. Pisotón y persecución: ángulo con atan2, radio horizontal y cambio de "
      "objetivo cuando el cubo entra en radioDeteccion.\n\n"
      "Para practicar: usar el bool que devuelve Pisoton para una victoria y una "
      "comprobación aparte para la derrota.")

# 35 --------------------------------------------------------------- preguntas
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
text(s, 0.0, 1.75, 13.33, 1.10, "¿PREGUNTAS?", 54, INK, SEM, align=PP_ALIGN.CENTER)
text(s, 0.0, 3.18, 13.33, 0.38, "Siguiente: laboratorio de Unity.", 18, INK, REG,
     align=PP_ALIGN.CENTER)
text(s, 0.0, 3.72, 13.33, 0.38,
     "La esfera ya patrulla, te persigue y reacciona al pisotón.", 14, BODY, REG,
     align=PP_ALIGN.CENTER)
picture_fit(s, ROOT / "decor" / "star.png", 1.55, 2.30, 0.85, 0.85, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 3.60, 4.15, 0.75, 0.75, border=False)
picture_fit(s, ROOT / "decor" / "tree-small.png", 1.10, 4.36, 1.15, 2.06, border=False)
picture_fit(s, ROOT / "decor" / "cloud-low.png", 9.85, 4.68, 2.65, 1.42, border=False)
notes(s,
      "Cierre del tema 8.6.1.\n\n"
      "Recuerda: el enemigo patrulla entre cuatro esquinas, detecta al jugador con "
      "un radio, cambia su objetivo y reacciona al pisotón con un ángulo y una "
      "distancia horizontal.\n\n"
      "En el laboratorio se puede ampliar con victoria, derrota, giro visual y una "
      "bandera para que el pisotón ocurra una sola vez.")

def embed_fonts(path):
    """Incrusta Neuromax y Neuromax SemBd en el .pptx (EOT de T8.5.2)."""
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


prs.save(PPTX)
embed_fonts(PPTX)
print("Guardado:", PPTX)
print("Diapositivas:", len(prs.slides))
