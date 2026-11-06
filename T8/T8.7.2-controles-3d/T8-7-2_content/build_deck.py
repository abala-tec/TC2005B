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
    "DECK_OUT", str(ROOT.parent / "T8.7.2-Controles-3D-Mario.pptx")
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
CS = "Assets/Scripts/escena5_controles/S5_VelmaWalk_3D.cs"
CS_CUBE = "Assets/Scripts/escena5_controles/S5_CubeMove.cs"


def snip(name):
    return SNIPPETS[name][0]


def nc(slide, intro, names, extra="", path=CS):
    """Notas con el código exacto que se ve en la imagen."""
    notes_code(slide, intro, [(path, snip(n)) for n in names], extra)


def code_img(slide, name, x, y, w, h):
    """Imagen de código alineada arriba a la izquierda."""
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


# ---------------------------------------------------------------- deck
prs = new_deck()
prs.core_properties.title = "T8.7.2 · Controles 3D estilo Mario"
prs.core_properties.author = "TC2005B · Construcción de Software"
prs.core_properties.subject = "De un control 2D a un control 3D con velocidades y salto en Unity"
prs.core_properties.keywords = "Unity, C#, Rigidbody, Vector2, 3D, SMB3, salto, TC2005B"
prs.core_properties.language = "es-MX"

# ---- portada
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
rect(s, 0.62, 0.32, 0.09, 0.09, ORANGE)
text(s, 0.81, 0.28, 10.0, 0.22, "8.7.2 · INTERACCIÓN HUMANO-COMPUTADORA", role="label")
text(s, 0.62, 0.92, 6.00, 2.70, "CONTROLES\nDE MARIO\nEN 3D", role="section", line_spacing=0.92)
text(s, 0.62, 3.64, 5.70, 0.80,
     "Cómo pasar del control 2D de Velma a un personaje que también camina hacia el fondo.",
     role="subtitle", line_spacing=1.02)
text(s, 0.62, 4.75, 5.55, 0.72,
     "Las mismas velocidades y el mismo salto, pero con dos ejes: X y Z.",
     role="note", color=BODY, line_spacing=1.02)
text(s, 0.62, 5.80, 5.40, 0.28, "TC2005B · Construcción de Software", role="note")
text(s, 0.62, 6.16, 5.40, 0.28, "Unity · C# · S5_VelmaWalk_3D", role="note", color=MUTED)
rect(s, 6.55, 0.66, 6.18, 4.95, DARK)
picture_fill(s, ROOT / "img" / "cover_sprite.png", 6.75, 0.86, 5.78, 4.55)
rect(s, 6.75, 0.86, 5.78, 4.55, None, WHITE, 1.2)
pill(s, 6.95, 0.72, 1.55, "UNITY · C#", WHITE, DARK)
picture_fit(s, ROOT / "decor" / "star.png", 0.55, 6.30, 0.75, 0.75, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 11.55, 6.10, 0.95, 0.95, border=False)
notes(s,
      "Bienvenida al tema 8.7.2. En el tema anterior (8.7.1) Velma ya corría y saltaba "
      "como en Super Mario Bros. 3, pero solo de izquierda a derecha.\n\n"
      "Hoy llevamos ese mismo control a 3D. La buena noticia es que casi todo el código "
      "se queda igual: solo cambia la forma de guardar la velocidad horizontal.\n\n"
      "Primero veremos qué cambia. Después clonamos el objeto y el script, y al final "
      "leemos S5_VelmaWalk_3D con detalle, en el mismo orden de las capturas de pantalla.")

# ---- agenda
s = new_slide()
header(s, "HOY", "LO QUE VEREMOS HOY",
       "Tres bloques llevan el control de 2D a 3D.")
rows = [
    ("01", "DE 2D A 3D", "Qué se queda igual, qué cambia y por qué hace falta un vector.", ORANGE),
    ("02", "CLONAR LA ESCENA", "Copiar el objeto de Velma y el script para no perder la versión 2D.", BLUE),
    ("03", "EL CÓDIGO PASO A PASO", "Solo lo que cambia: variables, Start, Update, suelo y salto.", GREEN),
]
for i, (num, title, desc, color) in enumerate(rows):
    y = 1.70 + i * 1.05
    card(s, 0.62, y, 12.09, 0.92, color)
    text(s, 0.82, y + 0.28, 0.45, 0.30, num, role="card_number", color=color)
    text(s, 1.42, y + 0.10, 10.8, 0.34, title, role="card_title_sm")
    text(s, 1.46, y + 0.50, 11.0, 0.30, desc, role="note", color=BODY)
text(s, 0.62, 4.95, 12.0, 0.40,
     "Al final veremos los límites del script y cómo mejorarlo.", role="body_strong")
footer(s, "Cada parte del código se ve como imagen y se copia completa en las notas.")
notes(s,
      "Recorrido del tema.\n\n"
      "1. De 2D a 3D: comparamos las dos versiones y explicamos por qué la velocidad "
      "horizontal pasa de un número a un vector.\n"
      "2. Clonar la escena: se ve cómo se duplica el objeto de Velma y el script.\n"
      "3. El código: solo explicamos lo que cambia. Lo que es igual que en 2D (salto, "
      "gravedad y detección del suelo) se repasa rápido.\n\n"
      "Las capturas siguen el orden real en que se hizo el trabajo en Unity.")

# ---- seccion 01
s = section_slide(prs, "01", "DE 2D\nA 3D",
                  "Casi todo el control se queda igual. Lo nuevo es el eje Z.",
                  "VECTOR2 · EJE Z · DIAGONAL", ORANGE)
notes(s, "Bloque 1. Antes de tocar Unity, vemos qué cambia y qué no cambia entre el "
         "control 2D y el 3D.")

# 1 ------------------------------------------------------------ punto de partida
K1 = "BLOQUE 01 · DE 2D A 3D"
s = new_slide()
header(s, K1, "DONDE EMPEZAMOS: S5_VELMAWALK_2D",
       "El control 2D ya sabe acelerar, frenar, correr y saltar.")
bullets(s, 0.62, 1.80, 6.10, [
    "Guarda una velocidad horizontal: vx.",
    "Guarda una velocidad vertical: vy.",
    "Se entrega al Rigidbody como (vx, vy, 0).",
    "FreezePositionZ mantiene a Velma en un plano.",
], gap=0.92)
tip(s, 7.20, 1.80, 5.50, 2.00, "LO QUE FALTA",
    "Velma no puede alejarse ni acercarse a la cámara. Falta un segundo eje de movimiento.")
