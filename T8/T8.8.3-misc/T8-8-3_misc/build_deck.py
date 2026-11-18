#!/usr/bin/env python3
"""Construye T8.8.3 - Audio, piedras arrastrables y Animator.

Sigue la plantilla FINAL-plantilla-videojuegos.pptx. El codigo se
muestra como imagen y se copia en las notas de cada diapositiva.
"""

import json
import os
import sys
from pathlib import Path

from PIL import Image
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent
PPTX = Path(os.environ.get(
    "DECK_OUT", str(ROOT.parent / "T8.8.3-Miscelaneos.pptx")
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


def notes_code(slide, intro, names, extra=""):
    value = intro.strip()
    for name in names:
        data = SNIPPETS[name]
        value += ("\n\nCÓDIGO DE LA DIAPOSITIVA ("
                  + data["file"] + ", " + data["note"] + "):\n\n")
        value += data["code"].strip("\n")
    if extra:
        value += "\n\n" + extra.strip()
    slide.notes_slide.notes_text_frame.text = value


def card(slide, x, y, w, h, accent=ORANGE, fill=WHITE, line=None):
    rect(slide, x, y, w, h, fill, line)
    rect(slide, x, y, 0.07, h, accent)


def pill(slide, x, y, w, value, color=BODY, fill=WHITE):
    rect(slide, x, y, w, 0.26, fill, LINE, 0.75, MSO_SHAPE.ROUNDED_RECTANGLE)
    text(slide, x, y + 0.04, w, 0.18, value, role="pill", color=color,
         align=PP_ALIGN.CENTER)


def shot(slide, name, x, y, w, h, fill=False):
    path = ROOT / "img" / name
    rect(slide, x, y, w, h, WHITE, LINE, 0.8)
    if fill:
        return picture_fill(slide, path, x + 0.05, y + 0.05,
                            w - 0.10, h - 0.10, border=False)
    return picture_fit(slide, path, x + 0.06, y + 0.06,
                       w - 0.12, h - 0.12, border=False)


FIG_MANIFEST = json.loads(
    (ROOT / "figuras" / "manifest.json").read_text(encoding="utf-8")
)
CODE_MANIFEST = json.loads(
    (ROOT / "codigo" / "manifest.json").read_text(encoding="utf-8")
)
MIN_IMG_PT = 12.0
IMG_AUDIT = []


def audit_image(kind, name, pic, data):
    pt = data["min_font"] * (pic.width / 914400) * 72 / data["width"]
    IMG_AUDIT.append((len(prs.slides), kind, name, pt))


def fig(slide, name, x, y, w, h, pad=0.06):
    rect(slide, x, y, w, h, WHITE, LINE, 1.0)
    pic = picture_fit(slide, ROOT / "figuras" / name, x + pad, y + pad,
                      w - 2 * pad, h - 2 * pad, border=False)
    audit_image("figura", name, pic, FIG_MANIFEST[name])
    return pic


def code_img(slide, name, x, y, w, h):
    pic = picture_fit(slide, ROOT / "codigo" / (name + ".png"),
                      x, y, w, h, border=False)
    audit_image("codigo", name, pic, CODE_MANIFEST[name])
    return pic


def table(slide, x, y, w, h, rows, col_widths, row_h=None,
          align=PP_ALIGN.LEFT):
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
            tbl.rows[i].height = Inches(
                row_h[i] if isinstance(row_h, list) else row_h
            )

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
            cell.fill.fore_color.rgb = DARK if i == 0 else (
                WHITE if i % 2 == 1 else SOFT)
            cell.margin_left = Inches(0.09)
            cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.03)
            cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    return tbl


def bullets(slide, x, y, w, items, gap=0.66, color=BODY):
    for i, item in enumerate(items):
        text(slide, x, y + i * gap, 0.18, 0.3, "•", role="bullet",
             color=ORANGE_TEXT)
        text(slide, x + 0.24, y + i * gap, w - 0.24, gap, item, role="body",
             color=color, line_spacing=1.02)


def steps(slide, x, y, w, items, gap=0.78):
    for i, item in enumerate(items):
        yy = y + i * gap
        circle(slide, x, yy - 0.02, 0.30, ORANGE)
        text(slide, x, yy - 0.02, 0.30, 0.30, str(i + 1), role="step_number",
             color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(slide, x + 0.44, yy, w - 0.44, gap, item, role="body",
             color=BODY, line_spacing=1.0)


def section_slide(number, title, subtitle, tags, color):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    text(s, 0.62, 0.98, 2.0, 1.0, number, role="section", color=color)
    text(s, 0.62, 1.92, 8.20, 1.60, title, role="section", color=INK,
         line_spacing=0.92)
    rect(s, 0.62, 3.85, 2.20, 0.07, color)
    text(s, 0.62, 4.12, 7.20, 0.90, subtitle, role="subtitle", color=INK,
         line_spacing=1.02)
    text(s, 0.62, 5.22, 8.00, 0.30, tags, role="label", color=BODY)
    picture_fit(s, ROOT / "decor" / "star.png", 9.56, 1.10, 1.10, 1.10,
                border=False)
    picture_fit(s, ROOT / "decor" / "mushroom.png", 11.35, 3.35, 0.95, 0.95,
                border=False)
    picture_fit(s, ROOT / "decor" / "cloud-low.png", 9.55, 4.95, 2.45, 1.40,
                border=False)
    picture_fit(s, ROOT / "decor" / "tree-small.png", 11.75, 4.75, 0.85, 1.55,
                border=False)
    return s


# ---------------------------------------------------------------- deck
prs = new_deck()
prs.core_properties.title = "T8.8.3 · Audio, piedras y Animator"
prs.core_properties.author = "TC2005B · Construcción de Software"
prs.core_properties.subject = "Audio, mouse click y animación en Unity"
prs.core_properties.keywords = "Unity, C#, AudioSource, Raycast, Animator, TC2005B"
prs.core_properties.language = "es-MX"

# ---- portada
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
rect(s, 0.62, 0.32, 0.09, 0.09, ORANGE)
text(s, 0.81, 0.28, 10.0, 0.22, "8.8.3 · TÓPICOS MISCELÁNEOS", role="label")
text(s, 0.62, 0.92, 6.00, 2.70, "AUDIO,\nPIEDRAS Y\nANIMACIÓN",
     role="section", line_spacing=0.92)
text(s, 0.62, 3.64, 5.70, 0.80,
     "Tres sistemas pequeños que hacen que la escena se sienta viva.",
     role="subtitle", line_spacing=1.02)
text(s, 0.62, 4.75, 5.55, 0.72,
     "Un AudioSource, un raycast y un Animator Controller.",
     role="note", color=BODY, line_spacing=1.02)
text(s, 0.62, 5.55, 5.40, 0.28, "TC2005B · Construcción de Software",
     role="note")
text(s, 0.62, 5.92, 5.40, 0.28, "Unity · C# · escena8_misc",
     role="note", color=MUTED)
rect(s, 6.55, 0.66, 6.18, 4.95, DARK)
picture_fill(s, ROOT / "img" / "2_drag_drop_dentro_escena.png",
             6.75, 0.86, 5.78, 4.55)
rect(s, 6.75, 0.86, 5.78, 4.55, None, WHITE, 1.2)
pill(s, 6.95, 0.72, 1.55, "UNITY · C#", WHITE, DARK)
picture_fit(s, ROOT / "decor" / "star.png", 0.55, 6.30, 0.75, 0.75,
            border=False)
picture_fit(s, ROOT / "decor" / "mushroom.png", 11.55, 6.10, 0.95, 0.95,
            border=False)
notes(s,
      "Bienvenida al tema 8.8.3. Ya tenemos movimiento, enemigos con BFS y una "
      "FSM para el enemigo. Ahora agregamos tres cosas que se sienten en la "
      "partida: audio, piedras que el jugador puede mover y animaciones con "
      "estados.\n\n"
      "Todo el código que se muestra viene de Assets/Scripts/escena8_misc. No "
      "se inventó código nuevo. Los archivos completos están en la carpeta "
      "csharp/ junto a esta presentación.\n\n"
      "Cada diapositiva con código tiene una imagen y el mismo fragmento en "
      "las notas del presentador.")

# ---- agenda
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "HOY", "LO QUE VEREMOS HOY",
       "Tres bloques, un mismo patrón: evento, código y componente.")
rows = [
    ("01", "AUDIO", "AudioSource, clips y PlayOneShot: un solo objeto para música y efectos.", ORANGE),
    ("02", "PIEDRAS", "Raycast para tomar, Rigidbody kinematic para mover y grid al soltar.", BLUE),
    ("03", "ANIMATOR", "Estados, parámetros y transiciones; el kickback de Velma.", GREEN),
]
for i, (num, title, desc, color) in enumerate(rows):
    y = 1.70 + i * 1.12
    card(s, 0.62, y, 12.09, 0.98, color)
    text(s, 0.82, y + 0.30, 0.45, 0.30, num, role="card_number", color=color)
    text(s, 1.42, y + 0.10, 10.8, 0.34, title, role="card_title_sm")
    text(s, 1.46, y + 0.52, 11.0, 0.32, desc, role="note", color=BODY)
text(s, 0.62, 5.25, 12.0, 0.40,
     "Al final, los tres sistemas se conectan con el mismo flujo de eventos.",
     role="body_strong")
footer(s, "Cada fragmento de código se ve como imagen y se copia en las notas.")
notes(s,
      "Recorrido del tema.\n\n"
      "1. Audio: cómo se agregó un AudioSource, cómo se asignaron los clips y "
      "por qué un solo AudioSource puede con música y efectos.\n"
      "2. Piedras: raycast para el click, Rigidbody kinematic mientras se "
      "arrastra y recálculo del grid al caer.\n"
      "3. Animator: el controlador como máquina de estados, sus parámetros y "
      "el golpe que empuja a Velma.\n\n"
      "El hilo conductor es el mismo: un evento del juego llama a código, y el "
      "código mueve un componente de Unity.")

# ---- seccion 01
s = section_slide("01", "AUDIO\nEN UNITY",
                  "Un AudioSource, seis clips y métodos estáticos para sonar desde cualquier script.",
                  "AUDIOCLIP · AUDIOSOURCE · PLAYONESHOT", ORANGE)
notes(s, "Bloque 1. El audio se concentra en un solo GameObject y se dispara "
         "con métodos estáticos. Primero vemos las piezas, luego la "
         "configuración y al final el código.")

# 4 ------------------------------------------------------------ piezas
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · AUDIO", "TRES PIEZAS DE AUDIO",
       "El clip son los datos; el AudioSource reproduce; el AudioListener oye.")
