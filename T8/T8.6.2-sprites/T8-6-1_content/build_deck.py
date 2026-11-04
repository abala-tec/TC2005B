#!/usr/bin/env python3
"""Construye T8.6.2 - Cámara, materiales y sprites.

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
    "DECK_OUT", str(ROOT.parent / "T8.6.2-Camara-Materiales-Sprites.pptx")
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


# ---------------------------------------------------------------- deck
prs = new_deck()
prs.core_properties.title = "T8.6.2 · Cámara, materiales y sprites"
prs.core_properties.author = "TC2005B · Construcción de Software"
prs.core_properties.subject = "Cámara, plano, spawner, materiales y sprites 2D"
prs.core_properties.keywords = "Unity, C#, cámara, material, sprite, spawner, TC2005B"
prs.core_properties.language = "es-MX"

# 0 ---------------------------------------------------------------- portada
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
rect(s, 0.62, 0.32, 0.09, 0.09, ORANGE)
text(s, 0.81, 0.28, 10.0, 0.22, "8.6.2 · CÁMARA, MATERIALES Y SPRITES", 9.5, INK, SEM)
text(s, 0.62, 0.92, 6.00, 2.70, "CÁMARA,\nMATERIALES\nY SPRITES", 48, INK, SEM,
     line_spacing=0.92)
text(s, 0.62, 3.64, 5.70, 0.80,
     "Cómo seguir al jugador, agrandar el escenario y convertir el personaje en un sprite 2D.",
     20, INK, REG, line_spacing=1.02)
text(s, 0.62, 4.55, 5.55, 0.72,
     "Cámara con Lerp, plano de 100 × 100, spawner de esferas y sprite con sombra.",
     14, BODY, REG, line_spacing=1.02)
text(s, 0.62, 5.62, 5.40, 0.28, "TC2005B · Construcción de Software", 12.5, INK, REG)
text(s, 0.62, 5.96, 5.40, 0.28, "Unity · C# · Sample_Game", 11, MUTED, REG)

rect(s, 6.55, 0.66, 6.18, 4.95, DARK)
picture_fill(s, ROOT / "img" / "cover_sprite.png", 6.75, 0.86, 5.78, 4.55)
rect(s, 6.75, 0.86, 5.78, 4.55, None, WHITE, 1.2)
pill(s, 6.95, 0.72, 1.55, "UNITY · C#", WHITE, DARK)
picture_fit(s, ROOT / "decor" / "star.png", 0.55, 6.30, 0.75, 0.75, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 11.55, 6.10, 0.95, 0.95, border=False)
notes(s,
      "Bienvenida al tema 8.6.2. Hoy completamos la escena del proyecto Sample_Game.\n\n"
      "El recorrido tiene cuatro bloques: una cámara que sigue al cubo, un plano más "
      "grande con un spawner de esferas, un material verde para el piso y un sprite "
      "2D para el personaje.\n\n"
      "Todo el código se muestra como imagen y se copia en las notas de cada "
      "diapositiva. La meta es que el alumno pueda repetir el proceso en Unity.")

# 1 ---------------------------------------------------------------- agenda
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "HOY", "LO QUE VEREMOS HOY",
       "Cuatro bloques construyen el escenario y el personaje.")
rows = [
    ("01", "CÁMARA", "Una cámara que sigue al cubo con suavidad.", ORANGE),
    ("02", "ESCENARIO", "Plano de 100 × 100 y un spawner de 50 esferas.", BLUE),
    ("03", "MATERIAL", "Un material verde para cambiar el color del piso.", GREEN),
    ("04", "SPRITE 2D", "Personaje 2D, sombra y volteo a izquierda y derecha.", PINK),
]
for i, (num, title, desc, color) in enumerate(rows):
    y = 1.64 + i * 0.80
    card(s, 0.62, y, 12.09, 0.72, color)
    text(s, 0.82, y + 0.16, 0.45, 0.30, num, role="card_number", color=color)
    text(s, 1.42, y + 0.10, 8.60, 0.30, title, 18, INK, SEM)
    text(s, 1.46, y + 0.43, 10.40, 0.25, desc, 12, BODY, REG)
text(s, 0.62, 5.15, 12.09, 0.62,
     "Cada bloque se prueba en Play antes de pasar al siguiente.", 15, INK, SEM,
     line_spacing=1.02)
text(s, 0.62, 5.78, 11.6, 0.30,
     "El proyecto parte de la escena de T8.6.1 y conserva el cubo, el HUD y la esfera.",
     12, BODY, REG)
notes(s,
      "Recorrido en cuatro bloques.\n\n"
      "1. Cámara: un script que copia la posición del cubo con un offset y suaviza "
      "el movimiento con Lerp.\n"
      "2. Escenario: el plano crece de 10 × 10 a 100 × 100 y un spawner crea 50 "
      "esferas alrededor de su centro.\n"
      "3. Material: se crea un material verde y se asigna al plano.\n"
      "4. Sprite: una hoja de 7 cuadros se convierte en sprite, recibe una sombra y "
      "se voltea con las flechas izquierda y derecha.\n\n"
      "La base es la escena de T8.6.1: el cubo ya se mueve, salta y cuenta caídas.")

# 2 ---------------------------------------------------------------- seccion 01
s = section_slide(prs, "01", "CÁMARA QUE SIGUE\nAL JUGADOR",
                  "La cámara deja de ser fija y acompaña al cubo.",
                  "TARGET · OFFSET · LATEUPDATE · LERP", ORANGE)
notes(s,
      "Bloque 1. La cámara del juego debe seguir al personaje. Si se queda fija, el "
      "cubo puede salir de la pantalla y el jugador pierde el control visual.\n\n"
      "La solución no es mover la cámara a la fuerza en cada fotograma. Primero se "
      "calcula una meta y después se acerca la cámara a esa meta con Lerp.")

# 3 ---------------------------------------------------------------- problema
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · CÁMARA", "LA CÁMARA FIJA PIERDE AL JUGADOR",
       "Si el cubo camina, sale de la pantalla y deja de verse.")
text(s, 0.62, 1.68, 5.55, 0.28, "LA IDEA", 9.5, ORANGE_TEXT, SEM)
text(s, 0.62, 2.02, 5.55, 0.80,
     "posición de la cámara =\nposición del cubo + offset", 21, INK, SEM,
     line_spacing=1.02)
bullets(s, 0.62, 3.05, 5.55, [
    "La cámara conserva la misma distancia y la misma altura.",
    "El offset se escribe en unidades de la escena.",
    "La rotación de la cámara no cambia: solo su posición.",
], size=12.5, gap=0.72)
card(s, 0.62, 5.16, 5.55, 0.82, ORANGE)
text(s, 0.86, 5.28, 5.10, 0.26, "Offset de la escena: (0, 5, -10).", 12, INK, SEM)
text(s, 0.86, 5.56, 5.10, 0.26, "La cámara queda arriba y detrás del cubo.", 10.5, BODY, REG)
shot(s, "sprite_juego.png", 6.72, 1.64, 5.95, 4.20)
text(s, 6.84, 5.88, 5.70, 0.26,
     "Vista del juego con la cámara colocada detrás del personaje.", 10, MUTED, REG)
footer(s, "La cámara no gira: se traslada. El ángulo de la vista se conserva.")
notes(s,
      "Una cámara fija solo muestra una parte de la escena. Cuando el cubo se mueve, "
      "puede salir del cuadro.\n\n"
      "La solución es calcular la posición de la cámara a partir de la posición del "
      "cubo: se suma un offset. El offset (0, 5, -10) coloca la cámara 5 unidades "
      "arriba y 10 unidades detrás.\n\n"
      "La rotación de la cámara no se modifica. Por eso la vista mantiene el mismo "
      "ángulo mientras el cubo camina.")

# 4 ---------------------------------------------------------------- crear script
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · CÁMARA", "CREAR EL SCRIPT S4_CameraFollower",
       "El script se crea en la carpeta Scripts y se llama igual que la clase.")
shot(s, "cam_crear_menu.png", 0.62, 1.64, 3.55, 3.55)
text(s, 0.74, 5.28, 3.30, 0.26, "Create > C# Script.", 10, MUTED, REG)
shot(s, "cam_script_icon.png", 4.45, 1.64, 3.40, 1.75)
text(s, 4.57, 3.48, 3.15, 0.26, "El archivo creado.", 10, MUTED, REG)
text(s, 8.20, 1.74, 4.40, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 8.20, 2.08, 4.35, [
    "Clic derecho en Assets > Scripts.",
    "Elige Create > C# Script.",
    "Escribe S4_CameraFollower.",
    "Presiona Enter para crear el archivo.",
], size=12.5, gap=0.62)
card(s, 8.20, 4.72, 4.35, 1.02, BLUE)
text(s, 8.44, 4.84, 3.90, 0.26, "El nombre importa.", 12.5, INK, SEM)
text(s, 8.44, 5.14, 3.90, 0.50,
     "El archivo y la clase deben llamarse igual o Unity no carga el componente.",
     10.5, BODY, REG, line_spacing=1.0)
footer(s, "La carpeta Scripts ya existe en el proyecto Sample_Game.")
notes(s,
      "Para crear el script, haz clic derecho en la carpeta Scripts y elige Create > "
      "C# Script. Escribe S4_CameraFollower con la misma mayúscula inicial.\n\n"
      "Unity crea un archivo con una clase vacía. El nombre del archivo y el nombre "
      "de la clase deben coincidir. Si no coinciden, el componente no se puede "
      "agregar al GameObject.\n\n"
      "La captura de la izquierda muestra el menú Create. La captura de la derecha "
      "muestra el archivo ya creado.")

# 5 ---------------------------------------------------------------- agregar componente
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · CÁMARA", "AGREGAR EL SCRIPT A MAIN CAMERA",
       "El componente se agrega al objeto que mueve la cámara.")
shot(s, "cam_add_component.png", 0.62, 1.64, 5.30, 3.40)
text(s, 0.74, 5.12, 5.05, 0.26, "Add Component > S4_CameraFollower.", 10, MUTED, REG)
text(s, 6.35, 1.74, 6.10, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 6.35, 2.08, 6.00, [
    "Selecciona Main Camera en la jerarquía.",
    "Haz clic en Add Component.",
    "Busca S4_CameraFollower.",
    "Presiona Enter para agregarlo.",
], size=12.5, gap=0.64)
card(s, 6.35, 4.85, 6.00, 0.92, ORANGE)
text(s, 6.59, 4.97, 5.50, 0.26, "Si no aparece, espera a que Unity compile.", 11.5, INK, SEM)
text(s, 6.59, 5.27, 5.50, 0.26, "El nombre debe estar sin errores de compilación.", 10.5, BODY, REG)
footer(s, "El componente aparece en el Inspector de Main Camera, no en el del cubo.")
notes(s,
      "Selecciona Main Camera en la jerarquía. En el Inspector, haz clic en Add "
      "Component y busca S4_CameraFollower.\n\n"
      "Si el script tiene errores de compilación, Unity no lo muestra en la lista. "
      "Revisa la consola y corrige los errores antes de continuar.\n\n"
      "El componente se agrega a Main Camera porque ese objeto es el que tiene el "
      "componente Camera y la transformación que queremos mover.")

# 6 ---------------------------------------------------------------- target
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · CÁMARA", "ASIGNAR EL TARGET: EL CUBO",
       "El campo Target debe apuntar al objeto Cube.")
shot(s, "cam_target_vacio.png", 0.62, 1.64, 4.15, 1.55)
text(s, 0.74, 3.25, 3.90, 0.26, "Target vacío: el script no sabe a quién seguir.", 10, MUTED, REG)
shot(s, "cam_select_cube.png", 4.95, 1.64, 3.90, 2.00)
text(s, 5.07, 3.72, 3.65, 0.26, "Selecciona Cube en la lista.", 10, MUTED, REG)
shot(s, "cam_target_cube.png", 9.05, 1.64, 3.62, 1.35)
text(s, 9.17, 3.07, 3.40, 0.26, "Target asignado.", 10, MUTED, REG)
card(s, 0.62, 4.05, 6.30, 1.02, PINK)
text(s, 0.86, 4.17, 5.85, 0.26, "Sin Target: NullReferenceException.", 12, INK, SEM)
text(s, 0.86, 4.47, 5.85, 0.48,
     "target.position se lee en LateUpdate y el campo todavía está vacío.",
     10.5, BODY, REG, line_spacing=1.0)
card(s, 7.18, 4.05, 5.50, 1.02, GREEN)
text(s, 7.42, 4.17, 5.00, 0.26, "Arrastra el Cube desde la jerarquía.", 12, INK, SEM)
text(s, 7.42, 4.47, 5.00, 0.48,
     "También puedes usar el círculo del campo y elegir la escena.",
     10.5, BODY, REG, line_spacing=1.0)
text(s, 0.62, 5.40, 12.05, 0.62,
     "El Target es un Transform, no el script del cubo. Solo se necesita su posición.",
     12, BODY, REG, line_spacing=1.0)
footer(s, "El campo Target acepta cualquier Transform: el Cube, otro personaje o un objeto vacío.")
notes(s,
      "El campo Target está vacío al agregar el componente. Si se ejecuta el juego "
      "así, target.position lanza NullReferenceException.\n\n"
      "Para asignarlo, arrastra el GameObject Cube desde la jerarquía hasta el campo "
      "Target. También puedes hacer clic en el círculo del campo y elegir Cube en la "
      "ventana Select Transform.\n\n"
      "El script solo necesita la posición del cubo. No necesita una referencia al "
      "script S4_CubeMove ni a sus campos.")

# 7 ---------------------------------------------------------------- codigo camara
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · CÁMARA", "EL CÓDIGO DE LA CÁMARA",
       "Tres campos y un método corto resuelven el seguimiento.")
code(s, "code_camara_campos.png", 0.62, 1.64, 6.05, 1.35)
text(s, 0.74, 3.08, 5.80, 0.26, "CAMPOS PÚBLICOS", 9.5, ORANGE_TEXT, SEM)
code(s, "code_camara_lateupdate.png", 0.62, 3.42, 6.25, 2.55)
text(s, 7.15, 1.74, 5.55, 0.28, "QUÉ HACE CADA PARTE", 9.5, ORANGE_TEXT, SEM)
fields = [
    ("target", "El Transform del cubo. Indica a quién se sigue."),
    ("offset", "La distancia entre la cámara y el cubo."),
    ("followspeed", "Qué parte del camino se recorre por fotograma."),
]
for i, (name, desc) in enumerate(fields):
    y = 2.10 + i * 0.72
    text(s, 7.15, y, 1.70, 0.26, name, 12, INK, SEM)
    text(s, 8.95, y - 0.01, 3.80, 0.50, desc, role="body", line_spacing=1.0)
card(s, 7.15, 4.35, 5.55, 0.92, ORANGE)
text(s, 7.39, 4.47, 5.05, 0.26, "LateUpdate corre después de Update.", 11.5, INK, SEM)
text(s, 7.39, 4.77, 5.05, 0.48,
     "Así la cámara sigue al cubo cuando ya terminó de moverse en ese fotograma.",
     10, BODY, REG, line_spacing=1.0)
text(s, 7.15, 5.47, 5.55, 0.52,
     "El script no cambia la rotación ni el campo de visión de la cámara.",
     11.5, BODY, REG, line_spacing=1.0)
footer(s, "El método se llama LateUpdate, con mayúscula inicial y sin parámetros.")
notes_code(s,
           "El script tiene tres campos públicos que aparecen en el Inspector: "
           "target, offset y followspeed.\n\n"
           "LateUpdate se ejecuta una vez por fotograma, después de Update. Se usa "
           "para que la cámara se mueva después de que el cubo ya cambió de posición.\n\n"
           "goalPosition es la posición que la cámara quiere alcanzar. "
           "Vector3.Lerp calcula un punto intermedio entre la posición actual y la "
           "meta. El factor followspeed va de 0 a 1.\n\n"
           "Al final, transform.position se reemplaza por smoothedPosition.",
           [
               ("Assets/Scripts/escena4_hash_grid/S4_CameraFollower.cs",
                """using UnityEngine;

