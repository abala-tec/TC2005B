from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pygments import lex
from pygments.lexers import CLexer
from pygments.token import Token

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

CODE = """float Q_rsqrt(float number)
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
}"""


def color_for(token):
    if token in Token.Comment:
        return MUTED
    if token in Token.Keyword.Type or token in Token.Keyword:
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


def render(code, name, font_size=44, line_height=64):
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", font_size, index=0)
    lines = code.split("\n")
    pad_x, pad_y = 62, 40
    max_width = max(font.getlength(line) for line in lines)
    width = max(1400, int(max_width) + pad_x * 2)
    height = pad_y * 2 + line_height * len(lines)
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, 10, height], fill=BAR)

    y = pad_y
    for line in lines:
        x = pad_x
        for token, text in lex(line, CLexer()):
            if text == "\n":
                continue
            color = color_for(token)
            draw.text((x, y), text, font=font, fill=color)
            x += font.getlength(text)
        y += line_height

    image.save(OUT / name)
    print(name, image.size)


if __name__ == "__main__":
    render(CODE, "code_rsqrt.png")
