#!/usr/bin/env python3
"""Construye T8.4 - id Software: Game Development Principles.

El diseño sigue la plantilla FINAL-plantilla-videojuegos.pptx:
fondo pixel art, Neuromax, tarjetas blancas y acentos naranja/rosa.
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
ASSETS = ROOT
PPTX = ROOT.parent / "T8.4-id-Software-Game-Development-Principles.pptx"

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
MONO = "Menlo"

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


def label(slide, x, y, w, value, color=ORANGE_TEXT):
    text(slide, x, y, w, 0.22, value, 9.5, color, SEM)


def pill(slide, x, y, w, value, color=BODY):
    rect(slide, x, y, w, 0.24, WHITE, LINE, 0.75, MSO_SHAPE.ROUNDED_RECTANGLE)
    text(slide, x, y + 0.035, w, 0.18, value, 7.5, color, SEM,
         align=PP_ALIGN.CENTER)


def bullets(slide, x, y, w, items, size=12.5, gap=0.62, color=BODY,
            accent=ORANGE):
    yy = y
    for item in items:
        rect(slide, x, yy + 0.08, 0.07, 0.07, accent)
        text(slide, x + 0.18, yy, w - 0.18, gap, item, size, color, REG,
             line_spacing=1.02)
        yy += gap


# ---------------------------------------------------------------- deck
prs = Presentation()
prs.slide_width = Inches(SW)
prs.slide_height = Inches(SH)
prs.core_properties.title = "T8.4 · id Software: Game Development Principles"
prs.core_properties.author = "TC2005B · Construcción de Software"
prs.core_properties.subject = "Historia de id Software, BSP, raíz cuadrada inversa y principios de desarrollo"
prs.core_properties.keywords = "id Software, Doom, Quake, BSP, raíz cuadrada inversa, TC2005B"
prs.core_properties.language = "es-MX"

# 1 ---------------------------------------------------------------- portada
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
rect(s, 0.62, 0.32, 0.09, 0.09, ORANGE)
text(s, 0.81, 0.28, 9.5, 0.22, "8.4 · GAME DEVELOPMENT PRINCIPLES", 9.5, INK, SEM)
text(s, 0.62, 0.92, 5.9, 2.72,
     "ID SOFTWARE:\nINGENIERÍA\nQUE CAMBIÓ\nLOS FPS", 46, INK, SEM,
     line_spacing=0.92)
text(s, 0.62, 3.94, 5.55, 0.72,
     "Línea del tiempo, BSP, raíz cuadrada inversa y cinco principios.",
     18, INK, REG, line_spacing=1.02)
text(s, 0.62, 4.70, 5.45, 0.62,
     "De Commander Keen a Doom Eternal: cómo un equipo pequeño cambió la industria.",
     14, BODY, REG, line_spacing=1.02)
text(s, 0.62, 5.50, 5.4, 0.28,
     "TC2005B · Construcción de Software", 12.5, INK, REG)

rect(s, 6.55, 0.66, 6.18, 4.95, DARK)
grid = [
    ("img/keen.png", 6.97, 0.92, "1990"),
    ("img/wolf3d.png", 9.72, 0.92, "1992"),
    ("img/doom.png", 6.97, 3.03, "1993"),
    ("img/quake.png", 9.72, 3.03, "1996"),
]
for path, gx, gy, year in grid:
    picture_fill(s, ASSETS / path, gx, gy, 2.55, 1.91)
    rect(s, gx + 0.08, gy + 0.08, 0.62, 0.22, DARK)
    text(s, gx + 0.16, gy + 0.115, 0.5, 0.16, year, 8.5, WHITE, SEM)
text(s, 6.97, 5.08, 5.4, 0.28,
     "Commander Keen · Wolfenstein 3D · Doom · Quake", 10.5, WHITE, REG)
s.shapes.add_picture(str(ASSETS / "template" / "cloud.png"), Inches(4.95), Inches(0.28),
                     Inches(1.2), Inches(0.52))
notes(s, """Bienvenida al tema 8.4: principios de desarrollo de videojuegos, contados a través de id Software.

La idea no es memorizar fechas: es entender cómo un equipo pequeño resolvió problemas técnicos muy difíciles con herramientas limitadas.

Recorrido: historia y línea del tiempo, BSP de Doom, raíz cuadrada inversa de Quake III y los cinco principios de desarrollo que John Romero resume de los primeros años de id.

Los archivos de apoyo están en T8-4_content: imágenes, diagramas, código y este generador.""")

# 2 ---------------------------------------------------------------- recorrido
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · RECORRIDO", "LO QUE VEREMOS HOY",
       "Cuatro bloques: historia, dos algoritmos y cinco principios.")
items = [
    ("01", "HISTORIA Y LÍNEA DEL TIEMPO",
     "De Commander Keen a Doom Eternal: los momentos que marcaron a id.", ORANGE),
    ("02", "BSP: PARTIR EL ESPACIO",
     "Cómo Doom ordenaba las paredes sin un z-buffer.", PINK),
    ("03", "RAÍZ CUADRADA INVERSA",
     "El truco de bits de Quake III Arena, explicado sin matemáticas pesadas.", ORANGE),
    ("04", "CINCO PRINCIPIOS",
     "Las reglas de trabajo que usó id Software en sus primeros años.", PINK),
]
y = 1.62
for num, ttl, desc, accent in items:
    card(s, 0.62, y, 12.09, 0.78, accent)
    text(s, 0.82, y + 0.18, 0.45, 0.3, num, 13, accent, SEM)
    text(s, 1.42, y + 0.12, 9.4, 0.32, ttl, 19, INK, SEM)
    text(s, 1.42, y + 0.44, 9.7, 0.25, desc, 12.8, BODY, REG)
    text(s, 12.05, y + 0.20, 0.45, 0.3, "→", 17, INK, REG)
    y += 0.86
text(s, 0.62, 5.28, 12.09, 0.36,
     "La pregunta guía: ¿cómo un equipo pequeño definió la tecnología de una década?",
     15, BODY, REG)
text(s, 0.62, 5.75, 12.09, 0.3,
     "Al final: dos algoritmos históricos y cinco reglas que puedes aplicar a tu proyecto.",
     12.3, MUTED, REG)
notes(s, """Recorrido en cuatro bloques.

1. Historia: los juegos y la línea del tiempo de id Software.
2. BSP: el algoritmo que permitió a Doom dibujar escenas 3D complejas en un CPU.
3. Raíz cuadrada inversa: el truco de Quake III para normalizar vectores muy rápido.
4. Principios: las cinco ideas de desarrollo que John Romero destaca de los primeros años de id.