public class S4_CameraFollower : MonoBehaviour
{
    public Transform target;  // El gameobject a seguir

    public Vector3 offset = new Vector3(0,5,-10);  // el ofset del objecto a la camara

    public float followspeed = 0.2f;   // la velocidad de seguimiento

    // Usamos LateUpdate para seguir los objetos despues de
    // haber sido afectados por fuerzas durante Update()
    void LateUpdate()
    {
        Vector3 goalPosition = target.position + offset;

        // Lerp interpola entre la posicion actual de la camara y la meta
        Vector3 smoothedPosition = Vector3.Lerp(
            transform.position, goalPosition, followspeed);

        transform.position = smoothedPosition;
    }
}"""),
           ])

# 8 ---------------------------------------------------------------- lerp
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · CÁMARA", "CÓMO FUNCIONA LERP",
       "La cámara se acerca a la meta en cada fotograma.")
fig(s, ROOT / "figuras" / "camara_lerp.png", 0.62, 1.64, 6.30, 3.30)
text(s, 0.74, 5.02, 6.05, 0.26, "Figura 1. La cámara recorre una parte del camino.", 10, MUTED, REG)
text(s, 7.20, 1.72, 5.55, 0.50, "Lerp(actual, meta, 0.2)", 20, INK, SEM)
bullets(s, 7.20, 2.42, 5.45, [
    "GoalPosition es el cubo más el offset.",
    "Lerp devuelve un punto entre actual y meta.",
    "0.2 significa el 20 % del camino por fotograma.",
    "El resultado se guarda en transform.position.",
], size=12.5, gap=0.64)
card(s, 7.20, 5.02, 5.45, 0.82, ORANGE)
text(s, 7.44, 5.14, 5.00, 0.26, "0.2 es una proporción, no una velocidad.", 11.5, INK, SEM)
text(s, 7.44, 5.43, 5.00, 0.26, "Si el factor es 1, salta; si es 0, no se mueve.", 10, BODY, REG)
footer(s, "La cámara nunca llega de golpe: persigue la meta.")
notes_code(s,
           "Lerp recibe tres valores: la posición actual, la meta y un factor entre 0 "
           "y 1. Devuelve un punto intermedio.\n\n"
           "Con 0.2, la cámara recorre el 20 % de la distancia que le falta en ese "
           "fotograma. En el siguiente fotograma vuelve a calcular y recorre otro 20 % "
           "del espacio restante. Por eso el movimiento se ve suave.\n\n"
           "El factor no es una velocidad en metros por segundo. Es una proporción. "
           "Si se pone 1, la cámara salta a la meta; si se pone 0, no se mueve.\n\n"
           "La rotación no se toca. La cámara mantiene el ángulo de la vista.",
           [("Assets/Scripts/escena4_hash_grid/S4_CameraFollower.cs",
             """Vector3 goalPosition = target.position + offset;

Vector3 smoothedPosition = Vector3.Lerp(
    transform.position, goalPosition, followspeed);