fig(s, "fig_audio_piezas.png", 0.55, 1.68, 6.85, 4.35)
bullets(s, 7.65, 1.82, 5.05, [
    "AudioClip: el .mp3 importado. No suena por sí solo.",
    "AudioSource: el componente que reproduce. Hay uno solo, en Sonidos.",
    "AudioListener: está en la Main Camera; sin él no se oye nada.",
    "Spatial Blend 2D: el volumen no depende de la distancia.",
], gap=0.98)
footer(s, "Assets/Audio tiene los seis clips que usa la escena.")
notes(s,
      "Tres piezas distintas, no una sola.\n\n"
      "AudioClip es el asset: el archivo importado con los datos de la onda. "
      "Puede estar en el proyecto y no sonar nunca.\n\n"
      "AudioSource es el componente del GameObject que reproduce clips. En la "
      "escena hay un GameObject vacío llamado Sonidos con un solo AudioSource. "
      "Ese objeto no se ve, pero existe durante toda la partida.\n\n"
      "AudioListener es el oído. La Main Camera lo trae por defecto. Sin "
      "listener, Unity calcula el audio pero no se escucha.\n\n"
      "Spatial Blend en 2D significa que el volumen no cambia con la distancia. "
      "Para un juego con cámara fija es lo que queremos.")

