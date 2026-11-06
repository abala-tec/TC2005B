# Controles de Super Mario Bros. 3 en Unity 3D

Guía paso a paso para mover al personaje en **X y Z**, con W/S para la profundidad.

> **Entregable:** esta guía y el script `S6_MarioMove3D.cs` que copiarás dentro de Unity.
> **No modifica el proyecto:** tú creas la escena y el script siguiendo los pasos.
> **No reemplaza la guía 2D:** la escena lateral sigue funcionando.

---

## 0. Qué cambia respecto a la guía 2D

Esta guía usa el **mismo código base** de la guía 2D. Solo cambia el plano de movimiento:

| Guía 2D | Guía 3D |
|---|---|
| Movimiento solo en X | Movimiento en X y Z |
| `float vx` | `Vector2 horizontal` |
| `A/D` o flechas izquierda/derecha | `A/D` y `W/S` |
| `FreezePositionZ` | `FreezeRotation` |
| Cámara lateral | Cámara 3/4 |
| Suelo de 30×6 | Suelo de 20×20 |

Lo que **no** cambia:

- Las velocidades de SMB3: `5.625`, `9.375`, `13.125`.
- La aceleración, el frenado y la gravedad.
- El salto variable.
- El momento en el aire.
- La detección de suelo por colisiones y normal del contacto.

**Importante:** esto ya no es SMB3 puro. SMB3 es 2D. Esta versión reutiliza su curva de movimiento, pero agrega profundidad.

Si quieres la explicación completa del desensamblado y de los valores, lee primero:

`T8/T8.9.3-controles-mario3/guia_controles_smb3.md`

---

## 1. Los números que se conservan

| Concepto | Valor en Unity |
|---|---:|
| Caminar | 5.625 u/s |
| Correr | 9.375 u/s |
| Aceleración | 12.3046875 u/s² |
| Frenado | 12.3046875 u/s² |
| Salto | 13.125 u/s |
| Gravedad normal | 70.3125 u/s² |
| Gravedad con salto sostenido | 14.0625 u/s² |
| Umbral de gravedad ligera | 7.5 u/s |
| Caída máxima | 15 u/s |
| Tope horizontal absoluto | 15 u/s |

**Regla:** 1 unidad de Unity = 1 tile = 16 píxeles. SMB3 corre a 60 fps. Por eso:

```text
velocidad Unity  = px/frame   × 3.75
aceleración Unity = px/frame² × 225
```

La fuente original es el desensamblado de SMB3:

- https://github.com/captainsouthbird/smb3
- Movimiento: `PRG/prg008.asm`
- Constantes: `smb3.asm`, líneas 3559–3568

---

## 2. Montar la escena 3D

### 2.1 Requisitos

- Unity 6.3 o superior. El proyecto usa `6000.3.26f1`.
- Paquete **Input System** instalado.
- `Active Input Handling` en **Input System Package (New)** o **Both**.

### 2.2 Crear la escena

1. Abre el proyecto `T8/Unity_Sample/Sample_Game`.
2. `File > New Scene`.
3. Elige **Basic** o **Empty**.
4. Guarda como `Assets/Scenes/escena7_mario3d.unity`.

Si elegiste **Empty**, agrega `GameObject > Light > Directional Light`.

Puedes usar otro nombre de escena. Solo no reemplaces `escena6_mario3` si ya hiciste la guía 2D.

### 2.3 Crear el suelo

1. `GameObject > 3D Object > Cube`.
2. Nómbralo `Suelo`.
3. Transform:
   - Position: `(0, -0.5, 0)`
   - Scale: `(20, 1, 20)`
4. La superficie superior queda en `y = 0`.

Es un cuadrado de 20×20 para que W/S tengan espacio.

### 2.4 Crear el jugador

1. `GameObject > 3D Object > Cube`.
2. Nómbralo `Mario`.
3. Transform:
   - Position: `(0, 0.5, 0)`
   - Scale: `(1, 1, 1)`
4. El cubo trae su `BoxCollider` automático.

### 2.5 Configurar el Rigidbody

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
| Constraints | **Freeze Rotation** |

`Freeze Rotation` congela los tres ejes. En la guía 2D solo congelábamos X y Z y además `FreezePositionZ`. Aquí **no** congeles la posición Z: W/S necesitan ese eje.

