#!/usr/bin/env python3
"""Construye T8.6.1 - Matemáticas básicas para videojuegos.

Diseño basado en FINAL-plantilla-videojuegos.pptx: fondo pixel art,
Neuromax, tarjetas blancas y acentos naranja/rosa.
"""
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

from make_code_images import CODE, CODE_DEFAULT

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT
PPTX = ROOT.parent / "T8.6.1-Matematicas-basicas.pptx"

# ---------------------------------------------------------------- palette
INK = RGBColor(0x13, 0x13, 0x15)
BODY = RGBColor(0x4F, 0x53, 0x61)
MUTED = RGBColor(0x6B, 0x72, 0x80)
ORANGE = RGBColor(0xF0, 0x8A, 0x3C)
ORANGE_TEXT = RGBColor(0xB4, 0x53, 0x09)
PINK = RGBColor(0xE8, 0x38, 0x6D)
YELLOW = RGBColor(0xFF, 0xC4, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x2B, 0x29, 0x3D)
SOFT = RGBColor(0xF4, 0xF7, 0xFA)
LINE = RGBColor(0xD9, 0xDE, 0xE8)

REG = "Neuromax"
SEM = "Neuromax SemBd"
SW, SH = 13.333, 7.5

CODE_HEADER = "CÓDIGO DE LA DIAPOSITIVA (archivo Assets/EnemigoEsfera.cs):\n\n"


# ---------------------------------------------------------------- helpers
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


def rect(slide, x, y, w, h, fill=WHITE, line=None, line_w=1.0, shape=MSO_SHAPE.RECTANGLE):
    shp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
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


def picture(slide, name, x, y, w, h, border=True, border_w=1.5):
    path = ASSETS / "img" / name
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


def code_picture(slide, name, x, y, w, h):
    path = ASSETS / "codigo" / name
    im = Image.open(path)
    iw, ih = im.size
    scale = min(w / iw, h / ih)
    nw, nh = iw * scale, ih * scale
    left, top = x + (w - nw) / 2, y + (h - nh) / 2
    return slide.shapes.add_picture(str(path), Inches(left), Inches(top),
                                    Inches(nw), Inches(nh))


def bg(slide):
    slide.shapes.add_picture(str(ASSETS / "template" / "bg.png"), 0, 0,
                             Inches(SW), Inches(SH))


def header(slide, kicker, title, subtitle):
    rect(slide, 0.62, 0.30, 0.09, 0.09, ORANGE)
    text(slide, 0.81, 0.27, 10.5, 0.22, kicker, 9.5, INK, SEM)
    text(slide, 0.62, 0.52, 11.95, 0.72, title, 36, INK, SEM,
         line_spacing=0.95)
    text(slide, 0.62, 1.18, 11.95, 0.38, subtitle, 16, BODY, REG)


def footer(slide, value, y=6.18, h=0.5):
    rect(slide, 0.55, y, 11.17, h, WHITE)
    text(slide, 0.75, y + 0.12, 10.8, 0.28, value, 12.2, BODY, REG)


def notes(slide, value):
    slide.notes_slide.notes_text_frame.text = value


def card(slide, x, y, w, h, accent=ORANGE, fill=WHITE):
    rect(slide, x, y, w, h, fill)
    rect(slide, x, y, 0.07, h, accent)


def shot(slide, name, x, y, w, h, label=None, border=True):
    picture(slide, name, x, y, w, h, border=border)
    if label:
        text(slide, x, y + h + 0.08, w, 0.22, label, 10.5, MUTED, REG)


def divider(numero, title_lines, subtitle, tags):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    rect(s, 0.62, 0.32, 0.09, 0.09, ORANGE)
    text(s, 0.81, 0.28, 9.5, 0.22, "BLOQUE " + numero, 9.5, INK, SEM)
    text(s, 0.62, 0.98, 2.0, 1.0, numero, 60, ORANGE, SEM)
    text(s, 0.62, 1.92, 7.4, 1.6, title_lines, 48, INK, SEM, line_spacing=0.95)
    rect(s, 0.62, 3.85, 2.2, 0.07, ORANGE)
    text(s, 0.62, 4.12, 6.6, 0.9, subtitle, 18, BODY, REG, line_spacing=1.05)
    text(s, 0.62, 5.22, 7.4, 0.3, tags, 13, ORANGE, SEM)
    s.shapes.add_picture(str(ASSETS / "template" / "cloud.png"), Inches(9.56), Inches(1.1),
                         Inches(1.84), Inches(0.8))
    s.shapes.add_picture(str(ASSETS / "template" / "cloud-low.png"), Inches(7.55), Inches(0.55),
                         Inches(1.4), Inches(0.58))
    s.shapes.add_picture(str(ASSETS / "template" / "star.png"), Inches(11.35), Inches(3.35),
                         Inches(1.05), Inches(1.0))
    s.shapes.add_picture(str(ASSETS / "template" / "chest.png"), Inches(9.55), Inches(4.95),
                         Inches(2.45), Inches(1.3))
    notes(s, {
        "01": "Bloque 1. Preparamos la esfera, su collider y su Rigidbody, y conectamos el cubo con el script.",
        "02": "Bloque 2. Medimos vectores, normalizamos la dirección y movemos la esfera entre las cuatro esquinas.",
        "03": "Bloque 3. Calculamos el ángulo con atan2 y decidimos si el cubo produjo un pisotón.",
        "04": "Bloque 4. Probamos el contacto, miramos la consola y calibramos el umbral.",
    }[numero])
    return s


def code_slide(kicker, title, subtitle, code_name, code_text, items,
               footer_note, note_text, max_w=7.4, max_h=4.05):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    header(s, kicker, title, subtitle)
    im = Image.open(ASSETS / "codigo" / code_name)
    iw, ih = im.size
    scale = min(max_w / iw, max_h / ih)
    cw, ch = iw * scale, ih * scale
    card_w, card_h = cw + 0.42, ch + 0.34
    rect(s, 0.55, 1.58, card_w, card_h, WHITE)
    code_picture(s, code_name, 0.55 + (card_w - cw) / 2,
                 1.58 + (card_h - ch) / 2, cw, ch)
    rect(s, 0.55 + card_w - 0.55, 1.66, 0.46, 0.22, WHITE, LINE, 0.75,
         MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 0.55 + card_w - 0.55, 1.695, 0.46, 0.16, "C#", 7.5, BODY, SEM,
         align=PP_ALIGN.CENTER)

    rx = 0.55 + card_w + 0.28
    rw = 12.66 - rx
    yy = 1.70
    for head, body in items:
        text(s, rx, yy, rw, 0.25, head, 15.0, INK, SEM)
        text(s, rx, yy + 0.27, rw, 0.42, body, 12.4, BODY, REG, line_spacing=0.98)
        yy += 0.77
    footer(s, footer_note)
    notes(s, note_text + "\n\n" + CODE_HEADER + code_text)
    return s


