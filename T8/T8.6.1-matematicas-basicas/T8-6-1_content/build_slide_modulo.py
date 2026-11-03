#!/usr/bin/env python3
"""Genera una diapositiva suelta sobre el módulo 4 de EnemigoEsfera.

Usa la misma plantilla que build_deck.py: fondo pixel art, Neuromax,
tarjetas blancas y acentos naranja/rosa. Escribe el .pptx en la carpeta
padre para poder insertarlo en T8.6.1.
"""

from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
PPTX = ROOT.parent / "T8.6.1-slide-modulo.pptx"

# ---------------------------------------------------------------- palette
INK = RGBColor(0x13, 0x13, 0x15)
BODY = RGBColor(0x4F, 0x53, 0x61)
MUTED = RGBColor(0x6B, 0x72, 0x80)
ORANGE = RGBColor(0xF0, 0x8A, 0x3C)
ORANGE_TEXT = RGBColor(0xB4, 0x53, 0x09)
PINK = RGBColor(0xE8, 0x38, 0x6D)
GREEN = RGBColor(0x2E, 0x8B, 0x57)
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


def card(slide, x, y, w, h, accent=ORANGE, fill=WHITE, line=None):
    rect(slide, x, y, w, h, fill, line)
    rect(slide, x, y, 0.07, h, accent)


def label(slide, x, y, w, value, color=ORANGE_TEXT):
    text(slide, x, y, w, 0.22, value, 9.5, color, SEM)


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
prs.core_properties.title = "T8.6.1 · Por qué el módulo 4"
prs.core_properties.author = "TC2005B · Construcción de Software"
prs.core_properties.subject = "Detalle de implementación de la patrulla"
prs.core_properties.language = "es-MX"

s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · PATRULLA", "POR QUÉ EL MÓDULO 4",
       "El salto de 1 a 3 evita repetir la esquina; el módulo evita salir del arreglo.")

# --- código
picture_fit(s, ROOT / "codigo" / "code_modulo.png", 0.62, 1.62, 6.95, 1.98,
            border=True, border_w=1.0)

# --- tarjeta: el salto nunca es 0
card(s, 8.10, 1.66, 4.60, 1.86, GREEN)
label(s, 8.32, 1.80, 4.20, "RANDOM.RANGE(1, 4)", GREEN)
text(s, 8.32, 2.06, 4.16, 0.62,
     "Devuelve 1, 2 o 3.\nNunca 0.", 15, INK, SEM, line_spacing=1.02)
text(s, 8.32, 2.78, 4.16, 0.66,
     "Por eso la esquina nueva siempre es distinta de la actual.",
     11, BODY, REG, line_spacing=1.02)

# --- tabla: el índice da la vuelta
label(s, 0.62, 3.86, 5.55, "EL ÍNDICE DA LA VUELTA")
table(s, 0.62, 4.02, 5.55, 1.70, [
    ["índice", "+1", "+2", "+3"],
    ["0", "1", "2", "3"],
    ["1", "2", "3", "0"],
    ["2", "3", "0", "1"],
    ["3", "0", "1", "2"],
], [1.35, 1.40, 1.40, 1.40], font_size=11, header_size=11,
    row_h=0.34, align=PP_ALIGN.CENTER)
text(s, 0.62, 5.82, 5.55, 0.24, "Ninguna fila repite el índice de partida.",
     10, BODY, REG)

# --- trampas
card(s, 6.50, 3.86, 6.20, 0.96, PINK)
label(s, 6.74, 3.96, 5.70, "SIN EL MÓDULO 4", PINK)
text(s, 6.74, 4.20, 5.74, 0.56,
     "3 + 3 = 6. esquinas[6] no existe: IndexOutOfRangeException.",
     11.5, BODY, REG, line_spacing=1.02)

card(s, 6.50, 4.96, 6.20, 1.04, ORANGE)
label(s, 6.74, 5.06, 5.70, "CON Random.Range(0, 4)")
text(s, 6.74, 5.30, 5.74, 0.64,
     "1 de cada 4 veces elige la misma esquina. La esfera no avanza hasta que el temporizador elige otra: hasta 5 s.",
     11.5, BODY, REG, line_spacing=1.02)

footer(s, "El operador % devuelve el resto de la división. Con 4 esquinas, equivale a dar la vuelta al arreglo.")

s.notes_slide.notes_text_frame.text = (
    "El bloque de llegada hace dos cosas a la vez: elige otra esquina y evita "
    "salirse del arreglo.\n\n"
    "Random.Range(1, 4) con enteros no incluye el límite superior, así que "
    "devuelve 1, 2 o 3, nunca 0. Sumar ese desplazamiento garantiza que el "
    "índice cambie: la esquina nueva siempre es distinta de la actual.\n\n"
    "El módulo 4 mantiene el resultado entre 0 y 3. Si la esfera está en la "
    "esquina 3 y el salto es 3, la suma da 6; 6 % 4 = 2, que es una posición "
    "válida. Sin el módulo, esquinas[6] lanzaría IndexOutOfRangeException.\n\n"
    "La alternativa obvia, indiceObjetivo = Random.Range(0, 4), también da un "
    "índice válido, pero puede repetir la esquina actual una de cada cuatro "
    "veces. En ese caso la distancia sigue siendo menor a 0.1, el método hace "
    "return y la esfera no se mueve en ese fotograma ni en los siguientes: "
    "queda detenida hasta que InvokeRepeating llama a NewRandom, como máximo "
    "cinco segundos después.\n\n"
    "En NewRandom sí se usa Random.Range(0, 4) porque ahí no hay una condición "
    "de llegada esperando; repetir la esquina solo mantiene el destino actual.\n\n"
    "CÓDIGO DE LA DIAPOSITIVA "
    "(Assets/Scripts/escena3_math/EnemigoEsfera.cs):\n\n"
    "if (distancia < 0.1f && !persiguiendo)\n"
    "{\n"
    "    // Elige otra esquina distinta: suma 1, 2 o 3 y da la vuelta\n"
    "    indiceObjetivo = (indiceObjetivo + UnityEngine.Random.Range(1, 4)) % 4;\n"
    "    return;\n"
    "}")

prs.save(PPTX)
print(PPTX)
