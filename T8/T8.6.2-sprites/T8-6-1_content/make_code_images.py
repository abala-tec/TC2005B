"""Genera las imágenes de código de T8.6.2 con el estilo de la plantilla."""

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
    "code_camara_campos.png": """public Transform target;  // El gameobject a seguir

public Vector3 offset = new Vector3(0, 5, -10);

public float followspeed = 0.2f;  // velocidad de seguimiento""",
    "code_camara_lateupdate.png": """void LateUpdate()
{
    // La meta es la posición del cubo más el offset
    Vector3 goalPosition = target.position + offset;

    // Lerp acerca la cámara a la meta poco a poco
    Vector3 smoothedPosition = Vector3.Lerp(
        transform.position, goalPosition, followspeed);

    transform.position = smoothedPosition;
}""",
    "code_spawner_campos.png": """[SerializeField] private GameObject enemigo;

public int numeroEnemigos = 50;

public int radio = 50;""",
    "code_spawner_bucle.png": """void Start()
{
    // La posición del objeto Spawner
    Vector3 spawn_pos = transform.position;

    // Repetir una vez por cada enemigo
    for (int i = 0; i < numeroEnemigos; i++)
    {
        // Aquí se crea cada enemigo
    }
}""",
    "code_spawner_random.png": """float rnd_x = UnityEngine.Random.Range(-radio, radio);
float rnd_z = UnityEngine.Random.Range(-radio, radio);

Vector3 enemy_pos = new Vector3(
    spawn_pos.x + rnd_x, 0.5f, spawn_pos.z + rnd_z);""",
    "code_random_malo.png": """float rnd_x = UnityEngine.Random.Range(0, radio);
float rnd_z = UnityEngine.Random.Range(0, radio);""",
    "code_random_bueno.png": """float rnd_x = UnityEngine.Random.Range(-radio, radio);
float rnd_z = UnityEngine.Random.Range(-radio, radio);""",
    "code_spawner_instantiate.png": """Quaternion enemy_rotation = Quaternion.identity;

GameObject nuevoEnemigo = Instantiate(
    enemigo, enemy_pos, enemy_rotation);

nuevoEnemigo.name = "EnemigoClon_" + i;""",
    "code_sprite_start.png": """private SpriteRenderer sprite = null;

void Start()
{
    rb = GetComponent<Rigidbody>();

    GameObject goSprite =
        GameObject.Find("velma_sprite_walk");

    sprite = goSprite.GetComponent<SpriteRenderer>();
}""",
    "code_sprite_flip.png": """if (keyboard.dKey.isPressed ||
    keyboard.rightArrowKey.isPressed)
{
    movement.x = 1f;
    sprite.flipX = false;
}

if (keyboard.aKey.isPressed ||
    keyboard.leftArrowKey.isPressed)
{
    movement.x = -1f;
    sprite.flipX = true;
}""",
}

SIZES = {
    "code_camara_campos.png": (40, 56),
    "code_camara_lateupdate.png": (38, 53),
    "code_spawner_campos.png": (42, 59),
    "code_spawner_bucle.png": (38, 53),
    "code_spawner_random.png": (36, 50),
    "code_random_malo.png": (38, 53),
    "code_random_bueno.png": (38, 53),
    "code_spawner_instantiate.png": (38, 53),
    "code_sprite_start.png": (40, 56),
    "code_sprite_flip.png": (38, 53),
}


if __name__ == "__main__":
    for name, code in SNIPPETS.items():
        size, line = SIZES[name]
        render(code, name, size, line)