# ---------------------------------------------------------------- deck
prs = Presentation()
prs.slide_width = Inches(SW)
prs.slide_height = Inches(SH)
prs.core_properties.title = "T8.6.1 · Matemáticas básicas para videojuegos"
prs.core_properties.author = "TC2005B · Construcción de Software"
prs.core_properties.subject = "Distancia, ángulos con atan2 y vectores en Unity"
prs.core_properties.keywords = "Unity, matemáticas, atan2, vectores, pisotón, TC2005B"
prs.core_properties.language = "es-MX"

# 1 ---------------------------------------------------------------- portada
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
rect(s, 0.62, 0.32, 0.09, 0.09, ORANGE)
text(s, 0.81, 0.28, 9.5, 0.22, "8.6.1 · MATEMÁTICAS", 9.5, INK, SEM)
text(s, 0.62, 1.02, 6.0, 2.45, "MATEMÁTICAS\nPARA ENEMIGOS", 52, INK, SEM, line_spacing=0.9)
rect(s, 0.62, 3.55, 2.2, 0.07, ORANGE)
text(s, 0.62, 3.80, 5.55, 0.45, "Distancia, ángulos y vectores en Unity", 20, INK, REG)
text(s, 0.62, 4.34, 5.4, 0.34, "Una esfera que patrulla y detecta un pisotón", 16, BODY, REG)
text(s, 0.62, 4.72, 5.4, 0.28, "TC2005B · Construcción de Software", 12.5, INK, REG)

rect(s, 6.55, 0.66, 6.18, 4.95, DARK)
shot(s, "07-escena-esfera.png", 6.92, 0.92, 2.72, 2.23)
text(s, 6.92, 3.20, 2.72, 0.22, "ESCENA", 10.5, WHITE, SEM)
shot(s, "diagrama-angulo.png", 9.86, 0.92, 2.55, 1.28)
text(s, 9.86, 2.24, 2.55, 0.22, "ÁNGULO", 10.5, WHITE, SEM)
shot(s, "diagrama-distancia.png", 8.00, 3.24, 4.35, 2.18)
text(s, 6.92, 5.46, 5.4, 0.22, "DISTANCIA + ÁNGULO = PISOTÓN", 10.5, WHITE, SEM)

s.shapes.add_picture(str(ASSETS / "template" / "cloud.png"), Inches(5.05), Inches(0.28),
                     Inches(1.35), Inches(0.56))
s.shapes.add_picture(str(ASSETS / "template" / "tree.png"), Inches(0.55), Inches(5.02),
                     Inches(1.1), Inches(1.97))
s.shapes.add_picture(str(ASSETS / "template" / "tree-small.png"), Inches(1.42), Inches(5.73),
                     Inches(0.8), Inches(1.22))
s.shapes.add_picture(str(ASSETS / "template" / "mushroom.png"), Inches(2.18), Inches(6.47),
                     Inches(0.61), Inches(0.37))
text(s, 10.15, 5.86, 2.6, 0.3, "Unity 6.3 LTS · URP 3D", 11.5, BODY, REG)
notes(s, """Bienvenida al tema 8.6.1. Hoy usamos matemáticas básicas para controlar un enemigo en Unity.

La meta es que una esfera patrulle entre las esquinas del plano y reconozca cuándo el cubo cae sobre ella. Para lograrlo medimos distancias, normalizamos direcciones y calculamos un ángulo con atan2.

El punto de partida es el proyecto Unity_Intro_2, que ya tiene el cubo con movimiento y salto. El proyecto final está en Unity_Intro_3.
""")

# 2 ---------------------------------------------------------------- recorrido
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · RECORRIDO", "LO QUE VEREMOS HOY",
       "La clase tiene cuatro bloques: de la esfera en la escena al pisotón.")
items = [
    ("01", "LA ESFERA EN LA ESCENA", "Agregamos la esfera, la hacemos cinemática y conectamos el cubo.", ORANGE),
    ("02", "DISTANCIA Y MOVIMIENTO", "Medimos vectores, normalizamos la dirección y patrullamos entre esquinas.", PINK),
    ("03", "ÁNGULO Y PISOTÓN", "Calculamos el ángulo con atan2 y decidimos si el cubo cae encima.", ORANGE),
    ("04", "PRUEBAS Y AJUSTES", "Probamos el contacto, calibramos el umbral y revisamos errores.", PINK),
]
y = 1.66
for num, ttl, desc, accent in items:
    card(s, 0.62, y, 12.09, 0.72, accent)
    text(s, 0.82, y + 0.16, 0.45, 0.3, num, 13, accent, SEM)
    text(s, 1.42, y + 0.11, 8.6, 0.32, ttl, 19, INK, SEM)
    text(s, 1.42, y + 0.42, 9.4, 0.25, desc, 12.8, BODY, REG)
    text(s, 12.05, y + 0.18, 0.45, 0.3, "→", 17, INK, REG)
    y += 0.80
text(s, 0.62, 5.74, 12.09, 0.3,
     "Al final, la esfera patrulla sola y reconoce un pisotón.", 15, BODY, REG)
notes(s, """Recorrido en cuatro bloques.

1. Preparamos la esfera, su collider y su Rigidbody, y conectamos el cubo con el script.
2. Medimos vectores, normalizamos la dirección y movemos la esfera entre las cuatro esquinas.
3. Calculamos el ángulo con atan2 y decidimos si el cubo produjo un pisotón.
4. Probamos el contacto, calibramos el umbral y revisamos los errores más comunes.

La explicación sigue el código final de EnemigoEsfera.cs y las capturas del proceso en Unity.
""")

# 3 ---------------------------------------------------------------- bloque 01
divider("01", "UNA ESFERA\nQUE PATRULLA",
        "Primero preparamos el objeto, su collider y su Rigidbody.",
        "ESFERA · COLLIDER · RIGIDBODY · SCRIPT")