### 2.6 Material sin fricción

1. En `Assets`, clic derecho > `Create > Physics > Physics Material` (en versiones anteriores, `Create > Physic Material`).
2. Nómbralo `SinFriccion`.
3. Configura:
   - Dynamic Friction: `0`
   - Static Friction: `0`
   - Bounciness: `0`
   - Friction Combine: `Minimum`
4. En `Mario`, abre el `BoxCollider` y asigna `SinFriccion` en `Material`.

Sin esto, el cubo puede pegarse a las paredes o frenarse solo.

### 2.7 Configurar la cámara

1. Selecciona `Main Camera`.
2. Transform:
   - Position: `(0, 14, -14)`
   - Rotation: `(45, 0, 0)`
3. Field of View: `60`.

Es una vista 3/4 fija. Con el suelo de 20×20, el área completa queda visible.

Cómo se siente:

- `W` mueve a Mario hacia el fondo de la pantalla (+Z).
- `S` lo trae hacia la cámara (-Z).
- `A/D` lo mueven a la izquierda/derecha.

### 2.8 Crear plataformas de prueba

Crea dos o tres cubos:

| Nombre | Position | Scale |
|---|---|---|
| `Plataforma1` | `(5, 1.5, 4)` | `(3, 1, 3)` |
| `Plataforma2` | `(-5, 2.5, -4)` | `(3, 1, 3)` |
| `Plataforma3` | `(0, 3.5, 7)` | `(4, 1, 2)` |

Alturas de la superficie:

- Plataforma 1: `y = 2`.
- Plataforma 2: `y = 3`.
- Plataforma 3: `y = 4`.

Así pruebas saltos en X y en Z, no solo en una línea.

### 2.9 Crear el script

1. En `Assets`, crea la carpeta `Scripts/escena7_mario3d`.
2. Clic derecho > `Create > C# Script`.
3. Nómbralo `S6_MarioMove3D`.
4. Reemplaza todo con el código de la sección 3.
5. Guarda y vuelve a Unity.

El nombre debe ser exactamente `S6_MarioMove3D` para que coincida con la clase.

### 2.10 Conectar el script

1. Selecciona `Mario`.
2. `Add Component > S6_MarioMove3D`.
3. Verifica que los valores de velocidad y gravedad estén como en el código.
4. No hay campos de suelo que asignar: el script usa las colisiones del cubo.

### 2.11 Guardar y probar

1. Guarda la escena.
2. Presiona **Play**.
3. Prueba:
   - `A/D`: izquierda/derecha.
   - `W/S`: profundidad.
   - `Shift` o `X`: correr.
   - `Espacio` o `Z`: saltar.
   - Mantén el salto: sube más.

---

## 3. El script completo