# 5 ------------------------------------------------------------ setup
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · AUDIO", "CÓMO SE AGREGÓ EL AUDIO",
       "Un GameObject vacío concentra el AudioSource y el script.")
steps(s, 0.62, 1.80, 6.05, [
    "Crear un GameObject vacío y llamarlo Sonidos.",
    "Add Component > Audio > AudioSource.",
    "Add Component > S8_SoundControl.",
    "Arrastrar los seis clips de Assets/Audio a sus campos.",
    "Dejar Play On Awake y Loop en off; Spatial Blend en 2D.",
], gap=0.80)
fig(s, "fig_audio_setup.png", 6.85, 1.68, 5.95, 4.50)
footer(s, "El AudioSource queda sin clip: Awake asigna la música al arrancar.")
notes(s,
      "Pasos exactos de la escena.\n\n"
      "1. GameObject > Create Empty, nombre Sonidos. No necesita Transform "
      "visible ni renderer; solo existe para colgar componentes.\n"
      "2. Add Component > Audio > AudioSource. Unity agrega el componente que "
      "reproduce audio.\n"
      "3. Add Component > S8_SoundControl. El script tiene "
      "[RequireComponent(typeof(AudioSource))], así que si el AudioSource "
      "faltara, Unity lo agregaría.\n"
      "4. En el Inspector del script aparecen seis campos públicos. Se "
      "arrastra cada clip desde Assets/Audio.\n"
      "5. Play On Awake se deja apagado porque la música la arranca el script "
      "en Awake. Loop también se deja apagado en el componente; el script lo "
      "activa para la música. Spatial Blend en 2D.\n\n"
      "El AudioSource del Inspector queda con Audio Clip = None. Eso es "
      "intencional: el clip base se asigna en tiempo de ejecución.")

# 6 ------------------------------------------------------------ fields
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · AUDIO", "EL SCRIPT: CAMPOS Y REQUISITO",
       "El script exige su AudioSource y guarda una referencia estática a sí mismo.")
code_img(s, "code_audio_fields", 0.62, 1.68, 6.0, 3.55)
bullets(s, 6.95, 1.82, 5.70, [
    "[RequireComponent] agrega el AudioSource si falta.",
    "Los clips son public para asignarlos en el Inspector.",
    "instancia es static: acceso global sin buscar el objeto.",
    "Un solo AudioSource para música y efectos.",
], gap=0.98)
footer(s, "Archivo: Assets/Scripts/escena8_misc/S8_SoundControl.cs")
notes_code(s,
           "El script tiene dos partes: los datos que se asignan en el "
           "Inspector y una referencia estática para que cualquier otro "
           "script lo encuentre.\n\n"
           "RequireComponent no crea el AudioSource al ejecutar: lo exige en "
           "el Editor. Si el componente falta, Unity lo agrega al agregar el "
           "script.\n\n"
           "Los AudioClip son public para que aparezcan como campos en el "
           "Inspector. No son static porque cada clip pertenece a esta "
           "instancia del componente.\n\n"
           "instancia es static y privada. Los métodos públicos son static y "
           "usan instancia para llegar al AudioSource.",
           ["code_audio_fields"])

# 7 ------------------------------------------------------------ awake
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · AUDIO", "ARRANQUE: AWAKE Y MÚSICA",
       "Awake corre una vez, antes de Start, y deja el audio listo.")
code_img(s, "code_audio_awake", 0.62, 1.68, 5.8, 3.36)
bullets(s, 6.90, 1.82, 5.75, [
    "instancia = this deja el acceso global listo.",
    "GetComponent cachea el AudioSource del objeto.",
    "El if evita un error si no hay música asignada.",
    "clip + loop + Play: la música arranca y se repite.",
], gap=0.98)
footer(s, "Awake no necesita que el jugador haga nada.")
notes_code(s,
           "Awake se ejecuta una sola vez, cuando se carga la escena, antes de "
           "cualquier Start. Es el lugar correcto para inicializar referencias.\n\n"
           "instancia = this guarda el único S8_SoundControl de la escena. "
           "asource = GetComponent<AudioSource>() cachea el componente para no "
           "buscarlo en cada efecto.\n\n"
           "La música se asigna al clip base del AudioSource. loop = true hace "
           "que se repita. Play() la inicia. El if protege el caso de que el "
           "campo background quede vacío en el Inspector.",
           ["code_audio_awake"])

# 8 ------------------------------------------------------------ oneshot
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · AUDIO", "EFECTOS: PLAYONESHOT",
       "PlayOneShot suma un sonido sin cortar la música ni los efectos anteriores.")
code_img(s, "code_audio_methods", 0.62, 1.68, 5.55, 3.88)
fig(s, "fig_audio_mezcla.png", 6.50, 1.68, 6.15, 2.87)
bullets(s, 6.55, 4.72, 6.05, [
    "Play() reemplaza el clip base; PlayOneShot no.",
    "Varios PlayOneShot se mezclan en el mismo AudioSource.",
    "El volumen opcional escala cada disparo.",
], gap=0.52)
footer(s, "Un AudioSource puede con varias voces a la vez.")
notes_code(s,
           "Cada método es un envoltorio de una línea: llama a PlayOneShot en "
           "el AudioSource compartido, con el clip correspondiente.\n\n"
           "La imagen muestra jump y airWush; el marcador // ... indica que "
           "hit y kick se omitieron por espacio. Los cuatro métodos siguen el "
           "mismo patrón.\n\n"
           "La documentación de Unity lo dice: PlayOneShot no cancela los "
           "clips que ya están sonando con PlayOneShot ni con Play. Por eso la "
           "música sigue y los efectos se suman.\n\n"
           "La diferencia con Play(): Play reemplaza el clip base y detiene lo "
           "anterior. Aquí la música usa Play y los efectos usan PlayOneShot.\n\n"
           "El segundo parámetro de PlayOneShot es volumeScale. El código no lo "
           "usa, así que queda en 1.",
           ["code_audio_methods"],
           "Referencia: https://docs.unity3d.com/ScriptReference/AudioSource.PlayOneShot.html")