# 4 ---------------------------------------------------------------- base
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · PUNTO DE PARTIDA", "PARTIMOS DE UN CUBO QUE YA SALTA",
       "El proyecto Unity_Intro_2 ya tiene movimiento, salto y contador de caídas.")
card(s, 0.62, 1.62, 5.65, 4.25, ORANGE)
text(s, 0.88, 1.80, 5.1, 0.3, "LO QUE YA EXISTE", 12, ORANGE_TEXT, SEM)
text(s, 0.88, 2.18, 5.05, 3.4,
     "El cubo se mueve con WASD y salta con la barra espaciadora.\n\n"
     "CubeMove conserva el Rigidbody, la detección de suelo y el contador de caídas.\n\n"
     "El nuevo enemigo será una esfera que patrulla el plano.\n\n"
     "No modificamos CubeMove: agregamos EnemigoEsfera.",
     15.5, BODY, REG, line_spacing=1.12)
shot(s, "07-escena-esfera.png", 6.85, 1.60, 5.55, 4.55)
notes(s, """El proyecto base es Unity_Intro_2. El cubo ya se mueve con WASD, salta con Space y cuenta las caídas.

Para este tema agregamos un enemigo nuevo: una esfera que patrulla las esquinas del plano. El cubo conserva su salto y su HUD; no modificamos CubeMove.

La escena de trabajo está en Unity_Intro_3. La esfera se llama Enemigo y el script se llama EnemigoEsfera.
""")

# 5 ---------------------------------------------------------------- crear script
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · SCRIPT", "CREAR EL SCRIPT DEL ENEMIGO",
       "En la carpeta Assets, haz clic derecho y elige Create → Scripting → MonoBehaviour Script.")
shot(s, "01-crear-script.png", 0.62, 1.58, 4.55, 3.03)
text(s, 0.62, 4.78, 4.55, 0.4, "Ruta: Create → Scripting → MonoBehaviour Script", 11.5, MUTED, REG)
card(s, 5.55, 1.58, 7.0, 4.4, PINK)
steps = [
    ("1", "Abre la carpeta Assets en la ventana Project."),
    ("2", "Haz clic derecho en un espacio vacío."),
    ("3", "Elige Create → Scripting → MonoBehaviour Script."),
    ("4", "Escribe el nombre EnemigoEsfera y presiona Enter."),
]
yy = 1.80
for num, txt in steps:
    text(s, 5.85, yy, 0.35, 0.3, num, 17, PINK, SEM)
    text(s, 6.30, yy - 0.02, 5.85, 0.55, txt, 16, INK, REG, line_spacing=1.0)
    yy += 0.92
text(s, 5.85, 5.55, 6.2, 0.28, "El archivo debe quedar dentro de Assets.", 12.5, MUTED, REG)
footer(s, "Unity compila el script cuando está dentro de la carpeta Assets.")
notes(s, """Para crear el script, abre la carpeta Assets en la ventana Project.

Haz clic derecho en un espacio vacío, elige Create, luego Scripting y finalmente MonoBehaviour Script. Escribe el nombre EnemigoEsfera.

El nombre del archivo debe coincidir con el nombre de la clase. Si no coincide, Unity muestra un error y no puede agregar el componente al GameObject.
""")

# 6 ---------------------------------------------------------------- script vacio
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · SCRIPT", "EL SCRIPT EMPIEZA VACÍO",
       "Unity crea la clase con Start y Update; ahí escribiremos la lógica.")
shot(s, "02-script-vacio.png", 0.62, 1.60, 5.2, 2.88)
text(s, 0.62, 4.62, 5.2, 0.28, "Esta es la plantilla inicial de EnemigoEsfera.cs.", 10.5, MUTED, REG)
card(s, 6.25, 1.58, 6.3, 4.25, ORANGE)
text(s, 6.52, 1.76, 5.7, 0.3, "TRES IDEAS BÁSICAS", 12, ORANGE_TEXT, SEM)
text(s, 6.52, 2.12, 5.7, 3.3,
     "EnemigoEsfera hereda de MonoBehaviour. Eso permite agregarlo a un GameObject.\n\n"
     "Start se ejecuta una vez, al comenzar la escena. Ahí preparamos las esquinas.\n\n"
     "Update se ejecuta una vez por frame. Ahí movemos la esfera y comprobamos el pisotón.",
     15, BODY, REG, line_spacing=1.12)
footer(s, "El nombre de la clase debe ser igual al nombre del archivo.")
notes(s, """Unity crea una clase vacía que hereda de MonoBehaviour.

Start se ejecuta una vez, al inicio de la escena. Update se ejecuta en cada frame, muchas veces por segundo.

El nombre de la clase debe coincidir con el nombre del archivo. En este caso, la clase y el archivo se llaman EnemigoEsfera.

CÓDIGO INICIAL DEL ARCHIVO:

""" + CODE_DEFAULT)

# 7 ---------------------------------------------------------------- agregar esfera
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · ESCENA", "AGREGAR LA ESFERA",
       "Abre GameObject → 3D Object → Sphere y cámbiale el nombre a Enemigo.")
shot(s, "03-crear-esfera.png", 0.62, 1.58, 4.3, 4.43)
card(s, 5.35, 1.58, 7.2, 4.35, PINK)
text(s, 5.62, 1.76, 6.55, 0.3, "MEDIDAS QUE IMPORTAN", 12, PINK, SEM)
text(s, 5.62, 2.12, 6.55, 3.4,
     "La esfera primitiva mide 1 unidad de diámetro; su radio es 0.5.\n\n"
     "El plano primitivo mide 10 × 10. Sus esquinas reales están en ±5.\n\n"
     "Para que la esfera no se salga, las esquinas de patrulla se meten 0.5: quedan en ±4.5.\n\n"
     "Renombra la esfera como Enemigo para encontrarla fácilmente.",
     15, BODY, REG, line_spacing=1.12)
footer(s, "El centro de la esfera debe quedar dentro del plano.")
notes(s, """Agrega una esfera con GameObject, 3D Object, Sphere. Renómbrala como Enemigo.

La esfera mide 1 unidad de diámetro, así que su radio es 0.5. El plano mide 10 por 10 unidades y sus esquinas reales están en 5 y -5.

Si el centro de la esfera llega a 5, medio cuerpo queda fuera del plano. Por eso las esquinas de patrulla se meten 0.5 y quedan en 4.5 y -4.5.
""")

