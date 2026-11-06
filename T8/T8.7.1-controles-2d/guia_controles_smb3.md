# Controles de Super Mario Bros. 3 en Unity

Guía paso a paso para construir la escena, copiar el código y entender por qué se siente como SMB3.

> **Entregable:** esta guía y el script `S6_MarioMove.cs` que copiarás dentro de Unity.
> **No modifica el proyecto:** tú creas la escena y el script siguiendo los pasos.

---

## 0. Resultado final

Al terminar tendrás:

- Una escena 3D con vista lateral, como la escena 5.
- Un cubo que camina, corre y salta.
- Salto variable: si mantienes el botón, sube más.
- La misma curva de aceleración, frenado y gravedad de SMB3.
- Una explicación de cada número para que puedas enseñarla.

**Tiempo estimado:** 2 horas para aprenderla y probarla. En clase: 3 horas con retos.

**Ruta recomendada:**

1. Lee las secciones 1, 2 y 3 (20 min).
2. Arma la escena (30 min).
3. Copia el script y prueba (20 min).
4. Ajusta valores y entiende cada línea (30 min).
5. Prepara la clase con la sección 8 (20 min).

### Resumen en 5 pasos

1. `Rigidbody` sin gravedad.
2. Leer izquierda/derecha, correr y salto.
3. Acelerar la velocidad horizontal hacia `5.625` (caminar) o `9.375` (correr).
4. Si salta y está en el suelo, poner `vy = 13.125`.
5. Aplicar gravedad `70.3125`, o `14.0625` si mantiene el salto y sube rápido.

Eso es todo. El resto de la guía explica de dónde salen esos números y cómo montarlo.

---

## 1. El código original de SMB3

### 1.1 Qué encontré

El código fuente original no es público. Lo que existe es un **desensamblado**: un proyecto que traduce la ROM a ensamblador legible y la reconstruye byte por byte.

Repositorio principal:

- https://github.com/captainsouthbird/smb3

Es el trabajo de Captain Southbird. Reensambla con NESASM y produce una ROM idéntica a *Super Mario Bros. 3 (U) (PRG1)*.

Versión más fácil de leer para clase:

- https://github.com/velipso/smb3-physics

Ese proyecto convierte la lógica de movimiento a JavaScript legible. No es el original, pero sirve para comparar.

### 1.2 Archivos que importan

| Qué | Archivo | Líneas |
|---|---|---|
| Constantes de velocidad | `smb3.asm` | 3559–3568 |
| Tabla de aceleración | `PRG/prg008.asm` | 1141–1159 |
| Fracción de aceleración | `PRG/prg008.asm` | 1167–1178 |
| Velocidad inicial del salto | `PRG/prg008.asm` | 1198–1204 |
| Selección de velocidad máxima | `PRG/prg008.asm` | 2346–2377 |
| Aceleración, frenado y derrape | `PRG/prg008.asm` | 2413–2497 |
| Salto y gravedad | `PRG/prg008.asm` | 2548–2670 |
| Límite de caída | `PRG/prg008.asm` | 6936–6956 |
| `FALLRATE_MAX` | `PRG/prg024.asm` | 21 |

Enlaces directos:

- https://github.com/captainsouthbird/smb3/blob/master/smb3.asm
- https://github.com/captainsouthbird/smb3/blob/master/PRG/prg008.asm
- https://github.com/captainsouthbird/smb3/blob/master/PRG/prg024.asm

### 1.3 Cómo leer los números de SMB3

SMB3 guarda las velocidades en **4.4 fixed point**:

- Los 4 bits altos son píxeles por frame.
- Los 4 bits bajos son dieciseisavos de píxel.

Entonces:

| Valor | Lectura | píxeles/frame |
|---|---|---:|
| `$18` | 24/16 | 1.5 |
| `$28` | 40/16 | 2.5 |
| `$38` | 56/16 | 3.5 |
| `$40` | 64/16 | 4.0 |
| `-$38` | -56/16 | -3.5 |

No necesitas aprender 6502. Solo necesitas estos valores y saber que el juego corre a **60 frames por segundo**.

### 1.4 Lo que dice el código original

**Velocidades máximas** (`smb3.asm`):