transform.position = smoothedPosition;""")])

# 9 ---------------------------------------------------------------- probar camara
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · CÁMARA", "AJUSTAR Y PROBAR LA CÁMARA",
       "Prueba primero con el cubo quieto y después caminando.")
table(s, 0.62, 1.66, 6.10, 2.10, [
    ["Campo", "Valor", "Para qué sirve"],
    ["Target", "Cube", "Objeto que se sigue."],
    ["Offset", "(0, 5, -10)", "Altura y distancia."],
    ["Followspeed", "0.2", "Suavidad del movimiento."],
], [1.55, 1.55, 2.65], font_size=12, header_size=11.5, row_h=0.50)
text(s, 0.62, 3.96, 6.10, 0.28, "PRUEBA EN PLAY", 9.5, ORANGE_TEXT, SEM)
steps(s, 0.62, 4.30, 5.95, [
    "Mueve el cubo con W, A, S, D.",
    "Comprueba que la cámara mantiene la distancia.",
    "Ajusta Followspeed si el movimiento es muy lento o muy brusco.",
], size=12, gap=0.52)
shot(s, "cam_target_cube.png", 7.05, 1.66, 5.55, 2.05)
text(s, 7.17, 3.82, 5.30, 0.26, "Inspector de Main Camera con el Target asignado.", 10, MUTED, REG)
card(s, 7.05, 4.35, 5.55, 0.92, PINK)
text(s, 7.29, 4.47, 5.05, 0.26, "Si la cámara vibra, baja Followspeed.", 11.5, INK, SEM)
text(s, 7.29, 4.77, 5.05, 0.26, "Si se queda atrás, súbelo un poco.", 10.5, BODY, REG)
footer(s, "El offset se escribe en unidades de la escena, no en píxeles de pantalla.")
notes(s,
      "Antes de probar, revisa el Inspector: Target debe ser Cube, Offset debe ser "
      "(0, 5, -10) y Followspeed debe ser 0.2.\n\n"
      "En Play, mueve el cubo con W, A, S, D o con las flechas. La cámara debe "
      "mantener la misma distancia y la misma altura.\n\n"
      "Si el movimiento se ve muy lento, sube Followspeed. Si la cámara vibra o se "
      "pasa de largo, baja Followspeed. El valor 0.2 es un punto de partida, no una "
      "regla fija.\n\n"
      "Si aparece NullReferenceException, el campo Target está vacío.")

# 10 --------------------------------------------------------------- seccion 02
s = section_slide(prs, "02", "ESCENARIO MÁS\nGRANDE",
                  "Un plano de 100 × 100 y un spawner que llena el mapa de enemigos.",
                  "ESCALA · POSICIÓN · COLLIDER · INSTANTIATE · RANDOM", BLUE)
notes(s,
      "Bloque 2. La escena original tiene un plano de 10 × 10. Para un juego con "
      "más espacio, el plano crece y se llena de enemigos.\n\n"
      "Primero se escala el plano. Después se crea un objeto vacío que marca el "
      "centro de aparición. Al final, un script crea 50 copias de la esfera alrededor "
      "de ese centro.")

# 11 --------------------------------------------------------------- escalar plano
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · ESCENARIO", "ESCALAR EL PLANO × 10",
       "El plano pasa de 10 × 10 a 100 × 100 unidades.")
fig(s, ROOT / "figuras" / "plano_escala.png", 0.62, 1.64, 6.55, 3.28)
text(s, 0.74, 5.00, 6.30, 0.26, "Figura 2. El tamaño cambia; el centro no.", 10, MUTED, REG)
text(s, 7.35, 1.70, 5.40, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 7.35, 2.04, 5.30, [
    "Selecciona Plane en la jerarquía.",
    "En Transform, escribe Scale X = 10.",
    "Escribe Scale Z = 10 y deja Y = 1.",
    "Comprueba el nuevo tamaño en la escena.",
], size=12, gap=0.54)
shot(s, "plano_escala_10.png", 7.35, 4.18, 2.70, 1.55)
text(s, 7.47, 5.80, 2.45, 0.26, "Scale 10, 1, 10.", role="caption", color=MUTED)
card(s, 10.25, 4.18, 2.40, 1.55, ORANGE)
text(s, 10.49, 4.30, 1.95, 0.24, "IMPORTANTE", 9.5, ORANGE_TEXT, SEM)
text(s, 10.49, 4.60, 1.95, 0.90,
     "La escala multiplica el tamaño. No cambia la posición del centro.",
     10.5, BODY, REG, line_spacing=1.0)
footer(s, "La escala del collider también cambia: el plano sigue funcionando como suelo.")
notes(s,
      "Selecciona el objeto Plane y cambia Scale a (10, 1, 10). El plano original "
      "mide 10 × 10; al multiplicar por 10, mide 100 × 100.\n\n"
      "La escala se aplica desde el centro del objeto. Por eso el plano crece hacia "
      "los dos lados: de -50 a 50 en X y en Z si el centro está en 0.\n\n"
      "El Mesh Collider también se escala. El cubo puede caminar sobre el plano "
      "grande sin cambiar el script de movimiento.")

# 12 --------------------------------------------------------------- mover plano
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · ESCENARIO", "MOVER EL PLANO, NO EL CUBO",
       "El cubo conserva su posición inicial cerca de una esquina.")
shot(s, "plano_posicion.png", 0.62, 1.64, 7.05, 4.12)
text(s, 0.74, 5.86, 6.80, 0.26, "Plane: Position (-45, 0, -45), Scale (10, 1, 10).", 10, MUTED, REG)
text(s, 7.95, 1.72, 4.80, 0.28, "POR QUÉ", 9.5, ORANGE_TEXT, SEM)
text(s, 7.95, 2.08, 4.70, 1.30,
     "El plano va de -95 a 5 en X y en Z. El cubo queda cerca de la esquina (5, 5).",
     15, INK, SEM, line_spacing=1.04)
bullets(s, 7.95, 3.55, 4.70, [
    "No muevas el Cube: cambia el inicio.",
    "Mueve el Plane: conserva el inicio.",
    "El spawner va en el centro del plano.",
], size=11.5, gap=0.60)
card(s, 7.95, 5.26, 4.70, 0.78, BLUE)
text(s, 8.19, 5.38, 4.25, 0.26, "Centro del plano: (-45, 0, -45).", 11.5, INK, SEM)
text(s, 8.19, 5.67, 4.25, 0.26, "Borde positivo: 5. Borde negativo: -95.", 10, BODY, REG)
footer(s, "El cubo queda cerca de la esquina (5, 5), no en el centro del plano.")
notes(s,
      "Al escalar, el plano crece desde su centro. Si el cubo estaba cerca de una "
      "esquina, ahora queda en el centro del plano grande.\n\n"
      "Para conservar la sensación de borde, mueve el plano a (-45, 0, -45). Así el "
      "plano va de -95 a 5 en X y en Z, y el cubo queda cerca de la esquina (5, 5).\n\n"
      "La posición del cubo no se toca. La posición inicial del jugador se conserva. "
      "El nuevo espacio queda detrás y a la izquierda del cubo.\n\n"
      "El spawner se coloca en el centro del plano nuevo, no en el centro del cubo.")

# 13 --------------------------------------------------------------- collider nombre
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · ESCENARIO", "EL COLLIDER Y EL NOMBRE DEL PLANO",
       "El plano sigue siendo el suelo, aunque sea más grande.")
shot(s, "plano_escala_10.png", 0.62, 1.64, 5.20, 3.10)
text(s, 0.74, 4.82, 4.95, 0.26, "El Mesh Collider se escala con el plano.", 10, MUTED, REG)
text(s, 6.15, 1.72, 6.20, 0.28, "REVISA ESTOS DETALLES", 9.5, ORANGE_TEXT, SEM)
bullets(s, 6.15, 2.08, 6.05, [
    "El Mesh Collider debe seguir activo.",
    "El objeto debe llamarse Plane.",
    "El cubo detecta el suelo con collision.gameObject.name == \"Plane\".",
    "El plano no necesita Rigidbody.",
], size=12, gap=0.66)
card(s, 6.15, 5.06, 6.05, 0.92, PINK)
text(s, 6.39, 5.18, 5.55, 0.26, "Si renombras el plano, el cubo no recupera el salto.", 11.5, INK, SEM)
text(s, 6.39, 5.47, 5.55, 0.26, "OnCollisionEnter busca el nombre exacto.", 10.5, BODY, REG)
footer(s, "El nombre Plane es parte del contrato entre el script del cubo y la escena.")
notes(s,
      "El Mesh Collider del plano se escala junto con el objeto. El cubo puede "
      "caminar sobre el plano grande sin cambiar el script de movimiento.\n\n"
      "El script S4_CubeMove usa OnCollisionEnter y compara el nombre del objeto con "
      "\"Plane\". Si el plano se renombra, el cubo no marca estaEnSuelo y no puede "
      "volver a saltar.\n\n"
      "El plano no necesita Rigidbody. Solo necesita el collider que ya trae. El "
      "Rigidbody es del cubo.")

# 14 --------------------------------------------------------------- que es spawner
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · SPAWNER", "¿QUÉ ES UN SPAWNER?",
       "Un objeto que crea copias de un enemigo durante el juego.")
text(s, 0.62, 1.70, 6.30, 0.28, "LA IDEA", 9.5, ORANGE_TEXT, SEM)
text(s, 0.62, 2.04, 6.20, 0.56, "Un molde, muchas copias.", 23, INK, SEM)
bullets(s, 0.62, 2.80, 6.10, [
    "El enemigo original es el molde que se copia.",
    "Instantiate crea una copia en una posición y rotación.",
    "El spawner repite la operación con un bucle.",
    "Las copias se llaman EnemigoClon_0, EnemigoClon_1, etc.",
], size=12.5, gap=0.68)
card(s, 0.62, 5.24, 6.10, 0.82, BLUE)
text(s, 0.86, 5.36, 5.65, 0.26, "El bucle se ejecuta una vez, en Start.", 11.5, INK, SEM)
text(s, 0.86, 5.65, 5.65, 0.26, "No se ejecuta en cada fotograma.", 10.5, BODY, REG)
shot(s, "spawn_resultado.png", 7.05, 1.64, 5.60, 3.78)
text(s, 7.17, 5.50, 5.35, 0.26, "50 esferas alrededor del centro del plano.", 10, MUTED, REG)
footer(s, "El molde sigue en la escena. Las copias son objetos nuevos en la jerarquía.")
notes(s,
      "Un spawner es un objeto que crea enemigos durante el juego. No es un enemigo "
      "nuevo: es el encargado de fabricar copias.\n\n"
      "El enemigo original se usa como molde. Instantiate recibe el molde, la "
      "posición y la rotación. Devuelve una copia nueva que se puede mover, borrar o "
      "renombrar.\n\n"
      "El spawner repite la operación con un bucle for. En este caso, 50 veces. Las "
      "copias se llaman EnemigoClon_0, EnemigoClon_1 y así hasta EnemigoClon_49.")

# 15 --------------------------------------------------------------- crear spawner
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · SPAWNER", "CREAR EL OBJETO SPAWNER",
       "Un objeto vacío marca el centro de la zona de aparición.")
shot(s, "spawn_crear_empty.png", 0.62, 1.64, 4.30, 3.40)
text(s, 0.74, 5.12, 4.05, 0.26, "GameObject > Create Empty.", 10, MUTED, REG)
shot(s, "spawn_posicion.png", 5.25, 1.64, 2.55, 1.50)
text(s, 5.37, 3.22, 2.30, 0.26, "Position (-50, 0, -50).", 10, MUTED, REG)
text(s, 8.20, 1.72, 4.45, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 8.20, 2.06, 4.40, [
    "Crea un objeto vacío con GameObject > Create Empty.",
    "Renómbralo Spawner.",
    "Escribe Position (-50, 0, -50).",
    "Comprueba el gizmo en el centro del plano.",
], size=12, gap=0.60)
card(s, 8.20, 4.86, 4.40, 0.92, ORANGE)
text(s, 8.44, 4.98, 3.95, 0.26, "El spawner no tiene mesh.", 11.5, INK, SEM)
text(s, 8.44, 5.27, 3.95, 0.26, "Solo guarda una posición.", 10.5, BODY, REG)
footer(s, "El centro del plano nuevo es (-45, 0, -45). El spawner se coloca cerca de (-50, 0, -50).")
notes(s,
      "Crea un objeto vacío con GameObject > Create Empty. Renómbralo Spawner.\n\n"
      "Coloca su posición en (-50, 0, -50). El plano nuevo va de -95 a 5, así que "
      "(-50, -50) queda cerca del centro del área jugable.\n\n"
      "El objeto vacío no tiene mesh ni collider. Solo marca un punto en la escena. "
      "El script usará transform.position para saber desde dónde crear los enemigos.")

# 16 --------------------------------------------------------------- crear script spawner
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · SPAWNER", "CREAR EL SCRIPT Y AGREGARLO",
       "S4_Spawner se agrega al objeto vacío.")
shot(s, "spawn_crear_script.png", 0.62, 1.64, 4.30, 3.55)
text(s, 0.74, 5.27, 4.05, 0.26, "Create > C# Script > S4_Spawner.", 10, MUTED, REG)
shot(s, "spawn_add_component.png", 5.30, 1.64, 3.55, 2.95)
text(s, 5.42, 4.68, 3.30, 0.26, "Add Component > S4_Spawner.", 10, MUTED, REG)
text(s, 9.15, 1.72, 3.60, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 9.15, 2.06, 3.55, [
    "Crea el script S4_Spawner.",
    "Selecciona el objeto Spawner.",
    "Agrega el componente.",
    "Revisa que no haya errores.",
], size=11.5, gap=0.58)
card(s, 9.15, 4.76, 3.55, 0.92, PINK)
text(s, 9.39, 4.88, 3.10, 0.48, "El script debe estar en la carpeta Scripts.",
     10.5, INK, SEM, line_spacing=1.0)
footer(s, "El nombre del archivo y el nombre de la clase deben coincidir.")
notes(s,
      "Crea el script S4_Spawner en la carpeta Scripts. El nombre del archivo y el "
      "nombre de la clase deben coincidir.\n\n"
      "Selecciona el objeto Spawner y agrega el componente con Add Component. Si el "
      "script tiene errores, Unity no lo muestra en la lista.\n\n"
      "El componente aparece en el Inspector del Spawner. Allí se asignan el enemigo, "
      "el número de copias y el radio.")

# 17 --------------------------------------------------------------- campos spawner
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · SPAWNER", "LOS CAMPOS DEL SPAWNER",
       "El Inspector decide cuántos enemigos y qué objeto se copia.")
code(s, "code_spawner_campos.png", 0.62, 1.72, 5.20, 1.55)
text(s, 0.74, 3.40, 4.95, 0.26, "CAMPOS DEL SCRIPT", 9.5, ORANGE_TEXT, SEM)
shot(s, "spawn_inspector.png", 0.62, 3.72, 5.20, 1.55)
text(s, 0.74, 5.36, 4.95, 0.26, "Inspector: Enemigo, 50 y radio 45.", 10, MUTED, REG)
text(s, 6.20, 1.72, 6.20, 0.28, "QUÉ SIGNIFICA CADA CAMPO", 9.5, ORANGE_TEXT, SEM)
fields = [
    ("enemigo", "El GameObject que se copia. Se asigna con el Inspector."),
    ("numeroEnemigos", "Cuántas copias se crean. En la escena, 50."),
    ("radio", "Distancia máxima desde el spawner. En la escena, 45."),
]
for i, (name, desc) in enumerate(fields):
    y = 2.10 + i * 0.86
    text(s, 6.20, y, 2.10, 0.26, name, 12, INK, SEM)
    text(s, 8.35, y - 0.01, 4.05, 0.62, desc, role="body", line_spacing=1.0)
card(s, 6.20, 4.90, 6.20, 0.92, ORANGE)
text(s, 6.44, 5.02, 5.70, 0.26, "radio = 45 mantiene las esferas dentro del plano.", 11.5, INK, SEM)
text(s, 6.44, 5.31, 5.70, 0.26, "Con radio 50, algunas quedarían fuera del borde.", 10.5, BODY, REG)
footer(s, "El valor del Inspector manda: si el script dice 50 y la escena dice 45, se usa 45.")
notes_code(s,
           "El script tiene tres campos. El campo enemigo se marca con "
           "[SerializeField] para que aparezca en el Inspector aunque sea privado.\n\n"
           "numeroEnemigos indica cuántas copias se crean. radio indica la distancia "
           "máxima desde el spawner.\n\n"
           "En la escena se usa radio = 45 para que las esferas queden dentro del "
           "plano de 100 × 100. El script trae 50 por defecto, pero el Inspector tiene "
           "la última palabra.",
           [("Assets/Scripts/escena4_hash_grid/S4_Spawner.cs",
             """[SerializeField] private GameObject enemigo;