# 8 ---------------------------------------------------------------- colocar esfera
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · TRANSFORM", "COLOCAR LA ESFERA EN UNA ESQUINA",
       "Usa Position = (4.5, 0.5, 4.5); Y = 0.5 evita que la esfera se hunda.")
card(s, 0.62, 1.58, 5.2, 1.85, ORANGE)
text(s, 0.86, 1.74, 4.75, 1.5,
     "La esfera aparece en el centro. La movemos a una esquina.\n\n"
     "Y = 0.5 es la mitad de la esfera: así queda apoyada sobre el plano.",
     15, BODY, REG, line_spacing=1.08)
shot(s, "06-inspector-esquina.png", 0.62, 3.66, 5.2, 1.66)
text(s, 0.62, 5.40, 5.2, 0.22, "El Inspector muestra la posición final.", 10.5, MUTED, REG)
shot(s, "07-escena-esfera.png", 6.85, 1.58, 5.55, 4.55)
footer(s, "Las cuatro esquinas de patrulla están en X y Z iguales a ±4.5.")
notes(s, """Selecciona Enemigo y cambia su Transform.

La posición final es X = 4.5, Y = 0.5, Z = 4.5. La altura Y es 0.5 porque la esfera tiene radio 0.5: así queda apoyada sobre el plano y no se hunde.

Las cuatro esquinas de patrulla serán (4.5, 0.5, 4.5), (4.5, 0.5, -4.5), (-4.5, 0.5, -4.5) y (-4.5, 0.5, 4.5).
""")

# 9 ---------------------------------------------------------------- rigidbody
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · FÍSICA", "HACERLA CINEMÁTICA",
       "Sphere Collider detecta el contacto; Rigidbody con Is Kinematic evita la gravedad.")
shot(s, "08-sphere-collider.png", 0.62, 1.58, 3.85, 4.15)
text(s, 0.62, 5.80, 3.85, 0.22, "Sphere Collider tiene radio 0.5.", 10.5, MUTED, REG)
card(s, 5.05, 1.58, 3.45, 3.0, PINK)
text(s, 5.30, 1.74, 3.0, 0.28, "DOS COMPONENTES", 12, PINK, SEM)
text(s, 5.30, 2.10, 3.0, 2.25,
     "Sphere Collider permite que el cubo choque con la esfera.\n\n"
     "Rigidbody con Is Kinematic evita que la gravedad mueva la esfera.",
     14, BODY, REG, line_spacing=1.10)
shot(s, "09-rigidbody.png", 8.85, 1.58, 3.75, 2.48)
text(s, 8.85, 4.14, 3.75, 0.22, "Is Kinematic está marcado.", 10.5, MUTED, REG)
text(s, 8.85, 4.55, 3.75, 1.2,
     "El script cambia transform.position; la física no debe moverla por su cuenta.",
     13, BODY, REG, line_spacing=1.05)
footer(s, "Sin Is Kinematic, la esfera cae por la gravedad y no puedes controlar su posición.")
notes(s, """La esfera necesita dos componentes.

Sphere Collider le permite chocar con el cubo. El radio debe ser 0.5, que coincide con el tamaño de la esfera.

Rigidbody le da presencia física, pero marcamos Is Kinematic. Así la gravedad no la mueve y el script puede cambiar transform.position sin pelear con la física.

Si olvidas Is Kinematic, la esfera cae al piso y el movimiento entre esquinas se vuelve impredecible.
""")

# 10 --------------------------------------------------------------- conectar cubo
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · INSPECTOR", "CONECTAR EL CUBO CON EL SCRIPT",
       "Arrastra el objeto Cube al campo Cubo; si queda vacío, el script falla.")
text(s, 0.62, 1.58, 5.35, 1.35,
     "El campo Cubo guarda una referencia al Transform del jugador. La esfera lo usa para calcular la distancia y el ángulo.",
     15, BODY, REG, line_spacing=1.08)
shot(s, "11-script-cubo-none.png", 0.62, 3.10, 5.35, 0.89)
text(s, 0.62, 4.04, 5.35, 0.22, "El campo Cubo está vacío.", 10.5, MUTED, REG)
shot(s, "13-parametros.png", 0.62, 4.42, 5.35, 0.89)
text(s, 0.62, 5.36, 5.35, 0.22, "El Cubo está asignado y los parámetros están listos.", 10.5, MUTED, REG)
shot(s, "12-asignar-cubo.png", 6.95, 1.58, 5.45, 2.79)
text(s, 6.95, 4.48, 5.45, 0.22, "Selecciona Cube en la lista Scene.", 10.5, MUTED, REG)
footer(s, "Si el campo Cubo queda en None, Pisoton lanza NullReferenceException.")
notes(s, """Selecciona Enemigo y busca el componente Enemigo Esfera.

El campo Cubo debe apuntar al Transform del cubo. Haz clic en el círculo del campo, elige la pestaña Scene y selecciona Cube.

Si el campo queda en None, el script intenta leer cubo.position y lanza una NullReferenceException cada vez que se ejecuta Pisoton.

En la escena, Velocidad vale 5 y Distancia Contacto vale 1.5. El script declara 1.1 por defecto, pero el Inspector manda.
""")

# 11 --------------------------------------------------------------- campos
code_slide(
    "8.6.1 · CÓDIGO", "LOS DATOS DE LA ESFERA",
    "Seis campos guardan el objetivo, la velocidad y los umbrales.",
    "code_campos.png", CODE["campos"],
    [
        ("cubo", "Guarda una referencia al Transform del jugador."),
        ("esquinas", "Contiene las cuatro posiciones del plano."),
        ("indiceObjetivo", "Indica la esquina que la esfera persigue."),
        ("velocidad", "Indica las unidades que avanza por segundo."),
        ("distanciaContacto", "Define el radio horizontal del pisotón."),
        ("anguloPisoton", "Define el ángulo mínimo en grados."),
    ],
    "En la escena, distanciaContacto vale 1.5 y anguloPisoton vale 60.",
    """Estos son los datos que el script necesita para trabajar.

Cubo es la referencia al jugador. Esquinas guarda las cuatro posiciones. IndiceObjetivo dice cuál esquina se persigue en este momento.

Velocidad controla cuántas unidades avanza la esfera por segundo. DistanciaContacto es el radio horizontal que se acepta para el pisotón. AnguloPisoton es el ángulo mínimo, medido desde la horizontal.

El Inspector puede cambiar estos valores sin editar el código.""",
    max_w=7.4, max_h=4.05,
)

