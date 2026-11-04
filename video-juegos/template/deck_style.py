"""Estilos canonicos para las presentaciones del curso TC2005B.

La plantilla FINAL-plantilla-videojuegos.pptx es la fuente de verdad.
Los textos no se agregan con un tamano libre: se agregan con un rol.
El rol fija tamano, fuente y peso; el validador comprueba que el PPTX
generado respete esa escala.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "FINAL-plantilla-videojuegos.pptx"
FONT_DIR = HERE / "fonts"

REG = "Neuromax"
SEM = "Neuromax SemBd"
MENLO = "Menlo"

INK = RGBColor(0x13, 0x13, 0x15)
BODY = RGBColor(0x4F, 0x53, 0x61)
MUTED = RGBColor(0x6B, 0x72, 0x80)


@dataclass(frozen=True)
class RoleStyle:
    size: float
    font: str = REG
    bold: bool = False


# Escala extraida de FINAL-plantilla-videojuegos.pptx.
ROLE_STYLE: dict[str, RoleStyle] = {
    "pill": RoleStyle(7.5, SEM),
    "label": RoleStyle(9.5, SEM),
    "caption": RoleStyle(14, REG),
    "note": RoleStyle(14, REG),
    "note_strong": RoleStyle(14, SEM),
    "body": RoleStyle(16, REG),
    "body_strong": RoleStyle(16, SEM),
    "bullet": RoleStyle(15, SEM),
    "footer": RoleStyle(16, REG),
    "step_number": RoleStyle(17, SEM),
    "card_number": RoleStyle(14, SEM),
    "card_title_sm": RoleStyle(20, SEM),
    "subtitle": RoleStyle(20, REG),
    "subtitle_strong": RoleStyle(20, SEM),
    "quote_sm": RoleStyle(22, SEM),
    "quote": RoleStyle(23, SEM),
    "card_title": RoleStyle(24, SEM),
    "card_title_lg": RoleStyle(28, SEM),
    "section_number": RoleStyle(32, SEM),
    "title": RoleStyle(36, SEM),
    "stat_sm": RoleStyle(40, SEM),
    "section": RoleStyle(48, SEM),
    "stat": RoleStyle(64, SEM),
    "stat_lg": RoleStyle(66, SEM),
    "closing": RoleStyle(80, SEM),
    "hero": RoleStyle(96, SEM),
    "table_head": RoleStyle(20, SEM),
    "table_body": RoleStyle(16, REG),
    "code_text": RoleStyle(16, MENLO),
}

# Compatibilidad con los build_deck.py viejos, que pasaban un tamano.
# El tamano solo sirve como pista; la salida siempre usa el rol.
SIZE_ROLE: dict[float, str] = {
    7.5: "pill",
    9.0: "label",
    9.5: "label",
    10.0: "note",
    10.5: "note",
    11.0: "note",
    11.5: "note",
    12.0: "body",
    12.2: "footer",
    12.5: "body",
    13.0: "body",
    13.5: "card_title_sm",
    14.0: "note",
    15.0: "body",
    16.0: "body",
    17.0: "card_title_sm",
    18.0: "card_title_sm",
    20.0: "subtitle",
    21.0: "subtitle",
    22.0: "quote_sm",
    23.0: "quote",
    24.0: "card_title",
    28.0: "card_title_lg",
    32.0: "section_number",
    36.0: "title",
    40.0: "stat_sm",
    48.0: "section",
    54.0: "closing",
    64.0: "stat",
    66.0: "stat_lg",
    80.0: "closing",
    96.0: "hero",
}


def role_for_size(size: float | None, font: str = REG, bold: bool = False) -> str:
    """Convierte un tamano viejo a un rol canonico."""
    if font == MENLO:
        return "code_text"
    if size is None:
        raise ValueError("Falta el rol o el tamano del texto")
    key = round(float(size), 1)
    role = SIZE_ROLE.get(key)
    if role is None:
        raise ValueError(
            f"Tamano {size} pt sin rol canonico. Agrega un rol a deck_style.py."
        )
    if (font == SEM or bold) and role in {"body", "note", "subtitle"}:
        role += "_strong"
    return role


def set_role(shape, role: str) -> None:
    """Guarda el rol en el alt text de la forma."""
    cNvPr = shape._element.find(".//" + qn("p:cNvPr"))
    if cNvPr is None:
        raise ValueError(f"No se encontro cNvPr en {shape.name}")
    cNvPr.set("descr", f"deck-role:{role}")


def get_role(shape) -> str | None:
    cNvPr = shape._element.find(".//" + qn("p:cNvPr"))
    if cNvPr is None:
        return None
    descr = cNvPr.get("descr", "")
    if descr.startswith("deck-role:"):
        return descr.split(":", 1)[1]
    return None


def apply_role(run, role: str, color: RGBColor = INK, italic: bool = False) -> None:
    style = ROLE_STYLE[role]
    run.font.name = style.font
    run.font.size = Pt(style.size)
    run.font.bold = style.bold
    run.font.italic = italic
    run.font.color.rgb = color


def add_text(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    value: str,
    role: str,
    color: RGBColor = INK,
    italic: bool = False,
    align=PP_ALIGN.LEFT,
    anchor=MSO_ANCHOR.TOP,
    line_spacing: float = 1.0,
    space_after: float = 0,
):
    """Agrega una caja de texto con un rol canonico."""
    if role not in ROLE_STYLE:
        raise KeyError(f"Rol desconocido: {role}")

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
        apply_role(r, role, color, italic)

    set_role(box, role)
    return box


def new_deck() -> Presentation:
    """Abre la plantilla y elimina sus diapositivas de ejemplo."""
    prs = Presentation(TEMPLATE)
    for sld_id in list(prs.slides._sldIdLst):
        r_id = sld_id.get(qn("r:id"))
        if r_id:
            prs.part.drop_rel(r_id)
        prs.slides._sldIdLst.remove(sld_id)

    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def add_slide(prs: Presentation):
    layout = next(
        (layout for layout in prs.slide_layouts if layout.name == "Blank"),
        prs.slide_layouts[6],
    )
    return prs.slides.add_slide(layout)