tip(s, 7.20, 4.00, 5.50, 1.55, "LA IDEA", "Reutilizar todo y cambiar solo la parte horizontal.",
    accent=GREEN)
footer(s, "Por eso clonamos el script 2D y no empezamos desde cero.")
notes(s,
      "Resumen de lo que ya teníamos en 8.7.1. S5_VelmaWalk_2D calcula dos velocidades: "
      "vx para ir a los lados y vy para subir y bajar. Al final se las entrega al "
      "Rigidbody con rb.linearVelocity = new Vector3(vx, vy, 0).\n\n"
      "Además congela la posición en Z. Por eso Velma vive en un plano, como en un "
      "juego de plataformas lateral.\n\n"
      "Para el control 3D queremos que Velma también pueda caminar hacia el fondo y hacia "
      "la cámara. Eso significa mover en dos ejes del suelo: X y Z. El salto y la "
      "gravedad no cambian, porque siguen usando el eje Y.")

# 2 ------------------------------------------------------------ que cambia
s = new_slide()
header(s, K1, "QUÉ CAMBIA DE 2D A 3D",
       "Son pocos cambios, y todos tienen que ver con el eje Z.")
tbl(s, 0.62, 1.70, 12.09, [
    ("Parte del script", "Versión 2D", "Versión 3D"),
    ("Velocidad horizontal", "float vx", "Vector2 horizontal"),
    ("Teclas de movimiento", "A y D", "A, D, W y S"),
    ("Restricciones (Start)", "Congela rotación y posición Z", "Solo congela la rotación"),
    ("Tope de velocidad", "Solo walkSpeed y runSpeed", "También maxHorizontalSpeed"),
    ("Salida al Rigidbody", "Vector3(vx, vy, 0)", "Vector3(horizontal.x, vy, horizontal.y)"),
], [3.0, 4.2, 4.89], row_h=0.60)
footer(s, "El salto, la gravedad y la detección del suelo quedan exactamente igual.")
notes(s,
      "Esta tabla resume todos los cambios del script. Se obtuvo comparando los archivos "
      "S5_VelmaWalk_2D.cs y S5_VelmaWalk_3D.cs.\n\n"
      "1. vx pasa de ser un número a ser un Vector2 llamado horizontal.\n"
      "2. Se agregan las teclas W y S para el eje Z.\n"
      "3. En Start ya no se congela la posición Z; solo se congela la rotación.\n"
      "4. Aparece un tope general, maxHorizontalSpeed, porque ahora hay dos ejes.\n"
      "5. Al final, la velocidad Z se toma de horizontal.y.\n\n"
      "No cambian: las velocidades de SMB3, la aceleración, el frenado, el salto "
      "variable, la gravedad ni el método OnCollision para saber si Velma está en el "
      "suelo.")

# 3 ------------------------------------------------------------ vector2
s = new_slide()
header(s, K1, "UN VECTOR EN VEZ DE UN NÚMERO",
       "horizontal guarda la velocidad en X y en Z a la vez.")
tbl(s, 0.62, 1.70, 7.40, [
    ("Tecla", "Entrada", "Eje en Unity"),
    ("D / flecha derecha", "inputX = +1", "X positivo"),
    ("A / flecha izquierda", "inputX = −1", "X negativo"),
    ("W / flecha arriba", "inputZ = +1", "Z positivo (al fondo)"),
    ("S / flecha abajo", "inputZ = −1", "Z negativo (a la cámara)"),
], [2.70, 2.00, 2.70], row_h=0.60)
tip(s, 8.40, 1.70, 4.31, 2.45, "OJO",
    "Un Vector2 tiene x e y. Aquí horizontal.y guarda la velocidad en Z, no en Y.",
    accent=PINK)
bullets(s, 8.40, 4.35, 4.31, [
    "El eje Y de Unity sigue siendo la altura.",
], gap=0.8)
footer(s, "Por eso el último paso usa Vector3(horizontal.x, vy, horizontal.y).")
notes(s,
      "Un Vector2 guarda dos números: x e y. En el script usamos esos dos números para "
      "las dos direcciones del suelo: horizontal.x es la velocidad en el eje X de Unity "
      "y horizontal.y es la velocidad en el eje Z.\n\n"
      "Esto puede confundir: en un Vector2 la segunda componente siempre se llama y, "
      "pero en este caso no es la altura. La altura se guarda aparte, en la variable "
      "vy.\n\n"
      "En la escena, W empuja a Velma hacia el fondo (Z positivo) y S la acerca a la "
      "cámara (Z negativo).")

# ---- seccion 02
s = section_slide(prs, "02", "CLONAR\nLA ESCENA",
                  "Copiamos a Velma y su script para conservar la versión 2D.",
                  "CTRL + D · RENOMBRAR · CONECTAR", BLUE)
notes(s, "Bloque 2. Primero se clona el objeto y después el script, como en las capturas.")

# 4 ------------------------------------------------------------ clonar objeto
K2 = "BLOQUE 02 · ESCENA"
s = new_slide()
header(s, K2, "CLONAR EL GAMEOBJECT DE VELMA",
       "Se duplica velma_sprite_walk y el nuevo se llama velma_sprite_walk_3D.")
shot(s, "1-clonar_game_object-2d-renombrar_el-nuevo_gameobject.png", 0.62, 1.70, 5.40, 2.57)
cap(s, 0.62, 4.40, 5.4, "Jerarquía: el objeto 2D en gris y el nuevo objeto 3D.")
steps(s, 6.50, 1.85, 6.2, [
    "Selecciona velma_sprite_walk en la Jerarquía.",
    "Presiona Ctrl + D para duplicarlo.",
    "Renombra la copia: velma_sprite_walk_3D.",
    "Apaga el objeto 2D para no ver dos Velmas.",
], gap=0.88)
footer(s, "La copia ya trae el sprite, el Rigidbody y el Box Collider.")
notes(s,
      "En la captura se ve la Jerarquía de la escena escena5_controles. velma_sprite_walk "
      "aparece en gris porque está desactivado, y velma_sprite_walk_3D está activo.\n\n"
      "Al duplicar el objeto se copian todos sus componentes: el SpriteRenderer, el "
      "Rigidbody y el Box Collider. Así no tenemos que configurarlos otra vez. El objeto "
      "2D se deja apagado y no se borra, por si queremos volver a probarlo.\n\n"
      "En Unity, Ctrl + D duplica el objeto seleccionado y F2 permite cambiarle el nombre.")