La pregunta guía es importante: id no tenía el equipo más grande ni el hardware más potente. Tenía foco, herramientas y una comprensión profunda de lo que el hardware podía hacer.""")

# 3 ---------------------------------------------------------------- quiénes
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · HISTORIA", "CUATRO PERSONAS, UNA SALA",
       "id Software nace el 1 de febrero de 1991, en Shreveport, Luisiana.")
text(s, 0.62, 1.72, 5.55, 0.9,
     "No era una gran empresa: era un grupo de amigos que quería hacer juegos mejores y más rápido.",
     14.2, INK, REG, line_spacing=1.04)
founders = [
    ("JOHN CARMACK", "Programación y motores", 0.62, 2.66),
    ("JOHN ROMERO", "Diseño y niveles", 3.30, 2.66),
    ("TOM HALL", "Diseño y mundos", 0.62, 3.36),
    ("ADRIAN CARMACK", "Arte y gráficos", 3.30, 3.36),
]
for name, role, fx, fy in founders:
    text(s, fx, fy, 2.55, 0.22, name, 10.5, ORANGE_TEXT, SEM)
    text(s, fx, fy + 0.24, 2.55, 0.28, role, 12.0, BODY, REG)

rect(s, 0.62, 4.28, 5.55, 1.18, WHITE)
rect(s, 0.62, 4.28, 0.07, 1.18, ORANGE)
text(s, 0.86, 4.40, 1.15, 0.72, "28", 40, ORANGE, SEM)
text(s, 1.92, 4.46, 3.95, 0.52,
     "juegos en cinco años y medio, con menos de diez personas.",
     12.6, INK, REG, line_spacing=1.0)
text(s, 1.92, 4.98, 3.95, 0.24,
     "Romero, GDC Europe 2016.", 9.5, MUTED, REG)
text(s, 0.62, 5.68, 5.55, 0.5,
     "El equipo se veía todos los días. Esa cercanía hizo posible iterar rápido.",
     12.2, BODY, REG, line_spacing=1.0)

rect(s, 6.35, 1.58, 6.4, 4.45, DARK)
picture_fill(s, ASSETS / "img" / "carmack.jpg", 6.75, 1.88, 2.62, 3.50)
picture_fill(s, ASSETS / "img" / "romero.jpg", 9.68, 1.88, 2.62, 3.50)
text(s, 6.75, 5.45, 2.62, 0.24, "JOHN CARMACK", 10.5, WHITE, SEM)
text(s, 6.75, 5.68, 2.62, 0.22, "Programación y motores", 9.3, WHITE, REG)
text(s, 9.68, 5.45, 2.62, 0.24, "JOHN ROMERO", 10.5, WHITE, SEM)
text(s, 9.68, 5.68, 2.62, 0.22, "Diseño y niveles", 9.3, WHITE, REG)
notes(s, """id Software se fundó el 1 de febrero de 1991. Los fundadores fueron John Carmack, John Romero, Tom Hall y Adrian Carmack. Jay Wilbur se unió poco después como gerente.

No era un estudio grande: eran cuatro personas en una sala, con experiencia previa haciendo juegos para Apple II y PC. Esa escala les permitía tomar decisiones rápido y probar ideas sin capas de aprobación.

El dato de los 28 juegos en cinco años y medio con menos de diez personas lo cuenta John Romero en su charla sobre los primeros años de id. Es una cifra de la época: no significa que hoy un equipo pequeño deba trabajar así.

Las fotos son de GDC 2010 (Carmack) y GDC 2023 (Romero), publicadas en Wikimedia Commons con licencia CC0.""")

# 4 ---------------------------------------------------------------- timeline
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · HISTORIA", "UNA LÍNEA DEL TIEMPO BREVE",
       "Diez momentos para ubicar a id Software. Fíjate en el cambio, no en la fecha.")
timeline = [
    ("1990", "Commander Keen"),
    ("1991", "Fundación de id"),
    ("1992", "Wolfenstein 3D"),
    ("1993", "Doom"),
    ("1996", "Quake"),
    ("1999", "Quake III Arena"),
    ("2004", "Doom 3"),
    ("2009", "ZeniMax compra id"),
    ("2016", "Doom (reinicio)"),
    ("2020", "Doom Eternal"),
]
line_y = 3.55
rect(s, 0.72, line_y, 11.94, 0.035, DARK)
rect(s, 12.50, line_y - 0.08, 0.25, 0.20, DARK, shape=MSO_SHAPE.RIGHT_ARROW)
for i, (year, desc) in enumerate(timeline):
    cx = 0.95 + i * 1.25
    circle(s, cx - 0.075, line_y - 0.06, 0.15, ORANGE, WHITE, 1.0)
    if i % 2 == 0:
        rect(s, cx - 0.01, 2.62, 0.02, 0.86, LINE)
        text(s, cx - 0.62, 1.88, 1.24, 0.32, year, 17.5, ORANGE, SEM,
             align=PP_ALIGN.CENTER)
        text(s, cx - 0.62, 2.22, 1.24, 0.38, desc, 9.6, INK, REG,
             align=PP_ALIGN.CENTER, line_spacing=0.98)
    else:
        rect(s, cx - 0.01, line_y + 0.04, 0.02, 0.18, LINE)
        text(s, cx - 0.62, 3.80, 1.24, 0.32, year, 17.5, ORANGE, SEM,
             align=PP_ALIGN.CENTER)
        text(s, cx - 0.62, 4.14, 1.24, 0.38, desc, 9.6, INK, REG,
             align=PP_ALIGN.CENTER, line_spacing=0.98)

rect(s, 0.62, 5.20, 11.95, 0.82, WHITE)
rect(s, 0.62, 5.20, 0.07, 0.82, PINK)
text(s, 0.88, 5.32, 11.4, 0.28,
     "2021: Microsoft compra ZeniMax; id pasa a Xbox Game Studios.",
     11.8, INK, REG)
text(s, 0.88, 5.64, 11.4, 0.24,
     "1990–1996: la etapa que definió los FPS. 2016–2020: el regreso de Doom.",
     10.8, MUTED, REG)
notes(s, """Línea del tiempo básica:

1990: Commander Keen, el primer gran éxito de la tecnología de desplazamiento suave de John Carmack, todavía en Softdisk.
1991: se funda id Software.
1992: Wolfenstein 3D populariza el juego de disparos en primera persona.
1993: Doom lleva el género a otra escala y usa el BSP para ordenar las paredes.
1996: Quake da el salto al 3D real con polígonos y usa la raíz cuadrada inversa en su motor.
1999: Quake III Arena, el juego que popularizó el código Q_rsqrt que veremos.
2004: Doom 3, con un motor nuevo y luces dinámicas.
2009: ZeniMax adquiere id Software.
2016: Doom reinicia la serie con un motor moderno.
2020: Doom Eternal.
2021: Microsoft compra ZeniMax; id pasa a formar parte de Xbox Game Studios.

