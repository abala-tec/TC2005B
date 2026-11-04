#!/usr/bin/env python3
"""Renderiza un PPTX a PNG y crea una hoja de contacto para revision visual.

Uso:
    python render_deck.py deck.pptx review/deck
"""

from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

THUMB_W = 320
COLS = 4
PAD = 10
LABEL_H = 18


def _run(cmd: list[str], env: dict | None = None) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(
            f"fallo {' '.join(cmd)}\n{result.stdout}\n{result.stderr}"
        )


def _slide_number(path: Path) -> int:
    digits = "".join(c for c in path.stem if c.isdigit())
    return int(digits or 0)


def render(pptx: Path, outdir: Path, dpi: int = 100) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["SAL_USE_VCLPLUGIN"] = "svp"

    with tempfile.TemporaryDirectory(prefix="deck-render-") as tmp:
        tmp_path = Path(tmp)
        _run(
            [
                "soffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(tmp_path),
                str(pptx),
            ],
            env=env,
        )
        pdfs = list(tmp_path.glob("*.pdf"))
        if not pdfs:
            raise RuntimeError("LibreOffice no genero ningun PDF")
        pdf = pdfs[0]

        _run(
            [
                "pdftoppm",
                "-png",
                "-r",
                str(dpi),
                str(pdf),
                str(tmp_path / "slide"),
            ]
        )
        pngs = sorted(tmp_path.glob("slide*.png"), key=_slide_number)
        if not pngs:
            raise RuntimeError("pdftoppm no genero imagenes")

        result: list[Path] = []
        for i, png in enumerate(pngs, 1):
            target = outdir / f"slide-{i:03d}.png"
            shutil.copyfile(png, target)
            result.append(target)
    return result


def contact_sheet(images: list[Path], output: Path) -> None:
    if not images:
        return
    thumbs: list[Image.Image] = []
    for path in images:
        img = Image.open(path).convert("RGB")
        ratio = THUMB_W / img.width
        thumbs.append(img.resize((THUMB_W, max(1, int(img.height * ratio)))))

    thumb_h = max(img.height for img in thumbs)
    rows = math.ceil(len(thumbs) / COLS)
    cell_w = THUMB_W + PAD
    cell_h = thumb_h + LABEL_H + PAD
    sheet = Image.new("RGB", (COLS * cell_w + PAD, rows * cell_h + PAD), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13
    )

    for i, img in enumerate(thumbs):
        row, col = divmod(i, COLS)
        x = PAD + col * cell_w
        y = PAD + row * cell_h
        sheet.paste(img, (x, y + LABEL_H))
        draw.text((x, y), f"slide {i + 1}", fill="#222222", font=font)

    sheet.save(output, quality=92)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", help="Archivo PowerPoint")
    parser.add_argument("outdir", help="Carpeta de salida para PNGs")
    parser.add_argument("--dpi", type=int, default=100)
    args = parser.parse_args(argv)

    pptx = Path(args.pptx)
    outdir = Path(args.outdir)
    try:
        images = render(pptx, outdir, args.dpi)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    sheet = outdir / "contact-sheet.jpg"
    contact_sheet(images, sheet)
    print(f"{len(images)} diapositivas en {outdir}")
    print(f"Hoja de contacto: {sheet}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