# 9 ------------------------------------------------------------ eventos
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 01 · AUDIO", "QUIÉN DISPARA CADA SONIDO",
       "Cada evento llama a un método distinto del mismo script.")
rows = [
    ("Evento", "Método", "Clip", "Cuándo"),
    ("Salto (Space / Z)", "play_jump()", "jump-sound.mp3", "jumpPressed && grounded"),
    ("Patada al aire (F)", "play_airWush()", "air-whoosh.mp3", "cada patada"),
    ("Patada conectada", "play_kick()", "kick-sound-effect.mp3", "RecibirPatada() == true"),
    ("Golpe de enemigo", "play_hit()", "classic_hurt.mp3", "GolpeVelma() == true"),
    ("Victoria", "(campo won)", "metal-slug-...mp3", "sin llamada en el código"),
    ("Música de fondo", "Play() en Awake", "Moog City.mp3", "inicio de la escena"),
]
table(s, 0.62, 1.72, 12.09, 4.22, rows, [3.10, 2.30, 3.60, 3.09],
      row_h=[0.62] * 7)
footer(s, "won está declarado y asignado, pero el código actual no lo reproduce.")
notes(s,
      "Tabla de eventos. La columna Método muestra la llamada exacta que hace "
      "S8_VelmaWalk_3D.\n\n"
      "Salto: play_jump() se llama dentro de if (jumpPressed && grounded).\n"
      "Patada: play_airWush() se llama siempre que se dispara el trigger kick, "
      "haya o no enemigo.\n"
      "Patada conectada: play_kick() se llama solo si RecibirPatada() devuelve "
      "true.\n"
      "Golpe: play_hit() se llama en el Update cuando la bandera "
      "velma_empujada se aplica.\n"
      "Victoria: el campo won existe y está asignado en el Inspector, pero "
      "ninguna línea del código actual llama a un método que lo reproduzca. "
      "Queda como material para el final del nivel.\n"
      "Música: Play() en Awake, con loop = true.")

# ---- seccion 02
s = section_slide("02", "PIEDRAS\nARRASTRABLES",
                  "Raycast para tomar, kinematic para mover y física para soltar.",
                  "RAYCAST · RIGIDBODY · GRID", BLUE)
notes(s, "Bloque 2. La piedra es un Rigidbody que el jugador puede tomar con "
         "el mouse, mover con el teclado y soltar. Al caer, se convierte en un "
         "obstáculo para el BFS del enemigo.")

# 11 ----------------------------------------------------------- importar
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · PIEDRAS", "IMPORTAR Y COLOCAR LA PIEDRA",
       "El modelo se importa, se arrastra a la escena y se duplica.")
shot(s, "2_drag_drop_dentro_escena.png", 0.62, 1.68, 5.80, 3.90, fill=True)
text(s, 0.70, 5.66, 5.65, 0.28, "1 · Arrastrar cubo_piedra a la escena.",
     role="caption", color=BODY)
shot(s, "1_importar_nuevo_asset.png", 6.75, 1.68, 5.80, 2.55, fill=True)
text(s, 6.83, 4.32, 5.65, 0.28, "2 · Importar el modelo a Assets/Models.",
     role="caption", color=BODY)
shot(s, "3_cambio_denombre_game_object.png", 6.75, 4.75, 5.80, 0.87)
text(s, 6.83, 5.68, 5.65, 0.28, "3 · Renombrar piedra_1 y revisar la capa.",
     role="caption", color=BODY)
footer(s, "Ctrl+D duplica la piedra: piedra_1, piedra_2 y piedra_3.")
notes(s,
      "Capturas del proceso real en Unity.\n\n"
      "1. El modelo cubo_piedra se arrastra desde Assets/Models a la escena. "
      "Unity crea un GameObject con MeshFilter, MeshRenderer y Collider.\n"
      "2. Si el modelo no está en el proyecto, se importa con Assets > Import "
      "New Asset y se copia dentro de Assets/Models.\n"
      "3. Se renombra a piedra_1 para identificarla. La capa se cambia a "
      "Paredes; eso es lo que permite que el BFS la vea como obstáculo.\n\n"
      "Ctrl+D duplica el objeto. Las tres piedras comparten el mismo script y "
      "la misma configuración; solo cambia su posición.")

# 12 ----------------------------------------------------------- componentes
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · PIEDRAS", "COMPONENTES, CAPA Y REFERENCIA",
       "BoxCollider para el rayo, Rigidbody kinematic y capa Paredes para el BFS.")
shot(s, "4_agregando_rigid_body_y_box_collider.png", 0.62, 1.68, 4.05, 4.35)
shot(s, "5_setup_layer_a_paredes_para_que_funcione_en_BFS.png",
     5.05, 1.68, 7.30, 1.09)
bullets(s, 5.05, 3.05, 7.40, [
    "BoxCollider: superficie que el raycast puede golpear.",
    "Rigidbody: Is Kinematic activo y Freeze Rotation en X, Y y Z.",
    "Layer Paredes: la piedra suelta bloquea el BFS.",
    "S8_RockDragDrop: player apunta a Velma para apagar sus controles.",
], gap=0.82)
footer(s, "Tres piedras con el mismo script; solo cambia su posición.")
notes(s,
      "El Inspector de piedra_1 muestra lo importante.\n\n"
      "Box Collider: sin collider, Physics.Raycast no puede golpear la piedra. "
      "El script lo exige con [RequireComponent(typeof(Collider))].\n\n"
      "Rigidbody: Is Kinematic está activo al inicio. Eso significa que la "
      "piedra no cae ni la mueve la física; el script la mueve. Freeze "
      "Rotation en X, Y y Z evita que gire mientras cae.\n\n"
      "Layer Paredes: la capa es lo que consulta S8_Grid con capaParedes. Una "
      "piedra suelta es, para el BFS, otra pared.\n\n"
      "S8_RockDragDrop tiene el campo player asignado a Velma. Así puede llamar "
      "a DisableControls(true) mientras la piedra está en el aire.")