```csharp
using UnityEngine;
using UnityEngine.InputSystem;

public class S6_MarioMove3D : MonoBehaviour
{
    [Header("Velocidades SMB3 (1 unidad = 1 tile)")]
    public float walkSpeed = 5.625f;          // $18 = 1.5 px/frame
    public float runSpeed = 9.375f;           // $28 = 2.5 px/frame
    public float acceleration = 12.3046875f;  // 0.0546875 px/frame²
    public float braking = 12.3046875f;       // frenado al soltar
    public float maxHorizontalSpeed = 15f;    // $40 = 4 px/frame

    [Header("Salto y gravedad")]
    public float jumpSpeed = 13.125f;         // $38 = 3.5 px/frame
    public float gravity = 70.3125f;          // 5/16 px/frame²
    public float jumpGravity = 14.0625f;      // 1/16 px/frame²
    public float jumpHoldLimit = 7.5f;        // $20 = 2 px/frame
    public float maxFallSpeed = 15f;          // $40 = 4 px/frame

    private Rigidbody rb;
    private Vector2 horizontal;               // x = izquierda/derecha, y = Z
    private float vy;
    private bool grounded;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
        rb.useGravity = false;                // la gravedad la pone este script
        rb.constraints = RigidbodyConstraints.FreezeRotation;
    }

    void Update()
    {
        Keyboard kb = Keyboard.current;
        if (kb == null) return;

        // 1. Entrada en X y Z
        float inputX = 0f;
        float inputZ = 0f;

        if (kb.dKey.isPressed || kb.rightArrowKey.isPressed) inputX += 1f;
        if (kb.aKey.isPressed || kb.leftArrowKey.isPressed) inputX -= 1f;
        if (kb.wKey.isPressed || kb.upArrowKey.isPressed) inputZ += 1f;
        if (kb.sKey.isPressed || kb.downArrowKey.isPressed) inputZ -= 1f;

        Vector2 input = new Vector2(inputX, inputZ);

        // Si va en diagonal, la suma no debe valer 1.414.
        if (input.sqrMagnitude > 1f) input.Normalize();

        bool runHeld = kb.leftShiftKey.isPressed || kb.xKey.isPressed;
        bool jumpPressed = kb.spaceKey.wasPressedThisFrame || kb.zKey.wasPressedThisFrame;
        bool jumpHeld = kb.spaceKey.isPressed || kb.zKey.isPressed;

        // 2. Suelo
        if (grounded && vy <= 0f) vy = 0f;

        // 3. Movimiento horizontal en XZ
        float topSpeed = runHeld ? runSpeed : walkSpeed;

        if (input != Vector2.zero)
        {
            Vector2 target = input * topSpeed;

            bool sameDirection = horizontal.sqrMagnitude > 0.01f &&
                                 Vector2.Dot(horizontal.normalized, input) > 0.1f;

            if (sameDirection && horizontal.magnitude > topSpeed)
            {
                // Va más rápido que la meta: en el suelo frena; en el aire conserva.
                if (grounded)
                    horizontal = Vector2.MoveTowards(horizontal, target, braking * Time.deltaTime);
            }
            else
            {
                horizontal = Vector2.MoveTowards(horizontal, target, acceleration * Time.deltaTime);
            }
        }
        else if (grounded)
        {
            // Sin input en el suelo: frena. En el aire conserva la velocidad.
            horizontal = Vector2.MoveTowards(horizontal, Vector2.zero, braking * Time.deltaTime);
        }

        // Tope absoluto de SMB3
        if (horizontal.magnitude > maxHorizontalSpeed)
            horizontal = horizontal.normalized * maxHorizontalSpeed;

        // 4. Salto: solo al presionar, no al mantener
        if (jumpPressed && grounded)
        {
            vy = jumpSpeed;
            grounded = false;
        }

        // 5. Gravedad
        if (!grounded)
        {
            bool lightGravity = jumpHeld && vy > jumpHoldLimit;
            vy -= (lightGravity ? jumpGravity : gravity) * Time.deltaTime;
            vy = Mathf.Max(vy, -maxFallSpeed);
        }

        // 6. Aplicar la velocidad al Rigidbody
        // horizontal.x -> X, horizontal.y -> Z
        rb.linearVelocity = new Vector3(horizontal.x, vy, horizontal.y);
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

En Unity 6 el API es `rb.linearVelocity`. En versiones anteriores se llama `rb.velocity`.

### Nota sobre el Input System

El código usa `Keyboard.current` porque el proyecto ya usa el Input System nuevo. Si tu proyecto usa el Input Manager viejo, cambia la lectura por `Input.GetAxisRaw("Horizontal")` y `Input.GetAxisRaw("Vertical")`, o activa **Both** en Project Settings.

---

## 4. Cómo funciona el movimiento XZ

### 4.1 Leer cuatro direcciones

```csharp
float inputX = 0f;
float inputZ = 0f;