```asm
PLAYER_TOPWALKSPEED  = $18   ; caminar: 1.5 px/frame
PLAYER_TOPRUNSPEED   = $28   ; correr con B: 2.5 px/frame
PLAYER_TOPPOWERSPEED = $38   ; medidor P lleno: 3.5 px/frame
PLAYER_MAXSPEED      = $40   ; tope absoluto: 4.0 px/frame
PLAYER_JUMP          = -$38  ; salto base: -3.5 px/frame
```

**Aceleración** (`PRG/prg008.asm`):

```asm
; F = fricción, N = normal, S = derrape
; Sin B                Con B
;  F   N   S   X        F   N   S   X
.byte -1,  0,  2,  0,  -1,  0,  2,  0   ; Small
.byte -1,  0,  2,  0,  -1,  0,  2,  0   ; Big
```

El valor normal es `0`, pero el juego suma una fracción de `1/16` en 14 de cada 16 frames. Por eso la aceleración real es:

```text
14/16 × 1/16 = 0.0546875 px/frame²
```

El original acumula esa fracción con un contador (`Counter_Wiggly`). Nosotros la convertimos en una aceleración constante: el resultado se siente igual y es mucho más fácil de leer.

**Salto** (`PRG/prg008.asm`):

```asm
Player_RootJumpVel:  .byte PLAYER_JUMP
Player_SpeedJumpInc: .byte $00, $02, $04, $08
```

El salto base es `-$38`. Si Mario corre, se le resta hasta `$08/16 = 0.5 px/frame` extra. Por eso un salto corriendo llega hasta `-$40`.

**Gravedad** (`PRG/prg008.asm`):

```asm
LDY #$05              ; gravedad normal: 5/16 px/frame²
LDA <Player_YVel
CMP #-$20             ; ¿sube más rápido que 2 px/frame?
BGS ...               ; si no, usa 5/16
LDA <Pad_Holding
BPL ...               ; si no mantiene A, usa 5/16
LDY #$01              ; si mantiene A y sube rápido: 1/16
...
TYA
ADD <Player_YVel      ; Player_YVel += gravedad
```

**Caída máxima** (`PRG/prg024.asm`):

```asm
FALLRATE_MAX = $40    ; 4.0 px/frame
```

---

## 2. Los números que importan

| Concepto | Constante | px/frame | Nota |
|---|---|---:|---|
| Caminar | `$18` | 1.5 | Velocidad máxima sin B |
| Correr | `$28` | 2.5 | Velocidad máxima con B |
| Medidor P lleno | `$38` | 3.5 | Solo con B y medidor lleno |
| Tope absoluto | `$40` | 4.0 | Nunca se supera |
| Salto base | `-$38` | -3.5 | Impulso inicial |
| Bonus de salto | `$00`–`$08` | 0–0.5 | Depende de la velocidad horizontal |
| Gravedad normal | `5/16` | 0.3125 | Bajando o sin A |
| Gravedad con A | `1/16` | 0.0625 | Subiendo y manteniendo A |
| Límite de caída | `$40` | 4.0 | Velocidad máxima bajando |
| Aceleración | `14/16 × 1/16` | 0.0546875 | Aproximación didáctica |
| Frenado | `14/16 × 1/16` | 0.0546875 | Valor de Mario grande |
| Derrape | `2/16` | 0.125 | Giro brusco, opcional |

**Regla de oro:** el salto no cambia el impulso si mantienes A. Lo que cambia es la **gravedad** mientras subes. Eso es lo que hace el salto variable de SMB3.

---

## 3. Conversión a Unity

### 3.1 Escala

Usaremos:

```text
1 unidad de Unity = 1 tile = 16 píxeles
```

Así el cubo mide 1 unidad y los números se leen como tiles.

Si usas un sprite de 16×16 píxeles, configura **Pixels Per Unit = 16**. Si usas un cubo, no hace falta.

### 3.2 Fórmulas

SMB3 corre a 60 fps. Unity usa segundos.

```text
velocidad Unity  = px/frame   × 60 / 16
aceleración Unity = px/frame² × 3600 / 16
```

Simplificado:

```text
velocidad Unity  = px/frame   × 3.75
aceleración Unity = px/frame² × 225
```

### 3.3 Tabla convertida