# 13 ----------------------------------------------------------- click
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · PIEDRAS", "CLICK: UN RAYO DESDE LA CÁMARA",
       "ScreenPointToRay convierte el mouse en un rayo; el primer collider decide.")
fig(s, "fig_rock_raycast.png", 0.55, 1.68, 6.50, 4.18)
code_img(s, "code_rock_click", 7.15, 1.68, 5.65, 4.00)
footer(s, "Sin Collider no hay hit; por eso el script lo exige.")
notes_code(s,
           "El click no usa OnMouseDown. Se lee el mouse con el nuevo Input "
           "System y se lanza un rayo desde la cámara.\n\n"
           "mouse.position.ReadValue() devuelve píxeles de pantalla. "
           "ScreenPointToRay(pos) convierte ese punto en un rayo que sale de la "
           "cámara y atraviesa ese píxel.\n\n"
           "Physics.Raycast devuelve el primer collider que golpea. Si el rayo "
           "toca otra piedra primero, hit.transform no es esta piedra y el "
           "arrastre no empieza.\n\n"
           "Si coincide, arrastrando = true, se calcula alturaArrastre (la Y "
           "actual más liftHeight) y se vuelve kinematic para que la gravedad "
           "no luche con el script.",
           ["code_rock_click"])

# 14 ----------------------------------------------------------- arrastre
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · PIEDRAS", "ARRASTRE: KINEMATIC Y TECLADO",
       "Mientras arrastra, la piedra ignora la gravedad y Velma se agacha.")
fig(s, "fig_rock_estados.png", 0.55, 1.68, 6.00, 3.80)
code_img(s, "code_rock_move", 6.75, 1.68, 6.20, 4.45)
footer(s, "DisableControls(true) también activa isDucking y frena a Velma.")
notes_code(s,
           "El arrastre no sigue el mouse píxel a píxel. La piedra sube a una "
           "altura fija y se mueve a saltos de grid con el teclado.\n\n"
           "Cada frame mientras arrastrando es true:\n"
           "- se llama DisableControls(true) en Velma: se agacha y deja de "
           "caminar;\n"
           "- la Y se fija en alturaArrastre, así no cae;\n"
           "- W/S o flechas arriba/abajo mueven en Z con rockStep = 2;\n"
           "- A/D o flechas izquierda/derecha repiten el patrón en X.\n\n"
           "El bloque de código muestra el eje Z. El eje X es simétrico y está "
           "en las líneas 76-83 del archivo completo.\n\n"
           "rockStep = 2.0 es múltiplo de la celda de 0.5, así que la piedra "
           "queda alineada al grid.",
           ["code_rock_move"],
           "El archivo completo está en csharp/S8_RockDragDrop.cs, líneas 60-84.")

# 15 ----------------------------------------------------------- soltar
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · PIEDRAS", "SOLTAR: LA FÍSICA TOMA EL CONTROL",
       "Al soltar, la gravedad baja la piedra; al tocar Piso o Paredes se congela.")
code_img(s, "code_rock_release", 0.62, 1.68, 5.70, 2.26)
bullets(s, 0.62, 4.10, 5.30, [
    "arrastrando = false: deja de seguir el mouse.",
    "dropped = true: la caída debe revisarse.",
    "isKinematic = false: la gravedad actúa.",
], gap=0.55)
code_img(s, "code_rock_collision", 6.40, 1.68, 6.30, 4.31)
footer(s, "Si el click se suelta sin haber arrastrado, no pasa nada.")
notes_code(s,
           "Soltar tiene dos pasos.\n\n"
           "Primero, en Update: si el botón izquierdo se soltó y arrastrando es "
           "true, se devuelve el control a Velma, se apaga arrastrando, se "
           "marca dropped y se vuelve kinematic = false para que la gravedad "
           "actúe.\n\n"
           "Segundo, en OnCollisionEnter: si dropped es true y el objeto "
           "golpeado está en Piso o Paredes, se congela. Se ponen las "
           "velocidades lineal y angular en cero y se vuelve kinematic = true. "
           "Por último se llama a S8_Grid.Instancia.calculaGrid().\n\n"
           "La bandera dropped evita que una piedra quieta recalcule el grid "
           "cada vez que algo la toca.",
           ["code_rock_release", "code_rock_collision"])

# 16 ----------------------------------------------------------- grid
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 02 · PIEDRAS", "AL CAER, EL GRID SE RECALCULA",
       "La piedra se congela y S8_Grid vuelve a marcar las celdas bloqueadas.")
fig(s, "fig_rock_grid.png", 0.55, 1.68, 7.95, 4.50)
bullets(s, 8.75, 1.82, 4.00, [
    "calculaGrid() recorre el plano con Physics.CheckBox.",
    "Cada celda con Paredes o piedra queda bloqueada.",
    "El siguiente BFS ya no cruza por ahí.",
    "El enemigo patrulla y persigue con el grid nuevo.",
], gap=0.98)
footer(s, "La piedra no es un caso especial: es otro obstáculo para el BFS.")
notes(s,
      "El grid es la representación que usa el BFS. S8_Grid guarda una matriz "
      "de bool: true significa bloqueada.\n\n"
      "calculaGrid() recorre todas las celdas y lanza un Physics.CheckBox en "
      "cada una, contra la capa Paredes. Las piedras sueltas también están en "
      "la capa Paredes, así que aparecen como bloqueadas.\n\n"
      "Antes de mover la piedra, el camino del enemigo cruzaba por el hueco. "
      "Después de soltarla, esas celdas quedan bloqueadas y el siguiente BFS "
      "encuentra otra ruta.\n\n"
      "La piedra no necesita código de pathfinding: solo cambia el mapa y "
      "avisa al grid que lo recalculé.")