# 5 ------------------------------------------------------------ clonar script
s = new_slide()
header(s, K2, "CLONAR EL SCRIPT Y CAMBIAR SU NOMBRE",
       "La copia de S5_VelmaWalk_2D se llama S5_VelmaWalk_3D.")
shot(s, "2-clonar_script_movimiento_2D_y_renombrar.png", 0.62, 1.70, 5.40, 2.39)
cap(s, 0.62, 4.20, 5.4, "Los dos scripts en la ventana Project.")
steps(s, 6.50, 1.85, 6.2, [
    "En Project, selecciona S5_VelmaWalk_2D.",
    "Presiona Ctrl + D y luego F2 para renombrar.",
    "Cambia el nombre a S5_VelmaWalk_3D.",
    "Cambia también la clase dentro del archivo.",
], gap=0.88)
footer(s, "Unity exige que el nombre de la clase sea igual al del archivo.")
notes(s,
      "Igual que en el tema anterior, se duplica el script para conservar el original. "
      "El nombre nuevo, S5_VelmaWalk_3D, sigue la regla del proyecto: S5 es la escena, "
      "Velma es el personaje, Walk es la acción y 3D es el tipo de control.\n\n"
      "Dentro del archivo hay que cambiar la línea public class S5_VelmaWalk_2D : "
      "MonoBehaviour por public class S5_VelmaWalk_3D : MonoBehaviour. Si el nombre de "
      "la clase no coincide con el del archivo, Unity no deja agregar el script.\n\n"
      "Después, en el objeto velma_sprite_walk_3D se quita el componente 2D y se agrega "
      "el 3D.")

# 6 ------------------------------------------------------------ conectar
s = new_slide()
header(s, K2, "CONECTAR EL PERSONAJE NUEVO",
       "Otros objetos de la escena deben apuntar a velma_sprite_walk_3D.")
items = [
    ("CÁMARA", "S5_CameraFollower", "El campo Target debe ser velma_sprite_walk_3D.", ORANGE),
    ("BOTÓN", "Reset", "El evento OnClick llama a ResetButtonClick del script 3D.", BLUE),
    ("ENEMIGO", "S5_EnemigoEsfera", "El campo cubo apunta al personaje nuevo para perseguirlo.", GREEN),
]
for i, (k, name, desc, color) in enumerate(items):
    x = 0.62 + i * 4.10
    card(s, x, 1.75, 3.89, 3.25, color)
    text(s, x + 0.25, 1.95, 3.4, 0.30, k, role="label", color=ORANGE_TEXT)
    text(s, x + 0.25, 2.40, 3.4, 0.40, name, role="card_title_sm")
    text(s, x + 0.25, 3.05, 3.4, 1.60, desc, role="note", color=BODY, line_spacing=1.05)
footer(s, "Si alguno sigue apuntando al objeto 2D, no hará nada al probar la escena.")
notes(s,
      "Esto no sale en las capturas, pero es necesario para que la escena funcione. En "
      "escena5_controles hay tres cosas que usan al personaje:\n\n"
      "- La Main Camera tiene el script S5_CameraFollower. Su campo Target está "
      "apuntando a velma_sprite_walk_3D.\n"
      "- El botón de la interfaz llama a ResetButtonClick en el evento OnClick. Debe "
      "llamar al método del script S5_VelmaWalk_3D.\n"
      "- El enemigo tiene un campo llamado cubo. Ese campo apunta al personaje que "
      "persigue.\n\n"
      "Si estos campos siguen apuntando al objeto 2D apagado, la cámara no seguirá a la "
      "Velma 3D y el botón reiniciará al personaje equivocado.")

# ---- seccion 03
s = section_slide(prs, "03", "EL CÓDIGO\nPASO A PASO",
                  "Solo explicamos lo nuevo. Lo que es igual que en 2D se repasa rápido.",
                  "VARIABLES · START · UPDATE · SALTO · SUELO", GREEN)
notes(s, "Bloque 3. Leemos S5_VelmaWalk_3D en el orden en que se tomaron las capturas.")

K3 = "BLOQUE 03 · CÓDIGO"

# 7 ------------------------------------------------------------ variables
s = new_slide()
header(s, K3, "VARIABLES: SOLO LO NUEVO",
       "Las velocidades y el salto son los mismos números que en 2D.")
shot(s, "3-variables_para3d_solo_mencionar_las_diferentes_a_la_version_2d.png",
     0.62, 1.64, 3.80, 4.42)
code_img(s, "code_vars_nuevas", 4.75, 1.64, 7.95, 2.55)
bullets(s, 4.75, 4.35, 7.95, [
    "maxHorizontalSpeed es nueva: tope de velocidad en el suelo.",
    "horizontal es un Vector2 y reemplaza a vx.",
], gap=0.70)
footer(s, "Todo lo demás (walkSpeed, runSpeed, jumpSpeed, gravity…) no cambió.")
nc(s, "En la captura se ven todas las variables, con el número de referencias que "
      "muestra el editor. Solo hay dos diferencias con la versión 2D:\n\n"
      "1. Variable pública nueva: maxHorizontalSpeed = 15. Es el valor $40 de SMB3, "
      "4 píxeles por cuadro. Limita la velocidad en el plano XZ (más adelante se ve "
      "cómo se usa).\n"
      "2. private Vector2 horizontal reemplaza a private float vx. Ahora guarda la "
      "velocidad en X y en Z.\n\n"
      "Siguen igual: walkSpeed 5.625, runSpeed 9.375, acceleration y braking 12.3046875, "
      "jumpSpeed 13.125, gravity 70.3125, jumpGravity 14.0625, jumpHoldLimit 7.5 y "
      "maxFallSpeed 15. Se explicaron en el tema 8.7.1.\n\n"
      "La variable cayendo sigue sin usarse; viene del script del cubo.",
   ["code_vars_nuevas"])

# 8 ------------------------------------------------------------ start
s = new_slide()
header(s, K3, "START: CAMBIAN LAS RESTRICCIONES",
       "En 3D ya no se congela la posición en Z.")