if (kb.dKey.isPressed || kb.rightArrowKey.isPressed) inputX += 1f;
if (kb.aKey.isPressed || kb.leftArrowKey.isPressed) inputX -= 1f;
if (kb.wKey.isPressed || kb.upArrowKey.isPressed) inputZ += 1f;
if (kb.sKey.isPressed || kb.downArrowKey.isPressed) inputZ -= 1f;
```

`inputX` vale `-1`, `0` o `1`. `inputZ` vale lo mismo.

Luego se juntan en un vector:

```csharp
Vector2 input = new Vector2(inputX, inputZ);
```

### 4.2 Normalizar la diagonal

Si presionas `W + D`, el vector vale `(1, 1)`. Su longitud es `1.414`, no `1`. Si no lo normalizas, Mario se movería 41% más rápido en diagonal.

```csharp
if (input.sqrMagnitude > 1f) input.Normalize();
```

`sqrMagnitude` evita calcular la raíz cuadrada cuando no hace falta. Es un detalle de rendimiento, no cambia el resultado.

### 4.3 Mover la velocidad horizontal

Antes tenías:

```csharp
float vx;
```

Ahora tienes:

```csharp
Vector2 horizontal; // X y Z
```

La aceleración es la misma, pero aplicada a un vector:

```csharp
horizontal = Vector2.MoveTowards(horizontal, target, acceleration * Time.deltaTime);
```

`MoveTowards` acerca la velocidad actual a la meta sin pasarse. Eso produce la curva de aceleración de SMB3.

### 4.4 La dirección importa

```csharp
bool sameDirection = horizontal.sqrMagnitude > 0.01f &&
                     Vector2.Dot(horizontal.normalized, input) > 0.1f;
```

`Vector2.Dot` mide si vas en la misma dirección que el input:

- `1` = misma dirección.
- `0` = perpendicular.
- `-1` = dirección contraria.

Si vas en la misma dirección y más rápido que la meta, el código frena en el suelo y conserva el momento en el aire. Es el mismo detalle de SMB3: soltar el botón de correr no te frena en seco.

### 4.5 Aplicar al Rigidbody

```csharp
rb.linearVelocity = new Vector3(horizontal.x, vy, horizontal.y);
```

El eje Y de Unity es el salto. El eje Z es la profundidad. Por eso `horizontal.y` se escribe en la Z del `Vector3`.

### 4.6 Lo que no cambió

- El salto sigue siendo un cambio instantáneo de `vy`.
- La gravedad sigue siendo `70.3125`, o `14.0625` si mantienes el salto y subes rápido.
- El suelo se sigue detectando con `OnCollisionEnter/Stay/Exit` y `contact.normal.y > 0.5`.
- El límite de caída sigue siendo `15`.

---

## 5. Probar y ajustar

### 5.1 Lista de pruebas

- [ ] `D` mueve a la derecha.
- [ ] `A` mueve a la izquierda.
- [ ] `W` mueve hacia el fondo.
- [ ] `S` mueve hacia la cámara.
- [ ] `W + D` va en diagonal.
- [ ] La diagonal no es más rápida que una dirección recta.
- [ ] `Shift` o `X` aumenta la velocidad.
- [ ] Al soltar en el suelo, frena.
- [ ] En el aire, al soltar, conserva la velocidad.
- [ ] `Espacio` salta una sola vez.
- [ ] Mantener salto sube más que un toque.
- [ ] No atraviesa el suelo ni las plataformas.
- [ ] El cubo no gira.

### 5.2 Valores esperados

| Prueba | Resultado aproximado |
|---|---|
| Llegar a velocidad de caminar | 0.46 s |
| Llegar a velocidad de correr | 0.76 s |
| Altura de salto mantenido | 4.5 unidades |
| Altura de salto tocado | 1.2 unidades |
| Caída máxima | 15 u/s |
| Velocidad diagonal | Igual que la recta |

### 5.3 Cómo ajustar

| Si quieres... | Cambia... |
|---|---|
| Que acelere más rápido | sube `acceleration` |
| Que se sienta más resbaloso | baja `braking` |
| Que el salto sea más alto | sube `jumpSpeed` |
| Que el salto sea más flotante | baja `gravity` o `jumpGravity` |
| Que caiga más rápido | sube `gravity` |
| Más velocidad máxima | sube `maxHorizontalSpeed`, pero recuerda que SMB3 topa en 15 |
| Que la cámara vea más área | aléjala o sube el Field of View |

---

## 6. Errores comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| W/S no hacen nada | `FreezePositionZ` sigue activo | Quita ese constraint; deja solo `FreezeRotation` |
| W/S mueven en Y | Confundiste `horizontal.y` con altura | `horizontal.y` debe ir en la Z del `Vector3` |
| La diagonal es más rápida | No normalizaste el input | Usa `input.Normalize()` |
| El cubo gira | Constraints mal | `FreezeRotation` |
| El cubo no salta | El collider no toca el suelo | Revisa posición y escala |
| El cubo se hunde | `Use Gravity` activo | Desactívalo |
| Se pega a las paredes | Falta el material sin fricción | Asigna `SinFriccion` |
| Atraviesa el suelo | Collision Detection en Discrete | Pon Continuous |
| La cámara no ve al jugador | Cámara mal posicionada | Position `(0, 14, -14)`, Rotation `(45, 0, 0)` |
| El jugador se sale de la vista | Se movió fuera del suelo de 20×20 | Usa una cámara que siga o agranda el suelo |
| `linearVelocity` no existe | Unity anterior a 6 | Usa `rb.velocity` |

---

## 7. Retos

### 7.1 Cámara que sigue al jugador

La cámara fija sirve para aprender. Para un juego real, sigue al jugador en X y Z sin subir con el salto:

```csharp
public class S6_CameraFollow3D : MonoBehaviour
{
    public Transform target;
    public Vector3 offset = new Vector3(0, 14, -14);