public int numeroEnemigos = 50;
public int radio = 50;""")])

# 18 --------------------------------------------------------------- bucle spawner
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · SPAWNER", "EL BUCLE QUE CREA LOS ENEMIGOS",
       "Un for repite el mismo bloque 50 veces.")
code(s, "code_spawner_bucle.png", 0.62, 1.64, 5.95, 3.55)
text(s, 0.74, 5.28, 5.70, 0.26, "Start()", 9.5, ORANGE_TEXT, SEM)
text(s, 6.95, 1.72, 5.55, 0.28, "PASO A PASO", 9.5, ORANGE_TEXT, SEM)
steps(s, 6.95, 2.06, 5.45, [
    "Guarda la posición del spawner en spawn_pos.",
    "El for empieza en i = 0 y termina cuando i = 50.",
    "En cada vuelta se crea un enemigo.",
    "Al final, i vale 50 y el bucle se detiene.",
], size=12, gap=0.62)
card(s, 6.95, 4.72, 5.55, 0.92, BLUE)
text(s, 7.19, 4.84, 5.05, 0.26, "for (int i = 0; i < 50; i++)", role="body", color=INK)
text(s, 7.19, 5.14, 5.05, 0.26, "i toma los valores 0, 1, 2 ... 49. Son 50 vueltas.",
     10.5, BODY, REG)
footer(s, "El bucle va dentro de Start para que las copias se creen una sola vez.")
notes_code(s,
           "Start se ejecuta una vez, antes del primer Update. Primero se guarda la "
           "posición del spawner en spawn_pos.\n\n"
           "El for empieza en i = 0. La condición i < numeroEnemigos se revisa antes "
           "de cada vuelta. Con 50 enemigos, i toma los valores 0 a 49: son 50 "
           "vueltas. Cuando i llega a 50, el bucle termina.\n\n"
           "Dentro del bucle se calcula la posición y se crea la copia. Si el bucle "
           "estuviera en Update, se crearían 50 enemigos en cada fotograma.",
           [("Assets/Scripts/escena4_hash_grid/S4_Spawner.cs",
             """void Start()
{
    Vector3 spawn_pos = transform.position; //posicion del spawner

    // repetir para cada enemigo
    for (int i=0; i<numeroEnemigos; i++)
    {
        // randomizar la posicion del enemigo alrededor un radio en un plano
        float rnd_x = UnityEngine.Random.Range(-radio, radio);
        float rnd_z = UnityEngine.Random.Range(-radio, radio);

        // set posicion y rotacion de cada esfera
        Vector3 enemy_pos = new Vector3( spawn_pos.x + rnd_x, 0.5f, spawn_pos.z + rnd_z );
        Quaternion enemy_rotation = Quaternion.identity;

        // crea nueva instancia
        GameObject nuevoEnemigo = Instantiate(enemigo, enemy_pos, enemy_rotation);

        // set del nombre del enemigo
        nuevoEnemigo.name = "EnemigoClon_" + i;
    }
}""")])

# 19 --------------------------------------------------------------- random posicion
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · SPAWNER", "ELEGIR UNA POSICIÓN AL AZAR",
       "Random.Range(-radio, radio) produce valores positivos y negativos.")
code(s, "code_spawner_random.png", 0.62, 1.72, 5.75, 1.45)
text(s, 0.74, 3.25, 5.50, 0.26, "POSICIÓN DE CADA ESFERA", 9.5, ORANGE_TEXT, SEM)
fig(s, ROOT / "figuras" / "spawner_radio.png", 6.55, 1.64, 6.10, 3.05)
text(s, 6.67, 4.78, 5.85, 0.26, "Figura 3. Las esferas se reparten dentro del radio.", 10, MUTED, REG)
card(s, 0.62, 3.60, 5.75, 1.08, ORANGE)
text(s, 0.86, 3.72, 5.25, 0.26, "La altura se fija en 0.5.", 11.5, INK, SEM)
text(s, 0.86, 4.02, 5.25, 0.50,
     "Así el centro de la esfera queda a la altura del plano y no flota.",
     10.5, BODY, REG, line_spacing=1.0)
text(s, 0.62, 4.88, 5.75, 0.72,
     "El desplazamiento se suma a spawn_pos. Si se suma a (0, 0, 0), las esferas se acumulan alrededor del origen.",
     role="body", color=BODY, line_spacing=1.02)
footer(s, "Random.Range con enteros no incluye el límite superior. Con -45 y 45, el 45 no sale.")
notes_code(s,
           "Cada esfera recibe dos valores aleatorios: uno para X y otro para Z. "
           "Random.Range(-radio, radio) devuelve un valor entre -45 y 45, sin incluir "
           "el 45.\n\n"
           "El desplazamiento se suma a la posición del spawner. Por eso las esferas "
           "quedan alrededor del spawner, no alrededor del origen del mundo.\n\n"
           "La altura se fija en 0.5. La esfera mide 1 de diámetro, así que su centro "
           "queda a media unidad del piso y no flota.\n\n"
           "La rotación se deja en Quaternion.identity: sin giro inicial.",
           [("Assets/Scripts/escena4_hash_grid/S4_Spawner.cs",
             """float rnd_x = UnityEngine.Random.Range(-radio, radio);
float rnd_z = UnityEngine.Random.Range(-radio, radio);

Vector3 enemy_pos = new Vector3(
    spawn_pos.x + rnd_x, 0.5f, spawn_pos.z + rnd_z);""")])

# 20 --------------------------------------------------------------- bug random
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · SPAWNER", "EL ERROR DE RANDOM.RANGE",
       "Si el rango empieza en 0, las esferas se van a una sola esquina.")
text(s, 0.62, 1.70, 5.55, 0.26, "MAL: Random.Range(0, radio)", 9.5, PINK, SEM)
code(s, "code_random_malo.png", 0.62, 1.98, 5.55, 0.80, border=False)
text(s, 0.62, 3.08, 5.55, 0.26, "BIEN: Random.Range(-radio, radio)", 9.5, GREEN, SEM)
code(s, "code_random_bueno.png", 0.62, 3.36, 5.55, 0.80, border=False)
text(s, 0.62, 4.46, 5.55, 0.60,
     "El rango con 0 solo genera valores positivos. El rango con -radio genera los dos signos.",
     role="body", color=BODY, line_spacing=1.0)
shot(s, "spawn_bug_posiciones.png", 6.65, 1.66, 5.95, 3.30)
text(s, 6.77, 5.06, 5.70, 0.26, "Resultado: las esferas se acumulan en un solo lado.", 10, MUTED, REG)
card(s, 0.62, 5.18, 5.55, 0.82, PINK)
text(s, 0.86, 5.30, 5.05, 0.26, "El error no detiene el juego.", 11.5, INK, SEM)
text(s, 0.86, 5.59, 5.05, 0.26, "Solo reparte mal los enemigos. Míralo en la escena.", 10, BODY, REG)
footer(s, "Revisa el rango: debe empezar en -radio, no en 0.")
notes_code(s,
           "La primera versión usaba Random.Range(0, radio). Ese rango solo devuelve "
           "valores positivos, así que todas las esferas se colocan a la derecha y "
           "arriba del spawner.\n\n"
           "El error no produce una excepción. El juego corre, pero los enemigos se "
           "acumulan en una sola esquina. Por eso hay que mirar la escena y no solo la "
           "consola.\n\n"
           "La corrección es Random.Range(-radio, radio). Ahora el desplazamiento "
           "puede ser negativo o positivo en X y en Z.",
           [("Versión con error, S4_Spawner.cs",
             """float rnd_x = UnityEngine.Random.Range(0, radio);
float rnd_z = UnityEngine.Random.Range(0, radio);"""),
            ("Versión corregida, S4_Spawner.cs",
             """float rnd_x = UnityEngine.Random.Range(-radio, radio);
float rnd_z = UnityEngine.Random.Range(-radio, radio);""")])

# 21 --------------------------------------------------------------- instantiate
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · SPAWNER", "CREAR LA COPIA CON INSTANTIATE",
       "Instantiate recibe el molde, la posición y la rotación.")
code(s, "code_spawner_instantiate.png", 0.62, 1.72, 5.75, 1.65)
text(s, 0.74, 3.45, 5.50, 0.26, "CREAR Y RENOMBRAR", 9.5, ORANGE_TEXT, SEM)
card(s, 0.62, 3.78, 5.75, 1.22, BLUE)
text(s, 0.86, 3.90, 5.25, 0.26, "Instantiate(enemigo, enemy_pos, enemy_rotation)", 10.5, INK, SEM)
text(s, 0.86, 4.22, 5.25, 0.62,
     "Devuelve una copia nueva. El molde original sigue en la escena.",
     10.5, BODY, REG, line_spacing=1.0)
text(s, 0.62, 5.22, 5.75, 0.62,
     "La copia conserva los componentes del molde: collider, Rigidbody y script.",
     role="body", color=BODY, line_spacing=1.0)
text(s, 6.70, 1.72, 5.75, 0.28, "LOS TRES DATOS", 9.5, ORANGE_TEXT, SEM)
fields = [
    ("enemigo", "El molde que se copia. En la escena, Enemigo."),
    ("enemy_pos", "La posición calculada para esta copia."),
    ("enemy_rotation", "Quaternion.identity: sin rotación inicial."),
]
for i, (name, desc) in enumerate(fields):
    y = 2.10 + i * 0.82
    text(s, 6.70, y, 1.85, 0.26, name, 12, INK, SEM)
    text(s, 8.65, y - 0.01, 3.80, 0.60, desc, role="body", line_spacing=1.0)
card(s, 6.70, 4.70, 5.75, 0.92, GREEN)
text(s, 6.94, 4.82, 5.25, 0.26, "La copia se guarda en nuevoEnemigo.", 11.5, INK, SEM)
text(s, 6.94, 5.11, 5.25, 0.26, "Así se puede cambiar su nombre o sus componentes.", 10.5, BODY, REG)
footer(s, "Instantiate no borra el molde: devuelve una copia nueva en la escena.")
notes_code(s,
           "Instantiate recibe tres datos: el GameObject que se copia, la posición y "
           "la rotación. Devuelve la copia nueva.\n\n"
           "La copia se guarda en la variable nuevoEnemigo. Después se cambia su "
           "nombre a EnemigoClon_i. El nombre ayuda a encontrar cada copia en la "
           "jerarquía.\n\n"
           "Quaternion.identity significa sin rotación. La esfera no necesita un giro "
           "inicial para este ejercicio.",
           [("Assets/Scripts/escena4_hash_grid/S4_Spawner.cs",
             """Quaternion enemy_rotation = Quaternion.identity;

GameObject nuevoEnemigo = Instantiate(
    enemigo, enemy_pos, enemy_rotation);