shot(s, "4-init_rigidbody_2d_mecionar_cambios_con_2d.png", 0.62, 1.64, 6.20, 1.72)
code_img(s, "code_constraints", 0.62, 3.55, 6.20, 2.40)
bullets(s, 7.20, 1.80, 5.50, [
    "Se mantiene useGravity = false.",
    "Se mantienen Interpolate y Continuous.",
    "FreezeRotation congela X, Y y Z de la rotación.",
    "Sin FreezePositionZ, Velma puede moverse en Z.",
], gap=0.88)
footer(s, "En el Inspector, la restricción pasa de 120 a 112.")
nc(s, "Start prepara el Rigidbody. Es igual que en 2D, menos la última línea.\n\n"
      "- useGravity = false: la gravedad la calcula el script, no Unity.\n"
      "- interpolation = Interpolate: suaviza el movimiento entre cuadros de física.\n"
      "- collisionDetectionMode = Continuous: evita atravesar el suelo.\n"
      "- constraints: en 2D se congelaban las tres rotaciones y la posición Z. En 3D "
      "solo se congela la rotación con FreezeRotation. Esa opción ya incluye X, Y y Z, "
      "por eso no hace falta unirlas con el símbolo |.\n\n"
      "Si FreezePositionZ siguiera activo, la tecla W y la tecla S no moverían a Velma. "
      "En la escena, el valor numérico de las restricciones pasa de 120 (2D) a 112 (3D).",
   ["code_start_3d", "code_constraints"])

# 9 ------------------------------------------------------------ input X
s = new_slide()
header(s, K3, "UPDATE: LEER LA TECLA A Y LA TECLA D",
       "Esta parte es igual que en 2D, pero la variable se llama inputX.")
shot(s, "5-update_start_user_input_para_3d.png", 0.62, 1.64, 5.60, 4.40)
code_img(s, "code_input_x", 6.50, 1.64, 6.20, 3.55)
bullets(s, 6.50, 5.15, 6.20, [
    "flipX voltea el sprite según la dirección.",
], gap=0.7)
footer(s, "La captura muestra también las líneas nuevas para W y S.")
nc(s, "Update corre en cada cuadro. Keyboard.current es el teclado del Input System; "
      "si no hay teclado, la función termina.\n\n"
      "Se declara inputX = 0. Si se presiona D o la flecha derecha, suma 1 y apaga flipX "
      "para que Velma mire a la derecha. Si se presiona A o la flecha izquierda, resta "
      "1 y activa flipX para que mire a la izquierda. Si se presionan las dos, se "
      "cancelan.\n\n"
      "En 2D esta variable se llamaba input. Ahora se llama inputX porque habrá otra "
      "para Z.",
   ["code_input_x"])

# 10 ----------------------------------------------------------- input Z
s = new_slide()
header(s, K3, "UPDATE: LEER W Y S Y ARMAR EL VECTOR",
       "Se agrega un segundo eje y se juntan los dos en un Vector2.")
code_img(s, "code_input_z", 0.62, 1.64, 7.40, 2.70)
bullets(s, 8.30, 1.76, 4.40, [
    "W o flecha arriba: inputZ = +1.",
    "S o flecha abajo: inputZ = −1.",
    "input junta inputX e inputZ.",
], gap=0.88)
tip(s, 0.62, 4.60, 12.09, 1.25, "RESULTADO",
    "input puede valer (1, 0), (0, −1), (1, 1) o (0, 0). Ocho direcciones y la quietud.")
footer(s, "Aún falta un paso: arreglar la diagonal.")
nc(s, "inputZ funciona igual que inputX, pero con las teclas W y S. Como el sprite solo "
      "se voltea a izquierda o derecha, estas teclas no cambian flipX.\n\n"
      "Después se crea Vector2 input = new Vector2(inputX, inputZ). Con eso, una sola "
      "variable guarda la dirección que el jugador quiere, en los dos ejes.\n\n"
      "Ejemplos: D da (1, 0); S da (0, −1); W y D juntas dan (1, 1); si no se toca nada, "
      "es (0, 0).\n\n"
      "La última línea normaliza el vector cuando es más largo que 1. Se explica en las "
      "siguientes dos diapositivas.",
   ["code_input_z"])

# 11 ----------------------------------------------------------- normalizar
s = new_slide()
header(s, K3, "NORMALIZAR: LA DIAGONAL NO DEBE SER MÁS RÁPIDA",
       "Si el vector mide más de 1, se reduce a un largo de exactamente 1.")
fig(s, ROOT / "figuras" / "fig_diagonal.png", 0.62, 1.64, 7.10, 4.67)
bullets(s, 8.00, 1.76, 4.70, [
    "W + D da (1, 1). Su largo es 1.41.",
    "Sin normalizar, iría 41 % más rápido.",
    "Normalize() lo deja en (0.71, 0.71).",
], gap=0.88)
code_img(s, "code_tope", 8.00, 4.55, 4.70, 0.55)
footer(s, "sqrMagnitude evita calcular una raíz cuadrada si no hace falta.")
notes_code_text = ("En una diagonal, el vector (1, 1) mide raíz de 2, que es 1.41. Si usáramos ese "
      "vector sin cambiarlo, Velma recorrería la diagonal 41 % más rápido que cuando va "
      "recto. Por eso se normaliza.\n\n"
      "La línea if (input.sqrMagnitude > 1f) input.Normalize(); hace dos cosas: "
      "sqrMagnitude es el largo al cuadrado (x² + z²), que se calcula sin raíz y por eso "
      "es más rápido. Si ese número es mayor que 1, Normalize() divide el vector entre su "
      "largo y lo deja con largo 1.\n\n"
      "Para (1, 1): largo = 1.41, y el vector normalizado es (0.71, 0.71). Con (1, 0) no "
      "se hace nada, porque ya mide 1.\n\n"
      "El archivo codigo/simulacion_control_3d.py repite estas cuentas.")
nc(s, notes_code_text, ["code_input_z"])

# 12 ----------------------------------------------------------- diagonal numeros
s = new_slide()
header(s, K3, "LA DIAGONAL EN NÚMEROS",
       "La gráfica compara la velocidad con y sin normalizar.")
fig(s, ROOT / "figuras" / "fig_velocidad_diag.png", 0.62, 1.64, 7.10, 4.02)
bullets(s, 8.00, 1.76, 4.70, [
    "Normalizado: llega a 5.625 u/s.",
    "Sin normalizar: llegaría a 7.95 u/s.",
    "Normalizado tarda 0.46 s; sin normalizar, 0.65 s.",
], gap=0.88)
tip(s, 8.00, 4.55, 4.70, 1.30, "FÓRMULA", "5.625 × 1.41 = 7.95 u/s")
footer(s, "La gráfica sale de codigo/simulacion_control_3d.py, una réplica en Python.")
notes(s,
      "La gráfica muestra la velocidad total (el largo de horizontal) cuando se mantienen "
      "presionadas las teclas W y D. Se calculó con codigo/simulacion_control_3d.py, que "
      "repite la lógica de Update en Python con pasos de 1/60 de segundo.\n\n"
      "Con normalización, la velocidad sube de 0 a 5.625 unidades por segundo, que es "
      "walkSpeed. Con la aceleración de 12.3 u/s², tarda 5.625 ÷ 12.3 = 0.46 segundos.\n\n"
      "Sin normalización, el objetivo sería (5.625, 5.625), que tiene largo 7.95. Es 41 % "
      "más rápido (tarda 0.65 s en llegar) y se sentiría como un error de control.\n\n"
      "El archivo de Python también incluye comprobaciones (assert) para estos números.")