    void LateUpdate()
    {
        transform.position = new Vector3(
            target.position.x + offset.x,
            offset.y,
            target.position.z + offset.z
        );
    }
}
```

Así la cámara mantiene la altura y sigue el movimiento horizontal.

### 7.2 Rotar el cubo hacia donde camina

1. Cambia el constraint a `FreezeRotationX | FreezeRotationZ` para permitir giro en Y.
2. Calcula el ángulo:

```csharp
if (horizontal.sqrMagnitude > 0.01f)
{
    float angle = Mathf.Atan2(horizontal.x, horizontal.y) * Mathf.Rad2Deg;
    transform.rotation = Quaternion.Euler(0f, angle, 0f);
}
```

`Atan2(x, z)` funciona porque el frente del cubo es +Z.

### 7.3 Medidor P

Cuando el jugador corra en el suelo, llena un medidor. Al llenarse, sube la velocidad máxima de `9.375` a `13.125`.

Pista:

```csharp
if (runHeld && grounded && horizontal.magnitude >= runSpeed) p += Time.deltaTime * 0.5f;
else p -= Time.deltaTime * 0.5f;
p = Mathf.Clamp01(p);

float topSpeed = (p >= 1f && runHeld) ? 13.125f : (runHeld ? runSpeed : walkSpeed);
```

### 7.4 Bonus de salto por velocidad

El original suma hasta `0.5 px/frame` al salto si Mario corre. En Unity son hasta `1.875 u/s`.

```csharp
float[] bonus = { 0f, 0.46875f, 0.9375f, 1.875f };
int index = Mathf.Min((int)(horizontal.magnitude / 3.75f), 3);
vy = jumpSpeed + bonus[index];
```

### 7.5 Animación

- Voltea el sprite según `horizontal.x`.
- Cambia el frame de caminata según `horizontal.magnitude`.
- Usa un frame distinto para salto y caída.

---

## 8. Checklist final

- [ ] Escena `escena7_mario3d` creada.
- [ ] Suelo de 20×20.
- [ ] Mario con `Rigidbody` y `Use Gravity` desactivado.
- [ ] Constraints en `FreezeRotation`, sin `FreezePositionZ`.
- [ ] Material `SinFriccion` asignado.
- [ ] Cámara en `(0, 14, -14)` con rotación `(45, 0, 0)`.
- [ ] Script `S6_MarioMove3D` adjunto.
- [ ] `A/D` y `W/S` funcionan.
- [ ] La diagonal no es más rápida.
- [ ] El salto corto y largo se sienten distintos.
- [ ] El cubo no atraviesa el suelo.
- [ ] Entiendes qué cambió respecto a la guía 2D.

---

## 9. Referencias

- Guía 2D: `T8/T8.9.3-controles-mario3/guia_controles_smb3.md`
- Desensamblado de SMB3: https://github.com/captainsouthbird/smb3
- Movimiento del jugador: https://github.com/captainsouthbird/smb3/blob/master/PRG/prg008.asm
- Constantes: https://github.com/captainsouthbird/smb3/blob/master/smb3.asm
- Port legible en JavaScript: https://github.com/velipso/smb3-physics

**Nota legal:** SMB3 y sus assets son propiedad de Nintendo. Este material es para estudio. No distribuyas ROMs ni assets del juego.