nuevoEnemigo.name = "EnemigoClon_" + i;""")])

# 22 --------------------------------------------------------------- asignar ejecutar
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · SPAWNER", "ASIGNAR EL ENEMIGO Y EJECUTAR",
       "El campo Enemigo debe apuntar al objeto Enemigo de la escena.")
card(s, 0.62, 1.66, 4.30, 1.10, PINK)
text(s, 0.86, 1.78, 3.95, 0.30, "NullReferenceException", role="body", color=INK)
text(s, 0.86, 2.10, 3.95, 0.65,
     "The variable enemigo de S4_Spawner has not been assigned.",
     role="caption", color=BODY, line_spacing=1.0)
shot(s, "spawn_asignar.png", 0.62, 3.10, 4.10, 2.75)
text(s, 0.74, 5.88, 3.85, 0.26, "Selecciona Enemigo en la lista.", role="caption", color=MUTED)
shot(s, "spawn_resultado.png", 5.10, 1.66, 4.10, 2.85)
text(s, 5.22, 4.54, 3.85, 0.26, "Play: aparecen las 50 esferas.", 10, MUTED, REG)
text(s, 9.55, 1.72, 3.15, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 9.55, 2.06, 3.10, [
    "Selecciona Spawner.",
    "Arrastra Enemigo al campo.",
    "Presiona Play.",
    "Cuenta las copias.",
], size=11, gap=0.52)
card(s, 5.10, 5.02, 4.10, 0.92, PINK)
text(s, 5.34, 5.14, 3.65, 0.26, "Si el campo está vacío,", 10.5, INK, SEM)
text(s, 5.34, 5.43, 3.65, 0.26, "Instantiate lanza un error.", 10.5, BODY, REG)
footer(s, "El objeto Enemigo debe existir en la escena antes de presionar Play.")
notes(s,
      "El error de la captura dice que el campo enemigo no está asignado. Instantiate "
      "necesita un GameObject; si recibe null, detiene el Start con una excepción.\n\n"
      "Para asignarlo, selecciona el Spawner, busca el campo Enemigo en el Inspector "
      "y arrastra el objeto Enemigo desde la jerarquía.\n\n"
      "Al presionar Play, el script crea 50 copias. Las copias aparecen alrededor del "
      "spawner, dentro del radio de 45 unidades.")

# 23 --------------------------------------------------------------- jerarquia performance
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · SPAWNER", "REVISAR LA JERARQUÍA Y EL RENDIMIENTO",
       "Las 50 copias son objetos nuevos. Eso tiene un costo.")
shot(s, "spawn_jerarquia.png", 0.62, 1.64, 5.85, 3.55)
text(s, 0.74, 5.30, 5.60, 0.26, "EnemigoClon_0 ... EnemigoClon_49.", 10, MUTED, REG)
text(s, 6.70, 1.72, 5.80, 0.28, "QUÉ OBSERVAR", 9.5, ORANGE_TEXT, SEM)
bullets(s, 6.70, 2.08, 5.70, [
    "Cada copia es un GameObject independiente.",
    "La jerarquía crece con cada enemigo.",
    "50 esferas están bien para una demostración.",
    "Para miles, haría falta otra técnica.",
], size=12, gap=0.66)
card(s, 6.70, 4.92, 5.80, 0.92, BLUE)
text(s, 6.94, 5.04, 5.30, 0.26, "El bucle está en Start, no en Update.", 11.5, INK, SEM)
text(s, 6.94, 5.33, 5.30, 0.26, "Si estuviera en Update, crearías 50 enemigos por fotograma.", 10, BODY, REG)
footer(s, "La copia conserva los componentes del molde: collider, Rigidbody y script.")
notes(s,
      "Después de presionar Play, la jerarquía muestra EnemigoClon_0, "
      "EnemigoClon_1 y así hasta EnemigoClon_49.\n\n"
      "Cada copia es un GameObject independiente. Tiene los mismos componentes que "
      "el molde: Transform, SphereCollider, Rigidbody y el script del enemigo.\n\n"
      "Para una demostración, 50 esferas están bien. Para miles de enemigos, "
      "Instantiate en un bucle no es la mejor técnica: haría falta agrupar objetos, "
      "reciclar copias o usar un sistema de partículas.\n\n"
      "Lo importante es que el bucle esté en Start. En Update se crearían 50 copias "
      "en cada fotograma.")

# 24 --------------------------------------------------------------- cierre escenario
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · CIERRE", "COMPROBAR EL ESCENARIO",
       "Antes de seguir, revisa estos cuatro puntos.")
checks = [
    ("Plano", "Scale (10, 1, 10) y Position (-45, 0, -45).", ORANGE),
    ("Nombre", "El objeto se llama Plane.", BLUE),
    ("Spawner", "Position (-50, 0, -50) y script S4_Spawner.", GREEN),
    ("Enemigo", "El campo Enemigo apunta al objeto Enemigo.", PINK),
]
for i, (title, desc, color) in enumerate(checks):
    x = 0.62 + (i % 2) * 6.10
    y = 1.70 + (i // 2) * 1.75
    card(s, x, y, 5.90, 1.45, color)
    text(s, x + 0.26, y + 0.16, 5.40, 0.30, title, 17, INK, SEM)
    text(s, x + 0.40, y + 0.58, 5.25, 0.70, desc, role="body", line_spacing=1.0)
text(s, 0.62, 5.40, 12.05, 0.62,
     "Si los cuatro puntos están bien, el escenario está listo para el material y el sprite.",
     14, INK, SEM, line_spacing=1.0)
footer(s, "No hay una pantalla de victoria: la señal es que las esferas aparecen y se mueven.")
notes(s,
      "Lista de comprobación del escenario:\n\n"
      "1. El plano tiene Scale (10, 1, 10) y Position (-45, 0, -45).\n"
      "2. El objeto se sigue llamando Plane.\n"
      "3. El spawner está en (-50, 0, -50) y tiene el script S4_Spawner.\n"
      "4. El campo Enemigo apunta al objeto Enemigo.\n\n"
      "Si los cuatro puntos están bien, el escenario está listo. El siguiente bloque "
      "cambia el color del piso con un material.")

# 25 --------------------------------------------------------------- seccion 03
s = section_slide(prs, "03", "MATERIALES",
                  "Un material cambia el color y la superficie de un objeto.",
                  "MATERIAL · SHADER · COLOR BASE · TEXTURA", GREEN)
notes(s,
      "Bloque 3. Un material define cómo se ve la superficie de un objeto. Incluye "
      "el shader, el color base y las texturas.\n\n"
      "En este ejercicio se crea un material llamado Grass y se pinta de verde. "
      "Después se asigna al plano.")

# 26 --------------------------------------------------------------- que es material
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · MATERIALES", "¿QUÉ ES UN MATERIAL?",
       "Es la receta que dice cómo se ve una superficie.")
text(s, 0.62, 1.72, 5.35, 0.28, "LA RECETA", 9.5, ORANGE_TEXT, SEM)
cards = [
    ("SHADER", "El programa que calcula la luz.\nEn este caso, URP Lit.", ORANGE),
    ("COLOR BASE", "El color principal del material.\nEn este caso, verde.", GREEN),
    ("TEXTURA", "Una imagen que se pega encima.\nEl pasto no usa textura.", BLUE),
]
for i, (title, desc, color) in enumerate(cards):
    y = 2.10 + i * 1.12
    card(s, 0.62, y, 5.35, 1.02, color)
    text(s, 0.86, y + 0.12, 5.00, 0.24, title, 9.5, color, SEM)
    text(s, 0.86, y + 0.40, 5.00, 0.52, desc, role="body", line_spacing=1.0)
shot(s, "mat_grass_asset.png", 6.55, 1.66, 2.40, 1.50)
text(s, 6.67, 3.22, 2.15, 0.26, "Material Grass.", role="caption", color=MUTED)
shot(s, "mat_resultado.png", 9.20, 1.66, 3.45, 3.10)
text(s, 9.32, 4.80, 3.20, 0.26, "El plano con el material.", role="caption", color=MUTED)
text(s, 6.55, 5.12, 6.10, 0.80,
     "El material no cambia la forma del objeto. Cambia su apariencia.",
     role="body", color=INK, line_spacing=1.02)
footer(s, "Un mismo material se puede asignar a varios objetos. Eso ahorra trabajo y memoria.")
notes(s,
      "Un material es la receta que dice cómo se ve una superficie. Tiene tres partes "
      "principales: el shader, el color base y las texturas.\n\n"
      "El shader es el programa que calcula la luz. En este ejercicio se usa "
      "Universal Render Pipeline / Lit.\n\n"
      "El color base es el color principal. En este caso, verde. La textura es "
      "opcional: el pasto no usa una imagen, solo color.\n\n"
      "El material no cambia la forma del objeto. Solo cambia su apariencia.")

# 27 --------------------------------------------------------------- crear material
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · MATERIALES", "CREAR EL MATERIAL GRASS",
       "El material se guarda en la carpeta Materiales.")
shot(s, "mat_crear_menu.png", 0.62, 1.64, 3.75, 3.95)
text(s, 0.74, 5.68, 3.50, 0.26, "Create > Material.", 10, MUTED, REG)
shot(s, "mat_grass_asset.png", 4.70, 1.64, 2.55, 1.55)
text(s, 4.82, 3.28, 2.30, 0.26, "Renómbralo Grass.", 10, MUTED, REG)
text(s, 7.70, 1.72, 4.95, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 7.70, 2.06, 4.90, [
    "Clic derecho en Assets > Materiales.",
    "Elige Create > Material.",
    "Renómbralo Grass.",
    "Revisa que el shader sea URP Lit.",
], size=12, gap=0.62)
card(s, 7.70, 4.82, 4.90, 0.92, GREEN)
text(s, 7.94, 4.94, 4.40, 0.26, "El material se guarda como archivo .mat.", 11.5, INK, SEM)
text(s, 7.94, 5.23, 4.40, 0.26, "Puedes reutilizarlo en otros objetos.", 10.5, BODY, REG)
footer(s, "No confundas el material con el shader: el material usa un shader.")
notes(s,
      "Para crear el material, haz clic derecho en la carpeta Materiales y elige "
      "Create > Material. Renómbralo Grass.\n\n"
      "Unity crea un archivo .mat. Ese archivo se puede asignar a cualquier objeto "
      "con un Mesh Renderer.\n\n"
      "Revisa que el shader sea Universal Render Pipeline / Lit. Si el proyecto usa "
      "URP, es el shader correcto para superficies que reciben luz.")

# 28 --------------------------------------------------------------- color
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · MATERIALES", "CAMBIAR EL COLOR BASE",
       "El color base se elige en Surface Inputs, dentro del material.")
shot(s, "mat_surface.png", 0.62, 1.64, 5.10, 2.55)
text(s, 0.74, 4.26, 4.85, 0.26, "Surface Inputs > Base Map.", 10, MUTED, REG)
shot(s, "mat_color.png", 5.95, 1.64, 4.25, 3.40)
text(s, 6.07, 5.12, 4.00, 0.26, "Selector de color: R 20, G 197, B 19.", 10, MUTED, REG)
text(s, 10.50, 1.72, 2.15, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 10.50, 2.06, 2.15, [
    "Abre Grass.",
    "Busca Base Map.",
    "Haz clic en el color.",
    "Elige el verde.",
], size=10.5, gap=0.58)
card(s, 10.50, 4.60, 2.15, 1.10, ORANGE)
text(s, 10.74, 4.72, 1.70, 0.86, "El color se guarda en el material.",
     role="body", color=INK, line_spacing=1.0)
footer(s, "El color base también se llama albedo. Es el color con luz blanca.")
notes(s,
      "Abre el material Grass y busca la sección Surface Inputs. El campo Base Map "
      "tiene un color blanco por defecto.\n\n"
      "Haz clic en el cuadro de color y elige un verde. En la captura, el selector "
      "muestra R 20, G 197, B 19.\n\n"
      "El color se guarda dentro del material. No se guarda en el plano. Si asignas "
      "el mismo material a otro objeto, también se verá verde.")

# 29 --------------------------------------------------------------- asignar material
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · MATERIALES", "ASIGNAR EL MATERIAL AL PLANO",
       "El material se arrastra al espacio del Mesh Renderer.")
shot(s, "mat_slot.png", 0.62, 1.64, 3.45, 1.85)
text(s, 0.74, 3.56, 3.20, 0.26, "Materials > Element 0.", 10, MUTED, REG)
shot(s, "mat_select.png", 4.30, 1.64, 3.85, 1.95)
text(s, 4.42, 3.66, 3.60, 0.26, "Selecciona Grass.", 10, MUTED, REG)
shot(s, "mat_resultado.png", 8.40, 1.64, 4.25, 3.55)
text(s, 8.52, 5.26, 4.00, 0.26, "Resultado en la escena.", 10, MUTED, REG)
text(s, 0.62, 3.95, 7.50, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 0.62, 4.25, 7.30, [
    "Selecciona Plane.",
    "Abre Mesh Renderer > Materials.",
    "Arrastra Grass a Element 0 o usa el círculo.",
    "Comprueba el color en la escena.",
], size=12, gap=0.40)
footer(s, "Arrastra Grass al Mesh Renderer, no al Collider.")
notes(s,
      "Selecciona el plano y abre el componente Mesh Renderer. En la lista Materials, "
      "Element 0 tiene un espacio para un material.\n\n"
      "Arrastra el material Grass desde la carpeta Materiales hasta ese espacio. "
      "También puedes hacer clic en el círculo y elegir Grass en la lista.\n\n"
      "El material cambia el color del plano en la escena y en el juego. El collider "
      "no cambia: el cubo sigue caminando sobre el mismo plano.")

# 30 --------------------------------------------------------------- cierre materiales
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · CIERRE", "COMPROBAR EL MATERIAL",
       "El piso debe verse verde y conservar su collider.")
shot(s, "mat_resultado.png", 0.62, 1.64, 6.05, 4.05)
text(s, 0.74, 5.80, 5.80, 0.26, "Plano con el material Grass.", 10, MUTED, REG)
checks = [
    ("Color", "El plano se ve verde.", GREEN),
    ("Shader", "Universal Render Pipeline / Lit.", ORANGE),
    ("Collider", "El cubo sigue tocando el suelo.", BLUE),
]
for i, (title, desc, color) in enumerate(checks):
    y = 1.72 + i * 1.18
    card(s, 7.00, y, 5.50, 0.98, color)
    text(s, 7.24, y + 0.14, 5.00, 0.34, title, role="card_title_sm", color=INK)
    text(s, 7.24, y + 0.50, 5.00, 0.30, desc, role="body")
text(s, 7.00, 5.38, 5.50, 0.62,
     "Si el plano se ve gris, el material no está asignado en Element 0.",
     11.5, BODY, REG, line_spacing=1.0)
footer(s, "El material no cambia la física. Solo cambia la apariencia.")
notes(s,
      "Comprueba tres cosas: el plano se ve verde, el shader es Universal Render "
      "Pipeline / Lit y el cubo sigue tocando el suelo.\n\n"
      "Si el plano se ve gris, el material no está asignado. Revisa Mesh Renderer > "
      "Materials > Element 0.\n\n"
      "El material no cambia el collider ni la física. El plano sigue siendo el mismo "
      "objeto con el mismo Mesh Collider.")

# 31 --------------------------------------------------------------- seccion 04
s = section_slide(prs, "04", "SPRITE 2D",
                  "Una imagen plana da vida al personaje dentro de un mundo 3D.",
                  "SPRITE · HOJA · ANIMATOR · SOMBRA · FLIP X", PINK)
notes(s,
      "Bloque 4. Un sprite es una imagen 2D que se dibuja en la escena. Se usa para "
      "personajes, enemigos, objetos y efectos.\n\n"
      "En este ejercicio, el cubo conserva su collider y su movimiento, pero se "
      "dibuja con un sprite de Velma. El resultado se parece al efecto de Paper Mario: "
      "un mundo 3D con un personaje 2D.")

# 32 --------------------------------------------------------------- que es sprite
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · SPRITE", "¿QUÉ ES UN SPRITE?",
       "Es una imagen 2D que se coloca en el mundo.")
text(s, 0.62, 1.72, 5.45, 0.28, "LA IDEA", 9.5, ORANGE_TEXT, SEM)
text(s, 0.62, 2.06, 5.40, 0.64, "Un mundo 3D con un personaje 2D.", 21, INK, SEM,
     line_spacing=1.0)
bullets(s, 0.62, 2.90, 5.35, [
    "En esta escena, la cámara no gira y el sprite se ve de frente.",
    "El cubo conserva el collider y el movimiento.",
    "El sprite es solo la parte visual.",
], size=12, gap=0.70)
card(s, 0.62, 5.16, 5.35, 0.82, PINK)
text(s, 0.86, 5.28, 4.90, 0.26, "Efecto Paper Mario.", 12, INK, SEM)
text(s, 0.86, 5.57, 4.90, 0.26, "Personaje plano, escenario con volumen.", 10.5, BODY, REG)
shot(s, "sprite_juego.png", 6.55, 1.64, 5.85, 4.00)
text(s, 6.67, 5.72, 5.60, 0.26, "El sprite reemplaza la vista del cubo, no su física.", 10, MUTED, REG)
footer(s, "El sprite no es un modelo 3D: es una imagen plana con transparencia.")
notes(s,
      "Un sprite es una imagen 2D que se dibuja en la escena. Se usa para personajes, "
      "enemigos, objetos y efectos.\n\n"
      "En este ejercicio, el cubo conserva su collider, su Rigidbody y su script de "
      "movimiento. El sprite es solo la parte visual. El jugador sigue controlando el "
      "cubo, pero ve a Velma.\n\n"
      "El efecto se parece a Paper Mario: un personaje plano dentro de un mundo con "
      "volumen. La cámara está fija, así que el sprite se ve de frente.")

# 33 --------------------------------------------------------------- instalar paquete
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · SPRITE", "INSTALAR EL PAQUETE 2D SPRITE",
       "El paquete agrega el editor de sprites y el Sprite Renderer.")
shot(s, "sprite_pkg_menu.png", 0.62, 1.64, 3.60, 3.60)
text(s, 0.74, 5.34, 3.35, 0.30, "Window > Package Manager.", role="caption", color=MUTED)
shot(s, "sprite_pkg_2d.png", 4.55, 1.64, 4.85, 3.10)
text(s, 4.67, 4.84, 4.60, 0.26, "Unity Registry > 2D Sprite > Install.", 10, MUTED, REG)
text(s, 9.75, 1.72, 2.90, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 9.75, 2.06, 2.85, [
    "Abre Package Manager.",
    "Elige Unity Registry.",
    "Busca 2D Sprite.",
    "Presiona Install.",
], size=10.5, gap=0.54)
card(s, 9.75, 4.68, 2.90, 0.90, BLUE)
text(s, 9.99, 4.80, 2.40, 0.48, "Espera a que Unity termine.", 10.5, INK, SEM, line_spacing=1.0)
footer(s, "El paquete 2D Sprite es oficial de Unity. No agrega código al juego.")
notes(s,
      "Abre Window > Package Management > Package Manager. En la lista de la "
      "izquierda, elige Unity Registry.\n\n"
      "Busca 2D Sprite y presiona Install. El paquete agrega el editor de sprites y "
      "las herramientas para cortar hojas de cuadros.\n\n"
      "Espera a que Unity termine de importar antes de continuar. Si el paquete ya "
      "está instalado, el botón dice Installed y no necesitas hacer nada.")

# 34 --------------------------------------------------------------- convertir imagen
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · SPRITE", "CONVERTIR LA IMAGEN EN SPRITE",
       "La textura debe cambiar de Texture Type a Sprite.")
shot(s, "sprite_texture_type.png", 0.62, 1.64, 3.30, 4.10)
text(s, 0.74, 5.82, 3.05, 0.30, "Texture Type: Sprite (2D and UI).", role="caption", color=MUTED)
shot(s, "sprite_mode_multiple.png", 4.20, 1.64, 3.70, 3.20)
text(s, 4.32, 4.92, 3.45, 0.26, "Sprite Mode: Multiple.", 10, MUTED, REG)
text(s, 8.35, 1.72, 4.30, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 8.35, 2.06, 4.25, [
    "Selecciona la imagen en Assets.",
    "Cambia Texture Type a Sprite (2D and UI).",
    "Cambia Sprite Mode a Multiple.",
    "Presiona Apply.",
], size=12, gap=0.62)
card(s, 8.35, 4.72, 4.30, 0.98, PINK)
text(s, 8.59, 4.84, 3.85, 0.26, "Multiple: la hoja tiene varios cuadros.", 10.5, INK, SEM)
text(s, 8.59, 5.14, 3.85, 0.26, "Single: la imagen es un solo sprite.", 10, BODY, REG)
footer(s, "La imagen original se llama velma_sprite_walk_2.png.")
notes(s,
      "Selecciona la imagen velma_sprite_walk_2.png en la carpeta Images. En el "
      "Inspector, cambia Texture Type a Sprite (2D and UI).\n\n"
      "Cambia Sprite Mode a Multiple, porque la imagen contiene varios cuadros de "
      "animación. Si fuera una sola imagen, se usaría Single.\n\n"
      "Presiona Apply. Unity vuelve a importar la imagen como sprite y habilita el "
      "botón Open Sprite Editor.")

# 35 --------------------------------------------------------------- cortar hoja
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · SPRITE", "CORTAR LA HOJA EN CUADROS",
       "El Sprite Editor divide la imagen en siete cuadros de 48 × 75.")
shot(s, "sprite_editor.png", 0.62, 1.64, 5.40, 2.45)
text(s, 0.74, 4.17, 5.15, 0.26, "Sprite Editor > Slice > Grid By Cell Size.", 10, MUTED, REG)
shot(s, "sprite_slice.png", 6.25, 1.64, 5.10, 2.35)
text(s, 6.37, 4.06, 4.85, 0.26, "Cuadro 0: 48 × 75, pivote Center.", 10, MUTED, REG)
text(s, 0.62, 4.55, 12.00, 0.28, "QUÉ HACER", 9.5, ORANGE_TEXT, SEM)
steps(s, 0.62, 4.89, 11.85, [
    "Abre Sprite Editor y elige Slice > Grid By Cell Size.",
    "Escribe 48 en X, 75 en Y y elige Pivot Center.",
    "Presiona Slice y después Apply para guardar los siete cuadros.",
], size=11.5, gap=0.42)
footer(s, "El Animator reproduce los siete cuadros en bucle a 12 FPS.")
notes(s,
      "Abre el Sprite Editor con el botón Open Sprite Editor. Elige Slice > Grid By "
      "Cell Size.\n\n"
      "Escribe 48 en X y 75 en Y, y elige Pivot Center. La hoja tiene siete cuadros "
      "de ese tamaño. Presiona Slice y después Apply.\n\n"
      "El Sprite Editor muestra cada cuadro con su nombre: velma_sprite_walk_2_0, "
      "velma_sprite_walk_2_1 y así hasta el 6.\n\n"
      "El Animator reproduce los siete cuadros en bucle a 12 FPS. El clip dura 0.58 "
      "segundos aproximadamente.")

# 36 --------------------------------------------------------------- crear objeto sprite
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · SPRITE", "CREAR EL OBJETO DEL SPRITE",
       "El sprite se agrega como hijo del Cube.")
shot(s, "sprite_objeto.png", 0.62, 1.64, 7.00, 3.58)
text(s, 0.74, 5.32, 6.75, 0.26, "El sprite es hijo de Cube. En la captura conserva el nombre del asset.", 10, MUTED, REG)
text(s, 7.90, 1.72, 4.75, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 7.90, 2.06, 4.70, [
    "Crea un objeto hijo del Cube y llámalo velma_sprite_walk.",
    "Agrega un Sprite Renderer.",
    "Asigna el sprite velma_sprite_walk_2_0.",
    "Agrega un Animator y el controlador.",
], size=11.5, gap=0.62)
card(s, 7.90, 4.90, 4.75, 0.92, PINK)
text(s, 8.14, 5.02, 4.25, 0.26, "Renómbralo velma_sprite_walk.", 11.5, INK, SEM)
text(s, 8.14, 5.31, 4.25, 0.26, "Así GameObject.Find lo encuentra desde el código.", 10, BODY, REG)
footer(s, "El cubo puede ocultar su Mesh Renderer para que no se vea la caja.")
notes(s,
      "Crea un objeto hijo del Cube y renómbralo velma_sprite_walk. En la captura, "
      "el objeto todavía conserva el nombre del sprite (velma_sprite_walk_2_0). "
      "Renómbralo antes de probar el código.\n\n"
      "Agrega un Sprite Renderer y asigna el primer cuadro del sprite. Después agrega "
      "un Animator y asigna el controlador velma_sprite_walk_2_0. Ese controlador "
      "reproduce el clip VelmaWalking.\n\n"
      "Al ser hijo del Cube, el sprite hereda la posición y la rotación del cubo. "
      "Cuando el cubo se mueve, el sprite se mueve con él.\n\n"
      "Si quieres que no se vea la caja, desactiva el Mesh Renderer del Cube. El "
      "collider y el Rigidbody deben seguir activos.")

# 37 --------------------------------------------------------------- escala sprite
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · SPRITE", "AJUSTAR TAMAÑO Y POSICIÓN",
       "El sprite debe cubrir el cubo y quedar apoyado en el piso.")
shot(s, "sprite_escala.png", 0.62, 1.64, 7.10, 3.55)
text(s, 0.74, 5.30, 6.85, 0.26, "El sprite se ve más grande que el cubo.", 10, MUTED, REG)
table(s, 7.95, 1.70, 4.65, 2.15, [
    ["Campo", "Valor"],
    ["Position", "(0, 0.348, 0)"],
    ["Scale", "(2.47, 2.47, 2.47)"],
    ["Animator", "VelmaWalking"],
], [1.55, 3.00], font_size=11.5, header_size=11, row_h=0.48)
card(s, 7.95, 4.10, 4.65, 0.92, ORANGE)
text(s, 8.19, 4.22, 4.15, 0.26, "El sprite no usa el tamaño del cubo.", 11, INK, SEM)
text(s, 8.19, 4.51, 4.15, 0.26, "Se ajusta con su propio Transform.", 10, BODY, REG)
text(s, 7.95, 5.20, 4.65, 0.72,
     "La altura 0.348 coloca los pies del sprite cerca del piso.",
     11, BODY, REG, line_spacing=1.0)
footer(s, "El sprite se puede mover un poco arriba o abajo para que los pies toquen el suelo.")
notes(s,
      "El objeto del sprite tiene su propio Transform. La posición (0, 0.348, 0) es "
      "local, respecto al cubo. La escala 2.47 hace que el sprite cubra la caja.\n\n"
      "La altura 0.348 coloca los pies del sprite cerca del piso. Si el sprite flota "
      "o se hunde, ajusta la Y.\n\n"
      "El Animator reproduce el clip VelmaWalking. El sprite se ve en el juego con la "
      "animación de caminata.")

# 38 --------------------------------------------------------------- resultado sprite
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · SPRITE", "EL RESULTADO EN EL JUEGO",
       "El personaje ya se ve como un sprite 2D.")
shot(s, "sprite_juego.png", 0.62, 1.64, 7.20, 4.15)
text(s, 0.74, 5.92, 6.95, 0.26, "Vista del juego con el sprite y el plano verde.", 10, MUTED, REG)
text(s, 8.05, 1.72, 4.65, 0.28, "QUÉ CAMBIÓ", 9.5, ORANGE_TEXT, SEM)
bullets(s, 8.05, 2.08, 4.55, [
    "El cubo conserva su collider y su movimiento.",
    "El sprite es hijo del cubo y lo sigue.",
    "La animación se reproduce en bucle.",
    "La cámara sigue funcionando.",
], size=11.5, gap=0.68)
card(s, 8.05, 5.02, 4.65, 0.92, GREEN)
text(s, 8.29, 5.14, 4.15, 0.26, "El cubo puede quedar oculto.", 11.5, INK, SEM)
text(s, 8.29, 5.43, 4.15, 0.26, "El sprite es la parte visible.", 10, BODY, REG)
footer(s, "El efecto Paper Mario funciona porque la cámara mantiene un ángulo fijo.")
notes(s,
      "En el juego se ve el sprite de Velma sobre el plano verde. El cubo sigue "
      "existiendo, pero su Mesh Renderer puede estar desactivado.\n\n"
      "El sprite es hijo del cubo, así que se mueve con él. El collider y el "
      "Rigidbody siguen en el cubo. La cámara sigue al cubo.\n\n"
      "La animación de caminata se reproduce en bucle. El sprite no cambia la física "
      "ni el movimiento.")

# 39 --------------------------------------------------------------- sombras cast
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · SOMBRA", "ACTIVAR LAS SOMBRAS",
       "El Sprite Renderer debe proyectar y recibir sombra.")
shot(s, "sombra_cast.png", 0.62, 1.64, 4.20, 3.30)
text(s, 0.74, 5.02, 3.95, 0.26, "Cast Shadows: On.", 10, MUTED, REG)
shot(s, "sombra_receive.png", 4.95, 1.64, 3.65, 1.55)
text(s, 5.07, 3.28, 3.40, 0.26, "Receive Shadows: activado.", 10, MUTED, REG)
text(s, 8.90, 1.72, 3.80, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 8.90, 2.06, 3.75, [
    "Selecciona el sprite.",
    "Abre Sprite Renderer.",
    "Activa Cast Shadows.",
    "Activa Receive Shadows.",
], size=11, gap=0.56)
card(s, 8.90, 4.66, 3.80, 0.92, ORANGE)
text(s, 9.14, 4.78, 3.30, 0.26, "La luz debe existir.", 11.5, INK, SEM)
text(s, 9.14, 5.07, 3.30, 0.26, "La Directional Light ya está en la escena.", 10, BODY, REG)
footer(s, "Si no hay luz direccional, el sprite no proyecta una sombra visible.")
notes(s,
      "Selecciona el objeto del sprite y abre el Sprite Renderer. Activa Cast Shadows "
      "para que el sprite proyecte sombra.\n\n"
      "Activa Receive Shadows para que el sprite también reciba la sombra de otros "
      "objetos.\n\n"
      "La escena ya tiene una Directional Light. Si no hay luz, el sprite no proyecta "
      "una sombra visible. Revisa que la luz esté activa y que su intensidad no sea "
      "cero.")

# 40 --------------------------------------------------------------- material sprite
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · SOMBRA", "CREAR EL MATERIAL DEL SPRITE",
       "El material Lit permite que el sprite reciba luz y proyecte sombra.")
shot(s, "sombra_material_default.png", 0.62, 1.64, 3.05, 1.45)
text(s, 0.74, 3.12, 2.90, 0.30, "Sprite-Unlit-Default.", role="caption", color=MUTED)
shot(s, "sombra_crear_material.png", 3.85, 1.64, 3.05, 1.45)
text(s, 3.97, 3.12, 2.90, 0.30, "Create > Material.", role="caption", color=MUTED)
shot(s, "sombra_materiales.png", 0.62, 3.50, 3.05, 1.45)
text(s, 0.74, 4.98, 2.90, 0.40, "Grass y SpriteMaterial.", role="caption", color=MUTED)
shot(s, "sombra_shader.png", 3.85, 3.50, 3.05, 1.45)
text(s, 3.97, 4.98, 2.90, 0.40, "Universal Render Pipeline / Lit.", role="caption", color=MUTED)
text(s, 7.35, 1.72, 5.30, 0.28, "PASOS", 9.5, ORANGE_TEXT, SEM)
steps(s, 7.35, 2.06, 5.30, [
    "Crea SpriteMaterial en la carpeta Materiales.",
    "Cambia el shader a Universal Render Pipeline / Lit.",
    "Asigna el material al Sprite Renderer.",
], size=11, gap=0.70)
card(s, 7.35, 4.40, 5.30, 1.10, GREEN)
text(s, 7.59, 4.52, 4.85, 0.26, "El material debe ser Lit.", role="body", color=INK)
text(s, 7.59, 4.84, 4.85, 0.55,
     "Sprite-Unlit-Default no recibe luz ni proyecta sombra.",
     role="note", color=BODY, line_spacing=1.0)
footer(s, "El material Sprite-Unlit-Default no recibe luz. Por eso se cambia a Lit.")
notes(s,
      "El Sprite Renderer usa un material llamado Sprite-Unlit-Default. Ese material "
      "no recibe luz, así que el sprite se ve plano y no proyecta una sombra "
      "convincente.\n\n"
      "Crea un material nuevo en la carpeta Materiales y llámalo SpriteMaterial. "
      "Cambia su shader a Universal Render Pipeline / Lit.\n\n"
      "Asigna SpriteMaterial al Sprite Renderer del sprite. Ahora el sprite recibe la "
      "luz de la escena y puede proyectar sombra.")

# 41 --------------------------------------------------------------- alpha clip
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · SOMBRA", "RECORTAR LA TRANSPARENCIA",
       "Alpha Clipping descarta los píxeles transparentes del sprite.")
shot(s, "sombra_lit.png", 0.62, 1.64, 4.65, 1.95)
text(s, 0.74, 3.64, 4.40, 0.26, "El sprite con el material Lit.", 10, MUTED, REG)
shot(s, "sombra_alpha.png", 5.40, 1.64, 4.35, 1.70)
text(s, 5.52, 3.40, 4.10, 0.26, "Alpha Clipping activado.", 10, MUTED, REG)
shot(s, "sombra_render_face.png", 9.95, 1.64, 2.80, 2.55)
text(s, 10.07, 4.24, 2.55, 0.30, "Render Face: Both.", role="caption", color=MUTED)
text(s, 0.62, 4.50, 12.05, 0.28, "POR QUÉ", 9.5, ORANGE_TEXT, SEM)
bullets(s, 0.62, 4.84, 12.00, [
    "Alpha Clipping corta los píxeles transparentes.",
    "Render Face Both muestra el sprite por los dos lados.",
    "Receive Shadows sigue activo en el material.",
], size=12, gap=0.40)
footer(s, "El umbral 0.5 decide qué píxeles se conservan y cuáles se descartan.")
notes(s,
      "El sprite tiene píxeles transparentes alrededor del personaje. Si el material "
      "es opaco, esos píxeles se ven como un borde blanco o negro.\n\n"
      "Activa Alpha Clipping en el material. El umbral 0.5 decide qué píxeles se "
      "conservan. Los píxeles con alfa menor a 0.5 se descartan.\n\n"
      "Cambia Render Face a Both. El sprite es una superficie plana y la cámara "
      "puede verlo desde los dos lados. También sirve para que la sombra se calcule "
      "mejor.\n\n"
      "Deja Receive Shadows activo en el material.")

# 42 --------------------------------------------------------------- sombra resultado
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · SOMBRA", "LA SOMBRA FINAL",
       "El sprite proyecta una sombra sobre el plano verde.")
shot(s, "sombra_resultado_3x.png", 0.62, 1.64, 4.60, 3.55)
text(s, 0.74, 5.30, 4.35, 0.26, "Sombra del sprite sobre el pasto.", 10, MUTED, REG)
text(s, 5.65, 1.72, 7.00, 0.28, "SI NO VES LA SOMBRA", 9.5, ORANGE_TEXT, SEM)
bullets(s, 5.65, 2.08, 6.90, [
    "Revisa que Cast Shadows esté en On.",
    "Revisa que el material sea URP Lit y tenga Alpha Clipping.",
    "Revisa que la Directional Light esté activa.",
    "Revisa que el plano reciba sombras.",
], size=12, gap=0.66)
card(s, 5.65, 4.96, 6.90, 0.92, GREEN)
text(s, 5.89, 5.08, 6.40, 0.26, "La sombra también se puede desactivar por rendimiento.", 11, INK, SEM)
text(s, 5.89, 5.37, 6.40, 0.26, "En un juego con muchos sprites, conviene medir el costo.", 10, BODY, REG)
footer(s, "La sombra ayuda a que el personaje se sienta apoyado en el piso.")
notes(s,
      "El sprite ya proyecta una sombra sobre el plano verde. La sombra se ve como "
      "una mancha oscura debajo del personaje.\n\n"
      "Si no ves la sombra, revisa cuatro cosas: Cast Shadows en On, material URP Lit "
      "con Alpha Clipping, Directional Light activa y plano que reciba sombras.\n\n"
      "La sombra ayuda a que el personaje se sienta apoyado en el piso. Sin sombra, el "
      "sprite parece flotar.\n\n"
      "En un juego con muchos sprites, la sombra tiene un costo. Se puede desactivar "
      "en objetos lejanos o en versiones de bajo rendimiento.")

# 43 --------------------------------------------------------------- flip manual
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · VOLTEO", "VOLTEAR EL SPRITE CON FLIP X",
       "La casilla Flip X refleja el sprite sin cambiar el objeto.")
shot(s, "flip_off.png", 0.62, 1.64, 5.85, 2.55)
text(s, 0.74, 4.28, 5.60, 0.26, "Flip X desactivado: mira a la derecha.", 10, MUTED, REG)
shot(s, "flip_on.png", 6.85, 1.64, 5.85, 2.55)
text(s, 6.97, 4.28, 5.60, 0.26, "Flip X activado: mira a la izquierda.", 10, MUTED, REG)
card(s, 0.62, 4.86, 5.85, 0.92, ORANGE)
text(s, 0.86, 4.98, 5.35, 0.26, "Es un espejo, no una rotación.", 11.5, INK, SEM)
text(s, 0.86, 5.27, 5.35, 0.26, "El collider y la posición no cambian.", 10.5, BODY, REG)
card(s, 6.85, 4.86, 5.85, 0.92, BLUE)
text(s, 7.09, 4.98, 5.35, 0.26, "El sprite sigue siendo el mismo.", 11.5, INK, SEM)
text(s, 7.09, 5.27, 5.35, 0.26, "Solo se dibuja al revés.", 10.5, BODY, REG)
footer(s, "Flip X se puede probar a mano en el Inspector antes de escribir código.")
notes(s,
      "La casilla Flip X del Sprite Renderer refleja el sprite en el eje X. Si está "
      "desactivada, el personaje mira a la derecha. Si está activada, mira a la "
      "izquierda.\n\n"
      "No es una rotación. El objeto no gira y el collider no cambia. Solo cambia la "
      "forma en que se dibuja el sprite.\n\n"
      "Prueba la casilla a mano en el Inspector antes de escribir el código. Así "
      "compruebas que el sprite se ve bien en las dos direcciones.")

# 44 --------------------------------------------------------------- code start
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · VOLTEO", "CÓDIGO: ENCONTRAR EL SPRITERENDERER",
       "El script del cubo guarda una referencia al sprite desde Start.")
code(s, "code_sprite_start.png", 0.62, 1.64, 5.95, 2.95)
text(s, 0.74, 4.72, 5.70, 0.26, "START DEL CUBO", 9.5, ORANGE_TEXT, SEM)
shot(s, "flip_start.png", 6.90, 1.64, 5.80, 2.55)
text(s, 7.02, 4.28, 5.55, 0.26, "GameObject.Find busca el objeto por su nombre.", 10, MUTED, REG)
bullets(s, 0.62, 5.10, 5.95, [
    "Find se ejecuta una sola vez, en Start.",
    "El nombre debe ser exacto.",
], size=11.5, gap=0.42)
card(s, 6.90, 4.76, 5.80, 0.92, ORANGE)
text(s, 7.14, 4.88, 5.30, 0.26, "Si el nombre cambia, sprite queda null.", 11, INK, SEM)
text(s, 7.14, 5.17, 5.30, 0.26, "Después, sprite.flipX lanza un error.", 10, BODY, REG)
footer(s, "GameObject.Find es lento. Se usa en Start, no en Update.")
notes_code(s,
           "El script del cubo necesita una referencia al SpriteRenderer. En Start, "
           "busca el objeto velma_sprite_walk con GameObject.Find y obtiene su "
           "componente SpriteRenderer.\n\n"
           "La búsqueda se hace una sola vez. GameObject.Find recorre la jerarquía y "
           "es lenta; no debe usarse en Update.\n\n"
           "Si el nombre del objeto no coincide, goSprite queda null y "
           "GetComponent lanza una excepción. El nombre debe ser exacto.",
           [("Assets/Scripts/escena4_hash_grid/S4_CubeMove.cs",
             """private SpriteRenderer sprite = null;