No hace falta memorizar las fechas. Lo importante es ver cómo cada juego trajo una solución técnica nueva.""")

# 5 ---------------------------------------------------------------- divider BSP
def divider(numero, title_lines, subtitle, tags, note_text, art="default"):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    rect(s, 0.62, 0.32, 0.09, 0.09, ORANGE)
    text(s, 0.81, 0.28, 9.5, 0.22, "BLOQUE " + numero, 9.5, INK, SEM)
    text(s, 0.62, 0.98, 2.0, 1.0, numero, 60, ORANGE, SEM)
    text(s, 0.62, 1.92, 7.4, 1.6, title_lines, 48, INK, SEM, line_spacing=0.95)
    rect(s, 0.62, 3.85, 2.2, 0.07, ORANGE)
    text(s, 0.62, 4.12, 6.6, 0.9, subtitle, 18, BODY, REG, line_spacing=1.05)
    text(s, 0.62, 5.22, 7.4, 0.3, tags, 13, ORANGE, SEM)
    s.shapes.add_picture(str(ASSETS / "template" / "cloud.png"), Inches(9.56),
                         Inches(1.1), Inches(1.84), Inches(0.8))
    s.shapes.add_picture(str(ASSETS / "template" / "cloud-low.png"), Inches(7.55),
                         Inches(0.55), Inches(1.4), Inches(0.58))
    s.shapes.add_picture(str(ASSETS / "template" / "star.png"), Inches(11.35),
                         Inches(3.35), Inches(1.05), Inches(1.0))
    s.shapes.add_picture(str(ASSETS / "template" / "chest.png"), Inches(9.55),
                         Inches(4.95), Inches(2.45), Inches(1.3))
    notes(s, note_text)
    return s


divider("02", "BSP:\nPARTIR EL ESPACIO",
        "Binary Space Partitioning: el algoritmo que ordenó las paredes de Doom.",
        "DOOM · 1993 · BSP · Z-BUFFER",
        """Bloque 2. Doom se ve en 3D, pero el mapa es 2D y el motor decide qué pared dibujar primero.

La idea central: partir el espacio con líneas y guardar los cortes en un árbol binario. Ese árbol permite recorrer las paredes en un orden correcto sin un z-buffer.

Lo veremos en tres pasos: el problema, la idea y cómo lo usa Doom.""")

# 6 ---------------------------------------------------------------- BSP problema
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · BSP", "DIBUJAR SIN Z-BUFFER",
       "Doom tenía que decidir qué pared tapa a cuál, sin comparar píxeles.")
bullets(s, 0.62, 1.72, 3.95, [
    "En 1993, muchas PCs no tenían GPU 3D.\nDoom dibujaba columnas de píxeles en el CPU,\nsin z-buffer.",
    "Sin z-buffer, el orden importa:\nla última pared que pintas tapa las anteriores.",
    "Ordenar por distancia no basta cuando\nlas paredes son grandes o se cruzan en la vista.",
], size=12.0, gap=0.72)
picture_fill(s, ASSETS / "img" / "doom.png", 0.62, 3.95, 2.75, 2.06,
             border_w=1.4)
text(s, 0.62, 6.04, 2.9, 0.2, "Doom (1993). Captura de pantalla.", 8.8, MUTED, REG)
rect(s, 4.72, 1.58, 7.96, 4.42, WHITE)
picture_fit(s, ASSETS / "diagramas" / "bsp_problema.png", 4.90, 1.72,
            7.60, 4.14, border=False)
footer(s, "El problema no es dibujar paredes: es saber en qué orden hacerlo.")
notes(s, """El problema: Doom se ve en 3D, pero se dibuja en un CPU de 1993. No había una tarjeta 3D con z-buffer en todas las máquinas.

El z-buffer guarda la profundidad de cada píxel. Así, el orden en que dibujas no importa: el píxel más cercano gana. Doom no tenía ese lujo para las paredes.

Si dibujas primero la pared cercana y después la lejana, la lejana tapa a la cercana. El resultado es incorrecto. Ordenar por distancia parece la solución, pero falla cuando una pared es grande o cruza la vista: no tiene una sola distancia.

La diapositiva muestra el mapa desde arriba y dos órdenes de dibujo. El orden correcto es de lejos a cerca. Doom lo hace de cerca a lejos y recorta lo que ya está tapado; el árbol BSP le da ese orden sin comparar píxeles.""")

# 7 ---------------------------------------------------------------- BSP idea
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · BSP", "PARTIR EL ESPACIO EN DOS",
       "Una línea divide el mapa. Cada mitad se vuelve a dividir. Al final, cada zona es convexa.")
bullets(s, 0.62, 1.72, 3.95, [
    "Cada corte es un nodo del árbol. La cámara queda de un lado: delante o detrás.",
    "Las hojas son zonas convexas: desde cualquier punto de la zona se ve toda la zona.",
    "Doom construye el árbol una vez, al preparar el mapa. En el juego solo lo recorre.",
], size=12.2, gap=0.78)
rect(s, 0.62, 4.30, 3.95, 1.10, WHITE)
text(s, 0.85, 4.43, 3.5, 0.24, "CONVEXO, EN UNA FRASE", 9.5, ORANGE_TEXT, SEM)
text(s, 0.85, 4.70, 3.45, 0.55,
     "Una línea recta entre dos puntos de la zona nunca sale de la zona.",
     11.8, BODY, REG, line_spacing=1.0)
rect(s, 4.72, 1.58, 7.96, 4.42, WHITE)
picture_fit(s, ASSETS / "diagramas" / "bsp_arbol.png", 4.90, 1.72,
            7.60, 4.14, border=False)
footer(s, "Doom dividía el mapa en cientos o miles de zonas convexas.")
notes(s, """La idea del BSP: tomar el mapa y partirlo con líneas. Cada línea divide una zona en dos. Si repites el proceso, obtienes zonas cada vez más pequeñas.

Esas zonas son convexas. Una zona convexa no tiene esquinas ocultas: si estás dentro, puedes ver toda la zona sin que una pared te tape una parte. Eso simplifica el dibujado.

El resultado se guarda en un árbol binario. Cada nodo es una línea de corte; cada hoja es una zona. Para saber de qué lado está la cámara, se evalúa la línea: delante o detrás.

Doom construye este árbol cuando se prepara el mapa, no en cada fotograma. En el juego, el motor solo recorre el árbol. Ese trabajo previo es lo que hace que el renderizado sea rápido.

El código de ejemplo bsp_demo.py, en T8-4_content, recorre un árbol BSP pequeño y muestra el orden para una cámara en cada zona.""")

# 8 ---------------------------------------------------------------- BSP recorrido
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · BSP", "RECORRER EL ÁRBOL, DIBUJAR EN ORDEN",
       "La cámara decide por dónde empezar; el árbol entrega las paredes de cerca a lejos.")
bullets(s, 0.62, 1.72, 3.95, [
    "En cada nodo, Doom mira de qué lado está la cámara y recorre primero ese lado.",
    "Dibuja las paredes de cerca a lejos y recorta lo que ya está tapado. No necesita z-buffer.",
    "El mismo árbol sirve para colisiones y para saber en qué zona está el jugador.",
], size=12.2, gap=0.80)
rect(s, 0.62, 4.35, 3.95, 1.20, WHITE)
rect(s, 0.62, 4.35, 0.07, 1.20, PINK)
text(s, 0.86, 4.48, 3.50, 0.24, "SIN Z-BUFFER", 9.5, PINK, SEM)
text(s, 0.86, 4.75, 3.45, 0.55,
     "El árbol no guarda píxeles: guarda el orden en que hay que dibujarlos.",
     11.8, BODY, REG, line_spacing=1.0)
rect(s, 4.72, 1.58, 7.96, 4.42, WHITE)
picture_fit(s, ASSETS / "diagramas" / "bsp_recorrido.png", 4.90, 1.72,
            7.60, 4.14, border=False)
footer(s, "Orden 1 a 7: primero la zona de la cámara; al final, la más lejana.")
notes(s, """Cómo lo usa Doom:

1. La cámara está en una zona. El árbol sabe de qué lado de cada línea está.
2. En cada nodo, el motor recorre primero el lado donde está la cámara.
3. Cuando termina un lado, dibuja la línea del nodo y sigue con el otro lado.
4. Así obtiene un orden de cerca a lejos. Con ese orden, puede recortar las paredes que ya están tapadas y no necesita z-buffer.

El mismo árbol se usa para colisiones: para saber si el jugador puede moverse a una posición, se recorren los nodos y las zonas. También sirve para encontrar en qué zona está.

El diagrama muestra el orden 1 a 7. Los círculos oscuros son zonas; los cuadrados naranjas son cortes. La cámara está en la zona 1. El orden empieza ahí y termina en la zona 7, la más lejana.

El código bsp_demo.py, en T8-4_content, imprime este orden para una cámara en cada zona.""")

# 9 ---------------------------------------------------------------- divider Quake
divider("03", "RAÍZ CUADRADA\nINVERSA",
        "El truco de bits que se popularizó con Quake III Arena (1999).",
        "QUAKE III · IEEE 754 · NEWTON · 0x5F3759DF",
        """Bloque 3. La raíz cuadrada inversa es la operación 1/√x.

En 3D se usa para normalizar vectores: hacer que midan 1. Quake III Arena la necesitaba muchas veces por fotograma.

El código que veremos es famoso porque usa los bits del número flotante para obtener una primera aproximación muy rápido, y después la corrige con una iteración de Newton.""")

# 10 --------------------------------------------------------------- por qué
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · QUAKE", "NORMALIZAR VECTORES, MILLONES DE VECES",
       "Para iluminar, mover la cámara o calcular reflejos, los vectores deben medir 1.")
bullets(s, 0.62, 1.70, 4.65, [
    "Normalizar un vector es dividirlo por su longitud: v / |v|.",
    "La longitud usa una raíz cuadrada; para normalizar hace falta 1/√x.",
    "En 1999, una raíz y una división eran más caras que sumar o multiplicar.",
    "Quake III lo hacía en el bucle interno, muchas veces por fotograma.",
], size=12.4, gap=0.66)
picture_fill(s, ASSETS / "img" / "quake3.png", 0.62, 4.10, 2.55, 1.91,
             border_w=1.4)
text(s, 0.62, 6.04, 2.8, 0.2, "Quake III Arena (1999).", 8.8, MUTED, REG)
rect(s, 5.55, 1.58, 7.12, 4.42, WHITE)
picture_fit(s, ASSETS / "diagramas" / "vector_unitario.png", 5.75, 1.72,
            6.72, 4.14, border=False)
footer(s, "Normalizar un vector es hacer que su longitud sea 1, sin cambiar su dirección.")
notes(s, """Por qué hace falta la raíz cuadrada inversa:

En un juego 3D, muchas operaciones necesitan vectores unitarios: la dirección de la cámara, la normal de una pared, la dirección de la luz, la reflexión de un disparo.

Normalizar un vector v es calcular v / |v|. La longitud |v| se obtiene con una raíz cuadrada. Por eso aparece 1/√x: si x es la longitud al cuadrado, 1/√x es el factor que lleva el vector a longitud 1.

En 1999, una raíz cuadrada y una división eran operaciones lentas comparadas con una suma o una multiplicación. Quake III hacía esta operación en el bucle interno, muchas veces por fotograma, así que valía la pena buscar un atajo.

El diagrama muestra un vector v = (3, 2). Su longitud es √13 ≈ 3.61. Al dividirlo por su longitud, queda un vector de longitud 1 en la misma dirección.

El código de Quake no calcula la raíz exacta: calcula una aproximación muy buena y muy rápida. Eso es suficiente para iluminar y mover la cámara.""")

# 11 --------------------------------------------------------------- código
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · QUAKE", "EL CÓDIGO",
       "Una función de C que estima 1/√x con bits y una corrección de Newton.")
rect(s, 0.55, 1.62, 6.40, 4.50, WHITE)
picture_fit(s, ASSETS / "codigo" / "code_rsqrt.png", 0.75, 1.76,
            6.00, 4.22, border=False)
pill(s, 6.08, 1.54, 0.62, "C")
steps = [
    ("01", "LEER LOS BITS",
     "memcpy copia el float a un entero de 32 bits. No cambia el número: cambia cómo lo miramos."),
    ("02", "LA CONSTANTE MÁGICA",
     "0x5f3759df - (i >> 1) produce una primera aproximación. Es una resta de enteros, muy barata."),
    ("03", "CORREGIR CON NEWTON",
     "Una iteración de Newton ajusta la aproximación. El error baja de 3.4 % a 0.175 %."),
]
yy = 1.66
for num, head, body in steps:
    text(s, 7.30, yy, 0.45, 0.24, num, 10.0, ORANGE, SEM)
    text(s, 7.78, yy - 0.02, 4.95, 0.28, head, 14.5, INK, SEM)
    text(s, 7.78, yy + 0.30, 4.95, 0.62, body, 12.0, BODY, REG,
         line_spacing=1.0)
    yy += 1.14
rect(s, 7.30, 5.12, 5.40, 0.78, WHITE)
text(s, 7.52, 5.24, 4.95, 0.24, "Sin comentarios en la imagen", 11.5, INK, SEM)
text(s, 7.52, 5.51, 4.95, 0.26,
     "El código completo está en las notas; el archivo .c, en T8-4_content.", 10.2, BODY, REG)
footer(s, "El código original de Quake usaba long; esta versión usa int32_t para ser portable.")
notes(s, """CÓDIGO DE LA DIAPOSITIVA (T8-4_content/fast_inv_sqrt.c):

#include <stdint.h>
#include <string.h>

float Q_rsqrt(float number)
{
    int32_t i;
    float x2, y;
    const float threehalfs = 1.5F;

    x2 = number * 0.5F;
    y = number;
    memcpy(&i, &y, sizeof(i));
    i = 0x5f3759df - (i >> 1);
    memcpy(&y, &i, sizeof(y));
    y = y * (threehalfs - (x2 * y * y));

    return y;
}

La imagen muestra solo la función. El archivo fast_inv_sqrt.c incluye las cabeceras y un main de prueba.

La función supone un float de 32 bits IEEE 754 y x > 0: 1/√x no está definida para x = 0 y no es real para x < 0.

El código original de Quake III usaba long y punteros para reinterpretar los bits. En una máquina de 64 bits, long puede medir 8 bytes, así que aquí usamos int32_t y memcpy para que sea portable y seguro.

Los pasos de la diapositiva:
1. Guardar el float en un entero de 32 bits con memcpy.
2. Restar la mitad del entero a la constante 0x5f3759df. Eso da una primera aproximación de 1/√x.
3. Volver a interpretar esos bits como float y aplicar una iteración de Newton.