# 12 --------------------------------------------------------------- bloque 02
divider("02", "DISTANCIA Y\nMOVIMIENTO",
        "Restar, medir, normalizar y sumar para mover la esfera.",
        "VECTORES · LONGITUD · NORMALIZACIÓN · DELTA TIME")

# 13 --------------------------------------------------------------- figura distancia
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · DISTANCIA", "LA DISTANCIA ES UN TRIÁNGULO",
       "La esfera y la esquina están a la misma altura, así que solo importan X y Z.")
picture(s, "diagrama-distancia.png", 0.86, 1.62, 11.6, 5.40, border=False)
notes(s, """Para saber si la esfera llegó a la esquina, medimos la distancia entre dos puntos.

La fórmula general es d = raíz de dx al cuadrado más dy al cuadrado más dz al cuadrado. En este caso, la esfera y la esquina están a la misma altura, así que dy = 0. La fórmula se reduce a d = raíz de dx al cuadrado más dz al cuadrado.

Con la esfera en (4.5, 0.5, 4.5) y la esquina opuesta en (-4.5, 0.5, -4.5), dx = -9 y dz = -9. La distancia es raíz de 162, que es 12.73.

La misma distancia horizontal se usa en Pisoton, pero ahí la altura dy se trata por separado con el ángulo.
""")

# 14 --------------------------------------------------------------- longitud normalizar
code_slide(
    "8.6.1 · CÓDIGO", "MEDIR Y NORMALIZAR",
    "Longitud mide el vector; Normalizar lo convierte en dirección unitaria.",
    "code_longitud.png", CODE["longitud"],
    [
        ("Longitud", "La función calcula √(x² + y² + z²) con Math.Sqrt."),
        ("Normalizar", "Divide cada componente entre la longitud."),
        ("Protección", "Si la longitud es casi cero, devuelve el vector cero."),
        ("Uso", "La dirección unitaria evita que la diagonal sea más rápida."),
    ],
    "Sin normalizar, una diagonal de 45° avanza √2 veces más rápido.",
    """Longitud calcula el tamaño de un vector con la raíz de la suma de los cuadrados.

Normalizar divide cada componente entre la longitud. El resultado tiene longitud 1 y conserva la dirección.

El guard evita dividir entre cero cuando el vector es casi nulo. En la práctica, la esfera ya llegó a la esquina y no necesita moverse.

Normalizar es importante porque, sin ello, una diagonal de 45 grados avanzaría 1.41 veces más rápido que una línea recta.""",
    max_w=7.4, max_h=4.05,
)

# 15 --------------------------------------------------------------- mover
code_slide(
    "8.6.1 · CÓDIGO", "MOVER LA ESFERA",
    "Resta el objetivo, mide, normaliza y suma un paso por frame.",
    "code_mover.png", CODE["mover"],
    [
        ("hacia", "Es el vector que falta para llegar a la esquina."),
        ("distancia", "Longitud(hacia) decide si ya llegó."),
        ("direccion", "Normalizar deja una dirección de longitud 1."),
        ("paso", "Es la velocidad por deltaTime: la distancia de este frame."),
        ("posición", "La posición nueva es la actual más dirección por paso."),
    ],
    "La altura Y se conserva para que la esfera no se eleve.",
    """MoverEsfera sigue cuatro pasos.

Primero resta la posición actual al objetivo para obtener el vector hacia. Después mide ese vector con Longitud.

Si la distancia es menor a 0.1, la esfera ya llegó. El código elige otra esquina y hace return para no mover ese frame.

Si no llegó, normaliza la dirección y calcula el paso con velocidad por deltaTime. La posición nueva es la posición actual más dirección por paso. La altura Y se conserva.""",
    max_w=7.4, max_h=4.05,
)

# 16 --------------------------------------------------------------- start timer
code_slide(
    "8.6.1 · CÓDIGO", "CAMBIAR DE ESQUINA CADA 5 SEGUNDOS",
    "InvokeRepeating llama a NewRandom al inicio y después cada cinco segundos.",
    "code_start.png", CODE["start"],
    [
        ("esquinas", "Guarda cuatro vectores a ±4.5 en X y Z."),
        ("NewRandom", "Elige un índice entre 0 y 3."),
        ("InvokeRepeating", "Llama a NewRandom cada 5 segundos."),
        ("primer disparo", "Ocurre casi de inmediato; puede cambiar la esquina inicial."),
        ("llegada", "Si la distancia es menor a 0.1, elige otra esquina distinta."),
    ],
    "El temporizador puede cambiar el objetivo mientras la esfera viaja.",
    """Start prepara las cuatro esquinas y coloca la esfera en una de ellas.

NewRandom elige un índice entre 0 y 3 con UnityEngine.Random.Range. El límite superior es exclusivo.

InvokeRepeating llama a NewRandom con un retardo de 0 segundos y luego cada 5 segundos. El primer disparo ocurre casi de inmediato, así que la esquina inicial puede cambiar otra vez al inicio.

Cuando la esfera llega a menos de 0.1 de la esquina, MoverEsfera elige un desplazamiento de 1, 2 o 3 y da la vuelta con el módulo 4. Ese desplazamiento nunca es cero, así que la esquina nueva es distinta.""",
    max_w=7.4, max_h=4.05,
)

# 17 --------------------------------------------------------------- bloque 03
divider("03", "CONTACTO Y\nPISOTÓN",
        "Medir la distancia no basta: hay que saber desde qué dirección llega el cubo.",
        "CONTACTO · ATAN2 · ÁNGULO · RESET")

# 18 --------------------------------------------------------------- contacto
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · CÓDIGO", "PRIMER INTENTO: CONTACTO",
       "La primera versión solo mide la distancia entre los centros.")
im = Image.open(ASSETS / "codigo" / "code_contacto.png")
iw, ih = im.size
scale = min(6.35 / iw, 3.25 / ih)
cw, ch = iw * scale, ih * scale
card_w, card_h = cw + 0.42, ch + 0.34
rect(s, 0.55, 1.58, card_w, card_h, WHITE)
code_picture(s, "code_contacto.png", 0.55 + (card_w - cw) / 2,
             1.58 + (card_h - ch) / 2, cw, ch)