void Start()
{
    rb = GetComponent<Rigidbody>();
    GameObject goSprite = GameObject.Find("velma_sprite_walk");
    sprite = goSprite.GetComponent<SpriteRenderer>();
}""")])

# 45 --------------------------------------------------------------- code flip
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · VOLTEO", "CÓDIGO: VOLTEAR AL CAMINAR",
       "Las flechas izquierda y derecha cambian flipX.")
code(s, "code_sprite_flip.png", 0.62, 1.64, 5.20, 3.85)
text(s, 0.74, 5.62, 4.95, 0.26, "CÓDIGO", 9.5, ORANGE_TEXT, SEM)
text(s, 6.10, 1.72, 6.55, 0.28, "DENTRO DE UPDATE", 9.5, ORANGE_TEXT, SEM)
text(s, 6.10, 2.06, 6.55, 0.62,
     "El bloque lee el teclado y cambia el sprite.",
     role="body", color=INK, line_spacing=1.0)
text(s, 6.10, 2.74, 6.55, 0.62,
     "El movimiento y el sprite cambian en el mismo bloque.",
     role="body", color=INK, line_spacing=1.0)
card(s, 6.10, 3.60, 6.55, 0.95, GREEN)
text(s, 6.34, 3.72, 6.05, 0.30, "Derecha: flipX = false.", role="body", color=INK)
text(s, 6.34, 4.06, 6.05, 0.30, "Izquierda: flipX = true.", role="body", color=INK)
footer(s, "La animación sigue corriendo: flipX solo cambia la dirección del dibujo.")
notes_code(s,
           "Dentro de Update se lee el teclado. Si se presiona D o la flecha derecha, "
           "movement.x se pone en 1 y flipX en false. Si se presiona A o la flecha "
           "izquierda, movement.x se pone en -1 y flipX en true.\n\n"
           "El cambio de flipX ocurre en el mismo bloque que el movimiento. Así el "
           "personaje mira hacia donde camina.\n\n"
           "La animación sigue corriendo. Flip X solo cambia la dirección del dibujo. "
           "El collider y la posición no cambian.",
           [("Assets/Scripts/escena4_hash_grid/S4_CubeMove.cs",
             """if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed) {
    movement.x = 1f;
    sprite.flipX = false;
}
if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed) {
    movement.x = -1f;
    sprite.flipX = true;
}""")])

# 46 --------------------------------------------------------------- prueba final
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · CIERRE", "PRUEBA FINAL",
       "El personaje camina, se voltea y proyecta sombra.")
shot(s, "sombra_resultado_3x.png", 0.62, 1.64, 4.70, 3.70)
text(s, 0.74, 5.44, 4.45, 0.26, "Sprite con sombra sobre el pasto.", 10, MUTED, REG)
checks = [
    ("Cámara", "Sigue al cubo sin saltos.", ORANGE),
    ("Plano", "Se ve verde y el cubo no se cae.", GREEN),
    ("Spawner", "Crea 50 esferas dentro del plano.", BLUE),
    ("Sprite", "Camina, se voltea y proyecta sombra.", PINK),
]
for i, (title, desc, color) in enumerate(checks):
    x = 5.75 + (i % 2) * 3.55
    y = 1.70 + (i // 2) * 1.35
    card(s, x, y, 3.40, 1.15, color)
    text(s, x + 0.22, y + 0.14, 3.00, 0.34, title, 13.5, INK, SEM)
    text(s, x + 0.22, y + 0.50, 3.00, 0.55, desc, role="body", line_spacing=1.0)
text(s, 5.75, 4.62, 6.95, 0.62,
     "Si una parte falla, revisa primero el Inspector y la consola de Unity.",
     11.5, BODY, REG, line_spacing=1.0)
footer(s, "La meta es una escena jugable, no una colección de scripts sueltos.")
notes(s,
      "Prueba final. Revisa cuatro cosas:\n\n"
      "1. La cámara sigue al cubo sin saltos.\n"
      "2. El plano se ve verde y el cubo no se cae.\n"
      "3. El spawner crea 50 esferas dentro del plano.\n"
      "4. El sprite camina, se voltea con las flechas y proyecta sombra.\n\n"
      "Si una parte falla, revisa primero el Inspector y la consola de Unity. La "
      "mayoría de los errores proviene de un campo vacío o de un nombre que no coincide.")

# 47 --------------------------------------------------------------- resumen
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 04 · CIERRE", "LO QUE APRENDISTE",
       "Cuatro técnicas convierten una escena básica en un juego con más vida.")
summary = [
    ("01", "CÁMARA", "Offset, LateUpdate y Lerp para seguir al cubo.", ORANGE),
    ("02", "ESCENARIO", "Plano de 100 × 100 y spawner de 50 esferas.", BLUE),
    ("03", "MATERIAL", "Shader, color base y asignación al plano.", GREEN),
    ("04", "SPRITE", "Hoja de cuadros, sombra y flipX.", PINK),
]
for i, (num, title, desc, color) in enumerate(summary):
    x = 0.62 if i % 2 == 0 else 6.44
    y = 1.62 if i < 2 else 3.14
    card(s, x, y, 5.55, 1.34, color)
    text(s, x + 0.26, y + 0.16, 0.40, 0.22, num, role="card_number", color=color)
    text(s, x + 0.76, y + 0.13, 4.50, 0.34, title, 18, INK, SEM)
    text(s, x + 0.89, y + 0.56, 4.45, 0.58, desc, role="body", line_spacing=1.0)
card(s, 0.62, 4.75, 11.37, 0.95, ORANGE)
text(s, 0.86, 4.89, 10.80, 0.30,
     "La base es siempre la misma: observar, ajustar en el Inspector y probar en Play.",
     15, INK, SEM)
text(s, 0.86, 5.25, 10.80, 0.26,
     "Para practicar: agrega una barra de vida y usa el spawner para crear enemigos más difíciles.",
     10.5, BODY, REG)
footer(s, "La escena ya tiene cámara, escenario, material y sprite. El siguiente paso es la interfaz y el audio.")
notes(s,
      "Resumen:\n\n"
      "1. Cámara: se calcula una meta con target.position + offset y se suaviza con "
      "Lerp en LateUpdate.\n"
      "2. Escenario: el plano se escala a 100 × 100 y se mueve para conservar el "
      "borde. El spawner crea 50 esferas con Instantiate y Random.Range.\n"
      "3. Material: se crea un material, se elige el color base y se asigna al Mesh "
      "Renderer del plano.\n"
      "4. Sprite: se corta la hoja en siete cuadros, se agrega un Sprite Renderer, se "
      "activa la sombra y se usa flipX para voltear.\n\n"
      "Para practicar: agrega una barra de vida y usa el spawner para crear enemigos "
      "más difíciles.")

# 48 --------------------------------------------------------------- preguntas
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
text(s, 0.0, 1.55, 13.33, 1.35, "¿PREGUNTAS?", 54, INK, SEM, align=PP_ALIGN.CENTER)
text(s, 0.0, 3.18, 13.33, 0.38, "Siguiente: laboratorio de Unity.", 18, INK, REG,
     align=PP_ALIGN.CENTER)
text(s, 0.0, 3.72, 13.33, 0.38,
     "La escena ya sigue al jugador, tiene un spawner y un sprite con sombra.",
     14, BODY, REG, align=PP_ALIGN.CENTER)
picture_fit(s, ROOT / "decor" / "star.png", 1.55, 2.30, 0.85, 0.85, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 3.60, 4.15, 0.75, 0.75, border=False)
picture_fit(s, ROOT / "decor" / "tree-small.png", 1.10, 4.36, 1.15, 2.06, border=False)
picture_fit(s, ROOT / "decor" / "cloud-low.png", 9.85, 4.68, 2.65, 1.42, border=False)
notes(s,
      "Cierre del tema 8.6.2.\n\n"
      "Recuerda: la cámara sigue al cubo con un offset y Lerp; el plano crece y el "
      "spawner crea esferas; el material cambia el color del piso; el sprite se corta, "
      "recibe sombra y se voltea con flipX.\n\n"
      "En el laboratorio se puede ampliar con una barra de vida, enemigos que atacan "
      "y un menú de inicio.")


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