# 13 ----------------------------------------------------------- banderas + topSpeed
s = new_slide()
header(s, K3, "BOTONES, SUELO Y TOPSPEED",
       "Estas líneas siguen igual que en 2D.")
shot(s, "5-init_del_proceso_camino_o_corro.png", 0.62, 1.64, 8.20, 1.14)
code_img(s, "code_banderas", 0.62, 3.05, 5.30, 2.35)
code_img(s, "code_suelo_top", 6.30, 3.05, 6.40, 1.95)
footer(s, "Correr (Shift o X) cambia el tope de velocidad en los dos ejes.")
nc(s, "Banderas de los botones (se leen una vez por cuadro):\n"
      "- runHeld: true mientras se mantiene Shift izquierdo o X.\n"
      "- jumpPressed: true solo en el cuadro en que se presiona Espacio o Z.\n"
      "- jumpHeld: true mientras se mantiene el botón de salto.\n\n"
      "Suelo: si Velma está en el suelo y su velocidad vertical es negativa o cero, "
      "vy se pone en 0. Así no se acumula una caída que no existe. El valor de grounded "
      "lo cambian las funciones OnCollision que vienen más adelante.\n\n"
      "topSpeed: si se mantiene el botón de correr vale runSpeed (9.375); si no, vale "
      "walkSpeed (5.625). En 3D este tope se usa para los dos ejes: X y Z. Es decir, "
      "correr también aumenta la velocidad hacia el fondo.",
   ["code_banderas", "code_suelo_top"])

# 14 ----------------------------------------------------------- colisiones
s = new_slide()
header(s, K3, "COLISIÓN CON EL SUELO: IGUAL QUE EN 2D",
       "Tres funciones de Unity avisan cuándo Velma toca algo.")
shot(s, "5.1-colision_con_el_suelo_Igual_que_en_2d.png", 0.62, 1.64, 5.45, 4.41)
code_img(s, "code_colision", 6.40, 1.64, 3.90, 3.00)
bullets(s, 6.40, 4.75, 6.30, [
    "Enter y Stay llaman a CheckGround.",
    "Exit baja la bandera grounded.",
], gap=0.62)
footer(s, "El suelo 3D también es una caja con collider, así que no hace falta cambiar nada.")
nc(s, "Estas funciones las llama Unity solas, gracias al Rigidbody y al Box Collider.\n\n"
      "- OnCollisionEnter: se llama una vez, en el cuadro en que Velma empieza a tocar un "
      "objeto.\n"
      "- OnCollisionStay: se llama en cada cuadro mientras siga tocándolo.\n"
      "- OnCollisionExit: se llama cuando deja de tocarlo. Ahí grounded pasa a false.\n\n"
      "Enter y Stay llaman a CheckGround, que decide si el objeto tocado es suelo. "
      "Funciona igual en 3D porque Unity 3D también calcula las colisiones con sus "
      "contactos. La captura muestra además los comentarios del archivo.",
   ["code_colision"])

# 15 ----------------------------------------------------------- checkground
s = new_slide()
header(s, K3, "CHECKGROUND: LA NORMAL DEL CONTACTO",
       "Solo cuenta como suelo un contacto que empuja hacia arriba.")
code_img(s, "code_checkground", 0.62, 1.64, 6.60, 3.70)
fig(s, ROOT / "figuras" / "fig_normales.png", 7.50, 1.64, 5.20, 2.64)
bullets(s, 7.50, 4.45, 5.20, [
    "normal.y mayor que 0.5: suelo.",
    "Una pared tiene normal.y cercana a 0.",
], gap=0.66)
footer(s, "Si vy es mayor que 0, Velma sube y no puede estar en el suelo.")
nc(s, "CheckGround recorre todos los puntos de contacto de la colisión. Cada punto "
      "tiene una normal: una flecha que sale de la superficie tocada y apunta hacia "
      "Velma.\n\n"
      "- Si es el suelo, la flecha apunta hacia arriba: normal.y vale casi 1.\n"
      "- Si es una pared, la flecha apunta hacia un lado: normal.y vale casi 0.\n\n"
      "Si normal.y es mayor que 0.5, se activa grounded y la función termina. La primera "
      "línea evita marcar suelo mientras Velma sube: justo después de saltar todavía "
      "toca el piso por un instante.\n\n"
      "En 3D esto sigue sirviendo, incluso con plataformas en Z, porque la altura sigue "
      "siendo el eje Y.",
   ["code_checkground"])

# 16 ----------------------------------------------------------- target y misma direccion
s = new_slide()
header(s, K3, "MOVER EN X Y Z: LA META Y LA DIRECCIÓN",
       "Aquí está el cambio más grande del script.")
shot(s, "6-movimiento_en_x_z_en_el_aire_y_en_suelo.png", 0.62, 1.64, 6.40, 4.28)
code_img(s, "code_target_same", 7.30, 1.64, 5.40, 1.70)
bullets(s, 7.30, 3.55, 5.40, [
    "target: el vector de velocidad que se quiere.",
    "sameDirection: true si ya va hacia donde se pide.",
    "Dot compara las dos direcciones.",
], gap=0.76)
footer(s, "En 2D bastaba comparar el signo de vx con el de input.")
nc(s, "Esta es la parte nueva más importante. En 2D se comparaba el signo de vx con el "
      "signo de input. En 3D no se puede, porque hay dos ejes. Se usa un producto "
      "punto.\n\n"
      "target = input × topSpeed es la velocidad que el jugador quiere. Por ejemplo, con "
      "W y caminando: (0, 1) × 5.625 = (0, 5.625).\n\n"
      "sameDirection es true si Velma ya se mueve (horizontal.sqrMagnitude > 0.01) y si el "
      "producto punto entre la dirección actual (horizontal.normalized) y la dirección "
      "deseada (input) es mayor que 0.1. Un producto punto positivo significa que los "
      "dos vectores apuntan más o menos hacia el mismo lado.",
   ["code_target_same"])

