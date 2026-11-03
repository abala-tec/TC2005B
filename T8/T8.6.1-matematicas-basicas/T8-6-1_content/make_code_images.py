"""Genera las imágenes de código de T8.6.1 con el estilo de la plantilla."""

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

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


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


def render(code, name, font_size=40, line_height=None):
    line_height = line_height or int(font_size * 1.4)
    font = ImageFont.truetype(FONT, font_size)
    lines = code.split("\n")
    pad_x, pad_y = 48, 34
    max_width = max(font.getlength(line) for line in lines)
    width = max(620, int(max_width) + pad_x * 2)
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

    image.save(OUT / name)
    print(name, image.size)


SNIPPETS = {
    "code_campos.png": """public Transform cubo;
private Vector3[] esquinas;
public int indiceObjetivo;
public float velocidad = 5.0f;
public float distanciaContacto = 1.1f;
public float anguloPisoton = 60f;
// radio de deteccion para perseguir
public float radioDeteccion = 3.0f;""",
    "code_start.png": """void Start()
{
    esquinas = new Vector3[4];
    esquinas[0] = new Vector3(-4.5f, 0.5f, -4.5f);
    esquinas[1] = new Vector3( 4.5f, 0.5f, -4.5f);
    esquinas[2] = new Vector3( 4.5f, 0.5f,  4.5f);
    esquinas[3] = new Vector3(-4.5f, 0.5f,  4.5f);

    NewRandom();
    transform.position = esquinas[indiceObjetivo];

    InvokeRepeating("NewRandom", 0f, 5f);
}""",
    "code_newrandom.png": """void NewRandom()
{
    indiceObjetivo = UnityEngine.Random.Range(0, 4);
}""",
    "code_invoke.png": """// En Start:
InvokeRepeating("NewRandom", 0f, 5f);""",
    "code_longitud.png": """static float Longitud(Vector3 v)
{
    return (float)Math.Sqrt(
        v.x * v.x + v.y * v.y + v.z * v.z);
}""",
    "code_normalizar.png": """static Vector3 Normalizar(Vector3 v)
{
    float longitud = Longitud(v);
    if (longitud < 0.0001f)
    {
        return new Vector3(0f, 0f, 0f);
    }
    return new Vector3(
        v.x / longitud, v.y / longitud, v.z / longitud);
}""",
    "code_resta.png": """Vector3 hacia = objetivo - transform.position;
float distancia = Longitud(hacia);""",
    "code_suma.png": """transform.position = new Vector3(
    transform.position.x + direccion.x * paso,
    transform.position.y,
    transform.position.z + direccion.z * paso
);""",
    "code_mover_objetivo.png": """void MoverEsfera()
{
    Vector3 objetivo = esquinas[indiceObjetivo];
    Vector3 hacia = objetivo - transform.position;
    float distancia = Longitud(hacia);

    if (distancia < 0.1f)
    {
        indiceObjetivo = (indiceObjetivo +
            UnityEngine.Random.Range(1, 4)) % 4;
        return;
    }""",
    "code_modulo.png": """if (distancia < 0.1f && !persiguiendo)
{
    // Elige otra esquina distinta: suma 1, 2 o 3 y da la vuelta
    indiceObjetivo = (indiceObjetivo +
        UnityEngine.Random.Range(1, 4)) % 4;
    return;
}""",
    "code_mover_paso.png": """    Vector3 direccion = Normalizar(hacia);
    float paso = velocidad * Time.deltaTime;

    transform.position = new Vector3(
        transform.position.x + direccion.x * paso,
        transform.position.y,
        transform.position.z + direccion.z * paso
    );
}""",
    "code_contacto.png": """bool Contacto()
{
    Vector3 haciaCubo = cubo.position - transform.position;
    float distanciaCubo = Longitud(haciaCubo);

    if (distanciaCubo <= distanciaContacto)
    {
        return true;
    }
    return false;
}""",
    "code_pisoton.png": """bool Pisoton()
{
    Vector3 haciaCubo = cubo.position - transform.position;
    float dx = haciaCubo.x;
    float dy = haciaCubo.y;
    float dz = haciaCubo.z;

    float horizontal = (float)Math.Sqrt(dx*dx + dz*dz);
    float angulo = (float)(Math.Atan2(dy, horizontal)
        * 180.0 / Math.PI);

    if (angulo >= anguloPisoton
        && horizontal <= distanciaContacto)
    {
        Debug.Log("PISOTON");
        Reset();
        return true;
    }
    return false;
}""",
    "code_reset.png": """void Reset()
{
    NewRandom();
    transform.position = esquinas[indiceObjetivo];
}""",
    "code_jump.png": """if (keyboard.spaceKey.wasPressedThisFrame
    && estaEnSuelo == true)
{
    rb.AddForce(Vector3.up * jumpForce,
        ForceMode.Impulse);
    estaEnSuelo = false;
}""",
    "code_suelo.png": """private void OnCollisionEnter(
    Collision collision)
{
    if (collision.gameObject.name == "Plane")
    {
        estaEnSuelo = true;
    }
}""",
    "code_persigue_detecta.png": """void MoverEsfera()
{
    bool persiguiendo = Longitud(
        cubo.position - transform.position)
        <= radioDeteccion;""",
    "code_persigue_objetivo.png": """    Vector3 objetivo;
    if (persiguiendo)
    {
        objetivo = cubo.position;
    }
    else
    {
        objetivo = esquinas[indiceObjetivo];
    }

    Vector3 hacia = objetivo - transform.position;
    float distancia = Longitud(hacia);""",
}

SIZES = {
    "code_campos.png": (44, 62),
    "code_start.png": (40, 56),
    "code_newrandom.png": (44, 62),
    "code_invoke.png": (44, 62),
    "code_longitud.png": (46, 64),
    "code_normalizar.png": (42, 59),
    "code_resta.png": (46, 64),
    "code_suma.png": (40, 56),
    "code_mover_objetivo.png": (42, 59),
    "code_modulo.png": (42, 59),
    "code_mover_paso.png": (42, 59),
    "code_contacto.png": (40, 56),
    "code_pisoton.png": (38, 53),
    "code_reset.png": (48, 66),
    "code_jump.png": (42, 59),
    "code_suelo.png": (42, 59),
    "code_persigue_detecta.png": (44, 62),
    "code_persigue_objetivo.png": (42, 59),
}


if __name__ == "__main__":
    for name, code in SNIPPETS.items():
        size, line = SIZES[name]
        render(code, name, size, line)
