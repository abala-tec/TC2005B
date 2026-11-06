"""Fragmentos de código que se muestran como imagen y se copian en las notas.

Salen de S5_VelmaWalk_3D.cs y S5_VelmaWalk_2D.cs. Solo se acortan algunos
comentarios y se parten líneas largas para que la imagen se lea bien.
"""

# nombre: (código, tamaño de letra, alto de línea)
SNIPPETS = {
    "code_vars_nuevas": ("""public float maxFallSpeed = 15f;        // $40 = 4 px/frame
public float maxHorizontalSpeed = 15f;  // $40 = 4 px/frame

private Rigidbody rb;
private Vector2 horizontal;  // antes: private float vx;
private float vy;""", 34, 50),

    "code_start_3d": ("""void Start()
{
    rb = GetComponent<Rigidbody>();
    sprite_render = GetComponent<SpriteRenderer>();

    rb.useGravity = false;
    rb.interpolation = RigidbodyInterpolation.Interpolate;
    rb.collisionDetectionMode =
        CollisionDetectionMode.Continuous;
    rb.constraints = RigidbodyConstraints.FreezeRotation;
}""", 32, 46),

    "code_constraints": ("""// 2D: congela rotación y la posición en Z
rb.constraints = RigidbodyConstraints.FreezeRotationX
               | RigidbodyConstraints.FreezeRotationY
               | RigidbodyConstraints.FreezeRotationZ
               | RigidbodyConstraints.FreezePositionZ;

// 3D: solo congela la rotación
rb.constraints = RigidbodyConstraints.FreezeRotation;""", 30, 44),

    "code_input_x": ("""void Update()
{
    Keyboard kb = Keyboard.current;
    if (kb == null) return;

    float inputX = 0f;  // derecha e izquierda
    if (kb.dKey.isPressed || kb.rightArrowKey.isPressed)
    {
        inputX += 1f;
        if (sprite_render != null) { sprite_render.flipX = false; }
    }
    if (kb.aKey.isPressed || kb.leftArrowKey.isPressed)
    {
        inputX -= 1f;
        if (sprite_render != null) { sprite_render.flipX = true; }
    }""", 28, 40),

    "code_input_z": ("""float inputZ = 0f;  // arriba y abajo (profundidad Z)
if (kb.wKey.isPressed || kb.upArrowKey.isPressed) inputZ += 1f;
if (kb.sKey.isPressed || kb.downArrowKey.isPressed) inputZ -= 1f;

// Vector con los 2 inputs
Vector2 input = new Vector2(inputX, inputZ);

// Si el vector es mayor a 1, normalízalo.
if (input.sqrMagnitude > 1f) input.Normalize();""", 28, 40),

    "code_banderas": ("""bool runHeld = kb.leftShiftKey.isPressed
            || kb.xKey.isPressed;

bool jumpPressed = kb.spaceKey.wasPressedThisFrame
                || kb.zKey.wasPressedThisFrame;

bool jumpHeld = kb.spaceKey.isPressed
             || kb.zKey.isPressed;""", 36, 52),

    "code_suelo_top": ("""// El suelo se detecta con OnCollisionEnter/Stay/Exit
if (grounded && vy <= 0f) vy = 0f;

// Si presiona run: topSpeed = runSpeed
// Si no:           topSpeed = walkSpeed  (en X y Z)
float topSpeed = runHeld ? runSpeed : walkSpeed;""", 34, 48),

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

    "code_horizontal_3d": ("""if (input != Vector2.zero)
{
    Vector2 target = input * topSpeed;

    bool sameDirection = horizontal.sqrMagnitude > 0.01f &&
        Vector2.Dot(horizontal.normalized, input) > 0.1f;

    if (sameDirection && horizontal.magnitude > topSpeed)
    {
        if (grounded)   // en el suelo frena
            horizontal = Vector2.MoveTowards(horizontal,
                target, braking * Time.deltaTime);
        // en el aire conserva el momento
    }
    else                // contraria o más lenta: acelera
    {
        horizontal = Vector2.MoveTowards(horizontal,
            target, acceleration * Time.deltaTime);
    }
}""", 28, 40),

    "code_target_same": ("""Vector2 target = input * topSpeed;

bool sameDirection = horizontal.sqrMagnitude > 0.01f &&
    Vector2.Dot(horizontal.normalized, input) > 0.1f;""", 34, 50),

    "code_sin_tecla_3d": ("""else if (grounded)
{
    // Sin input y en el suelo: frena hasta 0
    horizontal = Vector2.MoveTowards(horizontal,
        Vector2.zero, braking * Time.deltaTime);
}""", 34, 50),

    "code_tope": ("""if (horizontal.magnitude > maxHorizontalSpeed)
    horizontal = horizontal.normalized * maxHorizontalSpeed;""", 34, 50),

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

    "code_aplicar_3d": ("""rb.linearVelocity =
    new Vector3(horizontal.x, vy, horizontal.y);""", 38, 56),

    "code_reset_3d": ("""public void ResetButtonClick()
{
    rb.constraints = RigidbodyConstraints.FreezeAll;
    rb.rotation = Quaternion.identity;
    rb.position = new Vector3(0.0f, 1.0f, 0.0f);
    rb.constraints = RigidbodyConstraints.FreezeRotation;
}""", 34, 50),

    "code_usings": ("""using UnityEngine;
using UnityEngine.InputSystem;
using TMPro;
using UnityEditor.U2D;   // solo existe dentro del Editor""", 34, 50),
}