| Concepto | px/frame o px/frame² | Unity |
|---|---:|---:|
| Caminar | 1.5 px/frame | 5.625 u/s |
| Correr | 2.5 px/frame | 9.375 u/s |
| Medidor P lleno | 3.5 px/frame | 13.125 u/s |
| Tope horizontal | 4.0 px/frame | 15 u/s |
| Salto base | 3.5 px/frame | 13.125 u/s |
| Bonus de salto máximo | 0.5 px/frame | 1.875 u/s |
| Gravedad normal | 0.3125 px/frame² | 70.3125 u/s² |
| Gravedad con A | 0.0625 px/frame² | 14.0625 u/s² |
| Límite de caída | 4.0 px/frame | 15 u/s |
| Aceleración / frenado | 0.0546875 px/frame² | 12.3046875 u/s² |
| Derrape | 0.125 px/frame² | 28.125 u/s² |
| Umbral para gravedad ligera | 2.0 px/frame | 7.5 u/s |

No redondees si quieres fidelidad. Si redondeas, usa 12.3, 70.3 y 14.1; la diferencia es mínima.

---

## 4. Montar la escena en Unity

### 4.1 Requisitos

- Unity 6.3 o superior. El proyecto usa `6000.3.26f1`.
- Paquete **Input System** instalado.
- `Active Input Handling` en **Input System Package (New)** o **Both**.

Revisa:

```text
Edit > Project Settings > Player > Active Input Handling
```

### 4.2 Crear la escena

1. Abre el proyecto `T8/Unity_Sample/Sample_Game`.
2. `File > New Scene`.
3. Elige **Basic** o **Empty**.
4. Guarda como `Assets/Scenes/escena6_mario3.unity`.

Si elegiste **Empty**, agrega `GameObject > Light > Directional Light` para que los cubos no se vean negros.

### 4.3 Crear el suelo

1. `GameObject > 3D Object > Cube`.
2. Nómbralo `Suelo`.
3. En el Inspector:
   - Position: `(0, -0.5, 0)`
   - Scale: `(30, 1, 6)`
4. El cubo tiene su `BoxCollider` automático.
5. La superficie superior queda en `y = 0`.

Si prefieres usar el `Plane` de la escena 5, también funciona: el script no depende del tipo de collider, solo de la normal del contacto.

### 4.4 Crear el jugador

1. `GameObject > 3D Object > Cube`.
2. Nómbralo `Mario`.
3. Transform:
   - Position: `(0, 0.5, 0)`
   - Scale: `(1, 1, 1)`
4. El cubo tiene su `BoxCollider` automático.

### 4.5 Agregar el Rigidbody

Con `Mario` seleccionado:

1. `Add Component > Rigidbody`.
2. Configura:

| Propiedad | Valor |
|---|---|
| Mass | 1 |
| Drag | 0 |
| Angular Drag | 0.05 |
| Use Gravity | **desactivado** |
| Is Kinematic | desactivado |
| Interpolate | Interpolate |
| Collision Detection | Continuous |
| Constraints | Freeze Rotation X, Freeze Rotation Z, Freeze Position Z |

`Use Gravity` se desactiva porque el script aplica la gravedad de SMB3. Si la dejas activa, tendrás dos gravedades y el salto se sentirá mal.

**Material sin fricción (importante):**

1. En `Assets`, clic derecho > `Create > Physics > Physics Material` (en versiones anteriores aparece como `Create > Physic Material`).
2. Nómbralo `SinFriccion`.
3. Configura:
   - Dynamic Friction: `0`
   - Static Friction: `0`
   - Bounciness: `0`
   - Friction Combine: `Minimum`
4. En `Mario`, abre el `BoxCollider` y asigna `SinFriccion` en `Material`.

Sin esto, el cubo puede pegarse a las paredes o frenarse solo al rozar el suelo.

### 4.6 Configurar la cámara

1. Selecciona `Main Camera`.
2. Transform:
   - Position: `(0, 4, -16)`
   - Rotation: `(10, 0, 0)`
3. Field of View: `60`.

Es una cámara fija lateral para ver bien el salto. Si quieres que siga al jugador, al final tienes el reto de cámara lateral.

### 4.7 Crear plataformas de prueba

Crea dos cubos más:

