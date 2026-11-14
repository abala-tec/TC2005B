"""Genera las imágenes de código de T8.8.2 con el estilo de la plantilla."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pygments import lex
from pygments.lexers import CSharpLexer
from pygments.token import Token

from snippets import SNIPPETS

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "codigo"
OUT.mkdir(exist_ok=True)

BG = (43, 41, 61)
BAR = (240, 138, 60)
BASE = (237, 237, 242)
MUTED = (138, 143, 163)
ORANGE = (240, 138, 60)
PURPLE = (199, 146, 234)
YELLOW = (242, 201, 76)
GREEN = (168, 212, 138)
BLUE = (127, 209, 232)
PUNCT = (200, 203, 214)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def color_for(token):
    if token in Token.Comment:
        return MUTED
    if token in Token.Keyword:
        return ORANGE
    if token in Token.Name.Function:
        return PURPLE
    if token in Token.Name.Builtin:
        return BLUE
    if token in Token.Literal.Number:
        return YELLOW
    if token in Token.Literal.String:
        return GREEN
    if token in Token.Operator or token in Token.Punctuation:
        return PUNCT
    return BASE


def render(code, name, font_size, line_height):
    font = ImageFont.truetype(FONT, font_size)
    lines = code.split("\n")
    pad_x, pad_y = 44, 30
    width = max(560, int(max(font.getlength(l) for l in lines)) + pad_x * 2)
    height = pad_y * 2 + line_height * len(lines)
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, 10, height], fill=BAR)
    y = pad_y
    for line in lines:
        x = pad_x
        for token, text in lex(line, CSharpLexer()):
            if text == "\n":
                continue
            draw.text((x, y), text, font=font, fill=color_for(token))
            x += font.getlength(text)
        y += line_height
    image.save(OUT / (name + ".png"))
    print(name, image.size)


if __name__ == "__main__":
    for name, (code, size, line) in SNIPPETS.items():
        render(code, name, size, line)
