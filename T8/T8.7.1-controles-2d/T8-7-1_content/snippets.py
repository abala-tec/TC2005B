"""Fragmentos de código que se muestran como imagen y se copian en las notas.

Salen de S5_VelmaWalk_2D.cs y S5_CubeMove.cs. Solo se acortan algunos
comentarios y se parten líneas largas para que la imagen se lea bien.
"""

# nombre: (código, tamaño de letra, alto de línea)
SNIPPETS = {
    "code_cubemove": ("""// S5_CubeMove: el control simple
if (keyboard.dKey.isPressed ||
    keyboard.rightArrowKey.isPressed) {
    movement.x = 1f;
}
if (keyboard.aKey.isPressed ||
    keyboard.leftArrowKey.isPressed) {
    movement.x = -1f;
}

if (keyboard.spaceKey.wasPressedThisFrame
    && estaEnSuelo == true)
{
    rb.AddForce(Vector3.up * jumpForce,
                ForceMode.Impulse);
    estaEnSuelo = false;
}

transform.Translate(movement * speed * Time.deltaTime,
                    Space.World);""", 34, 48),

    "code_vars_velocidad": ("""[Header("Velocidades SMB3 (1 unidad = 1 tile)")]
public float walkSpeed = 5.625f;          // $18 = 1.5 px/frame
public float runSpeed = 9.375f;           // $28 = 2.5 px/frame
public float acceleration = 12.3046875f;  // 0.0546875 px/frame²
public float braking = 12.3046875f;       // rate de frenado""", 30, 44),

    "code_vars_salto": ("""[Header("Salto y gravedad")]
public float jumpSpeed = 13.125f;     // $38 = 3.5 px/frame
public float gravity = 70.3125f;      // 5/16 px/frame²
public float jumpGravity = 14.0625f;  // 1/16 px/frame²
public float jumpHoldLimit = 7.5f;    // $20 = 2 px/frame
public float maxFallSpeed = 15f;      // $40 = 4 px/frame""", 30, 44),

    "code_vars_privadas": ("""private Rigidbody rb;
private float vx;
private float vy;
private bool grounded;
private bool cayendo;
private SpriteRenderer sprite_render = null;""", 38, 54),

    "code_start": ("""void Start()
{
    rb = GetComponent<Rigidbody>();
    sprite_render = GetComponent<SpriteRenderer>();

    rb.useGravity = false;
    rb.interpolation = RigidbodyInterpolation.Interpolate;
    rb.collisionDetectionMode =
        CollisionDetectionMode.Continuous;
    rb.constraints = RigidbodyConstraints.FreezeRotationX
                   | RigidbodyConstraints.FreezeRotationY
                   | RigidbodyConstraints.FreezeRotationZ
                   | RigidbodyConstraints.FreezePositionZ;
}""", 32, 46),

    "code_update_teclado": ("""void Update()
{
    Keyboard kb = Keyboard.current;
    if (kb == null) return;

    float input = 0f;
    if (kb.dKey.isPressed || kb.rightArrowKey.isPressed)
    {
        input += 1f;
        if (sprite_render != null) { sprite_render.flipX = false; }
    }
    if (kb.aKey.isPressed || kb.leftArrowKey.isPressed)
    {
        input -= 1f;
        if (sprite_render != null) { sprite_render.flipX = true; }
    }""", 28, 40),

    "code_banderas": ("""bool runHeld = kb.leftShiftKey.isPressed
            || kb.xKey.isPressed;

bool jumpPressed = kb.spaceKey.wasPressedThisFrame
                || kb.zKey.wasPressedThisFrame;

bool jumpHeld = kb.spaceKey.isPressed
             || kb.zKey.isPressed;""", 36, 52),

    "code_suelo_top": ("""// El suelo se detecta con OnCollisionEnter/Stay/Exit
if (grounded && vy <= 0f) vy = 0f;

// Si presiona run: topSpeed = runSpeed
// Si no:           topSpeed = walkSpeed
float topSpeed = runHeld ? runSpeed : walkSpeed;""", 34, 48),

    "code_horizontal": ("""if (input != 0f)
{
    float target = input * topSpeed;

    if (Mathf.Sign(vx) == Mathf.Sign(input)
        && Mathf.Abs(vx) > topSpeed)
    {
        if (grounded)   // en el suelo frena
            vx = Mathf.MoveTowards(vx, target,
                                   braking * Time.deltaTime);
        // en el aire conserva el momento
    }
    else                // contraria o más lenta: acelera
    {
        vx = Mathf.MoveTowards(vx, target,
                               acceleration * Time.deltaTime);
    }
}""", 32, 46),

    "code_sin_tecla": ("""else if (grounded)
{
    // Sin input y en el suelo: frena hasta 0
    vx = Mathf.MoveTowards(vx, 0f,
                           braking * Time.deltaTime);
}""", 34, 50),

    "code_salto_inicio": ("""// Inicio del salto: siempre empieza en el suelo
if (jumpPressed && grounded)
{
    vy = jumpSpeed;    // velocidad del salto
    grounded = false;  // ya no está en el suelo
}""", 36, 52),

    "code_gravedad": ("""// Gravedad (cuando no está en el suelo)
if (!grounded)
{
    // true si mantiene el botón y va subiendo rápido
    bool lightGravity = jumpHeld && vy > jumpHoldLimit;

    // vy = vy - (G * delta de tiempo)
    vy -= (lightGravity ? jumpGravity : gravity)
          * Time.deltaTime;

    // tope de la velocidad de caída
    vy = Mathf.Max(vy, -maxFallSpeed);
}""", 32, 46),

    "code_aplicar": ("""rb.linearVelocity = new Vector3(vx, vy, 0f);""", 38, 54),

    "code_colision": ("""void OnCollisionEnter(Collision collision)
{
    CheckGround(collision);
}

void OnCollisionStay(Collision collision)
{
    CheckGround(collision);
}

void OnCollisionExit(Collision collision)
{
    grounded = false;
}""", 36, 50),

    "code_checkground": ("""void CheckGround(Collision collision)
{
    // si sube o salta, no cuenta como suelo
    if (vy > 0f) return;

    foreach (ContactPoint contact in collision.contacts)
    {
        if (contact.normal.y > 0.5f) // contacto desde abajo
        {
            grounded = true;
            return;
        }
    }
}""", 32, 46),

    "code_reset": ("""public void ResetButtonClick()
{
    rb.constraints = RigidbodyConstraints.FreezeAll;
    rb.rotation = Quaternion.identity;
    rb.position = new Vector3(0.0f, 1.0f, 0.0f);
    rb.constraints = RigidbodyConstraints.FreezeRotationX
                   | RigidbodyConstraints.FreezeRotationY
                   | RigidbodyConstraints.FreezeRotationZ
                   | RigidbodyConstraints.FreezePositionZ;
}""", 30, 44),
}
