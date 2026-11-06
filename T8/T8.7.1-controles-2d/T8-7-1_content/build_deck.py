#!/usr/bin/env python3
"""Construye T8.7.1 - Controles 2D estilo Mario.

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
    "DECK_OUT", str(ROOT.parent / "T8.7.1-Controles-2D-Mario.pptx")
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
CS = "Assets/Scripts/escena5_controles/S5_VelmaWalk_2D.cs"
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
prs.core_properties.title = "T8.7.1 · Controles 2D estilo Mario"
prs.core_properties.author = "TC2005B · Construcción de Software"
prs.core_properties.subject = "Control 2D con aceleración, salto y gravedad en Unity"
prs.core_properties.keywords = "Unity, C#, Rigidbody, SMB3, salto, gravedad, TC2005B"
prs.core_properties.language = "es-MX"

# ---- portada
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
rect(s, 0.62, 0.32, 0.09, 0.09, ORANGE)
text(s, 0.81, 0.28, 10.0, 0.22, "8.7.1 · INTERACCIÓN HUMANO-COMPUTADORA", role="label")
text(s, 0.62, 0.92, 6.00, 2.70, "CONTROLES\nDE MARIO\nEN 2D", role="section", line_spacing=0.92)
text(s, 0.62, 3.64, 5.70, 0.80,
     "Cómo pasar de un cubo con Translate a un personaje 2D que acelera, frena y salta.",
     role="subtitle", line_spacing=1.02)
text(s, 0.62, 4.75, 5.55, 0.72,
     "Control inspirado en Super Mario Bros. 3, hecho con Rigidbody y C#.",
     role="note", color=BODY, line_spacing=1.02)
text(s, 0.62, 5.80, 5.40, 0.28, "TC2005B · Construcción de Software", role="note")
text(s, 0.62, 6.16, 5.40, 0.28, "Unity · C# · S5_VelmaWalk_2D", role="note", color=MUTED)
rect(s, 6.55, 0.66, 6.18, 4.95, DARK)
picture_fill(s, ROOT / "img" / "cover_sprite.png", 6.75, 0.86, 5.78, 4.55)
rect(s, 6.75, 0.86, 5.78, 4.55, None, WHITE, 1.2)
pill(s, 6.95, 0.72, 1.55, "UNITY · C#", WHITE, DARK)
picture_fit(s, ROOT / "decor" / "star.png", 0.55, 6.30, 0.75, 0.75, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 11.55, 6.10, 0.95, 0.95, border=False)
notes(s,
      "Bienvenida al tema 8.7.1. En T8.6.2 el personaje ya era un sprite 2D, pero se "
      "movía como un cubo. Hoy cambiamos el control para que se sienta como un juego "
      "de plataformas.\n\n"
      "Primero veremos por qué el control simple no basta. Después preparamos la "
      "escena y, al final, leemos el script S5_VelmaWalk_2D línea por línea.")

# ---- agenda
s = new_slide()
header(s, "HOY", "LO QUE VEREMOS HOY",
       "Tres bloques llevan al personaje de un cubo simple a un control 2D.")
rows = [
    ("01", "DEL CUBO AL CONTROL 2D", "Qué hace S5_CubeMove y qué le falta para sentirse como Mario.", ORANGE),
    ("02", "PREPARAR LA ESCENA", "Quitar el cubo, agregar Rigidbody y Box Collider, y duplicar el script.", BLUE),
    ("03", "EL CÓDIGO PASO A PASO", "Variables, Start, Update, salto, gravedad, suelo y reinicio.", GREEN),
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
      "1. Del cubo al control 2D: el control simple (S5_CubeMove) y por qué un juego "
      "de plataformas necesita aceleración, frenado, salto variable y gravedad propia.\n"
      "2. Preparar la escena: en las capturas se ve cómo se quita el cubo, se agregan "
      "el Rigidbody y el Box Collider, y se duplica el script.\n"
      "3. El código: se explica S5_VelmaWalk_2D en el mismo orden en que se escribió.\n\n"
      "Las capturas de pantalla siguen el orden real del trabajo en Unity.")

# ---- seccion 01
s = section_slide(prs, "01", "DEL CUBO AL\nCONTROL 2D",
                  "El control simple funciona, pero no se siente como un juego de plataformas.",
                  "TRANSLATE · ACELERACIÓN · SMB3", ORANGE)
notes(s, "Bloque 1. Empezamos con lo que ya teníamos: un cubo que se mueve con una "
         "línea de código. Después vemos qué le falta.")

# 2 -------------------------------------------------------- punto de partida
s = new_slide()
header(s, "BLOQUE 01 · PUNTO DE PARTIDA", "EL PUNTO DE PARTIDA: S5_CUBEMOVE",
       "El control simple mueve al personaje con una sola línea.")
code_img(s, "code_cubemove", 0.62, 1.64, 5.40, 4.40)
bullets(s, 6.45, 1.80, 6.25, [
    "Lee las teclas A, D, W y S y arma un vector de movimiento.",
    "transform.Translate mueve el objeto a una velocidad fija.",
    "El salto es un impulso con AddForce y usa la gravedad de Unity.",
    "Sirve para probar, pero es un control pensado para 3D.",
], gap=0.92)
footer(s, "Es simple y directo, pero no tiene aceleración ni frenado.")
nc(s, "S5_CubeMove es el control que usamos hasta ahora. En cada Update lee el "
      "teclado y llena un vector llamado movement. Después llama a "
      "transform.Translate, que mueve el objeto sin pasar por la física.\n\n"
      "El salto sí usa física: AddForce con ForceMode.Impulse da un golpe hacia "
      "arriba. La bandera estaEnSuelo evita saltar en el aire.\n\n"
      "Es un buen punto de partida porque es corto y fácil de entender. Los "
      "fragmentos de la imagen están acortados; el archivo completo está en la carpeta "
      "codigo.", ["code_cubemove"], path=CS_CUBE)

# 3 -------------------------------------------------------- por que no basta
s = new_slide()
header(s, "BLOQUE 01 · PUNTO DE PARTIDA", "POR QUÉ NO BASTA PARA UN JUEGO 2D",
       "Un juego de plataformas necesita que el personaje tenga peso y ritmo.")
tbl(s, 0.62, 1.72, 12.09, [
    ("Acción", "Control simple", "Control tipo Mario"),
    ("Arrancar", "Llega a la velocidad máxima al instante.", "Acelera poco a poco."),
    ("Frenar", "Se detiene de golpe.", "Frena con suavidad."),
    ("Correr", "No existe.", "Una segunda velocidad con un botón."),
    ("Saltar", "Siempre sube lo mismo.", "Sube más si mantienes el botón."),
    ("Caer", "Usa la gravedad de Unity.", "Usa una gravedad propia que tú ajustas."),
], [2.2, 5.0, 4.89], row_h=0.62)
footer(s, "Cambiamos Translate por velocidades que el script calcula en cada cuadro.")
notes(s,
      "Comparación entre los dos controles.\n\n"
      "Con Translate el personaje tiene una sola velocidad y no tiene inercia: "
      "arranca y se detiene al instante. En Mario el personaje acelera, frena, corre "
      "y controla la altura del salto.\n\n"
      "La idea del nuevo script es guardar dos variables, vx y vy (velocidad "
      "horizontal y vertical), cambiarlas poco a poco en cada cuadro y entregárselas "
      "al Rigidbody.")

# 4 -------------------------------------------------------- unidades
s = new_slide()
header(s, "BLOQUE 01 · SMB3", "DE PÍXELES DE SMB3 A UNIDADES DE UNITY",
       "SMB3 mide píxeles por cuadro. Unity mide unidades por segundo.")
tbl(s, 0.62, 1.70, 7.55, [
    ("Variable", "Juego", "px/cuadro", "Unity"),
    ("walkSpeed", "$18", "1.5", "5.625"),
    ("runSpeed", "$28", "2.5", "9.375"),
    ("acceleration", "—", "0.0546875", "12.3046875"),
    ("jumpSpeed", "$38", "3.5", "13.125"),
    ("gravity", "—", "5/16", "70.3125"),
    ("jumpGravity", "—", "1/16", "14.0625"),
    ("jumpHoldLimit", "$20", "2", "7.5"),
    ("maxFallSpeed", "$40", "4", "15"),
], [2.25, 1.0, 1.85, 2.45], row_h=0.44)
bullets(s, 8.55, 1.76, 4.15, [
    "SMB3 suma una aceleración en cada cuadro.",
    "Hay un tope para caminar y otro para correr.",
], gap=0.92)
tip(s, 8.55, 3.70, 4.15, 1.35, "FÓRMULAS",
    "velocidad = px/cuadro × 60 ÷ 16\naceleración = px/cuadro² × 3600 ÷ 16")
footer(s, "1 unidad de Unity = 1 tile = 16 píxeles. El juego corre a 60 cuadros por segundo.")
notes(s,
      "Los números del script no son inventados. Vienen de la física de Super Mario "
      "Bros. 3 en el NES, que guarda las velocidades en píxeles por cuadro. El signo $ "
      "indica un número hexadecimal: $18 vale 24, y 24 entre 16 da 1.5 píxeles por "
      "cuadro.\n\n"
      "Para pasar a Unity usamos dos reglas: 1 unidad = 1 tile = 16 píxeles, y el "
      "juego corre a 60 cuadros por segundo.\n"
      "- Velocidad: px/cuadro × 60 ÷ 16. Ejemplo: 1.5 × 60 ÷ 16 = 5.625.\n"
      "- Aceleración: px/cuadro² × 3600 ÷ 16. Ejemplo: 0.0546875 × 3600 ÷ 16 = 12.3046875.\n\n"
      "El archivo codigo/convertir_unidades.py repite estas cuentas y comprueba que "
      "coinciden con los valores del script.\n\n"
      "Fuente de las velocidades de caminar y correr: TASVideos, 'Speed & Pixel "
      "Position Mechanics' de Super Mario Bros. 3 (tasvideos.org/GameResources/NES/SuperMarioBros3).")

# ---- seccion 02
s = section_slide(prs, "02", "PREPARAR\nLA ESCENA",
                  "Quitamos el cubo y dejamos que el Rigidbody mueva a Velma.",
                  "RIGIDBODY · BOX COLLIDER · SCRIPT", BLUE)
notes(s, "Bloque 2. Antes de escribir código dejamos la escena lista. Las capturas "
         "siguen el orden en que se hizo el trabajo en Unity.")

# 5 -------------------------------------------------------- quitar cubo
s = new_slide()
header(s, "BLOQUE 02 · ESCENA", "QUITAR EL CUBO DE LA ESCENA",
       "Velma deja de ser hija del cubo y se convierte en el personaje.")
shot(s, "1-elimando-el-cubo-dela-escena.png", 0.62, 1.70, 3.40, 3.10)
cap(s, 0.62, 4.90, 3.6, "Jerarquía de escena5_controles.")
steps(s, 4.60, 1.85, 8.1, [
    "Abre la escena escena5_controles.",
    "Borra el cubo de la Jerarquía.",
    "Deja a velma_sprite_walk como objeto principal del personaje.",
    "velma_sprite_walk_3D queda apagado: se usará en el tema 3D.",
], gap=0.88)
footer(s, "La cámara debe seguir ahora a velma_sprite_walk: revisa el campo Target.")
notes(s,
      "En T8.6.2 el sprite era hijo del cubo: el cubo tenía el Rigidbody y el sprite "
      "solo se veía. Ahora el sprite es el personaje, así que el cubo ya no hace falta.\n\n"
      "En la Jerarquía se ven Main Camera, Directional Light, Global Volume, Plane, "
      "Canvas, EventSystem, Enemigo, Spawner, velma_sprite_walk y velma_sprite_walk_3D. "
      "El último aparece en gris porque está desactivado.\n\n"
      "Al borrar el cubo, el Target del script de la cámara debe apuntar a "
      "velma_sprite_walk. Si el campo queda vacío, la cámara no sigue a nadie.")

# 6 -------------------------------------------------------- rigidbody
s = new_slide()
header(s, "BLOQUE 02 · ESCENA", "AGREGAR UN RIGIDBODY",
       "Selecciona velma_sprite_walk y usa Add Component > Rigidbody.")
shot(s, "2-asignando_rigidbody_velma_sprite_walk_gameobject.png", 0.62, 1.70, 5.60, 4.00)
bullets(s, 6.55, 1.80, 6.15, [
    "Use Gravity apagado: la gravedad la calcula el script.",
    "Interpolate suaviza el movimiento entre cuadros.",
    "Continuous evita atravesar el suelo.",
    "Freeze Position Z deja al personaje en el plano 2D.",
    "Freeze Rotation X, Y y Z evita que Velma gire.",
], gap=0.74)
footer(s, "El Rigidbody es el componente que mueve al objeto y detecta choques.")
notes(s,
      "Un Rigidbody permite que Unity mueva el objeto con física y que lo detecte en "
      "las colisiones.\n\n"
      "Valores de la captura: Mass 1, Linear Damping 0, Angular Damping 0.05, "
      "Use Gravity apagado, Is Kinematic apagado, Interpolate en Interpolate y "
      "Collision Detection en Continuous. En Constraints están marcados Freeze "
      "Position Z y Freeze Rotation X, Y y Z.\n\n"
      "Use Gravity se apaga porque la gravedad de Mario es propia: la calcula el "
      "script. Las restricciones también se escriben en Start (ver más adelante), así "
      "que el script funciona aunque se olviden en el Inspector.")

# 7 -------------------------------------------------------- box collider
s = new_slide()
header(s, "BLOQUE 02 · ESCENA", "AGREGAR UN BOX COLLIDER",
       "El collider es la forma con la que Velma choca con el piso.")
shot(s, "3-asignando_box_collider_a_velma_sprite_walk_gameobject.png", 0.62, 1.70, 5.60, 2.50)
cap(s, 0.62, 4.30, 5.6, "Add Component > Box Collider.")
bullets(s, 6.55, 1.80, 6.15, [
    "Size: X 0.48, Y 0.75 y Z 0.1. Es una caja delgada.",
    "Center en 0, 0, 0: la caja queda centrada en el sprite.",
    "Is Trigger apagado: queremos chocar, no atravesar.",
    "Sin collider, el Rigidbody no detecta el piso.",
], gap=0.84)
footer(s, "El tamaño de la caja se ajusta al cuerpo del sprite, no al cuadro completo.")
notes(s,
      "El Box Collider es una caja invisible. Unity usa esa caja para saber cuándo "
      "Velma toca el piso, una pared o un enemigo.\n\n"
      "Valores de la captura: Is Trigger apagado, Center (0, 0, 0) y Size "
      "(0.48, 0.75, 0.1). La caja es delgada en Z porque el juego es 2D.\n\n"
      "Si Is Trigger estuviera activo, Velma atravesaría el piso y no se llamarían "
      "las funciones OnCollisionEnter y OnCollisionStay del script.")

# 8 -------------------------------------------------------- duplicar script
s = new_slide()
header(s, "BLOQUE 02 · SCRIPT", "DUPLICAR EL SCRIPT S5_CUBEMOVE",
       "No empezamos de cero: copiamos el script anterior.")
shot(s, "4-duplicando_s5_cube_move.png", 0.62, 1.70, 2.80, 2.70)
cap(s, 0.62, 4.50, 3.0, "S5_CubeMove.")
steps(s, 4.10, 1.85, 8.6, [
    "En la ventana Project, selecciona S5_CubeMove.",
    "Presiona Ctrl + D para duplicarlo.",
    "Así el script original queda intacto para comparar.",
], gap=0.90)
footer(s, "Ctrl + D crea una copia con el nombre S5_CubeMove 1.")
notes(s,
      "Duplicar el script nos deja comparar el control viejo y el nuevo. Además "
      "conserva el código que sí nos sirve, por ejemplo la lectura del teclado y el "
      "volteo del sprite.\n\n"
      "En Unity, Ctrl + D duplica el archivo seleccionado en la ventana Project.")

# 9 -------------------------------------------------------- renombrar archivo
s = new_slide()
header(s, "BLOQUE 02 · SCRIPT", "CAMBIAR EL NOMBRE DEL ARCHIVO",
       "La copia se renombra como S5_VelmaWalk_2D.")
shot(s, "5-cambiando_nombre_al_script_duplicado.png", 0.62, 1.70, 2.60, 3.00)
cap(s, 0.62, 4.80, 3.0, "S5_VelmaWalk_2D.")
steps(s, 4.10, 1.85, 8.6, [
    "Selecciona la copia y presiona F2.",
    "Escribe el nombre nuevo: S5_VelmaWalk_2D.",
    "Presiona Enter para confirmar.",
], gap=0.90)
footer(s, "El prefijo S5 indica la escena 5; 2D indica el tipo de control.")
notes(s,
      "El nombre S5_VelmaWalk_2D sigue la regla del proyecto: S5 es la escena 5, "
      "Velma es el personaje, Walk es la acción y 2D es el tipo de control. Más "
      "adelante habrá una versión S5_VelmaWalk_3D.\n\n"
      "En Unity, F2 permite renombrar el archivo seleccionado en la ventana Project "
      "(en Mac se usa Enter).")

# 10 ------------------------------------------------------- renombrar clase
s = new_slide()
header(s, "BLOQUE 02 · SCRIPT", "CAMBIAR EL NOMBRE DE LA CLASE",
       "El nombre de la clase debe ser igual al del archivo.")
shot(s, "6-cambiando_nombre_al_script_duplicado_dentro_del_codigo.png", 0.62, 1.70, 6.70, 2.90)
cap(s, 0.62, 4.70, 6.7, "En public class, el nombre resaltado.")
bullets(s, 7.70, 1.80, 5.00, [
    "Cambia S5_CubeMove por S5_VelmaWalk_2D.",
    "Si los nombres no coinciden, Unity no deja agregar el script.",
    "Después borra el código del cubo y escribe el nuevo.",
], gap=0.92)
footer(s, "Regla de Unity: un MonoBehaviour se llama igual que su archivo .cs.")
notes(s,
      "Dentro del archivo, la línea public class S5_CubeMove : MonoBehaviour debe "
      "decir public class S5_VelmaWalk_2D : MonoBehaviour. Unity busca la clase con el "
      "mismo nombre que el archivo. Si no coinciden, aparece un error y el script no se "
      "puede agregar a un objeto.\n\n"
      "En la captura también se ven las primeras líneas con using. Hay una que "
      "conviene borrar: using UnityEditor.U2D. Se explica en la diapositiva de límites "
      "y mejoras.")

# ---- seccion 03
s = section_slide(prs, "03", "EL CÓDIGO\nPASO A PASO",
                  "Cada parte de S5_VelmaWalk_2D, en el orden en que se escribió.",
                  "VARIABLES · START · UPDATE · SALTO · SUELO", GREEN)
notes(s, "Bloque 3. Leemos el script completo en el mismo orden del archivo: "
         "variables, Start, Update y colisiones.")

K = "BLOQUE 03 · CÓDIGO"

# 11 ------------------------------------------------------- vars velocidad
s = new_slide()
header(s, K, "VARIABLES DE VELOCIDAD", "Cinco campos públicos que puedes cambiar en el Inspector.")
code_img(s, "code_vars_velocidad", 0.62, 1.64, 9.20, 2.00)
tbl(s, 0.62, 3.95, 12.09, [
    ("Campo", "Qué controla", "Valor"),
    ("walkSpeed", "Velocidad máxima al caminar", "5.625 unidades/s"),
    ("runSpeed", "Velocidad máxima al correr", "9.375 unidades/s"),
    ("acceleration", "Cuánto sube la velocidad en cada segundo", "12.30 unidades/s²"),
    ("braking", "Cuánto baja la velocidad al frenar", "12.30 unidades/s²"),
], [2.4, 6.0, 3.69], row_h=0.44)
nc(s, "Estas variables definen la velocidad horizontal. Son public, así que aparecen "
      "en el Inspector y se pueden ajustar sin tocar el código.\n\n"
      "[Header] solo pone un título en el Inspector para agrupar los campos.\n\n"
      "walkSpeed y runSpeed son los topes de velocidad. acceleration y braking dicen "
      "qué tan rápido cambia la velocidad: una aceleración de 12.3 unidades por "
      "segundo al cuadrado tarda 0.46 s en llegar a walkSpeed.\n\n"
      "Los comentarios muestran el valor original de SMB3 en píxeles por cuadro.",
   ["code_vars_velocidad"])

# 12 ------------------------------------------------------- vars salto
s = new_slide()
header(s, K, "VARIABLES DE SALTO Y GRAVEDAD", "Cinco campos más definen cómo sube y cómo cae Velma.")
code_img(s, "code_vars_salto", 0.62, 1.64, 9.00, 2.20)
tbl(s, 0.62, 4.00, 12.09, [
    ("Campo", "Qué controla", "Valor"),
    ("jumpSpeed", "Velocidad hacia arriba al empezar el salto", "13.125 u/s"),
    ("gravity", "Gravedad normal: hace caer a Velma", "70.3125 u/s²"),
    ("jumpGravity", "Gravedad suave mientras subes con el botón", "14.0625 u/s²"),
    ("jumpHoldLimit", "Bajo esta velocidad termina la gravedad suave", "7.5 u/s"),
    ("maxFallSpeed", "Velocidad máxima de caída", "15 u/s"),
], [2.4, 6.6, 3.09], row_h=0.42)
nc(s, "jumpSpeed es la velocidad con la que Velma sale del suelo. gravity es la "
      "aceleración hacia abajo. jumpGravity es una gravedad mucho más débil que solo "
      "se usa mientras el jugador mantiene el botón de salto y Velma sube rápido.\n\n"
      "jumpHoldLimit es el límite de esa ayuda: cuando la velocidad vertical baja de "
      "7.5, la gravedad vuelve a ser la normal. maxFallSpeed evita que la caída se "
      "acelere sin parar.\n\n"
      "Las unidades son u/s (unidades por segundo) y u/s² (unidades por segundo al "
      "cuadrado).",
   ["code_vars_salto"])

# 13 ------------------------------------------------------- vars privadas
s = new_slide()
header(s, K, "VARIABLES PRIVADAS", "El script guarda su propio estado en seis campos.")
code_img(s, "code_vars_privadas", 0.62, 1.70, 5.20, 2.40)
tip(s, 0.62, 4.40, 5.20, 1.45, "private",
    "No aparecen en el Inspector. Solo las usa este script.")
tbl(s, 6.20, 1.70, 6.51, [
    ("Campo", "Para qué sirve"),
    ("rb", "El Rigidbody de Velma."),
    ("vx", "Velocidad horizontal."),
    ("vy", "Velocidad vertical."),
    ("grounded", "Es true si pisa el suelo."),
    ("cayendo", "Viene del cubo; aún no se usa."),
    ("sprite_render", "Dibuja el sprite y lo voltea."),
], [2.15, 4.36], row_h=0.58)
nc(s, "vx y vy son lo más importante: el script calcula la velocidad y después se "
      "la entrega al Rigidbody. Por eso no usamos AddForce.\n\n"
      "grounded dice si Velma está en el suelo. Se actualiza en las funciones de "
      "colisión que veremos más adelante.\n\n"
      "cayendo se heredó de S5_CubeMove y todavía no se usa. sprite_render guarda el "
      "componente SpriteRenderer para poder voltear la imagen con flipX.",
   ["code_vars_privadas"])

# 14 ------------------------------------------------------- Start
s = new_slide()
header(s, K, "START: PREPARAR EL RIGIDBODY", "Start se ejecuta una vez, antes del primer cuadro.")
code_img(s, "code_start", 0.62, 1.64, 6.90, 4.30)
bullets(s, 7.85, 1.76, 4.85, [
    "GetComponent busca los componentes del mismo objeto.",
    "useGravity = false: la gravedad la calcula el script.",
    "Interpolate suaviza el movimiento.",
    "Continuous evita atravesar el suelo.",
    "constraints congela la rotación y la posición en Z.",
], gap=0.82)
footer(s, "El símbolo | une varias restricciones en un solo valor.")
nc(s, "En Start se obtienen los componentes y se configura el Rigidbody por código. "
      "Así el script funciona aunque los valores del Inspector se cambien por "
      "accidente.\n\n"
      "- GetComponent<Rigidbody>() y GetComponent<SpriteRenderer>() buscan los "
      "componentes del mismo objeto.\n"
      "- useGravity = false apaga la gravedad de Unity.\n"
      "- interpolation = Interpolate suaviza el movimiento entre cuadros de física.\n"
      "- collisionDetectionMode = Continuous evita que Velma atraviese el piso cuando "
      "se mueve rápido.\n"
      "- constraints congela las tres rotaciones y la posición en Z. El símbolo | une "
      "las restricciones. Un sprite 2D no debe girar ni salir del plano.",
   ["code_start"])

# 15 ------------------------------------------------------- Update teclado
s = new_slide()
header(s, K, "UPDATE: LEER EL TECLADO", "Update se ejecuta en cada cuadro del juego.")
code_img(s, "code_update_teclado", 0.62, 1.64, 7.30, 4.40)
bullets(s, 8.20, 1.76, 4.50, [
    "Keyboard.current es el teclado. Si es null, se sale.",
    "input vale 1 con D o →, y -1 con A o ←.",
    "Sin teclas, input vale 0.",
    "flipX voltea el sprite hacia donde camina.",
], gap=0.92)
footer(s, "isPressed es true todo el tiempo que la tecla está abajo.")
nc(s, "Update corre una vez por cuadro. Primero se obtiene el teclado con "
      "Keyboard.current; si no hay teclado, la función termina con return.\n\n"
      "La variable input resume la dirección: +1 hacia la derecha, -1 hacia la "
      "izquierda y 0 si no hay tecla. Si se presionan las dos teclas a la vez, se "
      "suman y quedan en 0.\n\n"
      "Al mismo tiempo se voltea el sprite con flipX: false mira a la derecha y true "
      "mira a la izquierda. La comprobación sprite_render != null evita un error si "
      "el objeto no tiene SpriteRenderer.\n\n"
      "El código usa el nuevo Input System (UnityEngine.InputSystem). La imagen "
      "muestra el código sin la sangría de la función.",
   ["code_update_teclado"])

# 16 ------------------------------------------------------- banderas
s = new_slide()
header(s, K, "BANDERAS DE LOS BOTONES", "Tres valores true o false resumen los botones.")
code_img(s, "code_banderas", 0.62, 1.64, 6.30, 3.00)
tip(s, 0.62, 4.85, 6.30, 1.05, "isPressed y wasPressedThisFrame",
    "isPressed: mientras está abajo. wasPressedThisFrame: solo un cuadro.")
bullets(s, 7.30, 1.80, 5.40, [
    "runHeld: Shift o X permiten correr.",
    "jumpPressed: Espacio o Z, solo el cuadro en que se presionan.",
    "jumpHeld: Espacio o Z, mientras sigan presionadas.",
], gap=0.92)
nc(s, "Estas tres variables se calculan una vez por cuadro y se usan más abajo.\n\n"
      "- runHeld es true mientras se mantiene Shift o X.\n"
      "- jumpPressed es true solo en el cuadro exacto en que se presiona Espacio o Z. "
      "Sirve para iniciar el salto una sola vez.\n"
      "- jumpHeld es true mientras la tecla sigue abajo. Sirve para controlar la "
      "altura del salto.\n\n"
      "El operador || significa 'o'. En el archivo original cada bandera está en una "
      "sola línea; en la imagen se partieron para que se lean mejor.",
   ["code_banderas"])

# 17 ------------------------------------------------------- suelo y topSpeed
s = new_slide()
header(s, K, "SUELO Y VELOCIDAD MÁXIMA", "Dos líneas preparan los cálculos del cuadro.")
code_img(s, "code_suelo_top", 0.62, 1.64, 7.00, 2.60)
tip(s, 0.62, 4.55, 7.00, 1.30, "Operador ?:",
    "condición ? valor si es verdad : valor si es falso")
bullets(s, 8.00, 1.80, 4.70, [
    "Si está en el suelo y no sube, vy se queda en 0.",
    "Así la gravedad no acumula velocidad de caída.",
    "topSpeed es el tope: correr o caminar.",
], gap=0.92)
nc(s, "Primera línea: si Velma está en el suelo y su velocidad vertical no es "
      "positiva, vy se pone en 0. Sin esta línea, la gravedad seguiría restando "
      "velocidad mientras Velma está parada, y al caminar fuera de un borde caería "
      "demasiado rápido.\n\n"
      "Segunda línea: topSpeed elige el tope de velocidad. Si runHeld es true, usa "
      "runSpeed; si no, usa walkSpeed. El operador ?: es un if corto.\n\n"
      "El suelo se detecta con las funciones OnCollisionEnter, OnCollisionStay y "
      "OnCollisionExit, que se explican en la diapositiva Detectar el suelo.",
   ["code_suelo_top"])

# 18 ------------------------------------------------------- acelerar
s = new_slide()
header(s, K, "ACELERAR Y FRENAR CON TECLA", "Si hay una tecla, vx se acerca a una velocidad meta.")
code_img(s, "code_horizontal", 0.62, 1.64, 6.50, 4.40)
bullets(s, 7.45, 1.76, 5.25, [
    "target es la meta: input × topSpeed.",
    "Misma dirección y más rápido que el tope: frena en el suelo o conserva en el aire.",
    "En otro caso, acelera hacia target.",
    "MoveTowards cambia vx sin pasarse de target.",
], gap=0.98)
footer(s, "Mathf.Sign devuelve 1 si el número es positivo y -1 si es negativo.")
nc(s, "Este bloque se ejecuta cuando hay una tecla presionada (input distinto de 0).\n\n"
      "target es la velocidad que Velma quiere alcanzar: input × topSpeed. Con la "
      "tecla derecha y correr, target vale 9.375; con la izquierda, -9.375.\n\n"
      "Caso 1: Velma ya va en la misma dirección y más rápido que el tope (por "
      "ejemplo, venía corriendo y soltó Shift). En el suelo frena con braking. En el "
      "aire no hace nada: conserva su impulso, como en Mario.\n\n"
      "Caso 2: en cualquier otra situación (parte del reposo, va más lenta que el tope "
      "o cambia de dirección) acelera hacia target con acceleration.\n\n"
      "Mathf.MoveTowards(vx, target, delta) acerca vx a target sumando o restando "
      "como máximo delta. Como delta = aceleración × Time.deltaTime, la velocidad "
      "cambia igual en cualquier computadora.",
   ["code_horizontal"])

# 19 ------------------------------------------------------- frenar / MoveTowards
s = new_slide()
header(s, K, "FRENAR SIN TECLA Y MOVETOWARDS", "Sin tecla y en el suelo, vx baja hasta cero.")
fig(s, ROOT / "figuras" / "fig_velocidad.png", 0.62, 1.64, 6.20, 3.60)
cap(s, 0.62, 5.32, 6.2, "vx al caminar y al correr. Se suelta la tecla en 1 s.")
code_img(s, "code_sin_tecla", 7.15, 1.64, 5.55, 1.65)
bullets(s, 7.15, 3.55, 5.55, [
    "En el aire no se frena: Velma conserva su impulso.",
    "MoveTowards(a, b, d) acerca a hacia b, máximo d por cuadro.",
], gap=0.92)
footer(s, "Caminar tarda 0.46 s en llegar al tope; correr tarda 0.76 s.")
nc(s, "Este es el último caso del bloque horizontal. Si no hay tecla y Velma está en "
      "el suelo, vx baja hasta 0 con braking. Si está en el aire, no se ejecuta nada y "
      "vx se conserva.\n\n"
      "Ejemplo de MoveTowards: con vx = 0, target = 5.625 y delta = 12.3 × (1/60) = "
      "0.205, el primer cuadro da 0.205, el segundo 0.41, y así hasta llegar a 5.625 "
      "en unos 28 cuadros (0.46 s). Cuando falta menos que delta, MoveTowards devuelve "
      "target y no se pasa.\n\n"
      "La gráfica sale de codigo/simulacion_control.py, una copia en Python de la "
      "lógica del script: se mantiene la tecla 1 s y luego se suelta.",
   ["code_sin_tecla"])

# 20 ------------------------------------------------------- iniciar salto
s = new_slide()
header(s, K, "INICIAR EL SALTO", "El salto empieza solo si Velma está en el suelo.")
code_img(s, "code_salto_inicio", 0.62, 1.64, 6.60, 2.30)
bullets(s, 7.55, 1.76, 5.15, [
    "jumpPressed es true solo en el cuadro en que se presiona.",
    "grounded evita el doble salto en el aire.",
    "vy = jumpSpeed lanza a Velma hacia arriba.",
    "grounded = false deja actuar la gravedad.",
], gap=0.98)
tip(s, 0.62, 4.40, 6.60, 1.40, "Por qué no hay AddForce",
    "Asignamos la velocidad directamente. Así el salto siempre empieza igual.")
nc(s, "Cuando se presiona Espacio o Z y Velma está en el suelo, vy recibe el valor "
      "jumpSpeed (13.125 unidades por segundo hacia arriba) y grounded pasa a false.\n\n"
      "La condición jumpPressed && grounded tiene dos partes. jumpPressed hace que el "
      "salto empiece una sola vez, aunque se mantenga la tecla. grounded impide saltar "
      "otra vez mientras Velma está en el aire.\n\n"
      "Se asigna la velocidad directamente en lugar de usar AddForce para que el salto "
      "sea idéntico cada vez.",
   ["code_salto_inicio"])

# 21 ------------------------------------------------------- gravedad
s = new_slide()
header(s, K, "GRAVEDAD EN EL AIRE", "Mientras no toca el suelo, vy baja en cada cuadro.")
code_img(s, "code_gravedad", 0.62, 1.64, 6.80, 4.30)
bullets(s, 7.70, 1.76, 5.00, [
    "lightGravity: mantiene el botón y vy > 7.5.",
    "Con lightGravity resta 14.06; si no, resta 70.31.",
    "Time.deltaTime hace que no dependa de los FPS.",
    "Mathf.Max limita la caída a -15.",
], gap=0.94)
footer(s, "Fórmula: vy = vy - G × Δt. Es la fórmula de la caída libre.")
nc(s, "Este bloque solo corre cuando Velma no está en el suelo.\n\n"
      "lightGravity es true cuando se cumplen dos cosas: el jugador mantiene el "
      "botón de salto (jumpHeld) y Velma todavía sube rápido (vy mayor que "
      "jumpHoldLimit). Es la primera parte del salto.\n\n"
      "Después se resta la gravedad: vy = vy - G × Δt. Si lightGravity es true, G es "
      "jumpGravity (14.0625); si es false, G es gravity (70.3125). Con la gravedad "
      "suave, Velma sube más alto; con la normal, el salto se acorta y la caída es "
      "rápida.\n\n"
      "Time.deltaTime es el tiempo del último cuadro; sirve para que el resultado no "
      "cambie según los FPS.\n\n"
      "Mathf.Max(vy, -maxFallSpeed) pone un tope: la caída nunca pasa de -15.",
   ["code_gravedad"])

# 22 ------------------------------------------------------- salto corto/largo
s = new_slide()
header(s, K, "SALTO CORTO Y SALTO LARGO", "El mismo código produce dos alturas distintas.")
fig(s, ROOT / "figuras" / "fig_salto.png", 0.62, 1.64, 6.30, 3.62)
cap(s, 0.62, 5.34, 6.3, "Altura de Velma en tiles, con 60 cuadros por segundo.")
bullets(s, 7.30, 1.80, 5.40, [
    "Toque rápido: solo actúa gravity. Sube cerca de 1.1 tiles.",
    "Botón mantenido: la gravedad suave dura 0.4 s. Sube cerca de 4.4 tiles.",
    "Soltar el botón a tiempo permite controlar el salto.",
], gap=1.05)
footer(s, "Los valores salen de la simulación en codigo/simulacion_control.py.")
notes(s,
      "La gráfica compara dos saltos con los mismos parámetros.\n\n"
      "Toque rápido: el jugador suelta el botón de inmediato. Solo actúa gravity "
      "(70.3125). Velma sube hasta cerca de 1.1 tiles y cae.\n\n"
      "Botón mantenido: mientras vy sea mayor que 7.5, actúa jumpGravity (14.0625). "
      "Pasar de 13.125 a 7.5 tarda (13.125 - 7.5) ÷ 14.0625 = 0.4 s. Después vuelve "
      "gravity y Velma termina de subir. La altura total es cerca de 4.4 tiles.\n\n"
      "Esta es la clave del salto de Mario: la altura depende de cuánto tiempo se "
      "mantiene el botón. Los números exactos pueden variar un poco en Unity porque "
      "Update usa el tiempo real de cada cuadro.")

# 23 ------------------------------------------------------- detectar suelo
s = new_slide()
header(s, K, "DETECTAR EL SUELO", "Unity avisa al script cuando Velma toca algo.")
code_img(s, "code_colision", 0.62, 1.64, 5.40, 4.30)
bullets(s, 6.40, 1.76, 6.30, [
    "OnCollisionEnter: empieza a tocar algo.",
    "OnCollisionStay: lo sigue tocando, en cada paso de la física.",
    "OnCollisionExit: deja de tocar. grounded baja a false.",
    "Necesita el Rigidbody y el Box Collider que agregamos.",
], gap=0.92)
footer(s, "Enter y Stay llaman a CheckGround; Exit apaga grounded.")
nc(s, "Unity llama a estas tres funciones solas cuando el Rigidbody de Velma "
      "choca con otro collider.\n\n"
      "- OnCollisionEnter se llama una vez, al empezar el contacto.\n"
      "- OnCollisionStay se llama en cada paso de la física mientras dura el "
      "contacto. Sirve para volver a marcar el suelo si grounded se apagó por error.\n"
      "- OnCollisionExit se llama cuando termina el contacto y apaga grounded.\n\n"
      "Enter y Stay llaman a CheckGround para decidir si el objeto tocado es un suelo.",
   ["code_colision"])

# 24 ------------------------------------------------------- CheckGround
s = new_slide()
header(s, K, "CHECKGROUND: ¿ES SUELO?", "Un contacto es suelo si empuja a Velma hacia arriba.")
code_img(s, "code_checkground", 0.62, 1.64, 6.50, 3.80)
fig(s, ROOT / "figuras" / "fig_normales.png", 7.45, 1.64, 5.25, 2.80)
bullets(s, 7.45, 4.62, 5.25, [
    "vy > 0: sube, no es suelo.",
    "normal.y > 0.5: toca desde abajo.",
], gap=0.52)
footer(s, "La normal es la flecha que sale de la superficie hacia el personaje.")
nc(s, "CheckGround recibe la información de la colisión.\n\n"
      "Primera regla: si vy es mayor que 0, Velma va subiendo y la función termina. "
      "Esto evita marcar el suelo justo después de saltar, cuando el collider "
      "todavía toca el piso.\n\n"
      "Después se revisan todos los puntos de contacto (ContactPoint). Cada punto "
      "tiene una normal, que es una flecha de largo 1 perpendicular a la superficie "
      "y apuntando hacia Velma. En un piso plano la normal es (0, 1): normal.y vale 1. "
      "En una pared la normal es horizontal: normal.y vale 0.\n\n"
      "Si normal.y es mayor que 0.5, el contacto viene de abajo y se llama suelo. El "
      "umbral 0.5 acepta pisos un poco inclinados (hasta 60 grados).",
   ["code_checkground"])

# 25 ------------------------------------------------------- reset
s = new_slide()
header(s, K, "REINICIAR AL PERSONAJE", "Un botón puede devolver a Velma a su posición inicial.")
code_img(s, "code_reset", 0.62, 1.64, 6.70, 3.30)
bullets(s, 7.60, 1.76, 5.10, [
    "FreezeAll detiene todo antes de mover a Velma.",
    "rotation y position vuelven a la pose inicial.",
    "La posición inicial es (0, 1, 0).",
    "Al final se restauran las restricciones de Start.",
], gap=0.92)
footer(s, "Se puede llamar desde el evento OnClick de un botón de la interfaz.")
nc(s, "ResetButtonClick es una función pública, así que un botón de la interfaz "
      "puede llamarla desde su evento OnClick.\n\n"
      "Primero se congela todo el Rigidbody con FreezeAll. Después se pone la rotación "
      "en identidad y la posición en (0, 1, 0). Al final se vuelven a poner las mismas "
      "restricciones que en Start.\n\n"
      "Nota: la función no pone vx ni vy en 0. Se explica en la diapositiva de límites "
      "y mejoras.",
   ["code_reset"])

# 26 ------------------------------------------------------- rigidbody params
s = new_slide()
header(s, K, "RIGIDBODY: PARÁMETROS NECESARIOS", "Estos valores hacen que la simulación funcione.")
shot(s, "16-_rigidbody_parametros_necesarios_que_la_simulacion_funcione.png", 0.62, 1.70, 6.10, 3.60)
tbl(s, 7.05, 1.70, 5.66, [
    ("Parámetro", "Valor"),
    ("Use Gravity", "Apagado"),
    ("Interpolate", "Interpolate"),
    ("Collision Detection", "Continuous"),
    ("Freeze Position", "Z"),
    ("Freeze Rotation", "X, Y y Z"),
], [3.0, 2.66], row_h=0.56)
footer(s, "Sin estos valores Velma flota, gira o atraviesa el suelo.")
notes(s,
      "Resumen de lo que debe tener el Rigidbody para que el script funcione.\n\n"
      "- Use Gravity apagado: si estuviera encendido, Unity y el script aplicarían "
      "gravedad al mismo tiempo.\n"
      "- Interpolate: movimiento suave entre cuadros de física.\n"
      "- Continuous: evita atravesar el suelo.\n"
      "- Freeze Position Z: mantiene el juego en el plano 2D.\n"
      "- Freeze Rotation X, Y y Z: el sprite no debe girar.\n\n"
      "Start del script escribe estos mismos valores, por eso se ven iguales a los de "
      "la diapositiva de Start.")

# 27 ------------------------------------------------------- flujo
s = new_slide()
header(s, K, "EL ORDEN COMPLETO DE UPDATE", "Siete pasos se repiten en cada cuadro.")
pasos = ["Leer el teclado", "Leer los botones", "Suelo y tope", "Mover en X",
         "Iniciar salto", "Gravedad en Y", "Aplicar vx y vy"]
cols = [0.62, 3.80, 6.98, 10.16]
for i, name in enumerate(pasos):
    x = cols[i % 4]
    y = 1.70 if i < 4 else 2.95
    card(s, x, y, 2.55, 0.90, ORANGE if i < 6 else GREEN)
    text(s, x + 0.20, y + 0.12, 0.40, 0.30, str(i + 1), role="card_number",
         color=ORANGE_TEXT if i < 6 else GREEN)
    text(s, x + 0.20, y + 0.44, 2.25, 0.30, name, role="body_strong")
    if i % 4 != 3 and i != 6:
        text(s, x + 2.58, y + 0.22, 0.60, 0.40, "→", role="card_title_sm",
             color=BODY, align=PP_ALIGN.CENTER)
text(s, 0.62, 4.15, 6.0, 0.30, "EL ÚLTIMO PASO", role="label", color=ORANGE_TEXT)
code_img(s, "code_aplicar", 0.62, 4.50, 6.30, 0.75)
bullets(s, 7.40, 4.20, 5.30, [
    "Se entrega la velocidad al Rigidbody; Z siempre vale 0.",
    "En Unity 6 se llama linearVelocity. Antes era velocity.",
], gap=0.80)
footer(s, "El script decide la velocidad; Unity mueve al objeto y revisa los choques.")
nc(s, "Resumen del orden de Update:\n\n"
      "1. Leer el teclado y voltear el sprite.\n"
      "2. Leer los botones de correr y saltar.\n"
      "3. Poner vy en 0 si está en el suelo y elegir topSpeed.\n"
      "4. Calcular vx: acelerar, frenar o conservar.\n"
      "5. Iniciar el salto si se presionó el botón en el suelo.\n"
      "6. Aplicar la gravedad si está en el aire.\n"
      "7. Entregar vx y vy al Rigidbody.\n\n"
      "El orden importa. Por ejemplo, el salto se decide antes de la gravedad: en el "
      "cuadro del salto, vy ya vale jumpSpeed cuando se resta la gravedad.\n\n"
      "Esta versión del proyecto usa Unity 6, donde la propiedad se llama "
      "Rigidbody.linearVelocity. En versiones anteriores se llamaba velocity.",
   ["code_aplicar"])

# 28 ------------------------------------------------------- limites
s = new_slide()
header(s, "BLOQUE 03 · CIERRE", "LÍMITES Y MEJORAS",
       "El script funciona, pero hay cinco cosas que se pueden mejorar.")
tbl(s, 0.62, 1.70, 12.09, [
    ("Límite", "Qué pasa", "Mejora"),
    ("using UnityEditor.U2D", "Falla al exportar el juego.", "Borrar esa línea."),
    ("OnCollisionExit", "Cualquier contacto que termina apaga grounded.", "Contar contactos o usar un raycast."),
    ("ResetButtonClick", "No pone vx y vy en 0.", "Agregar vx = 0; vy = 0;"),
    ("Update", "La física va en FixedUpdate.", "Mover el cálculo a FixedUpdate."),
    ("Salto estricto", "Pulsar tarde en el borde no salta.", "Agregar coyote time."),
], [2.9, 5.0, 4.19], row_h=0.74)
footer(s, "Ninguno impide probar el control en el editor, pero todos lo mejoran.")
notes(s,
      "Límites que se encontraron al leer el código.\n\n"
      "1. using UnityEditor.U2D: el espacio UnityEditor solo existe dentro del editor. "
      "Al exportar el juego aparece un error de compilación. La línea no se usa y se "
      "puede borrar.\n"
      "2. OnCollisionExit: apaga grounded cuando termina cualquier contacto, aunque "
      "Velma siga tocando otro piso. Se puede contar cuántos contactos de suelo hay.\n"
      "3. ResetButtonClick: cambia la posición pero no reinicia vx ni vy; Velma puede "
      "seguir moviéndose después de reiniciar.\n"
      "4. Update: el Rigidbody se actualiza en FixedUpdate. Con Interpolate el "
      "resultado es aceptable, pero lo más preciso es calcular la velocidad en "
      "FixedUpdate.\n"
      "5. Coyote time: un pequeño margen de tiempo para saltar justo después de "
      "salir del borde. Mario original no lo tiene, pero muchos juegos modernos sí.")

# 29 ------------------------------------------------------- resumen
s = new_slide()
header(s, "BLOQUE 03 · CIERRE", "LO QUE APRENDISTE",
       "Cuatro ideas convierten un cubo en un personaje de plataformas.")
summary = [
    ("01", "MOVIMIENTO", "vx cambia poco a poco con MoveTowards.", ORANGE),
    ("02", "SALTO", "vy empieza en jumpSpeed y la gravedad lo baja.", BLUE),
    ("03", "SUELO", "OnCollision y la normal deciden grounded.", GREEN),
    ("04", "FÍSICA", "Rigidbody sin gravedad y con Z congelado.", PINK),
]
for i, (num, title, desc, color) in enumerate(summary):
    x = 0.62 if i % 2 == 0 else 6.44
    y = 1.70 if i < 2 else 3.30
    card(s, x, y, 5.55, 1.40, color)
    text(s, x + 0.26, y + 0.16, 0.40, 0.25, num, role="card_number", color=color)
    text(s, x + 0.76, y + 0.12, 4.50, 0.34, title, role="card_title_sm")
    text(s, x + 0.76, y + 0.58, 4.60, 0.70, desc, role="body", color=BODY, line_spacing=1.0)
tip(s, 0.62, 5.00, 11.37, 1.00, "Para practicar",
    "Cambia gravity y jumpGravity en el Inspector y mira cómo cambia el salto.")
notes(s,
      "Resumen:\n\n"
      "1. Movimiento: vx se acerca a una meta con MoveTowards. Acelera, frena y "
      "tiene dos velocidades.\n"
      "2. Salto: vy empieza en jumpSpeed y la gravedad lo reduce. Mantener el botón "
      "da una gravedad más suave.\n"
      "3. Suelo: OnCollisionEnter y OnCollisionStay llaman a CheckGround, que revisa "
      "la normal del contacto.\n"
      "4. Física: Rigidbody sin gravedad de Unity, con Z y rotaciones congeladas.\n\n"
      "Para practicar: cambia gravity (70.3) y jumpGravity (14.1) en el Inspector. "
      "Con valores más bajos Velma se siente más ligera; con valores más altos, más "
      "pesada.")

# 30 ------------------------------------------------------- preguntas
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
text(s, 0.0, 1.55, 13.33, 1.35, "¿PREGUNTAS?", role="closing", align=PP_ALIGN.CENTER)
text(s, 0.0, 3.18, 13.33, 0.38, "Siguiente: el control en 3D (tema 8.7.2).", role="subtitle",
     align=PP_ALIGN.CENTER)
text(s, 0.0, 3.72, 13.33, 0.38, "Velma ya corre, salta y cae con un control inspirado en Mario.",
     role="note", color=BODY, align=PP_ALIGN.CENTER)
picture_fit(s, ROOT / "decor" / "star.png", 1.55, 2.30, 0.85, 0.85, border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 3.60, 4.15, 0.75, 0.75, border=False)
picture_fit(s, ROOT / "decor" / "tree-small.png", 1.10, 4.36, 1.15, 2.06, border=False)
picture_fit(s, ROOT / "decor" / "cloud-low.png", 9.85, 4.68, 2.65, 1.42, border=False)
notes(s, "Cierre del tema 8.7.1. Recuerda: el control es una pareja de velocidades, "
         "vx y vy, que el script cambia en cada cuadro y entrega al Rigidbody.\n\n"
         "En el siguiente tema se repite la idea en 3D.")

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