rect(s, 0.55 + card_w - 0.55, 1.66, 0.46, 0.22, WHITE, LINE, 0.75, MSO_SHAPE.ROUNDED_RECTANGLE)
text(s, 0.55 + card_w - 0.55, 1.695, 0.46, 0.16, "C#", 7.5, BODY, SEM, align=PP_ALIGN.CENTER)

text(s, 7.55, 1.70, 4.85, 0.25, "QUÉ HACE", 12, PINK, SEM)
text(s, 7.55, 2.02, 4.85, 2.15,
     "Calcula Longitud(haciaCubo) con X, Y y Z.\n\n"
     "Si la distancia es menor que distanciaContacto, devuelve true.\n\n"
     "No distingue si el cubo está arriba, al lado o abajo.",
     13.5, BODY, REG, line_spacing=1.06)
shot(s, "14b-prueba-consola.png", 7.55, 4.20, 4.85, 1.84)
notes(s, """La primera versión se llamaba Contacto y solo medía la distancia entre los centros.

Calculaba Longitud(haciaCubo) e incluía X, Y y Z. Si la distancia era menor que distanciaContacto, devolvía true.

El problema es que un golpe lateral también entraba en el umbral. La función no distinguía si el cubo estaba arriba, al lado o abajo.

En la prueba, la consola se llenó de OK porque cualquier contacto cumplía la condición. Por eso se reemplazó por Pisoton.

""" + CODE_HEADER + CODE["contacto"])

# 19 --------------------------------------------------------------- angulo figura
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · ÁNGULO", "SEPARAR LA ALTURA DEL PLANO",
       "La distancia horizontal es √(dx² + dz²); el ángulo sale de atan2(dy, horizontal).")
picture(s, "diagrama-angulo.png", 0.86, 1.62, 11.6, 5.40, border=False)
notes(s, """Para decidir si el cubo cayó encima, separamos la altura de la distancia horizontal.

Horizontal es raíz de dx al cuadrado más dz al cuadrado. Es la distancia vista desde arriba. La altura dy no entra en horizontal.

El ángulo de elevación sale de atan2(dy, horizontal). Atan2 recibe primero la altura y luego la distancia horizontal. Devuelve radianes, así que se multiplica por 180 y se divide entre pi.

El ángulo de 60 grados se mide desde la horizontal. Eso equivale a 30 grados desde la vertical.

La condición también pide horizontal menor o igual a distanciaContacto. Las dos condiciones juntas forman un cono recortado por un cilindro. No es una esfera de contacto.
""")

# 20 --------------------------------------------------------------- pisoton
code_slide(
    "8.6.1 · CÓDIGO", "LA FUNCIÓN PISOTON",
    "El ángulo y el radio horizontal deben cumplirse al mismo tiempo.",
    "code_pisoton.png", CODE["pisoton"],
    [
        ("haciaCubo", "Va del centro de la esfera al centro del cubo."),
        ("horizontal", "Es √(dx² + dz²); no incluye la altura."),
        ("atan2", "Recibe primero dy y luego horizontal."),
        ("grados", "Multiplica por 180 / π para convertir radianes."),
        ("condición", "Pide ángulo suficiente y radio horizontal."),
    ],
    "60° desde la horizontal equivale a 30° desde la vertical.",
    """Pisoton calcula el vector que va de la esfera al cubo y separa dx, dy y dz.

Horizontal es la raíz de dx al cuadrado más dz al cuadrado. Esa distancia no incluye la altura.

Atan2 calcula el ángulo de elevación. Recibe primero dy y luego horizontal. La multiplicación por 180 y la división entre pi convierten radianes a grados.

La condición exige que el ángulo sea mayor o igual a anguloPisoton y que horizontal sea menor o igual a distanciaContacto.

Si se cumple, escribe PISOTON, llama a Reset y devuelve true. Si no, devuelve false. El valor de retorno todavía se ignora en Update.""",
    max_w=7.4, max_h=4.05,
)

# 21 --------------------------------------------------------------- reset update
code_slide(
    "8.6.1 · CÓDIGO", "RESET Y UPDATE",
    "Reset reubica la esfera; Update decide el orden de las llamadas.",
    "code_reset_update.png", CODE["reset_update"],
    [
        ("Reset", "Elige una esquina aleatoria y teletransporta la esfera."),
        ("juego", "La esfera no desaparece ni termina la partida."),
        ("Update", "Primero mueve; después comprueba el pisotón."),
        ("Contacto", "Quedó comentada como paso didáctico."),
        ("retorno", "El bool de Pisoton se ignora por ahora."),
    ],
    "No hay pantalla de victoria ni derrota; solo el log y el teletransporte.",
    """Reset elige una esquina nueva con NewRandom y cambia transform.position.

La esfera no desaparece y el juego no termina. El InvokeRepeating sigue activo, así que el objetivo puede cambiar otra vez a los cinco segundos.

Update llama primero a MoverEsfera y después a Pisoton. Contacto quedó comentada como paso didáctico.

Pisoton devuelve un bool, pero Update lo ignora. Ese valor queda disponible para una victoria o una derrota futura.

NewRandom puede repetir la misma esquina. Si eso pasa, la esfera no se mueve y el log PISOTON puede repetirse en cada frame. No hay una bandera resuelto que lo impida.""",
    max_w=7.4, max_h=4.05,
)

# 22 --------------------------------------------------------------- bloque 04
divider("04", "PRUEBAS Y\nAJUSTES",
        "Probamos, miramos la consola y calibramos el umbral.",
        "PRUEBAS · CONSOLA · UMBRAL · ERRORES")

# 23 --------------------------------------------------------------- pruebas
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · PRUEBAS", "PROBAR EL PISOTÓN",
       "Cuatro pruebas separan el contacto lateral del pisotón real.")