La siguiente diapositiva muestra el ejemplo completo con x = 0.25.

No es magia: la constante acerca el valor y Newton lo corrige. El error máximo es de 0.175 % después de una iteración.""")

# 12 --------------------------------------------------------------- pipeline
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · QUAKE", "EL TRUCO, PASO A PASO",
       "Leer bits, aplicar la constante y corregir: tres ideas detrás de una función de C.")
rect(s, 0.55, 1.62, 12.15, 4.10, WHITE)
picture_fit(s, ASSETS / "diagramas" / "rsqrt_pipeline.png", 0.75, 1.72,
            11.75, 3.55, border=False)
text(s, 0.78, 5.18, 11.65, 0.28,
     "Ejemplo con x = 0.25: el valor exacto es 2.0 y el truco devuelve 1.9966 (0.17 % de error).",
     12.8, INK, REG)
footer(s, "La constante mágica da una pista; una iteración de Newton la corrige.")
notes(s, """El ejemplo usa x = 0.25. Su 1/√x exacto es 2.0.

1. Los bits de 0.25 son 0x3e800000.
2. Al desplazar a la derecha y restar de 0x5f3759df, queda 0x3ff759df. Interpretado como float, es 1.9324. Error: 3.4 %.
3. Una iteración de Newton: y = y * (1.5 - 0.5*x*y*y) = 1.9966. Error: 0.17 %.

La constante no es magia: está elegida para que la resta de enteros se parezca a la operación 1/√x. Newton corrige la diferencia.

El código completo está en fast_inv_sqrt.c. La gráfica de error (rsqrt_error.png) está en la carpeta de diagramas por si quieres mostrarla.""")

# 13 --------------------------------------------------------------- comparación
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · QUAKE", "¿POR QUÉ FUE RELEVANTE?",
       "No era exacto, pero era mucho más rápido que la alternativa de su época.")

# table header
rect(s, 0.62, 1.62, 6.55, 0.40, DARK)
text(s, 0.80, 1.71, 2.0, 0.22, "MÉTODO", 9.0, WHITE, SEM)
text(s, 2.75, 1.71, 1.35, 0.22, "ERROR", 9.0, WHITE, SEM)
text(s, 4.15, 1.71, 2.85, 0.22, "VELOCIDAD (1999)", 9.0, WHITE, SEM)

rows = [
    ("1/sqrt(x) exacto", "≈0 %", "Lento: raíz + división", WHITE, None),
    ("Tabla de valores", "Depende", "Rápido, pero usa memoria", WHITE, None),
    ("Newton con mala pista", "Converge", "Necesita varias iteraciones", WHITE, None),
    ("Q_rsqrt (Quake)", "0.175 %", "~4× más rápido", SOFT, ORANGE),
    ("rsqrtss (hardware)", "Mejor", "1 instrucción, pero no en todas las PCs", SOFT, BLUE),
]
yy = 2.02
for method, err, speed, fill, accent in rows:
    rect(s, 0.62, yy, 6.55, 0.66, fill)
    if accent:
        rect(s, 0.62, yy, 0.07, 0.66, accent)
    text(s, 0.82, yy + 0.10, 1.95, 0.24, method, 10.0, INK, SEM)
    text(s, 2.75, yy + 0.10, 1.30, 0.24, err, 10.0, BODY, REG)
    text(s, 4.15, yy + 0.10, 2.85, 0.42, speed, 9.8, BODY, REG,
         line_spacing=0.95)
    yy += 0.70

rect(s, 7.45, 1.58, 5.22, 3.28, WHITE)
picture_fit(s, ASSETS / "diagramas" / "rsqrt_bars.png", 7.65, 1.72,
            4.82, 3.00, border=False)
rect(s, 7.45, 5.02, 5.22, 0.90, WHITE)
rect(s, 7.45, 5.02, 0.07, 0.90, PINK)
text(s, 7.68, 5.14, 4.80, 0.24, "EL TRUCO", 9.5, PINK, SEM)
text(s, 7.68, 5.40, 4.80, 0.42,
     "Con una sola iteración, el error cabe en 0.175 %. Hoy el CPU tiene instrucciones mejores.",
     10.8, BODY, REG, line_spacing=0.98)
footer(s, "Fuente: Chris Lomont, Fast Inverse Square Root (2003); Matthew Robertson (2012).")
notes(s, """Comparación con otros métodos:

- 1/sqrt(x) exacto: usa una raíz cuadrada y una división. Es correcto, pero en 1999 era lento.
- Tabla de valores: se precalculan aproximaciones en una tabla. Es rápido, pero ocupa memoria y la precisión depende del tamaño de la tabla.
- Newton con una mala pista: converge, pero necesita varias iteraciones para acercarse.
- Q_rsqrt: usa los bits para obtener una pista muy buena y una sola iteración de Newton. Error máximo 0.175 %, unas cuatro veces más rápido en pruebas de 2003.
- rsqrtss: instrucción de hardware que calcula una aproximación de 1/√x en un solo paso. Es la opción moderna, pero no estaba en todas las PCs de 1999.

El gráfico compara el error máximo (3.4 % solo con la constante, 0.175 % con Newton) y la velocidad relativa (1x para 1/sqrt exacto, ~4x para Q_rsqrt en pruebas de 2003).

Hoy no usarías Q_rsqrt en código nuevo: el CPU y la GPU tienen instrucciones específicas. Pero el ejercicio enseña dos cosas: cómo se representan los floats y cuánto importa el costo real de una operación.

Fuentes: Chris Lomont, "Fast Inverse Square Root" (2003); Matthew Robertson, "A Brief History of InvSqrt" (2012).""")

# 13 --------------------------------------------------------------- divider principios
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
rect(s, 0.62, 0.32, 0.09, 0.09, ORANGE)
text(s, 0.81, 0.28, 9.5, 0.22, "BLOQUE 04", 9.5, INK, SEM)
text(s, 0.62, 0.98, 2.0, 1.0, "04", 60, ORANGE, SEM)
text(s, 0.62, 1.92, 5.7, 1.6, "CINCO\nPRINCIPIOS", 48, INK, SEM,
     line_spacing=0.95)
rect(s, 0.62, 3.62, 2.2, 0.07, ORANGE)
text(s, 0.62, 3.88, 5.7, 0.90,
     "Lo que John Romero aprendió en los primeros años de id Software.",
     18, BODY, REG, line_spacing=1.05)
text(s, 0.62, 4.95, 5.7, 0.26,
     "GDC EUROPE 2016 · STRANGE LOOP 2022", 11.5, ORANGE, SEM)
text(s, 0.62, 5.35, 5.7, 0.65,
     "No son reglas eternas: son decisiones que funcionaron para un equipo pequeño y un hardware limitado.",
     11.5, BODY, REG, line_spacing=1.0)

rect(s, 6.55, 0.95, 6.15, 4.95, DARK)
principles = [
    ("01", "SIN PROTOTIPOS"),
    ("02", "EL JUEGO SIEMPRE CORRE"),
    ("03", "CÓDIGO SIMPLE"),
    ("04", "HERRAMIENTAS PRIMERO"),
    ("05", "CÓDIGO PARA ESTE JUEGO"),
]
yy = 1.18
for num, name in principles:
    text(s, 6.85, yy, 0.45, 0.26, num, 10.5, ORANGE, SEM)
    text(s, 7.38, yy - 0.03, 4.95, 0.32, name, 16.5, WHITE, SEM)
    if num != "05":
        rect(s, 6.85, yy + 0.48, 5.35, 0.012, RGBColor(0x4A, 0x48, 0x5C))
    yy += 0.82
text(s, 6.85, 5.38, 5.35, 0.26,
     "Una selección de los cinco más importantes.", 10.5, RGBColor(0xB8, 0xBC, 0xC8), REG)
s.shapes.add_picture(str(ASSETS / "template" / "star.png"), Inches(11.72),
                     Inches(0.38), Inches(0.78), Inches(0.74))
notes(s, """Bloque 4. John Romero resume los principios de programación de los primeros años de id Software.