# 17 ----------------------------------------------------------- producto punto
s = new_slide()
header(s, K3, "EL PRODUCTO PUNTO EN POCAS PALABRAS",
       "Dice qué tanto apuntan dos direcciones hacia el mismo lado.")
tbl(s, 0.62, 1.70, 8.10, [
    ("Velma va hacia…", "El jugador pide…", "Dot", "Resultado"),
    ("Derecha (1, 0)", "Derecha (1, 0)", "1", "Misma dirección"),
    ("Derecha (1, 0)", "Diagonal (0.7, 0.7)", "0.7", "Misma dirección"),
    ("Derecha (1, 0)", "Arriba (0, 1)", "0", "Distinta (de lado)"),
    ("Derecha (1, 0)", "Izquierda (−1, 0)", "−1", "Contraria"),
], [2.40, 2.60, 0.90, 2.20], row_h=0.62)
tip(s, 9.05, 1.70, 3.66, 2.50, "REGLA",
    "Dot mayor que 0.1: misma dirección. Si no, se acelera hacia la meta.")
footer(s, "Fórmula: Dot(a, b) = a.x × b.x + a.y × b.y, con vectores de largo 1.")
notes(s,
      "El producto punto de dos vectores de largo 1 siempre es un número entre −1 y 1.\n\n"
      "- 1: apuntan al mismo lado.\n"
      "- 0: forman una esquina de 90 grados.\n"
      "- −1: apuntan a lados contrarios.\n\n"
      "El script usa 0.1 como límite. Dot mayor que 0.1 significa que Velma ya va más o "
      "menos hacia donde el jugador pide. En ese caso, si va más rápido que topSpeed, "
      "se frena (si está en el suelo) o se conserva la velocidad (si está en el aire).\n\n"
      "Si Velma va hacia un lado distinto o contrario, se acelera hacia la nueva meta. "
      "Eso permite cambiar de dirección. La fórmula en Python está en "
      "codigo/simulacion_control_3d.py, función dot.")

# 18 ----------------------------------------------------------- acelerar / frenar
s = new_slide()
header(s, K3, "ACELERAR O FRENAR CON MOVETOWARDS",
       "Vector2.MoveTowards acerca un vector a otro sin pasarse.")
code_img(s, "code_horizontal_3d", 0.62, 1.64, 6.60, 4.40)
bullets(s, 7.50, 1.76, 5.20, [
    "Misma dirección y más rápido: en el suelo frena.",
    "Misma dirección y más rápido, en el aire: conserva.",
    "Cualquier otro caso: acelera hacia target.",
], gap=0.92)
tip(s, 7.50, 4.55, 5.20, 1.30, "PASO", "acceleration × Time.deltaTime en cada cuadro.")
footer(s, "Es la misma lógica de 2D, con vectores en vez de números.")
nc(s, "Si el jugador pide moverse (input distinto de cero):\n\n"
      "1. Si Velma ya va hacia donde se pide y su velocidad supera a topSpeed (por "
      "ejemplo, soltó el botón de correr), entonces en el suelo se frena con braking y en "
      "el aire no se hace nada: se conserva el impulso, como en Mario.\n"
      "2. En cualquier otro caso (parte del reposo, va más lento o cambia de dirección) "
      "se acelera hacia target con acceleration.\n\n"
      "Vector2.MoveTowards(actual, meta, paso) mueve el vector actual en línea recta "
      "hacia la meta y no la pasa. El paso es la aceleración por Time.deltaTime, que es "
      "lo que se avanza en ese cuadro. Al ser un vector, el cambio ocurre en X y en Z al "
      "mismo tiempo.",
   ["code_horizontal_3d"])

# 19 ----------------------------------------------------------- sin tecla
s = new_slide()
header(s, K3, "SIN TECLAS: FRENAR EN EL SUELO",
       "En el aire no se frena: Velma conserva su velocidad.")
code_img(s, "code_sin_tecla_3d", 0.62, 1.64, 7.20, 2.20)
tbl(s, 0.62, 4.15, 12.09, [
    ("Situación", "Qué pasa con horizontal"),
    ("Sin teclas y en el suelo", "Baja hasta (0, 0) con braking."),
    ("Sin teclas y en el aire", "No cambia: conserva el momento."),
], [4.60, 7.49], row_h=0.50)
footer(s, "Por eso en el aire no puedes detener un salto largo soltando las teclas.")
nc(s, "Este bloque va después del if de la diapositiva anterior. Corre cuando no hay "
      "teclas de movimiento y Velma está en el suelo.\n\n"
      "MoveTowards acerca horizontal a Vector2.zero, que es (0, 0), con la rapidez de "
      "braking. Así Velma se detiene poco a poco.\n\n"
      "Si Velma está en el aire, ninguna de las dos ramas se ejecuta y horizontal queda "
      "igual. Es el mismo comportamiento de Mario: el impulso se conserva hasta que "
      "vuelve a tocar el suelo.",
   ["code_sin_tecla_3d"])

# 20 ----------------------------------------------------------- tope + salto
s = new_slide()
header(s, K3, "TOPE MÁXIMO E INICIO DEL SALTO",
       "Dos pasos cortos: limitar la velocidad y empezar a saltar.")
shot(s, "7-max_velocity_y_Jump_start_process.png", 0.62, 1.64, 6.00, 2.09)
code_img(s, "code_tope", 0.62, 4.00, 6.00, 0.65)
code_img(s, "code_salto_inicio", 6.90, 1.64, 5.80, 1.90)
bullets(s, 6.90, 3.80, 5.80, [
    "magnitude es el largo del vector.",
    "Si pasa de 15, se recorta con normalized.",
    "vy = jumpSpeed solo si jumpPressed y grounded.",
], gap=0.72)
footer(s, "El salto es igual que en 2D: solo cambia vy.")
nc(s, "Tope máximo: si el largo de horizontal supera maxHorizontalSpeed (15 u/s), el "
      "vector se convierte en un vector de largo 1 (normalized) y se multiplica por 15. "
      "Eso conserva la dirección pero limita la rapidez. Es el valor $40 de SMB3.\n\n"
      "Inicio del salto: si se presionó el botón de salto en este cuadro (jumpPressed) y "
      "Velma está en el suelo (grounded), vy toma el valor de jumpSpeed (13.125). "
      "Además, grounded pasa a false porque ya salió del suelo.\n\n"
      "El salto empieza siempre desde el suelo. No se puede saltar en el aire.",
   ["code_tope", "code_salto_inicio"])

# 21 ----------------------------------------------------------- gravedad
s = new_slide()
header(s, K3, "GRAVEDAD: IGUAL QUE EN 2D",
       "Mientras Velma no toca el suelo, vy baja en cada cuadro.")