shot(s, "14a-prueba-escena.png", 0.62, 1.58, 4.75, 4.30)
text(s, 0.62, 5.92, 4.75, 0.22, "La esfera patrulla mientras el cubo salta.", 10.5, MUTED, REG)
card(s, 5.75, 1.58, 6.9, 4.35, ORANGE)
tests = [
    ("CONTACTO LATERAL", "Camina contra la esfera sin saltar. No debe aparecer PISOTON."),
    ("CAÍDA DESDE ARRIBA", "Salta y cae sobre la esfera. Debe aparecer PISOTON y la esfera debe reubicarse."),
    ("BORDE", "Salta cerca del borde. El ángulo no debe alcanzar 60 grados."),
    ("TEMPORIZADOR", "Espera cinco segundos. El índice objetivo debe cambiar."),
]
yy = 1.78
for head, body in tests:
    text(s, 6.00, yy, 6.35, 0.25, head, 13, ORANGE_TEXT, SEM)
    text(s, 6.00, yy + 0.28, 6.35, 0.5, body, 12.4, BODY, REG, line_spacing=1.0)
    yy += 0.98
footer(s, "Revisa la consola: el log PISOTON confirma la detección.")
notes(s, """Prueba el sistema en este orden.

Primero camina contra la esfera sin saltar. No debe aparecer PISOTON, porque el ángulo es bajo.

Después salta y cae sobre la esfera. Debe aparecer PISOTON y la esfera debe cambiar de esquina.

Prueba también un salto cerca del borde. El ángulo no debe alcanzar 60 grados.

Por último, espera cinco segundos sin tocar nada. El índice objetivo debe cambiar, aunque puede repetir la misma esquina.
""")

# 23 --------------------------------------------------------------- calibrar
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · AJUSTE", "AJUSTAR EL UMBRAL",
       "Cuanto más lejos del centro, más alto debe estar el cubo para cumplir 60°.")
vals = [
    ("0.5", "0.87", "1.37", ORANGE),
    ("1.0", "1.73", "2.23", PINK),
    ("1.5", "2.60", "3.10", ORANGE),
]
x = 0.62
for horiz, dy, cy, accent in vals:
    card(s, x, 1.85, 3.72, 2.25, accent)
    text(s, x + 0.25, 2.02, 3.2, 0.25, f"horizontal = {horiz}", 12, accent, SEM)
    text(s, x + 0.25, 2.40, 1.1, 0.7, dy, 32, INK, SEM)
    text(s, x + 1.35, 2.52, 2.1, 0.3, "dy mínimo", 12, MUTED, REG)
    text(s, x + 0.25, 3.18, 3.2, 0.3, f"Centro del cubo: y = {cy}", 12.5, BODY, REG)
    text(s, x + 0.25, 3.55, 3.2, 0.3, "Así el ángulo llega a 60°.", 11.5, MUTED, REG)
    x += 4.10
rect(s, 0.62, 4.55, 12.09, 1.45, WHITE)
text(s, 0.88, 4.72, 11.5, 0.28, "CÓMO LEER LA TABLA", 11.5, ORANGE_TEXT, SEM)
text(s, 0.88, 5.05, 11.5, 0.82,
     "dy mínimo = horizontal × tan(60°). Cuanto mayor es la distancia lateral, más alto debe estar el cubo. "
     "El radio efectivo del pisotón es menor que distanciaContacto porque el salto tiene altura limitada.",
     13.5, BODY, REG, line_spacing=1.05)
footer(s, "En la escena, distanciaContacto vale 1.5 y anguloPisoton vale 60.")
notes(s, """El umbral de 60 grados y el radio de 1.5 no son independientes.

Para que el ángulo llegue a 60 grados, la altura mínima es horizontal por tangente de 60 grados.

Con horizontal 0.5, dy mínimo es 0.87 y el centro del cubo debe estar en y = 1.37. Con horizontal 1.0, dy mínimo es 1.73 y el centro debe estar en y = 2.23. Con horizontal 1.5, dy mínimo es 2.60 y el centro debe estar en y = 3.10.

Por eso el radio efectivo es menor que 1.5: el salto normal no alcanza esas alturas. Calibra distanciaContacto y anguloPisoton con el salto real del cubo.

En la escena, distanciaContacto vale 1.5. El script declara 1.1 por defecto, pero el Inspector manda.
""")

# 24 --------------------------------------------------------------- errores
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · REVISIÓN", "ERRORES COMUNES",
       "Estos detalles explican la mayoría de los fallos al probar la esfera.")
errs = [
    ("01", "RANDOM AMBIGUO", "Usa UnityEngine.Random.Range, no Random.Range.", ORANGE),
    ("02", "ATAN2 EN RADIANES", "Convierte con 180 / Math.PI.", PINK),
    ("03", "HORIZONTAL NO ES 3D", "La altura dy se usa en el ángulo, no en horizontal.", ORANGE),
    ("04", "RESET REPITE ESQUINA", "No hay bandera resuelto; el log puede repetirse.", PINK),
    ("05", "LA ESFERA SE CAE", "Activa Is Kinematic en el Rigidbody.", ORANGE),
    ("06", "EL CUBO NO SALTA", "estaEnSuelo solo se activa con el plano.", PINK),
]
for i, (num, head, body, accent) in enumerate(errs):
    col, row = i % 3, i // 3
    x = 0.62 + col * 4.10
    y = 1.72 + row * 1.95
    card(s, x, y, 3.82, 1.72, accent)
    text(s, x + 0.22, y + 0.14, 0.4, 0.22, num, 10, accent, SEM)
    text(s, x + 0.22, y + 0.40, 3.35, 0.3, head, 12.5, INK, SEM)
    text(s, x + 0.22, y + 0.78, 3.35, 0.72, body, 11.8, BODY, REG, line_spacing=1.0)
footer(s, "Corrige estos puntos antes de ajustar los umbrales.")
notes(s, """Revisa estos errores antes de calibrar.

Random ambiguo: usa UnityEngine.Random.Range porque el archivo tiene using System.

Atan2 devuelve radianes. Multiplica por 180 y divide entre Math.PI.

Horizontal no es la distancia 3D. La altura dy se usa en el ángulo.

Reset puede repetir la misma esquina porque NewRandom puede devolver el mismo índice. No hay bandera resuelto.

Si la esfera se cae, revisa Is Kinematic. Si el cubo no recupera el salto sobre la esfera, recuerda que estaEnSuelo solo se activa al chocar con el plano.
""")

# 25 --------------------------------------------------------------- resumen
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.6.1 · RESUMEN", "LO QUE APRENDISTE",
       "Cuatro ideas para mover y detectar enemigos con matemáticas.")