| Nombre | Position | Scale |
|---|---|---|
| `Plataforma1` | `(8, 1.5, 0)` | `(3, 1, 3)` |
| `Plataforma2` | `(13, 2.5, 0)` | `(2, 1, 3)` |

La plataforma 1 tiene su superficie en `y = 2`. La plataforma 2 en `y = 3`.

También puedes agregar una pared al final, pero no es necesaria.

### 4.8 Crear el script

1. En `Assets`, crea la carpeta `Scripts/escena6_mario3`.
2. Clic derecho > `Create > C# Script`.
3. Nómbralo `S6_MarioMove`.
4. Abre el archivo y reemplaza todo con el código de la sección 5.
5. Guarda y vuelve a Unity.

### 4.9 Conectar el script

1. Selecciona `Mario`.
2. `Add Component > S6_MarioMove`.
3. Verifica que los valores de velocidad y gravedad estén como en el código.
4. No hay campos de suelo que asignar: el script usa las colisiones del cubo.

### 4.10 Guardar y probar

1. Guarda la escena.
2. Presiona **Play**.
3. Prueba:
   - `A` / `D` o flechas: mover.
   - `Shift` o `X`: correr.
   - `Espacio` o `Z`: saltar.
   - Mantén el salto: sube más.

Si el cubo no responde, revisa la sección 9.

---

## 5. El script completo

Crea `S6_MarioMove.cs` con este contenido:

```csharp
using UnityEngine;
using UnityEngine.InputSystem;

public class S6_MarioMove : MonoBehaviour
{
    [Header("Velocidades SMB3 (1 unidad = 1 tile)")]
    public float walkSpeed = 5.625f;          // $18 = 1.5 px/frame
    public float runSpeed = 9.375f;           // $28 = 2.5 px/frame
    public float acceleration = 12.3046875f;  // 0.0546875 px/frame²
    public float braking = 12.3046875f;       // frenado al soltar

    [Header("Salto y gravedad")]
    public float jumpSpeed = 13.125f;         // $38 = 3.5 px/frame
    public float gravity = 70.3125f;          // 5/16 px/frame²
    public float jumpGravity = 14.0625f;      // 1/16 px/frame²
    public float jumpHoldLimit = 7.5f;        // $20 = 2 px/frame
    public float maxFallSpeed = 15f;          // $40 = 4 px/frame

    private Rigidbody rb;
    private float vx;
    private float vy;
    private bool grounded;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
        rb.useGravity = false;                // la gravedad la pone este script
        rb.constraints = RigidbodyConstraints.FreezeRotationX
                       | RigidbodyConstraints.FreezeRotationZ
                       | RigidbodyConstraints.FreezePositionZ;
    }

    void Update()
    {
        Keyboard kb = Keyboard.current;
        if (kb == null) return;

        // 1. Leer entrada
        float input = 0f;
        if (kb.dKey.isPressed || kb.rightArrowKey.isPressed) input += 1f;
        if (kb.aKey.isPressed || kb.leftArrowKey.isPressed) input -= 1f;

        bool runHeld = kb.leftShiftKey.isPressed || kb.xKey.isPressed;
        bool jumpPressed = kb.spaceKey.wasPressedThisFrame || kb.zKey.wasPressedThisFrame;
        bool jumpHeld = kb.spaceKey.isPressed || kb.zKey.isPressed;

        // 2. El suelo se detecta con OnCollisionEnter/Stay/Exit
        if (grounded && vy <= 0f) vy = 0f;

        // 3. Movimiento horizontal
        float topSpeed = runHeld ? runSpeed : walkSpeed;

        if (input != 0f)
        {
            float target = input * topSpeed;

            // Si va en la misma dirección pero más rápido que la meta...
            if (Mathf.Sign(vx) == Mathf.Sign(input) && Mathf.Abs(vx) > topSpeed)
            {
                // ...en el suelo frena; en el aire conserva el momento.
                if (grounded)
                    vx = Mathf.MoveTowards(vx, target, braking * Time.deltaTime);
            }
            else
            {
                vx = Mathf.MoveTowards(vx, target, acceleration * Time.deltaTime);
            }
        }
        else if (grounded)
        {
            // Sin input en el suelo: frena. En el aire conserva la velocidad.
            vx = Mathf.MoveTowards(vx, 0f, braking * Time.deltaTime);
        }

        // 4. Salto: solo al presionar, no al mantener
        if (jumpPressed && grounded)
        {
            vy = jumpSpeed;
            grounded = false;
        }

        // 5. Gravedad
        if (!grounded)
        {
            // Si sube rápido y mantiene el salto, gravedad ligera.
            bool lightGravity = jumpHeld && vy > jumpHoldLimit;
            vy -= (lightGravity ? jumpGravity : gravity) * Time.deltaTime;
            vy = Mathf.Max(vy, -maxFallSpeed);
        }

        // 6. Aplicar la velocidad al Rigidbody
        rb.linearVelocity = new Vector3(vx, vy, 0f);
    }

    void OnCollisionEnter(Collision collision)
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
    }

    void CheckGround(Collision collision)
    {
        if (vy > 0f) return; // subiendo: no cuenta como suelo

        foreach (ContactPoint contact in collision.contacts)
        {
            if (contact.normal.y > 0.5f)
            {
                grounded = true;
                return;
            }
        }
    }
}
```

