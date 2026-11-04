#!/usr/bin/env python3
"""Valida un PPTX contra la escala tipografica de la plantilla.

Uso:
    python validate_deck.py --strict deck.pptx
    python validate_deck.py --audit  deck.pptx

--strict exige que cada forma de texto tenga un rol de deck_style.py.
--audit solo reporta; sirve para decks viejos o editados a mano.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from lxml import etree
from PIL import ImageFont
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Inches, Length

from deck_style import FONT_DIR, MENLO, REG, ROLE_STYLE, SEM, get_role

PX_PER_IN = 96.0
PX_PER_PT = PX_PER_IN / 72.0
THEME_NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
EXPECTED_W = Inches(13.333)
EXPECTED_H = Inches(7.5)
EPSILON = Inches(0.01)

AUDIT_SIZES = {
    7.5, 9.0, 9.5, 10.0, 10.5, 12.0, 12.2, 12.5, 13.0, 13.5, 14.0, 15.0,
    16.0, 17.0, 18.0, 20.0, 21.0, 22.0, 23.0, 24.0, 28.0, 32.0, 36.0,
    40.0, 48.0, 54.0, 64.0, 66.0, 80.0, 96.0,
}


@dataclass
class Report:
    path: Path
    strict: bool
    slides: int = 0
    runs: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def format(self) -> str:
        lines = [
            f"{'STRICT' if self.strict else 'AUDIT'}: {self.path}",
            f"{self.slides} diapositivas, {self.runs} runs",
        ]
        if self.errors:
            lines.append(f"{len(self.errors)} errores:")
            lines.extend(f"  FAIL {e}" for e in self.errors)
        if self.warnings:
            lines.append(f"{len(self.warnings)} advertencias:")
            lines.extend(f"  WARN {w}" for w in self.warnings)
        if not self.errors:
            lines.append("PASS")
        return "\n".join(lines)


def _walk_shapes(shapes, in_group: bool = False):
    for shape in shapes:
        yield shape, in_group
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from _walk_shapes(shape.shapes, True)


def _font_path(font_name: str | None, bold: bool) -> Path | None:
    if font_name == MENLO:
        for path in (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"),
        ):
            if path.exists():
                return path
        return None
    if font_name == SEM or "SemBd" in (font_name or "") or bold:
        path = FONT_DIR / "Neuromax-SemiBold.otf"
    else:
        path = FONT_DIR / "Neuromax-Regular.otf"
    return path if path.exists() else None


@lru_cache(maxsize=128)
def _load_font(path: str, size_px: int):
    return ImageFont.truetype(path, size_px)


def _split_word(word: str, font, max_width: float) -> list[str]:
    parts: list[str] = []
    current = ""
    for char in word:
        candidate = current + char
        if font.getlength(candidate) <= max_width:
            current = candidate
        else:
            if current:
                parts.append(current)
            current = char
    if current:
        parts.append(current)
    return parts or [""]


def _wrap(text: str, font, max_width: float) -> list[str]:
    lines: list[str] = []
    for raw in text.replace("\v", "\n").split("\n"):
        words = raw.split()
        if not words:
            lines.append("")
            continue
        line = ""
        for word in words:
            candidate = (line + " " + word).strip()
            if font.getlength(candidate) <= max_width:
                line = candidate
                continue
            if line:
                lines.append(line)
                line = ""
            if font.getlength(word) > max_width:
                pieces = _split_word(word, font, max_width)
                lines.extend(pieces[:-1])
                line = pieces[-1]
            else:
                line = word
        lines.append(line)
    return lines or [""]


def _spacing_factor(para, line_height_px: float) -> float:
    value = para.line_spacing
    if value is None:
        return 1.0
    if isinstance(value, Length):
        return max(value.pt * PX_PER_PT / line_height_px, 0.1)
    return max(float(value), 0.1)


def _measure(tf, width_emu: int, height_emu: int, default_size: float,
             default_font: str, default_bold: bool) -> float | None:
    """Devuelve cuanto se desborda el texto, en pulgadas. None si no se mide."""
    usable_w = (float(width_emu) - float(tf.margin_left) - float(tf.margin_right)) / 914400 * PX_PER_IN
    usable_h = (float(height_emu) - float(tf.margin_top) - float(tf.margin_bottom)) / 914400 * PX_PER_IN
    if usable_w <= 0 or usable_h <= 0:
        return 99.0

    total = 0.0
    for para in tf.paragraphs:
        text = para.text
        size = default_size
        font_name = default_font
        bold = default_bold
        for run in para.runs:
            if not run.text.strip():
                continue
            if run.font.size:
                size = run.font.size.pt
            if run.font.name:
                font_name = run.font.name
            if run.font.bold is not None:
                bold = bool(run.font.bold)

        path = _font_path(font_name, bold)
        if path is None:
            return None
        font = _load_font(str(path), max(1, int(round(size * PX_PER_PT))))
        ascent, descent = font.getmetrics()
        line_h = ascent + descent
        spacing = _spacing_factor(para, line_h)
        lines = _wrap(text, font, usable_w) if text else [""]
        total += len(lines) * line_h * spacing
        if para.space_before:
            total += para.space_before.pt * PX_PER_PT
        if para.space_after:
            total += para.space_after.pt * PX_PER_PT

    return max((total - usable_h) / PX_PER_IN, 0.0)


def _check_theme(report: Report, path: Path) -> None:
    try:
        with zipfile.ZipFile(path) as z:
            root = etree.fromstring(z.read("ppt/theme/theme1.xml"))
    except (KeyError, zipfile.BadZipFile, etree.XMLSyntaxError) as exc:
        report.errors.append(f"theme: no se pudo leer ppt/theme/theme1.xml ({exc})")
        return

    major = root.find(".//a:majorFont/a:latin", THEME_NS)
    minor = root.find(".//a:minorFont/a:latin", THEME_NS)
    major_name = major.get("typeface") if major is not None else None
    minor_name = minor.get("typeface") if minor is not None else None
    if major_name != SEM:
        report.errors.append(f"theme: majorFont={major_name!r}, esperado {SEM!r}")
    if minor_name != REG:
        report.errors.append(f"theme: minorFont={minor_name!r}, esperado {REG!r}")


def _check_autofit(report: Report, path: Path) -> None:
    try:
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if not (name.startswith("ppt/slides/slide") and name.endswith(".xml")):
                    continue
                xml = z.read(name).decode("utf-8", "replace")
                if "<a:normAutofit" in xml:
                    report.errors.append(f"{name}: normAutofit prohibido (puede encoger la fuente)")
                if "<a:spAutoFit" in xml:
                    report.errors.append(f"{name}: spAutoFit prohibido (puede mover el layout)")
    except zipfile.BadZipFile:
        report.errors.append("autofit: archivo PPTX invalido")


def _check_bounds(report: Report, shape, slide_w: int, slide_h: int) -> None:
    left, top = int(shape.left), int(shape.top)
    right, bottom = left + int(shape.width), top + int(shape.height)
    if left < -EPSILON or top < -EPSILON or right > slide_w + EPSILON or bottom > slide_h + EPSILON:
        report.errors.append(
            f"{shape.name}: fuera de la diapositiva "
            f"({left/914400:.2f},{top/914400:.2f})-({right/914400:.2f},{bottom/914400:.2f})"
        )


def _check_text_frame(report: Report, shape, slide_no: int, strict: bool,
                      tolerance: float) -> None:
    tf = shape.text_frame
    if not tf.text.strip():
        return

    role = get_role(shape)
    style = ROLE_STYLE.get(role) if role else None
    if strict:
        if role is None:
            report.errors.append(f"slide {slide_no} {shape.name}: falta rol deck-role")
        elif role not in ROLE_STYLE:
            report.errors.append(f"slide {slide_no} {shape.name}: rol desconocido {role!r}")

    sizes: list[float] = []
    for para in tf.paragraphs:
        for run in para.runs:
            if not run.text.strip():
                continue
            report.runs += 1
            size = run.font.size.pt if run.font.size else None
            font = run.font.name
            if size is not None:
                sizes.append(size)

            if strict and style is not None:
                if size is None:
                    report.errors.append(f"slide {slide_no} {shape.name}: run sin tamano explicito")
                elif abs(size - style.size) > 0.01:
                    report.errors.append(
                        f"slide {slide_no} {shape.name}: {role} usa {size:g} pt, esperado {style.size:g}"
                    )
                if font is None:
                    report.errors.append(f"slide {slide_no} {shape.name}: run sin fuente explicita")
                elif font != style.font:
                    report.errors.append(
                        f"slide {slide_no} {shape.name}: {role} usa {font!r}, esperado {style.font!r}"
                    )
                if run.font.bold is not None and bool(run.font.bold) != style.bold:
                    report.errors.append(
                        f"slide {slide_no} {shape.name}: {role} bold={run.font.bold}, esperado {style.bold}"
                    )
            elif not strict:
                if size is None:
                    report.warnings.append(f"slide {slide_no} {shape.name}: run sin tamano explicito")
                elif size not in AUDIT_SIZES:
                    report.warnings.append(f"slide {slide_no} {shape.name}: tamano {size:g} pt fuera de escala")
                if font is None:
                    report.warnings.append(f"slide {slide_no} {shape.name}: run sin fuente explicita")

    default_size = style.size if style else (max(sizes) if sizes else 16.0)
    default_font = style.font if style else REG
    default_bold = style.bold if style else False
    overflow = _measure(tf, shape.width, shape.height, default_size, default_font, default_bold)
    if overflow is not None and overflow > tolerance:
        report.errors.append(
            f"slide {slide_no} {shape.name}: desborde {overflow:.2f} in "
            f"(caja {shape.height/914400:.2f} in, texto {tf.text[:40]!r})"
        )


def _check_table(report: Report, shape, slide_no: int, strict: bool,
                 tolerance: float) -> None:
    table = shape.table
    role = get_role(shape)
    if strict and role != "table":
        report.errors.append(f"slide {slide_no} {shape.name}: tabla sin rol deck-role:table")

    for row_no, row in enumerate(table.rows):
        expected = ROLE_STYLE["table_head" if row_no == 0 else "table_body"]
        for col_no, cell in enumerate(row.cells):
            tf = cell.text_frame
            if not tf.text.strip():
                continue
            for para in tf.paragraphs:
                for run in para.runs:
                    if not run.text.strip():
                        continue
                    report.runs += 1
                    size = run.font.size.pt if run.font.size else None
                    font = run.font.name
                    if strict:
                        if size is None or abs(size - expected.size) > 0.01:
                            report.errors.append(
                                f"slide {slide_no} {shape.name} tabla[{row_no},{col_no}]: "
                                f"usa {size} pt, esperado {expected.size:g}"
                            )
                        if font != expected.font:
                            report.errors.append(
                                f"slide {slide_no} {shape.name} tabla[{row_no},{col_no}]: "
                                f"usa {font!r}, esperado {expected.font!r}"
                            )
            width = table.columns[col_no].width
            height = row.height
            overflow = _measure(tf, width, height, expected.size, expected.font, expected.bold)
            if overflow is not None and overflow > tolerance:
                report.errors.append(
                    f"slide {slide_no} {shape.name} tabla[{row_no},{col_no}]: "
                    f"desborde {overflow:.2f} in ({tf.text[:40]!r})"
                )


def validate(path: str | Path, strict: bool = False, tolerance: float = 0.05) -> Report:
    path = Path(path)
    report = Report(path=path, strict=strict)
    if not path.exists():
        report.errors.append("archivo no encontrado")
        return report

    try:
        prs = Presentation(path)
    except Exception as exc:  # noqa: BLE001
        report.errors.append(f"no se pudo abrir el PPTX: {exc}")
        return report

    report.slides = len(prs.slides)
    if abs(int(prs.slide_width) - int(EXPECTED_W)) > EPSILON:
        report.errors.append(
            f"slide_width={prs.slide_width/914400:.3f} in, esperado {EXPECTED_W/914400:.3f}"
        )
    if abs(int(prs.slide_height) - int(EXPECTED_H)) > EPSILON:
        report.errors.append(
            f"slide_height={prs.slide_height/914400:.3f} in, esperado {EXPECTED_H/914400:.3f}"
        )

    _check_theme(report, path)
    _check_autofit(report, path)

    for slide_no, slide in enumerate(prs.slides, 1):
        for shape, in_group in _walk_shapes(slide.shapes):
            if not in_group:
                _check_bounds(report, shape, prs.slide_width, prs.slide_height)
            if shape.has_text_frame:
                _check_text_frame(report, shape, slide_no, strict, tolerance)
            if shape.has_table:
                _check_table(report, shape, slide_no, strict, tolerance)

    if not strict:
        report.warnings = report.errors + report.warnings
        report.errors = []

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", help="Archivo PowerPoint a validar")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--strict", action="store_true", help="Exige roles y escala exacta")
    mode.add_argument("--audit", action="store_true", help="Solo reporta (default)")
    parser.add_argument("--tolerance", type=float, default=0.05,
                        help="Tolerancia de desborde en pulgadas (default 0.05)")
    args = parser.parse_args(argv)

    report = validate(args.pptx, strict=args.strict, tolerance=args.tolerance)
    print(report.format())
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
