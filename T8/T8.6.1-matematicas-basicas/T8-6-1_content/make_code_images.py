#!/usr/bin/env python3
"""Genera las imágenes de código para T8.6.1."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pygments import lex
from pygments.lexers import CSharpLexer
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
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

CODE = {}

CODE["campos"] = """public class EnemigoEsfera : MonoBehaviour
{
    public Transform cubo;
    private Vector3[] esquinas;
    public int indiceObjetivo;
    public float velocidad = 5.0f;
    public float distanciaContacto = 1.1f;
    public float anguloPisoton = 60f;
}"""

CODE["start"] = """void Start()
{
    esquinas = new Vector3[4];
    esquinas[0] = new Vector3(-4.5f, 0.5f, -4.5f);
    esquinas[1] = new Vector3( 4.5f, 0.5f, -4.5f);
    esquinas[2] = new Vector3( 4.5f, 0.5f,  4.5f);
    esquinas[3] = new Vector3(-4.5f, 0.5f,  4.5f);

    // setup de la primera esquina
    NewRandom();
    transform.position = esquinas[indiceObjetivo];

    InvokeRepeating("NewRandom", 0f, 5f);
}

void NewRandom()
{
    indiceObjetivo = UnityEngine.Random.Range(0, 4);
}"""

CODE["longitud"] = """static float Longitud(Vector3 v)
{
    return (float)Math.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}

static Vector3 Normalizar(Vector3 v)
{
    float longitud = Longitud(v);
    if (longitud < 0.0001f) {
        return new Vector3(0f, 0f, 0f);
    }
    return new Vector3(v.x / longitud, v.y / longitud, v.z / longitud);
}"""

CODE["mover"] = """void MoverEsfera()
{
    Vector3 objetivo = esquinas[indiceObjetivo];
    Vector3 hacia = objetivo - transform.position;
    float distancia = Longitud(hacia);

    if (distancia < 0.1f)
    {
        // Elige otra esquina distinta: suma 1, 2 o 3 y da la vuelta
        indiceObjetivo = (indiceObjetivo + UnityEngine.Random.Range(1, 4)) % 4;
        return;
    }

    Vector3 direccion = Normalizar(hacia);
    float paso = velocidad * Time.deltaTime;

    transform.position = new Vector3(
        transform.position.x + direccion.x * paso,
        transform.position.y,                       // la altura no cambia
        transform.position.z + direccion.z * paso
    );
}"""

CODE["contacto"] = """// bool Contacto()
// {
//     Vector3 haciaCubo = cubo.position - transform.position;
//     float distanciaCubo = Longitud(haciaCubo);
//
//     if (distanciaCubo <= distanciaContacto)
//     {
//         return true;
//     }
//     return false;
// }"""

CODE["pisoton"] = """bool Pisoton()
{
    Vector3 haciaCubo = cubo.position - transform.position;
    float dx = haciaCubo.x;
    float dy = haciaCubo.y;
    float dz = haciaCubo.z;

    float horizontal = (float) Math.Sqrt(dx*dx + dz*dz);  // distancia horizontal
    float angulo = (float)(Math.Atan2(dy, horizontal) * 180.0 / Math.PI); // angulo vertical

    if (angulo >= anguloPisoton && horizontal <= distanciaContacto){
        Debug.Log("PISOTON");
        Reset();
        return true;
    }
    return false;

}"""

CODE["reset_update"] = """void Reset()
{
    NewRandom();
    transform.position = esquinas[indiceObjetivo];
}

void Update()
{
    MoverEsfera();
    // Contacto();
    Pisoton();
}"""

CODE_DEFAULT = """using UnityEngine;

public class EnemigoEsfera : MonoBehaviour
{
    void Start()
    {
    }

    void Update()
    {
    }
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


def render(code, name, max_width=1800):
    # Busca el tamaño de letra más grande que quepa en el ancho objetivo.
    for size in range(44, 27, -1):
        font = ImageFont.truetype(FONT_PATH, size)
        max_line = max(font.getlength(line) for line in code.split("\n"))
        if max_line + 124 <= max_width:
            break
    line_height = int(size * 1.42)
    pad_x, pad_y = 62, 38
    lines = code.split("\n")
    width = max(1400, int(max_line) + pad_x * 2)
    height = pad_y * 2 + line_height * len(lines)
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, 10, height], fill=BAR)

    y = pad_y
    for code_line in lines:
        x = pad_x
        for token, text_part in lex(code_line, CSharpLexer()):
            if text_part == "\n":
                continue
            draw.text((x, y), text_part, font=font, fill=color_for(token))
            x += font.getlength(text_part)
        y += line_height

    image.save(OUT / name)
    print(name, image.size, "font", size)


if __name__ == "__main__":
    for key, value in CODE.items():
        render(value, f"code_{key}.png")
    render(CODE_DEFAULT, "code_default.png")