### Nota para Unity anterior a 6

En Unity 6 el API es `rb.linearVelocity`. En versiones anteriores se llama `rb.velocity`. Este proyecto usa Unity 6.3, así que deja `linearVelocity`.

### Nota sobre el Input System

El código usa `Keyboard.current` porque el proyecto ya usa el Input System nuevo. Si tu proyecto usa el Input Manager viejo, cambia la lectura por `Input.GetAxisRaw("Horizontal")`, `Input.GetButtonDown("Jump")` y `Input.GetButton("Fire3")`, o activa **Both** en Project Settings.

---

## 6. Cómo funciona, línea por línea

### 6.1 Leer la entrada

```csharp
float input = 0f;
if (kb.dKey.isPressed || kb.rightArrowKey.isPressed) input += 1f;
if (kb.aKey.isPressed || kb.leftArrowKey.isPressed) input -= 1f;
```

`input` vale:

- `1` si va a la derecha,
- `-1` si va a la izquierda,
- `0` si no presiona nada.

`jumpPressed` usa `wasPressedThisFrame`: solo es verdadero el frame en que presionas. `jumpHeld` usa `isPressed`: es verdadero mientras mantienes.

Esa diferencia es la que permite el salto variable.

### 6.2 Detectar el suelo con colisiones

```csharp
void OnCollisionEnter(Collision collision) { CheckGround(collision); }
void OnCollisionStay(Collision collision)  { CheckGround(collision); }
void OnCollisionExit(Collision collision)  { grounded = false; }

void CheckGround(Collision collision)
{
    if (vy > 0f) return; // subiendo: no cuenta como suelo

    foreach (ContactPoint contact in collision.contacts)
    {
        if (contact.normal.y > 0.5f)
        {
            grounded = true;
            return;
        }
    }
}
```

Unity llama estos métodos automáticamente cuando el `BoxCollider` de Mario toca otro collider:

- `OnCollisionEnter`: empieza el contacto.
- `OnCollisionStay`: sigue el contacto, frame a frame.
- `OnCollisionExit`: termina el contacto.

Cada contacto tiene una **normal**: el vector perpendicular a la superficie. Si `normal.y > 0.5`, la superficie empuja hacia arriba. Eso es suelo.

Así una pared no cuenta como suelo: su normal apunta hacia los lados (`y ≈ 0`).

El `if (vy > 0f) return;` evita que el contacto que todavía existe en el frame del salto vuelva a poner `grounded = true`. Si estás subiendo, no hay suelo.

Ventaja: no necesitas capa, ni tag, ni hijo `Pies`, ni `Physics.CheckSphere`. El mismo collider del cubo hace el trabajo.

`OnCollisionStay` mantiene la bandera en `true` mientras sigue tocando. `OnCollisionExit` la limpia al saltar o al salir de la plataforma.

Limitación: si el cubo toca dos superficies a la vez y sale de una, `OnCollisionExit` pone `grounded = false`; el siguiente `OnCollisionStay` de la otra lo vuelve a poner en `true`. Puede haber un frame de falsa caída. En este laboratorio no se nota.

### 6.3 Movimiento horizontal

```csharp
float topSpeed = runHeld ? runSpeed : walkSpeed;
```

Sin B, la meta es `5.625`. Con B, `9.375`.