shot(s, "8-proceso_salto_es_igual_que_en_2d.png", 0.62, 1.64, 6.20, 2.32)
code_img(s, "code_gravedad", 7.10, 1.64, 5.60, 3.30)
bullets(s, 0.62, 4.20, 6.20, [
    "lightGravity: gravedad suave al mantener el botón.",
    "maxFallSpeed limita la caída.",
], gap=0.70)
footer(s, "La gravedad solo cambia vy. No afecta a X ni a Z.")
nc(s, "La gravedad solo se aplica si Velma no está en el suelo.\n\n"
      "- lightGravity es true si se mantiene el botón de salto y vy es mayor que "
      "jumpHoldLimit (7.5). Es la primera parte del salto, cuando Velma sube rápido.\n"
      "- Si lightGravity es true se usa jumpGravity (14.06); si no, gravity (70.31).\n"
      "- vy = vy − G × Time.deltaTime: se resta la gravedad por cada fracción de tiempo.\n"
      "- Mathf.Max(vy, −maxFallSpeed) limita la caída a 15 u/s hacia abajo.\n\n"
      "Esto no cambió respecto a 2D porque la gravedad actúa en el eje Y, y el eje Y es "
      "el mismo en 2D y en 3D.",
   ["code_gravedad"])

# 22 ----------------------------------------------------------- salto corto y largo
s = new_slide()
header(s, K3, "SALTO CORTO Y SALTO LARGO",
       "Mantener el botón de salto hace subir más a Velma.")
fig(s, ROOT / "figuras" / "fig_salto.png", 0.62, 1.64, 7.40, 4.15)
bullets(s, 8.30, 1.76, 4.40, [
    "Toque rápido: sube 1.1 tiles.",
    "Mantener: sube 4.4 tiles.",
    "Se puede saltar desde cualquier plataforma.",
], gap=0.88)
footer(s, "La figura se calculó con la simulación del tema 8.7.1; el salto no cambió.")
notes(s,
      "Esta gráfica es la misma del tema anterior. Como la gravedad y el salto solo usan "
      "vy, funcionan igual en 3D.\n\n"
      "Si se suelta el botón pronto, la gravedad normal (70.31) frena el salto rápido y "
      "Velma sube solo 1.1 tiles. Si se mantiene, durante la subida se usa la gravedad "
      "suave (14.06) y Velma llega a 4.4 tiles.\n\n"
      "Un tile es una unidad de Unity (16 píxeles en SMB3).")

# 23 ----------------------------------------------------------- aplicar
s = new_slide()
header(s, K3, "APLICAR LA VELOCIDAD AL RIGIDBODY",
       "El último paso junta horizontal y vy en un Vector3.")
shot(s, "9-resultado_final_aplicado_al_rigid_body.png", 0.62, 1.64, 7.00, 0.75)
code_img(s, "code_aplicar_3d", 0.62, 2.70, 7.00, 0.95)
tbl(s, 0.62, 3.95, 7.00, [
    ("Vector3", "Toma el valor de", "Eje"),
    ("x", "horizontal.x", "Izquierda y derecha"),
    ("y", "vy", "Arriba y abajo"),
    ("z", "horizontal.y", "Fondo y cámara"),
], [1.50, 2.50, 3.00], row_h=0.46)
tip(s, 8.00, 1.64, 4.71, 2.20, "UNITY 6",
    "La propiedad se llama linearVelocity. Antes se llamaba velocity.")
footer(s, "El script decide la velocidad y Unity mueve al objeto y revisa los choques.")
nc(s, "Este es el último paso de Update. Se arma un Vector3 con tres números: x, y y z.\n\n"
      "- x es horizontal.x: velocidad hacia los lados.\n"
      "- y es vy: velocidad vertical, la del salto y la gravedad.\n"
      "- z es horizontal.y: velocidad hacia el fondo o hacia la cámara.\n\n"
      "En 2D la tercera componente era siempre 0. Aquí ya no.\n\n"
      "En Unity 6 la propiedad se llama Rigidbody.linearVelocity. En versiones anteriores "
      "se llamaba velocity. No usamos AddForce porque el script calcula directamente la "
      "velocidad que quiere.",
   ["code_aplicar_3d"])

# 24 ----------------------------------------------------------- flujo
s = new_slide()
header(s, K3, "EL ORDEN COMPLETO DE UPDATE",
       "Ocho pasos se repiten en cada cuadro.")
pasos = ["Leer A, D, W y S", "Armar y normalizar", "Leer los botones", "Suelo y topSpeed",
         "Mover en X y Z", "Iniciar salto", "Gravedad en Y", "Aplicar al Rigidbody"]
cols = [0.62, 3.80, 6.98, 10.16]
for i, name in enumerate(pasos):
    x = cols[i % 4]
    y = 1.70 if i < 4 else 2.95
    card(s, x, y, 2.55, 0.90, ORANGE if i < 7 else GREEN)
    text(s, x + 0.20, y + 0.12, 0.40, 0.30, str(i + 1), role="card_number",
         color=ORANGE_TEXT if i < 7 else GREEN)
    text(s, x + 0.20, y + 0.44, 2.25, 0.30, name, role="body_strong")
    if i % 4 != 3:
        text(s, x + 2.58, y + 0.22, 0.60, 0.40, "→", role="card_title_sm",
             color=BODY, align=PP_ALIGN.CENTER)
bullets(s, 0.62, 4.30, 12.0, [
    "El orden importa: el salto se decide antes de la gravedad.",
    "La parte nueva en 3D son los pasos 1, 2 y 5.",
], gap=0.70)
footer(s, "Los pasos 3, 4, 6, 7 y 8 son iguales o casi iguales que en el script 2D.")
notes(s,
      "Resumen del orden de Update en S5_VelmaWalk_3D:\n\n"
      "1. Leer las teclas A, D, W y S. A y D también voltean el sprite.\n"
      "2. Armar el vector input y normalizarlo si es mayor que 1.\n"
      "3. Leer los botones de correr y de salto.\n"
      "4. Poner vy en 0 si está en el suelo, y elegir topSpeed.\n"
      "5. Mover horizontal: acelerar, frenar o conservar, y aplicar el tope máximo.\n"
      "6. Iniciar el salto si se presionó el botón en el suelo.\n"
      "7. Aplicar la gravedad si está en el aire.\n"
      "8. Entregar horizontal y vy al Rigidbody.\n\n"
      "El orden importa. Por ejemplo, el salto se decide antes de la gravedad: en el "
      "cuadro del salto, vy ya vale jumpSpeed cuando se resta la gravedad.")