En la charla original hay más de diez. Para esta clase seleccionamos los cinco que mejor explican el método de trabajo de id:

01. Sin prototipos: el juego se mantiene siempre publicable y se pule sobre la marcha.
02. El juego siempre debe correr: todo el equipo puede ejecutarlo; el motor tiene valores por defecto.
03. Código absolutamente simple: menos casos especiales, menos errores.
04. Grandes herramientas: editores, compiladores y pruebas.
05. Código para este juego, no para el futuro.

La idea no es copiar las reglas de 1993 tal cual. Es entender por qué funcionaron y qué parte sigue siendo útil hoy.""")

# 14 --------------------------------------------------------------- principios 1 y 2
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · PRINCIPIOS", "SIEMPRE ALGO QUE MOSTRAR",
       "Los dos primeros principios tienen que ver con el estado del proyecto.")

def principle_card(x, num, title, body, en_id, para_ti, accent):
    card(s, x, 1.62, 5.95, 4.28, accent)
    text(s, x + 0.27, 1.80, 2.0, 0.22, "PRINCIPIO " + num, 9.5, accent, SEM)
    text(s, x + 0.27, 2.05, 5.35, 0.42, title, 23, INK, SEM)
    text(s, x + 0.27, 2.55, 5.30, 0.92, body, 12.6, BODY, REG,
         line_spacing=1.02)
    text(s, x + 0.27, 3.62, 2.0, 0.22, "EN ID", 9.5, ORANGE_TEXT, SEM)
    text(s, x + 0.27, 3.86, 5.30, 0.72, en_id, 11.5, INK, REG,
         line_spacing=1.0)
    text(s, x + 0.27, 4.76, 2.4, 0.22, "PARA TU PROYECTO", 9.5, PINK, SEM)
    text(s, x + 0.27, 5.00, 5.30, 0.60, para_ti, 11.5, BODY, REG,
         line_spacing=1.0)

principle_card(0.62, "01", "SIN PROTOTIPOS",
                "El juego se mantiene jugable desde el primer día. La calidad no se deja para el final: se pule mientras se construye.",
                "28 juegos en cinco años y medio, con menos de diez personas. No había tiempo para demos desechables.",
                "Hoy, en proyectos grandes, sí conviene prototipar. id podía hacerlo porque sus juegos eran pequeños.",
                ORANGE)
principle_card(6.42, "02", "EL JUEGO SIEMPRE CORRE",
                "Cualquiera del equipo debe poder ejecutar el juego en cualquier momento. Si falla una carga, el motor usa valores por defecto.",
                "Probaban a fondo antes de integrar y corregían el error en cuanto aparecía.",
                "Si no compila, no sigas agregando funciones. Primero arregla lo que está roto.",
                PINK)
footer(s, "La regla de oro: si el juego no se puede ejecutar, no hay nada que probar.")
notes(s, """Principio 1: sin prototipos.

En id no había tiempo para hacer una demo, tirarla y empezar de nuevo. El juego se mantenía jugable y publicable desde el primer día. La calidad se pulía sobre la marcha.

El dato de los 28 juegos en cinco años y medio con menos de diez personas lo cuenta Romero. No significa que hoy haya que trabajar así: en un proyecto grande, prototipar es una buena idea. id podía saltarse el prototipo porque sus juegos eran pequeños y el equipo estaba en una sala.

Principio 2: el juego siempre debe correr.

Cualquiera del equipo debe poder ejecutar el juego. Si una carga falla, el motor debe tener valores por defecto y no quedarse en pantalla negra. Probar antes de integrar y corregir el error en cuanto aparece evita que el código nuevo se construya sobre una base rota.

Para tu proyecto de Unity: si no compila, no sigas agregando funciones. Primero arregla lo que está roto.""")

# 15 --------------------------------------------------------------- principios 3 y 4
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · PRINCIPIOS", "SIMPLE Y BIEN EQUIPADO",
       "El código y las herramientas son parte del diseño.")

principle_card(0.62, "03", "CÓDIGO SIMPLE",
                "Funciones con una sola idea: menos casos especiales, menos errores y más facilidad para cambiar.",
                "Si una función se complicaba, la partían o la reescribían.",
                "Si no puedes explicar una función en una frase, todavía no está lista.",
                ORANGE)

# card 04 con captura del editor
x = 6.42
card(s, x, 1.62, 5.95, 4.28, PINK)
text(s, x + 0.27, 1.80, 2.0, 0.22, "PRINCIPIO 04", 9.5, PINK, SEM)
text(s, x + 0.27, 2.05, 5.35, 0.42, "HERRAMIENTAS PRIMERO", 23, INK, SEM)
text(s, x + 0.27, 2.55, 3.20, 1.30,
     "El tiempo que inviertes en editores, compiladores y pruebas se recupera. Una herramienta buena te deja pensar en el juego.",
     12.4, BODY, REG, line_spacing=1.0)
text(s, x + 0.27, 3.86, 3.20, 0.22, "EN ID", 9.5, ORANGE_TEXT, SEM)
text(s, x + 0.27, 4.10, 3.18, 0.62,
     "Construyeron sus propios editores de mapas y su motor; probaban antes de integrar.",
     11.2, INK, REG, line_spacing=1.0)
text(s, x + 0.27, 4.76, 2.4, 0.22, "PARA TU PROYECTO", 9.5, PINK, SEM)
text(s, x + 0.27, 5.00, 3.18, 0.55,
     "Aprende a usar el editor, el depurador y Git. No trabajes a ciegas.",
     11.2, BODY, REG, line_spacing=1.0)
picture_fill(s, ASSETS / "img" / "doom_editor.png", x + 3.58, 2.55,
             2.10, 1.58, border_w=1.2)
text(s, x + 3.58, 4.18, 2.10, 0.20, "Doom Construction Kit", 8.2, MUTED, REG)
footer(s, "Una buena herramienta no hace el juego: te deja dedicar tiempo a lo que sí importa.")
notes(s, """Principio 3: código absolutamente simple.

Romero insiste en mirar las funciones y preguntarse cómo simplificarlas. Menos casos especiales significa menos errores y más facilidad para cambiar el código después.