# ---- seccion 03
s = section_slide("03", "ANIMATOR\nY KICKBACK",
                  "El Animator Controller es una FSM; el código solo mueve sus parámetros.",
                  "STATES · PARAMETERS · TRIGGERS", GREEN)
notes(s, "Bloque 3. El Animator Controller de Unity es una máquina de estados "
         "visual. Aquí lo conectamos con el código y con el golpe que empuja a "
         "Velma.")

# 18 ----------------------------------------------------------- concepto
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · ANIMATOR", "EL ANIMATOR ES UNA MÁQUINA DE ESTADOS",
       "Estados con clips, transiciones con condiciones y parámetros que escribe C#.")
fig(s, "fig_anim_concepto.png", 0.55, 1.68, 7.25, 4.58)
bullets(s, 8.05, 1.82, 4.70, [
    "Estado: un clip y su velocidad.",
    "Transición: flecha con condiciones.",
    "Parámetro: Bool, Trigger, Float o Int.",
    "Any State: origen comodín.",
    "Exit Time: porcentaje del clip para salir.",
], gap=0.80)
footer(s, "Una capa: en cada frame hay un solo estado activo.")
notes(s,
      "Un Animator Controller es una máquina de estados finitos, igual que la "
      "FSM del enemigo, pero visual.\n\n"
      "Estado: un nodo que reproduce un clip. Solo hay un estado activo por "
      "capa en cada momento.\n\n"
      "Transición: una flecha de un estado a otro. Puede tener condiciones "
      "basadas en parámetros y un Exit Time.\n\n"
      "Parámetro: una variable del controlador que el script puede escribir. "
      "Los tipos son Bool, Trigger, Float e Int.\n\n"
      "Any State: un nodo especial que permite entrar desde cualquier estado. "
      "Se usa para golpes y muertes.\n\n"
      "Exit Time: el porcentaje del clip que debe transcurrir antes de que la "
      "transición pueda ocurrir, si Has Exit Time está activo.\n\n"
      "Referencia: https://docs.unity3d.com/Manual/AnimationParameters.html")

# 19 ----------------------------------------------------------- velma fsm
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · ANIMATOR", "SEIS ESTADOS Y CINCO PARÁMETROS",
       "El controlador velma_sprite_walk_2_0 define movimiento y reacciones.")
fig(s, "fig_anim_velma.png", 0.45, 1.66, 9.15, 4.58)
bullets(s, 9.80, 1.80, 2.95, [
    "Entry entra a VelmaWalking.",
    "Any State: kick → VelmaKick.",
    "Any State: push → VelmaDrop.",
    "Kick y Drop vuelven con Exit Time = 1.",
    "Bools: isRunning, isJumping, isDucking.",
    "Jump → Run si isRunning sigue true.",
], gap=0.72)
footer(s, "El Animator no lee el teclado: lee parámetros.")
notes(s,
      "Este es el controlador real velma_sprite_walk_2_0.controller, el mismo "
      "que está en la carpeta animator/.\n\n"
      "Estados: VelmaWalking (por defecto), VelmaRun, VelmaJump, VelmaDuck, "
      "VelmaKick y VelmaDrop.\n\n"
      "Parámetros: isRunning, isJumping y isDucking son Bool; kick y push son "
      "Trigger.\n\n"
      "Transiciones principales:\n"
      "- Walking -> Run si isRunning = true; Run -> Walking si es false.\n"
      "- Walking o Run -> Jump si isJumping = true; Jump -> Walking si es "
      "false. Si isRunning sigue true, Jump -> Run.\n"
      "- Walking -> Duck si isDucking = true; Duck -> Walking si es false.\n"
      "- Any State -> Kick con trigger kick; Any State -> Drop con trigger "
      "push.\n"
      "- Kick y Drop vuelven a Walking con Exit Time = 1 y sin condiciones.\n\n"
      "El controlador se puede abrir en Unity con Window > Animation > "
      "Animator.")

# 20 ----------------------------------------------------------- parametros
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · ANIMATOR", "BOOL, TRIGGER Y EXIT TIME",
       "Bool permanece; Trigger se consume; Exit Time no es un parámetro.")
rows = [
    ("Parámetro", "Tipo", "Lo escribe", "Efecto"),
    ("isRunning", "Bool", "SetBool cada frame", "Walking <-> VelmaRun"),
    ("isJumping", "Bool", "SetBool cada frame", "Entra a VelmaJump"),
    ("isDucking", "Bool", "DisableControls", "Entra a VelmaDuck"),
    ("kick", "Trigger", 'SetTrigger("kick")', "Any State → VelmaKick"),
    ("push", "Trigger", 'SetTrigger("push")', "Any State → VelmaDrop"),
]
table(s, 0.62, 1.72, 7.45, 3.72, rows, [1.55, 1.05, 1.95, 2.90],
      row_h=[0.62] * 6)
code_img(s, "code_anim_duck", 8.15, 1.72, 5.00, 1.96)
bullets(s, 8.15, 3.85, 4.50, [
    "SetBool mantiene el valor.",
    "SetTrigger se consume.",
    "Exit Time espera el clip.",
    "DisableControls activa isDucking.",
], gap=0.62)
footer(s, "El código nunca dice “reproduce VelmaDuck”; solo cambia isDucking.")
notes_code(s,
           "Un Bool es un valor que permanece. isRunning se pone true mientras "
           "Velma corre y false cuando se detiene; el Animator reacciona a ese "
           "valor cada frame.\n\n"
           "Un Trigger es un Bool que el controlador apaga cuando una "
           "transición lo consume. Por eso kick y push se disparan una sola vez "
           "aunque se llamen varias veces seguidas.\n\n"
           "Exit Time no es un parámetro: es una propiedad de la transición. "
           "Con Exit Time = 1, la transición espera a que el clip termine.\n\n"
           "DisableControls hace dos cosas: controls_disabled = true (el Update "
           "de Velma se detiene) y SetBool(\"isDucking\", value) (el Animator "
           "entra a VelmaDuck).",
           ["code_anim_duck"],
           "El controlador tiene 5 parámetros y 6 estados; el diagrama de la "
           "diapositiva anterior los muestra todos.")