# 25 ----------------------------------------------------------- reset
s = new_slide()
header(s, K3, "REINICIAR A VELMA",
       "El botón de la interfaz regresa al personaje al inicio.")
code_img(s, "code_reset_3d", 0.62, 1.64, 7.30, 2.45)
bullets(s, 8.20, 1.76, 4.50, [
    "FreezeAll detiene todo un momento.",
    "Se limpia la rotación y se mueve a (0, 1, 0).",
    "Se vuelve a FreezeRotation.",
], gap=0.88)
tip(s, 0.62, 4.40, 12.09, 1.30, "DETALLE",
    "Se mueve rb.position, no transform.position. Así Unity no se confunde con la física.")
footer(s, "Esta función se llama desde el evento OnClick del botón.")
nc(s, "ResetButtonClick es una función pública. El botón de la escena la llama con su "
      "evento OnClick.\n\n"
      "1. Se congela todo con FreezeAll para que Unity no mueva al personaje mientras "
      "lo reiniciamos.\n"
      "2. rb.rotation = Quaternion.identity quita cualquier rotación.\n"
      "3. rb.position se pone en (0, 1, 0): el punto de inicio, un poco arriba del piso.\n"
      "4. Se vuelve a poner FreezeRotation para que Velma pueda moverse otra vez.\n\n"
      "Ojo: en la versión 2D esta línea final también congelaba la posición Z. En 3D ya no.",
   ["code_reset_3d"])

# 26 ----------------------------------------------------------- limites
s = new_slide()
header(s, K3, "LÍMITES Y MEJORAS",
       "El script funciona, pero tiene detalles que conviene mejorar.")
tbl(s, 0.62, 1.64, 12.09, [
    ("Límite", "Por qué pasa", "Mejora"),
    ("using UnityEditor.U2D", "Solo existe en el Editor y rompe la compilación del juego.", "Borrar esa línea."),
    ("Dirección respecto al mundo", "W siempre va al +Z, aunque la cámara gire.", "Mover según la cámara."),
    ("Sprite plano en 3D", "Se ve de lado si la cámara gira.", "Hacer que mire a la cámara."),
    ("Salto estricto", "Pulsar tarde en el borde no salta.", "Agregar coyote time."),
    ("Variable cayendo", "No se usa en ningún lugar.", "Borrarla."),
], [3.20, 5.60, 3.29], row_h=0.62)
footer(s, "Estas mejoras no se hicieron para no cambiar el script de la clase.")
notes(s,
      "Límites que se encontraron al revisar el código:\n\n"
      "- using UnityEditor.U2D: es un espacio de nombres que solo existe dentro del "
      "Editor. Funciona al probar en Unity, pero al compilar el juego (Build) da error. "
      "El script no lo necesita y se puede borrar.\n"
      "- Dirección fija: W siempre mueve hacia +Z. Con una cámara fija está bien. Si la "
      "cámara gira, el control se siente raro. Se puede mover a Velma según el frente de "
      "la cámara.\n"
      "- El sprite es un plano 2D. Si la cámara gira se verá de lado. Una mejora es "
      "usar un billboard (que el sprite siempre mire a la cámara).\n"
      "- Coyote time: dar unos milisegundos para saltar después de salir del borde de una "
      "plataforma.\n"
      "- La variable cayendo viene del script del cubo y no se usa.\n\n"
      "Se dejaron como están porque este es el script que se hizo en clase.")

# 27 ----------------------------------------------------------- resumen
s = new_slide()
header(s, K3, "RESUMEN: 2D CONTRA 3D", "Cuatro ideas para recordar.")
items = [
    ("01", "UN VECTOR", "horizontal guarda X y Z. Reemplaza a vx.", ORANGE),
    ("02", "NORMALIZAR", "La diagonal mide 1.41. Se reduce a 1 para no ir más rápido.", BLUE),
    ("03", "SIN FREEZE Z", "En Start solo se congela la rotación.", GREEN),
    ("04", "TODO LO DEMÁS IGUAL", "Salto, gravedad y suelo usan el eje Y, que no cambió.", PINK),
]
for i, (num, title, desc, color) in enumerate(items):
    x = 0.62 + (i % 2) * 6.17
    y = 1.70 + (i // 2) * 2.00
    card(s, x, y, 5.92, 1.80, color)
    text(s, x + 0.25, y + 0.20, 0.60, 0.30, num, role="card_number", color=color)
    text(s, x + 0.25, y + 0.62, 5.40, 0.40, title, role="card_title_sm")
    text(s, x + 0.25, y + 1.08, 5.40, 0.55, desc, role="note", color=BODY, line_spacing=1.0)
footer(s, "Con unos cuantos cambios, el mismo control sirve para 2D y para 3D.")
notes(s,
      "Resumen del tema.\n\n"
      "1. Un vector: horizontal es un Vector2 que guarda la velocidad en X y en Z.\n"
      "2. Normalizar: la diagonal no debe ser más rápida, así que se reduce a largo 1.\n"
      "3. En Start se deja de congelar la posición Z.\n"
      "4. El salto, la gravedad y la detección del suelo no cambian, porque trabajan sobre "
      "el eje Y.\n\n"
      "Con estos cambios, las mismas velocidades de Super Mario Bros. 3 funcionan en un "
      "espacio 3D.")

# ---- cierre
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
text(s, 0.0, 1.55, 13.33, 1.35, "¿PREGUNTAS?", role="closing", align=PP_ALIGN.CENTER)
text(s, 0.0, 3.18, 13.33, 0.38, "Velma ya camina en X y en Z.", role="subtitle",
     align=PP_ALIGN.CENTER)
text(s, 0.0, 3.72, 13.33, 0.38, "Mismas velocidades de Mario, ahora con profundidad.",
     role="note", color=BODY, align=PP_ALIGN.CENTER)
picture_fit(s, ROOT / "decor" / "star.png", 1.55, 2.30, 0.85, 0.85, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 3.60, 4.15, 0.75, 0.75, border=False)
picture_fit(s, ROOT / "decor" / "tree-small.png", 1.10, 4.36, 1.15, 2.06, border=False)
picture_fit(s, ROOT / "decor" / "cloud-low.png", 9.85, 4.68, 2.65, 1.42, border=False)
notes(s, "Cierre del tema 8.7.2. Recuerda: el control 3D es el control 2D con un vector "
         "horizontal en lugar de un número, una diagonal normalizada y sin congelar el "
         "eje Z.")

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