En id, si una función se complicaba, la partían o la reescribían. La simplicidad no es escribir menos por escribir menos: es quitar lo que sobra.

Principio 4: grandes herramientas, grandes juegos.

El tiempo que inviertes en herramientas y pruebas se recupera. id construyó sus propios editores de mapas y su propio motor. También probaba a fondo antes de integrar y corregía los errores en cuanto aparecían.

La captura es del Doom Construction Kit, un editor de mapas de Doom. No es una herramienta de id, pero muestra el tipo de programa que un diseñador usaba para construir niveles. La imagen es de Wikimedia Commons, con licencia CC0.

Para tu proyecto: aprende el editor de Unity, el depurador y Git. No trabajes a ciegas.""")

# 16 --------------------------------------------------------------- principio 5 + aplicación
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · PRINCIPIOS", "CÓDIGO PARA ESTE JUEGO",
       "No escribas para el juego que imaginas; resuelve el que tienes hoy.")
card(s, 0.62, 1.62, 6.05, 3.62, ORANGE)
text(s, 0.89, 1.80, 2.0, 0.22, "PRINCIPIO 05", 9.5, ORANGE, SEM)
text(s, 0.89, 2.05, 5.45, 0.78, "CÓDIGO PARA ESTE JUEGO,\nNO PARA EL FUTURO", 22, INK, SEM,
     line_spacing=0.95)
text(s, 0.89, 2.95, 5.40, 0.78,
     "Resuelve el problema que tienes hoy. No intentes adivinar las necesidades del próximo juego.",
     12.6, BODY, REG, line_spacing=1.02)
text(s, 0.89, 3.86, 2.0, 0.22, "EN ID", 9.5, ORANGE_TEXT, SEM)
text(s, 0.89, 4.10, 5.35, 0.55,
     "Cada motor se reescribió para el juego que venía; no arrastraron código viejo.",
     11.5, INK, REG, line_spacing=1.0)
text(s, 0.89, 4.66, 2.4, 0.22, "PARA TU PROYECTO", 9.5, PINK, SEM)
text(s, 0.89, 4.90, 5.35, 0.35,
     "Encapsula la funcionalidad para poder cambiarla sin romper el resto.",
     11.5, BODY, REG, line_spacing=1.0)

rect(s, 7.05, 1.62, 5.62, 3.62, WHITE)
rect(s, 7.05, 1.62, 0.07, 3.62, PINK)
text(s, 7.32, 1.80, 4.9, 0.24, "CÓMO LO APLICAS", 9.5, PINK, SEM)
checks = [
    "Haz que el juego compile y corra hoy.",
    "Divide el código en funciones pequeñas.",
    "Prueba antes de integrar; corrige el error al momento.",
    "Invierte en tus herramientas: editor, depurador, Git.",
    "Escribe para el juego que estás haciendo.",
]
yy = 2.15
for item in checks:
    rect(s, 7.32, yy + 0.08, 0.08, 0.08, ORANGE)
    text(s, 7.52, yy, 4.85, 0.34, item, 11.8, INK, REG, line_spacing=1.0)
    yy += 0.55
text(s, 0.62, 5.55, 12.05, 0.38,
     "La pregunta no es qué motor usarás en cinco años; es qué problema tienes hoy.",
     15, BODY, REG)
footer(s, "Cada juego de id tuvo su propio motor. No intentaron escribir el motor definitivo.")
notes(s, """Principio 5: escribe código para este juego, no para el futuro.

Romero dice que no tenía sentido reutilizar código de un juego a otro: cada juego tenía sus propios problemas y su propia optimización. En id, cada motor se reescribió para el juego que venía.

Eso no significa ignorar el diseño. Significa no adivinar las necesidades del próximo proyecto. Resuelve el problema actual, con las herramientas actuales, y encapsula la funcionalidad para poder cambiarla después.

Para tu proyecto de Unity:
- Haz que el juego compile y corra hoy.
- Divide el código en funciones pequeñas.
- Prueba antes de integrar y corrige el error al momento.
- Aprende a usar el editor, el depurador y Git.
- Escribe para el juego que estás haciendo, no para el que sueñas.

La frase de cierre: la pregunta no es qué motor usarás en cinco años; es qué problema tienes hoy.""")

# 17 --------------------------------------------------------------- síntesis
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "8.4 · CIERRE", "LO QUE ID NOS DEJA",
       "Cuatro ideas que puedes usar aunque tu juego sea pequeño.")
cards = [
    ("01", "EL ORDEN ES UN ALGORITMO",
     "BSP: partir el espacio para dibujar en orden, sin z-buffer.", ORANGE),
    ("02", "CONOCE TU HARDWARE",
     "Raíz cuadrada inversa: los bits y el costo real de las operaciones importan.", PINK),
    ("03", "SIMPLIFICA",
     "Código corto, herramientas buenas y pruebas constantes.", ORANGE),
    ("04", "HAZLO HOY",
     "Un juego jugable vale más que una idea perfecta.", PINK),
]
positions = [(0.62, 1.62), (6.42, 1.62), (0.62, 3.02), (6.42, 3.02)]
for (num, ttl, desc, accent), (x, y) in zip(cards, positions):
    card(s, x, y, 5.95, 1.22, accent)
    text(s, x + 0.25, y + 0.14, 0.40, 0.22, num, 9.8, accent, SEM)
    text(s, x + 0.72, y + 0.11, 4.95, 0.28, ttl, 16.5, INK, SEM)
    text(s, x + 0.72, y + 0.44, 4.95, 0.62, desc, 11.5, BODY, REG,
         line_spacing=1.0)

rect(s, 0.62, 4.55, 8.35, 1.45, WHITE)
rect(s, 0.62, 4.55, 0.07, 1.45, ORANGE)
text(s, 0.90, 4.70, 7.80, 0.28, "UNA IDEA PARA LLEVARTE", 9.5, ORANGE_TEXT, SEM)
text(s, 0.90, 4.98, 7.75, 0.82,
     "“La programación es una forma de arte creativa basada en la lógica. Cada programador es diferente.”\n— John Romero",
     13.5, INK, REG, line_spacing=1.02)
picture_fill(s, ASSETS / "img" / "doom2016.jpg", 9.35, 4.58, 3.05, 1.42,
             border_w=1.4)
text(s, 9.35, 6.03, 3.05, 0.18, "Doom (2016). Captura de pantalla.", 8.5, MUTED, REG)
footer(s, "Un equipo pequeño, obsesionado con entender el problema, puede cambiar una industria.")
notes(s, """Cierre.

Cuatro ideas para llevarte:

1. El orden es un algoritmo: el BSP de Doom convierte un problema de dibujo en un recorrido de árbol.
2. Conoce tu hardware: la raíz cuadrada inversa de Quake solo tiene sentido si sabes cuánto cuestan una raíz y una división.
3. Simplifica: código corto, herramientas buenas y pruebas constantes.
4. Hazlo hoy: un juego jugable vale más que una idea perfecta.