# 21 ----------------------------------------------------------- code map
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · ANIMATOR", "DEL CÓDIGO AL ANIMATOR",
       "El script escribe parámetros; el Animator decide qué estado se activa.")
fig(s, "fig_anim_code_map.png", 0.55, 1.72, 11.90, 4.25)
footer(s, "Cada línea de C# corresponde a una flecha del controlador.")
notes_code(s,
           "Esta es la relación completa entre el código y el Animator.\n\n"
           "SetBool(\"isRunning\", ...) se llama cada frame en Update. El "
           "controlador tiene transiciones Walking <-> Run con ese Bool.\n\n"
           "SetBool(\"isJumping\", !grounded) se llama cada frame. Cuando "
           "grounded es false, el Bool es true y el Animator entra a "
           "VelmaJump.\n\n"
           "SetBool(\"isDucking\", value) se llama desde DisableControls. Se "
           "usa mientras la piedra está en el aire.\n\n"
           "SetTrigger(\"kick\") se llama al presionar F en el suelo. "
           "SetTrigger(\"push\") se llama cuando velma_empujada se aplica.\n\n"
           "El script no reproduce clips ni conoce los estados: solo escribe "
           "parámetros. El Animator evalúa las transiciones.",
           ["code_anim_set", "code_anim_duck", "code_anim_kick", "code_push"],
           "SetTrigger(\"kick\") está en S8_VelmaWalk_3D.cs, líneas 112-115. "
           "SetTrigger(\"push\") está en las líneas 122-129.")

# 22 ----------------------------------------------------------- exit
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · ANIMATOR", "SALIR DEL ESTADO Y CONSULTARLO",
       "Exit Time devuelve a Walking; IsName permite saber si el clip sigue activo.")
fig(s, "fig_anim_exit.png", 0.55, 1.68, 6.20, 2.89)
bullets(s, 0.62, 4.62, 6.00, [
    "VelmaKick no tiene condiciones de salida.",
    'IsName("VelmaKick") consulta la capa 0.',
    "Solo hay daño si el estado actual es la patada.",
], gap=0.45)
code_img(s, "code_anim_check", 6.95, 1.68, 6.20, 4.17)
footer(s, "La animación y el gameplay leen la misma FSM.")
notes_code(s,
           "La transición de salida de VelmaKick tiene Exit Time = 1 y ninguna "
           "condición. Cuando el clip termina, el Animator vuelve solo a "
           "VelmaWalking. No hay código que pida el regreso.\n\n"
           "Para el gameplay, CheckVelmaKick consulta el estado actual con "
           "GetCurrentAnimatorStateInfo(0).IsName(\"VelmaKick\"). La capa 0 es "
           "la Base Layer.\n\n"
           "Si el estado actual es la patada y el objeto es de la capa "
           "Enemigos, se llama a RecibirPatada(). Si el enemigo devuelve true, "
           "suena play_kick().\n\n"
           "Ese IsName es la unión entre animación y reglas: el daño solo "
           "ocurre durante el clip de patada.",
           ["code_anim_check"],
           "El clip de la patada tiene 6 sprites a 12 fps; el detalle está en "
           "el tema 8.8.2.")

# 23 ----------------------------------------------------------- golpe
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · ANIMATOR", "GOLPE: EL ENEMIGO DECIDE",
       "OnCollisionEnter llama a GolpeVelma; el cono de visión responde.")
fig(s, "fig_kickback_flujo.png", 0.55, 1.68, 6.50, 4.44)
code_img(s, "code_enemy_hit", 7.15, 1.68, 5.90, 2.95)
bullets(s, 7.15, 4.75, 5.60, [
    "Solo Enter, no Stay: un golpe por contacto.",
    "GolpeVelma usa el cono frontal del enemigo.",
    "Si hubo golpe, se omite CheckVelmaKick.",
], gap=0.50)
footer(s, "El enemigo no empuja: autoriza el golpe.")
notes_code(s,
           "OnCollisionEnter llama a CheckEnemyHit. Si hubo golpe, retorna true "
           "y se omite CheckVelmaKick en ese frame.\n\n"
           "CheckEnemyHit revisa que el objeto sea de la capa Enemigos y llama "
           "a GolpeVelma(transform.position). El enemigo decide con su cono de "
           "visión: si Velma está dentro del ángulo frontal, devuelve true.\n\n"
           "OnCollisionStay no llama a CheckEnemyHit. Por eso el golpe no se "
           "repite mientras los cuerpos siguen tocándose.\n\n"
           "El empuje no lo hace el enemigo: el enemigo solo autoriza. Velma "
           "calcula el vector y aplica el impulso en su propio Update.",
           ["code_enemy_hit"])

# 24 ----------------------------------------------------------- vector
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · ANIMATOR", "EL VECTOR QUE APUNTA LEJOS",
       "away = Velma − Enemigo; se aplana en Y y se normaliza.")