```csharp
vx = Mathf.MoveTowards(vx, target, acceleration * Time.deltaTime);
```

`MoveTowards` cambia `vx` como máximo `acceleration * dt` por frame. Eso es una aceleración constante.

No es un `AddForce`. Es cambiar la velocidad directamente, que es lo que hace SMB3: su velocidad horizontal se acerca a la meta en pasos de `1/16`.

### 6.4 El detalle del aire

```csharp
else if (grounded)
{
    vx = Mathf.MoveTowards(vx, 0f, braking * Time.deltaTime);
}
```

Si no presionas nada:

- En el suelo, Mario frena.
- En el aire, conserva su velocidad.

Ese detalle es clave en SMB3. Una vez que saltas, no puedes frenar en seco en el aire. Por eso los saltos se sienten comprometidos.

### 6.5 Salto

```csharp
if (jumpPressed && grounded)
{
    vy = jumpSpeed;
    grounded = false;
}
```

El salto no es una fuerza. Es un cambio instantáneo de velocidad: `vy = 13.125`.

Solo ocurre si:

- presionaste este frame, y
- estás en el suelo.

Si mantienes el botón, no vuelve a saltar. Solo cambia la gravedad.

### 6.6 Gravedad variable

```csharp
bool lightGravity = jumpHeld && vy > jumpHoldLimit;
vy -= (lightGravity ? jumpGravity : gravity) * Time.deltaTime;
```

En Unity, arriba es positivo. La gravedad resta.

- Si `vy > 7.5` y mantienes el salto: gravedad ligera `14.0625`.
- Si no: gravedad normal `70.3125`.

`7.5` es la conversión de `-$20` (2 px/frame). Es el punto donde SMB3 deja de aplicar gravedad ligera.

Por eso:

- Salto corto: sueltas pronto, gravedad normal, sube poco.
- Salto largo: mantienes, gravedad ligera, sube unos 4.5 tiles.

### 6.7 Límite de caída

```csharp
vy = Mathf.Max(vy, -maxFallSpeed);
```

Evita que Mario caiga más rápido que `4 px/frame`. Sin esto, la gravedad acumulada lo haría caer como una piedra.

### 6.8 Aplicar la velocidad

```csharp
rb.linearVelocity = new Vector3(vx, vy, 0f);
```

Se escribe la velocidad final en el `Rigidbody`. El motor de física se encarga de mover y resolver colisiones.

No uses `transform.Translate` para esto: atravesaría paredes. `linearVelocity` respeta colliders.

**Nota técnica:** este script usa `Update` y `Time.deltaTime` para que sea fácil de leer. En un juego más grande, la física se mueve a `FixedUpdate`. Si lo haces, guarda el salto en una bandera durante `Update` y consúmela en `FixedUpdate`, porque `wasPressedThisFrame` se puede perder entre pasos de física.

### 6.9 ¿Por qué no usar AddForce?

`AddForce` depende de la masa, del drag y del paso de física. Para replicar una curva exacta es más difícil.

SMB3 no usa fuerzas: escribe velocidades. Nosotros hacemos lo mismo.

### 6.10 ¿Por qué desactivar Use Gravity?

La gravedad de Unity es `-9.81`. La de SMB3, en nuestra escala, es `-70.3125`. Si dejas las dos, el cubo cae siete veces más rápido.

El script controla toda la gravedad vertical.

---

## 7. Probar y ajustar

### 7.1 Lista de pruebas

Marca cada una:

- [ ] `D` mueve a la derecha.
- [ ] `A` mueve a la izquierda.
- [ ] `Shift + D` llega más rápido y a más velocidad.
- [ ] Al soltar, frena en el suelo.
- [ ] En el aire, al soltar, conserva la velocidad.
- [ ] `Espacio` salta solo una vez.
- [ ] Mantener `Espacio` sube más que un toque.
- [ ] Cae más rápido de lo que sube.
- [ ] No atraviesa el suelo.
- [ ] No atraviesa las plataformas.
- [ ] No gira ni se mueve en Z.

### 7.2 Valores esperados

Con los valores del script:

| Prueba | Resultado aproximado |
|---|---|
| Llegar a velocidad de caminar | 0.46 s |
| Llegar a velocidad de correr | 0.76 s |
| Altura de salto mantenido | 4.5 unidades (≈72 px) |
| Altura de salto tocado | 1.2 unidades (≈20 px) |
| Tiempo de salto mantenido | 0.87 s |
| Caída máxima | 15 u/s |

Son aproximaciones. Lo importante es la sensación: salto corto seco, salto largo flotante, carrera con inercia.

### 7.3 Cómo ajustar

| Si quieres... | Cambia... |
|---|---|
| Que acelere más rápido | sube `acceleration` |
| Que se sienta más resbaloso | baja `braking` |
| Que el salto sea más alto | sube `jumpSpeed` |
| Que el salto sea más flotante | baja `gravity` o `jumpGravity` |
| Que caiga más rápido | sube `gravity` |
| Que el salto corto sea más corto | sube `jumpGravity` |
| Que el salto máximo dure más | baja `jumpGravity` |
| Que la caída tenga tope más alto | sube `maxFallSpeed` |

Haz un cambio a la vez y vuelve a probar. Anota el valor y lo que sentiste.

---

## 8. Guion para clase

### 8.1 Tres ideas para explicar

**Idea 1: velocidad no es posición.**

La posición es dónde está. La velocidad es cuánto cambia la posición por segundo. Si `vx = 5.625`, el cubo avanza 5.625 unidades cada segundo.

**Idea 2: aceleración es el cambio de velocidad.**

SMB3 no pasa de 0 a 2.5 de golpe. La velocidad sube poco a poco. Esa razón de cambio es la aceleración. En el código, `MoveTowards` la aplica.

**Idea 3: el salto es velocidad, la gravedad es aceleración.**

Saltar es poner `vy = 13.125` de golpe. La gravedad le resta velocidad cada frame. Mantener A no cambia el impulso: cambia la gravedad mientras sube.

### 8.2 Tres preguntas para el grupo

1. ¿Por qué Mario se siente pesado al arrancar pero ligero cuando ya corre?
2. ¿Por qué un salto corto y uno largo no tienen la misma altura?
3. ¿Qué cambiarías para que se sienta como Sonic? ¿Y como un juego de hielo?

### 8.3 Demostraciones rápidas

Hazlas en vivo, con el Inspector abierto:

| Cambio | Efecto | Idea |
|---|---|---|
| `acceleration = 100` | Arranca casi instantáneo | La aceleración define el peso |
| `gravity = 20` | Salto lunar | La gravedad define la caída |
| `jumpSpeed = 20` | Salto enorme | El impulso define la altura |
| `useGravity = true` | Cae muchísimo más rápido | No dupliques gravedad |
| `walkSpeed = 15` | Todo es vértigo | La escala importa |

### 8.4 Distribución de 3 horas

| Tiempo | Actividad |
|---|---|
| 15 min | Mostrar el desensamblado y la tabla de valores |
| 20 min | Explicar velocidad, aceleración y gravedad |
| 40 min | Armar la escena paso a paso |
| 30 min | Copiar el script y hacer que funcione |
| 25 min | Probar, medir y ajustar valores |
| 30 min | Retos: derrape, medidor P, bonus de salto |
| 20 min | Compartir resultados y comparar con SMB3 |

---

## 9. Errores comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| No se mueve | Input System desactivado | Project Settings > Player > Active Input Handling |
| No se mueve | Script no adjunto a Mario | Agrega `S6_MarioMove` al cubo |
| No salta | El collider de Mario no toca el suelo | Revisa posición y escala |
| No salta | El `BoxCollider` de Mario está desactivado | Actívalo |
| Salta en el aire al tocar una pared | No se revisa la normal del contacto | Usa `contact.normal.y > 0.5f` |
| Se queda pegado en el aire | Tocó una superficie con normal hacia arriba | Revisa la geometría |
| Salta infinito | Usaste `isPressed` para el salto | Usa `wasPressedThisFrame` |
| Se hunde en el suelo | `Use Gravity` activo | Desactívalo en el Rigidbody |
| Cae lentísimo | `gravity` muy bajo | Usa `70.3125` |
| Cae altísimo | `gravity` muy alto o doble gravedad | Revisa `Use Gravity` |
| Se resbala demasiado | `braking` muy bajo | Súbelo |
| Se detiene de golpe | `acceleration` muy alta | Bájala |
| Gira en el aire | Constraints mal | Freeze Rotation X y Z |
| Se mueve en Z | Constraints mal | Freeze Position Z |
| Atraviesa el suelo | Collision Detection en Discrete | Pon Continuous |
| El salto se siente corto | `jumpGravity` muy alto | Bájalo |
| El salto se siente flotante | `gravity` muy baja | Súbela |
| La cámara no ve al jugador | Cámara mal posicionada | Position `(0, 4, -16)` |
| `linearVelocity` no existe | Unity anterior a 6 | Usa `rb.velocity` |

