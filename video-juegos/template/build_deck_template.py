#!/usr/bin/env python3
"""Esqueleto minimo para un deck nuevo.

Copia este archivo a la carpeta del tema y reemplaza el contenido.
La regla: cada texto usa un rol de deck_style.py; nunca un tamano libre.
"""

from __future__ import annotations

import sys
from pathlib import Path

from deck_style import add_slide, add_text, new_deck
from validate_deck import validate

OUT = Path(__file__).with_name("ejemplo-deck.pptx")


def build() -> None:
    prs = new_deck()
    prs.core_properties.title = "Ejemplo"
    prs.core_properties.author = "TC2005B"

    # Portada
    s = add_slide(prs)
    add_text(s, 0.62, 0.28, 10.0, 0.22, "TEMA · SECCION", role="label")
    add_text(s, 0.62, 0.92, 7.0, 2.70, "TITULO\nDEL TEMA", role="title")
    add_text(s, 0.62, 3.64, 6.0, 0.80, "Subtitulo que explica el objetivo.", role="subtitle")

    # Contenido
    s = add_slide(prs)
    add_text(s, 0.62, 0.27, 10.5, 0.22, "BLOQUE 01", role="label")
    add_text(s, 0.62, 0.52, 11.95, 0.72, "TITULO DE DIAPOSITIVA", role="title")
    add_text(s, 0.62, 1.18, 11.95, 0.40, "Una idea por diapositiva.", role="body")
    add_text(s, 0.62, 1.90, 11.95, 0.72,
             "El cuerpo va a 16 pt. Si no cabe, se recorta el texto o se parte la diapositiva.",
             role="body")
    add_text(s, 0.75, 6.30, 11.40, 0.28, "Nota de cierre.", role="footer")

    # Cierre
    s = add_slide(prs)
    add_text(s, 0.62, 0.27, 10.5, 0.22, "CIERRE", role="label")
    add_text(s, 0.62, 0.52, 11.95, 0.72, "LO QUE APRENDISTE", role="title")
    add_text(s, 0.62, 1.90, 11.95, 0.72, "Resumen breve.", role="body")

    prs.save(OUT)


def main() -> int:
    build()
    report = validate(OUT, strict=True)
    print(report.format())
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