fig(s, "fig_kickback_vector.png", 0.55, 1.68, 6.30, 3.99)
code_img(s, "code_kick_away", 7.05, 1.68, 5.55, 2.98)
bullets(s, 6.95, 4.72, 5.60, [
    "away.y = 0: el empuje es horizontal.",
    "sqrMagnitude > 0.0001 evita normalizar cero.",
    "empuje_dir queda en XZ; la bandera espera Update.",
], gap=0.45)
footer(s, "El enemigo solo autoriza; Velma aplica el empuje.")
notes_code(s,
           "El vector away va del enemigo a Velma: posición de Velma menos "
           "posición del enemigo.\n\n"
           "away.y = 0 elimina la altura. El empuje es horizontal, en el plano "
           "XZ.\n\n"
           "Antes de normalizar se revisa sqrMagnitude > 0.0001. Si los dos "
           "cuerpos están exactamente en el mismo punto, el vector sería cero y "
           "normalizarlo daría NaN.\n\n"
           "empuje_dir guarda la dirección normalizada en XZ. velma_empujada = "
           "true es la bandera que el Update revisa en el siguiente frame.",
           ["code_kick_away"])

# 25 ----------------------------------------------------------- impulso
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "BLOQUE 03 · ANIMATOR", "IMPULSO, SONIDO Y ANIMACIÓN",
       "En el siguiente Update, Velma suma kickBack y dispara push.")
fig(s, "fig_kickback_timeline.png", 0.50, 1.68, 8.00, 4.00)
code_img(s, "code_push", 8.65, 1.68, 4.55, 2.39)
bullets(s, 8.65, 4.12, 4.00, [
    "Solo en el suelo; si no, espera.",
    "kickBack = 10; el tope de 15 lo recorta.",
    "push entra a VelmaDrop desde Any State.",
    "play_hit() suena una vez.",
], gap=0.55)
footer(s, "La animación no mueve a Velma: el impulso lo hace el Rigidbody.")
notes_code(s,
           "El golpe se detecta en OnCollisionEnter, pero el impulso se aplica "
           "en el siguiente Update.\n\n"
           "La condición if (grounded && velma_empujada) hace que el empuje "
           "espere si Velma está en el aire. La bandera sigue true hasta que "
           "toque el suelo.\n\n"
           "Al aplicarse:\n"
           "- SetTrigger(\"push\") dispara la transición Any State -> "
           "VelmaDrop;\n"
           "- horizontal += empuje_dir * kickBack suma el impulso;\n"
           "- velma_empujada = false apaga la bandera;\n"
           "- play_hit() reproduce classic_hurt.\n\n"
           "kickBack = 10. Más abajo, el Update limita horizontal a "
           "maxHorizontalSpeed = 15. Por eso el impulso se siente fuerte pero "
           "no infinito.\n\n"
           "VelmaDrop vuelve a VelmaWalking con Exit Time = 1. El clip termina "
           "solo; no hay código de regreso.",
           ["code_push"],
           "La animación no desplaza a Velma: el Rigidbody aplica la velocidad "
           "horizontal y la gravedad se calcula en el mismo Update.")

# 26 ----------------------------------------------------------- resumen
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "RESUMEN", "TRES SISTEMAS, UNA IDEA",
       "Evento del juego → código → componente de Unity.")
cards = [
    ("01", "AUDIO", "Un AudioSource y métodos static: el evento correcto dispara el clip.", ORANGE),
    ("02", "PIEDRAS", "Raycast para tomar; kinematic para mover; física y grid al soltar.", BLUE),
    ("03", "ANIMATOR", "El código escribe parámetros; el Animator evalúa estados.", GREEN),
    ("04", "KICKBACK", "El enemigo autoriza; Velma aplica el vector y dispara push.", PINK),
]
for i, (num, title, desc, color) in enumerate(cards):
    col, row = i % 2, i // 2
    x = 0.62 + col * 6.15
    y = 1.72 + row * 1.85
    card(s, x, y, 5.90, 1.60, color)
    text(s, x + 0.22, y + 0.18, 0.45, 0.30, num, role="card_number", color=color)
    text(s, x + 0.78, y + 0.14, 4.90, 0.34, title, role="card_title_sm")
    text(s, x + 0.80, y + 0.62, 4.80, 0.80, desc, role="note", color=BODY,
         line_spacing=1.02)
text(s, 0.62, 5.55, 12.0, 0.45,
     "Los tres siguen el mismo patrón: un evento dispara código y el código "
     "mueve un componente.", role="body_strong")
footer(s, "Siguiente: generación de assets con IA.")
notes(s,
      "Cierre.\n\n"
      "Audio: un solo AudioSource con clip base en loop y efectos con "
      "PlayOneShot. Los scripts llaman a métodos static.\n\n"
      "Piedras: raycast para el click, Rigidbody kinematic mientras se "
      "arrastra, gravedad al soltar y recálculo del grid al tocar Piso o "
      "Paredes.\n\n"
      "Animator: el controlador es una FSM. El código escribe Bool y Trigger; "
      "el Animator decide el estado. IsName permite que el gameplay consulte "
      "la animación.\n\n"
      "Kickback: el enemigo autoriza el golpe con su cono, Velma calcula away, "
      "normaliza y aplica kickBack; el trigger push reproduce VelmaDrop.\n\n"
      "Todo el código está en Assets/Scripts/escena8_misc y en csharp/.")

# ---------------------------------------------------------------- auditoria
bad = [row for row in IMG_AUDIT if row[3] < MIN_IMG_PT]
print(f"AUDITORIA DE TEXTO EN PNG (minimo {MIN_IMG_PT:g} pt efectivos)")
for slide_no, kind, name, pt in IMG_AUDIT:
    flag = "FAIL" if pt < MIN_IMG_PT else "OK  "
    print(f"  {flag} slide {slide_no:02d} {kind:7s} {name:28s} {pt:5.2f} pt")
if bad:
    print(f"{len(bad)} imagen(es) por debajo del minimo")
    raise SystemExit(1)
print(f"OK: {len(IMG_AUDIT)} PNG con texto >= {MIN_IMG_PT:g} pt efectivos")

# ---------------------------------------------------------------- guardar
tmp = PPTX.with_suffix(".tmp.pptx")
prs.save(tmp)
report = validate(tmp, strict=True)
print(report.format())
if report.errors:
    raise SystemExit(1)
tmp.replace(PPTX)
print(f"OK: {PPTX} ({len(prs.slides)} diapositivas)")