---

## 10. Retos

### 10.1 Derrape

En SMB3, si presionas la dirección contraria, usa una aceleración más fuerte: `2/16 = 0.125 px/frame²`, o `28.125 u/s²`.

Pista:

```csharp
bool turning = vx != 0f && Mathf.Sign(input) != Mathf.Sign(vx);
float rate = turning ? 28.125f : acceleration;
```

Agrégalo en la rama donde `input != 0` y `grounded` es verdadero.

### 10.2 Medidor P

SMB3 llena un medidor mientras corres en el suelo. Cuando está lleno, la velocidad máxima sube de `$28` a `$38`.

Pista:

```csharp
// p va de 0 a 1
if (runHeld && grounded && Mathf.Abs(vx) >= runSpeed) p += Time.deltaTime * 0.5f;
else p -= Time.deltaTime * 0.5f;
p = Mathf.Clamp01(p);

float topSpeed = (p >= 1f && runHeld) ? 13.125f : (runHeld ? runSpeed : walkSpeed);
```

Ajusta `0.5f` para que el medidor tarde lo que quieras.

### 10.3 Bonus de salto por velocidad

El original resta hasta `$08/16 = 0.5 px/frame` al impulso del salto según la velocidad horizontal. En Unity son hasta `1.875 u/s`.

Pista:

```csharp
float[] bonus = { 0f, 0.46875f, 0.9375f, 1.875f };
int index = Mathf.Min((int)(Mathf.Abs(vx) / 3.75f), 3);
vy = jumpSpeed + bonus[index];
```

### 10.4 Animación

- Voltea el sprite con `flipX` según `vx`.
- Cambia el frame de caminata según `Mathf.Abs(vx)`.
- Usa un frame distinto para salto y caída.

### 10.5 Cámara lateral

La cámara fija sirve para aprender. Para el juego final, sigue al jugador solo en X:

```csharp
Vector3 p = transform.position;
p.x = Mathf.Lerp(p.x, target.position.x + offset.x, speed * Time.deltaTime);
transform.position = p;
```

Así la cámara no sube con el salto, como en SMB3.

### 10.6 Sonido

Agrega un `AudioSource` y reproduce:

- sonido de salto al presionar,
- sonido de aterrizaje al tocar suelo,
- sonido de pasos mientras caminas.

No es parte de la física, pero es parte de la sensación.

---

## 11. Checklist final

- [ ] Escena `escena6_mario3` creada.
- [ ] Suelo y plataformas con `BoxCollider`.
- [ ] Mario con `BoxCollider` activo.
- [ ] Mario con `Rigidbody` y `Use Gravity` desactivado.
- [ ] `Mario` con constraints de rotación y Z.
- [ ] Script `S6_MarioMove` adjunto.
- [ ] Caminar, correr y saltar funcionan.
- [ ] Salto corto y largo se sienten distintos.
- [ ] El cubo no atraviesa el suelo.
- [ ] Entiendes qué hace cada valor.
- [ ] Puedes explicar las tres ideas de la sección 8.

---

## 12. Referencias

- Desensamblado de SMB3: https://github.com/captainsouthbird/smb3
- Movimiento del jugador: https://github.com/captainsouthbird/smb3/blob/master/PRG/prg008.asm
- Constantes: https://github.com/captainsouthbird/smb3/blob/master/smb3.asm
- Port legible en JavaScript: https://github.com/velipso/smb3-physics
- Notas de física de SMB3: https://frameadvance.net/games/super-mario-bros-3/

**Nota legal:** SMB3 y sus assets son propiedad de Nintendo. Este material es para estudio. No distribuyas ROMs ni assets del juego. Usa cubos o sprites propios en clase.
