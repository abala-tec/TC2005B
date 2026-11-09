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
    "DECK_OUT_CAPA", str(ROOT.parent / "T8.8.1-Capa-Paredes.pptx")
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
prs.core_properties.title = "T8.8.1 · La capa Paredes"
prs.core_properties.author = "TC2005B · Construcción de Software"
prs.core_properties.subject = "Crear la capa Paredes en Unity y usarla en el grid del BFS"
prs.core_properties.keywords = "Unity, C#, LayerMask, Physics.CheckBox, grid, TC2005B"
prs.core_properties.language = "es-MX"

K = "EXTRA · LA CAPA PAREDES"

# 1 ------------------------------------------------------------ crear y asignar
s = new_slide()
header(s, K, "CREAR LA CAPA PAREDES Y ASIGNARLA",
       "Una capa le dice a la física cuáles objetos son paredes.")
steps(s, 0.62, 1.85, 7.30, [
    "Selecciona el objeto paredes en la Hierarchy.",
    "En el Inspector abre el menú Layer y elige Add Layer.",
    "En una capa vacía (aquí la User Layer 6) escribe Paredes.",
    "Selecciona paredes otra vez, abre Layer y elige Paredes. Acepta Yes, change children.",
    "Selecciona el objeto Grid. En S6_Grid, el campo Capa Paredes debe decir Paredes.",
], gap=0.84)
card(s, 8.30, 1.70, 4.41, 2.70, BLUE)
text(s, 8.55, 1.82, 3.9, 0.30, "HIERARCHY", role="label", color=INK)
text(s, 8.55, 2.22, 3.9, 0.34, "paredes  ·  Layer: Paredes", role="body", font=SEM, color=INK)
for i, n in enumerate(["pared_1", "pared_2", "pared_3", "pared_4", "pared_5", "pared_6"]):
    col, row = divmod(i, 3)
    text(s, 8.85 + col * 1.9, 2.72 + row * 0.42, 1.8, 0.32, "└ " + n, role="note", color=BODY)
text(s, 8.55, 4.00, 3.9, 0.30, "Los hijos heredan la capa.", role="caption", color=MUTED)
tip(s, 8.30, 4.60, 4.41, 1.50, "OJO CON EL NOMBRE",
    "En el proyecto la capa se llama Paredes (capa 6). Cada pared necesita un Collider.",
    accent=PINK)
notes(s,
      "Proceso para crear la capa y usarla.\n\n"
      "1. Una capa (Layer) es una etiqueta que Unity guarda en cada GameObject. La física puede "
      "filtrar por capa, y eso es lo que necesitamos: que el grid solo detecte las paredes.\n"
      "2. Se crea en Inspector > Layer > Add Layer. Se escribe el nombre en una capa de usuario "
      "vacía. En este proyecto quedó en la capa 6 con el nombre Paredes (ProjectSettings/TagManager).\n"
      "3. Se asigna al objeto paredes, que es el padre de pared_1 a pared_6. Al cambiar la capa Unity "
      "pregunta si también se cambian los hijos: hay que elegir Yes, change children. En la escena "
      "los siete objetos quedan con la capa 6.\n"
      "4. En el objeto Grid, el componente S6_Grid tiene el campo capaParedes. Ahí se elige la capa "
      "Paredes. Sin este paso la capa existe, pero el grid no sabe que debe usarla.\n\n"
      "Cada pared debe tener un Collider (el cubo trae un Box Collider). Sin Collider la física no "
      "la detecta, aunque tenga la capa correcta.")

# 2 ------------------------------------------------------------ uso en el código
s = new_slide()
header(s, K, "DÓNDE SE USA LA CAPA EN EL CÓDIGO",
       "S6_Grid la pasa a Physics.CheckBox al crear el grid.")
code_img(s, "code_capa", 0.62, 1.70, 7.00, 4.40)
tip(s, 7.95, 1.70, 4.76, 1.45, "1 · EL CAMPO",
    "capaParedes es un LayerMask. En el Inspector se elige la capa Paredes.")
tip(s, 7.95, 3.30, 4.76, 1.45, "2 · EL CHECKBOX",
    "CheckBox solo revisa los colliders de esa capa. Lo demás no bloquea.", accent=BLUE)
tip(s, 7.95, 4.90, 4.76, 1.20, "3 · EL RESULTADO",
    "true en bloqueada[x, z]: BFS no entra en esa casilla.", accent=GREEN)
footer(s, "Si capaParedes queda en Nothing, ninguna casilla se bloquea.")
nc(s, "Esta es la única parte del código donde se usa la capa.\n\n"
      "capaParedes es un LayerMask, un número donde cada bit es una capa. La capa Paredes es la 6, "
      "así que el valor guardado en la escena es 64 (1 desplazado 6 bits). Unity lo muestra como un "
      "menú con nombres, por eso no hay que calcularlo a mano.\n\n"
      "En Awake, por cada casilla del grid se llama a Physics.CheckBox. El último parámetro es "
      "capaParedes: la física solo considera los colliders de esa capa. Si hay uno dentro de la caja, "
      "devuelve true y la casilla queda bloqueada.\n\n"
      "Esa matriz bloqueada la usa después Libre(), y BFS la revisa para no entrar a una pared.",
   ["code_capa"])

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