summary = [
    ("01", "DISTANCIA", "Longitud mide el vector; la horizontal separa XZ de Y.", ORANGE),
    ("02", "DIRECCIÓN", "Normalizar evita que la diagonal sea más rápida.", PINK),
    ("03", "ÁNGULO", "atan2(dy, horizontal) mide la elevación del cubo.", ORANGE),
    ("04", "PISOTÓN", "Ángulo mínimo y radio horizontal deben cumplirse juntos.", PINK),
]
for i, (num, head, body, accent) in enumerate(summary):
    x = 0.62 + i * 3.08
    card(s, x, 1.80, 2.86, 2.9, accent)
    text(s, x + 0.22, 2.00, 0.5, 0.3, num, 14, accent, SEM)
    text(s, x + 0.22, 2.40, 2.4, 0.3, head, 19, INK, SEM)
    text(s, x + 0.22, 2.95, 2.4, 1.45, body, 14, BODY, REG, line_spacing=1.06)
text(s, 0.62, 5.10, 12.09, 0.35,
     "La misma base sirve para persecución: cambiar el objetivo y repetir.", 15, BODY, REG)
footer(s, "Restar, medir, normalizar y sumar son cuatro operaciones para mover un enemigo.")
notes(s, """Resumen de lo aprendido.

La distancia se calcula con Longitud. Para el pisotón usamos la distancia horizontal, que ignora la altura.

Normalizar convierte el vector en una dirección de longitud 1 y evita que la diagonal sea más rápida.

Atan2 calcula el ángulo de elevación con dy y horizontal. El ángulo se mide desde la horizontal.

El pisotón exige ángulo suficiente y radio horizontal suficiente. Las dos condiciones se cumplen al mismo tiempo.

La misma base sirve para persecución: cambia el objetivo de la esquina al cubo y repite las operaciones.
""")

# 26 --------------------------------------------------------------- creditos
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "CRÉDITOS", "CRÉDITOS Y REFERENCIAS",
       "Estos son los créditos y las referencias del tema.")
text(s, 0.62, 1.90, 5.8, 2.0,
     "Las capturas de Unity 6.3 y VS Code se elaboraron para este curso.\n\n"
     "El proyecto Unity_Intro_3 y el código EnemigoEsfera.cs son material del curso TC2005B.\n\n"
     "La guía del enemigo esfera, las figuras y los diagramas también son material del curso.",
     12, INK, REG, line_spacing=1.05)
text(s, 6.65, 1.90, 6.0, 2.0,
     "La documentación de Unity explica Vector3, Mathf.Atan2, Rigidbody e InvokeRepeating.\n\n"
     "Las marcas y herramientas citadas pertenecen a sus dueños y se usan con fines educativos.",
     12, INK, REG, line_spacing=1.05)
rect(s, 0.62, 3.70, 12.09, 1.35, WHITE)
text(s, 0.88, 3.86, 11.5, 0.25, "ENLACES DE CONSULTA", 10.5, ORANGE_TEXT, SEM)
text(s, 0.88, 4.16, 11.5, 0.75,
     "https://docs.unity3d.com/ScriptReference/Vector3.html\n"
     "https://docs.unity3d.com/ScriptReference/Mathf.Atan2.html\n"
     "https://docs.unity3d.com/ScriptReference/MonoBehaviour.InvokeRepeating.html",
     10.5, BODY, REG, line_spacing=1.0)
rect(s, 0.62, 5.35, 12.09, 0.5, WHITE)
text(s, 0.85, 5.48, 11.6, 0.25,
     "Los enlaces completos también están en las notas del presentador.", 10.5, BODY, REG)
notes(s, """Créditos y referencias.

Las capturas de Unity y VS Code se elaboraron para este curso. El proyecto Unity_Intro_3 y el código EnemigoEsfera.cs son material del curso.

La guía enemigo esfera, las figuras y los diagramas también son material del curso.

Enlaces:
https://docs.unity3d.com/ScriptReference/Vector3.html
https://docs.unity3d.com/ScriptReference/Mathf.Atan2.html
https://docs.unity3d.com/ScriptReference/MonoBehaviour.InvokeRepeating.html
https://docs.unity3d.com/Manual/class-Rigidbody.html
""")

# 27 --------------------------------------------------------------- preguntas
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
s.shapes.add_picture(str(ASSETS / "template" / "cloud.png"), Inches(1.7), Inches(2.0),
                     Inches(1.15), Inches(0.5))
s.shapes.add_picture(str(ASSETS / "template" / "cloud-low.png"), Inches(10.3), Inches(0.8),
                     Inches(1.15), Inches(0.48))
s.shapes.add_picture(str(ASSETS / "template" / "tree.png"), Inches(1.9), Inches(4.75),
                     Inches(1.05), Inches(1.88))
s.shapes.add_picture(str(ASSETS / "template" / "tree-small.png"), Inches(1.15), Inches(5.1),
                     Inches(0.8), Inches(1.22))
s.shapes.add_picture(str(ASSETS / "template" / "mushroom.png"), Inches(3.0), Inches(6.05),
                     Inches(0.55), Inches(0.33))
s.shapes.add_picture(str(ASSETS / "template" / "chest.png"), Inches(9.9), Inches(5.15),
                     Inches(1.8), Inches(0.95))
s.shapes.add_picture(str(ASSETS / "template" / "star.png"), Inches(11.9), Inches(5.2),
                     Inches(0.9), Inches(0.86))
text(s, 0.0, 2.05, 13.33, 1.2, "¿PREGUNTAS?", 80, INK, SEM, align=PP_ALIGN.CENTER)
text(s, 0.0, 3.58, 13.33, 0.35, "El siguiente tema es T8.6.2 · Colisiones.", 16, DARK, REG,
     align=PP_ALIGN.CENTER)
text(s, 0.0, 4.12, 13.33, 0.35, "La esfera ya patrulla; ahora aprende a chocar.", 16, ORANGE_TEXT, SEM,
     align=PP_ALIGN.CENTER)
notes(s, """Cierre del tema.

Recuerda las cuatro operaciones: restar para obtener el vector, medir con Longitud, normalizar para obtener la dirección y sumar para mover.

La esfera ya patrulla y reconoce un pisotón. En el siguiente tema veremos colisiones entre rectángulos y cubos.

Los archivos del tema están en T8-6-1_content y el proyecto final en Unity_Intro_3.
""")

prs.save(PPTX)
print("Guardado:", PPTX)
print("Diapositivas:", len(prs.slides))