La frase de Romero es de la charla de GDC Europe 2016: la programación es una forma de arte creativa basada en la lógica, y cada programador es diferente.

La imagen es una captura de Doom (2016), la versión moderna de la serie. El motor cambió por completo, pero la idea de resolver el juego actual sigue igual.""")

# 18 --------------------------------------------------------------- créditos
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
header(s, "CRÉDITOS", "CRÉDITOS DE LAS IMÁGENES",
       "Fuentes, licencias y atribuciones del material utilizado.")
rect(s, 0.62, 1.70, 5.55, 3.30, WHITE)
text(s, 0.86, 1.84, 3.0, 0.22, "IMÁGENES Y RECURSOS", 9.5, ORANGE_TEXT, SEM)
text(s, 0.86, 2.12, 5.05, 2.75,
     "•  Capturas de Commander Keen, Wolfenstein 3D, Doom, Quake, Quake III y Doom (2016): id Software, Bethesda y ZeniMax. Uso educativo, baja resolución.\n\n"
     "•  Fotos de John Carmack y John Romero: GDC, Wikimedia Commons, CC0.\n\n"
     "•  Doom Construction Kit: captura de software libre, Wikimedia Commons, CC0.\n\n"
     "•  Diagramas BSP y vector, y gráfica de barras: elaborados para esta clase.\n\n"
     "•  Plantilla pixel art: TC2005B. Tipografía Neuromax: 1001fonts, EULA incluida.",
     10.5, BODY, REG, line_spacing=1.0)
rect(s, 6.45, 1.70, 5.55, 3.30, WHITE)
text(s, 6.69, 1.84, 3.0, 0.22, "FUENTES", 9.5, PINK, SEM)
text(s, 6.69, 2.12, 5.05, 2.75,
     "•  John Romero, “Programming principles from the early days of id Software”, GDC Europe 2016 (Game Developer).\n\n"
     "•  John Romero, “The Early Days of id Software: Programming Principles”, Strange Loop 2022.\n\n"
     "•  Chris Lomont, “Fast Inverse Square Root”, 2003.\n\n"
     "•  Matthew Robertson, “A Brief History of InvSqrt”, 2012.\n\n"
     "•  id Software, código fuente de Quake III Arena (q_math.c).\n\n"
     "•  Wikipedia y Wikimedia Commons: id Software, Doom, Quake.",
     10.5, BODY, REG, line_spacing=1.0)
rect(s, 0.62, 5.25, 11.38, 0.72, WHITE)
text(s, 0.86, 5.37, 10.9, 0.24,
     "Material educativo sin fines comerciales. Los enlaces completos están en las notas.",
     10.8, INK, REG)
text(s, 0.86, 5.66, 10.9, 0.22,
     "Datos y versiones verificados en octubre de 2026.", 9.8, MUTED, REG)
footer(s, "Gracias a id Software por los juegos y a la comunidad por preservar su historia.")
notes(s, """Créditos y enlaces completos:

Imágenes:
- Commander Keen 3: https://en.wikipedia.org/wiki/File:Keen3Gameplay.png (captura, uso educativo).
- Wolfenstein 3D: https://en.wikipedia.org/wiki/File:Wolf3d_pc.png (captura, uso educativo).
- Doom: https://en.wikipedia.org/wiki/File:Doom_ingame_1.png (captura, uso educativo).
- Quake: https://en.wikipedia.org/wiki/File:Quake_gameplay.png (captura, uso educativo).
- Quake III Arena: https://en.wikipedia.org/wiki/File:Quake_III_Arena_q3dm0.png (captura, uso educativo).
- Doom (2016): https://en.wikipedia.org/wiki/File:Screenshot_for_Doom_2016.jpg (captura, uso educativo).
- John Carmack: https://commons.wikimedia.org/wiki/File:John_Carmack_GDC_2010.jpg (CC0).
- John Romero: https://commons.wikimedia.org/wiki/File:John_Romero_GDC_2023.jpg (CC0).
- Doom Construction Kit: https://commons.wikimedia.org/wiki/File:Doom_Construction_Kit_screenshot.png (CC0).
- Plantilla, fondos y pixel art: TC2005B.
- Tipografía Neuromax: 1001fonts, EULA en T8-4_content/fonts.

Fuentes:
- John Romero, GDC Europe 2016: https://www.gamedeveloper.com/design/programming-principles-from-the-early-days-of-id-software
- John Romero, Strange Loop 2022: https://thestrangeloop.com/2022/id----the-early-days-of-id-software-programming-principles.html
- Chris Lomont, Fast Inverse Square Root: https://lomont.org/papers/2003/InvSqrt.pdf
- Matthew Robertson, A Brief History of InvSqrt: https://mrober.io/papers/rsqrt.pdf
- Quake III Arena source: https://github.com/id-Software/Quake-III-Arena/blob/master/code/game/q_math.c
- Fast inverse square root, Wikipedia: https://en.wikipedia.org/wiki/Fast_inverse_square_root
- BSP, Wikipedia: https://en.wikipedia.org/wiki/Binary_space_partitioning
- id Software, Wikipedia: https://en.wikipedia.org/wiki/Id_Software

Las capturas de juegos son material con derechos de autor. Se usan en baja resolución con fines educativos y sin fines comerciales. Las marcas pertenecen a sus dueños.""")

# 19 --------------------------------------------------------------- preguntas
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
text(s, 0, 1.72, SW, 1.1, "¿PREGUNTAS?", 80, INK, SEM, align=PP_ALIGN.CENTER)
text(s, 0, 3.22, SW, 0.38, "Siguiente: 8.5 · Introducción a Unity.", 20, BODY, REG,
     align=PP_ALIGN.CENTER)
text(s, 0, 3.78, SW, 0.36,
     "Un equipo pequeño puede cambiar una industria. La clave es entender el problema.",
     16, ORANGE, REG, align=PP_ALIGN.CENTER)
s.shapes.add_picture(str(ASSETS / "template" / "cloud.png"), Inches(1.35),
                     Inches(2.22), Inches(0.85), Inches(0.81))
s.shapes.add_picture(str(ASSETS / "template" / "star.png"), Inches(3.85),
                     Inches(3.95), Inches(0.75), Inches(0.72))
s.shapes.add_picture(str(ASSETS / "template" / "tree.png"), Inches(1.10),
                     Inches(4.36), Inches(1.15), Inches(2.06))
s.shapes.add_picture(str(ASSETS / "template" / "chest.png"), Inches(9.85),
                     Inches(4.68), Inches(2.64), Inches(1.4))
notes(s, """Cierre y espacio para preguntas.

Recuerda: id Software no tenía el equipo más grande ni el hardware más potente. Tenía un grupo pequeño, herramientas propias, código simple y una comprensión profunda de lo que el hardware podía hacer.

Los archivos de apoyo están en T8-4_content: imágenes, diagramas, fast_inv_sqrt.c, bsp_demo.py y este generador.

Para la siguiente clase: 8.5, introducción a Unity. Llegar con el editor instalado y el proyecto base abierto.""")

prs.save(PPTX)
print("Guardado:", PPTX)
print("Diapositivas:", len(prs.slides))
