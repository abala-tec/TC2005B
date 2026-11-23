# Guía: nuevo combate Velma ↔ Zombie (escena9_final)

Esta guía sirve para actualizar las escenas anteriores (7 y 8) y las diapositivas.
El código de referencia ya está en `escena9_final`.

**Estado:**

| | escena7_fsm | escena8_misc | escena9_final |
|---|---|---|---|
| Código | ✅ migrado | ✅ migrado | ✅ referencia |
| Diapositivas | ✅ T8.8.2 (golpe) · ⏳ 16–20 (sprites/Animator) | ✅ T8.8.3 | — |

**Diapositivas modificadas** (números según el orden de la presentación; editadas directo en el PPTX, sin regenerar el deck):

| Presentación | Diapositiva + notas | Solo imagen + notas | Solo notas | Total |
|---|---|---|---|---|
| T8.8.2 `T8.8.2-Enemigos-FSM.pptx` (escena 7) | 2, 3, 5, 11, 21, 22, 23, 26, 27 | 4 (diagrama FSM) | 1 | **11** |
| T8.8.3 `T8.8.3-Miscelaneos.pptx` (escena 8) | 2, 6, 17, 18, 19, 21, 22, 23, 24, 25 | 8, 20 | — | **12** |

- T8.8.2, imágenes de código nuevas: 11, 21, 22, 23. Pendientes: 16–20 (tutorial de sprite/Animator con `VelmaKick`).
- T8.8.3, imágenes nuevas: 6, 21, 22, 23, 24 (código) y 8, 18, 20, 21, 22, 24 (figuras).

> **Animator:** las tres escenas comparten el mismo controller (`Animations/velma_sprite_walk_2_0.controller`). Desde el commit `d28751b` ("add hack instead")
> el trigger es **`"hack"`** y el estado es **`VelmaHack`**. Antes eran `"kick"` / `VelmaKick`. Por eso las escenas 7 y 8 ahora llaman a `SetTrigger("hack")`.
> Con `SetTrigger("kick")` la animación **no aparecía**: ese trigger ya no existe en el controller.
>
> **Tecla:** escenas 7 y 8 → **F**. Escena 9 → **espacio**.
>
> **Sin impulso hacia adelante (escenas 7 y 8):** se borró `kickImpulse` / `hachazoImpulso` y la línea `horizontal += dir * kickImpulse`.
> Velma ya no se lanza hacia adelante al dar el hachazo; solo se activa la esfera del golpe. `dir` se sigue calculando porque marca hacia dónde va la esfera.
> (La escena 9 todavía conserva `hachazoImpulso = 1.5`.)

> **Velma ya no patea: pega con un hacha.** Todo lo que antes era "patada" / "kick" ahora se llama **hachazo**.
> En las diapositivas cambia también los textos ("patada" → "hachazo", "patear" → "dar un hachazo").

---

## 1. Las reglas nuevas (para las diapositivas)

| Situación | Resultado |
|---|---|
| Velma le da un hachazo al zombie mientras **patrulla** (no la ha visto) | Muere de **1 hachazo** |
| Velma le da un hachazo al zombie mientras la **persigue** | Muere a los **3 hachazos** (`golpes_persiguiendo` en el Inspector) |
| El zombie toca a Velma **de frente** (dentro de `golpe_angulo`) | Velma recibe golpe y empujón |
| Velma acaba de recibir golpe | **1 segundo de invulnerabilidad** (`invulnerableTiempo`) |
| El hachazo pega pero el zombie no muere | El zombie **retrocede** un poco (`retroceso_distancia`); mientras retrocede no camina ni golpea |
| El zombie muere | Se quedan solo el **sprite en el suelo**: se apagan collider y Rigidbody |

- Ya **no existe** la regla de "golpe por la espalda / fuera del cono". Se borraron `PorDetras()` (escena9) e `InsideConeCheck()` (escena8), y la condición del cono en `RecibirPatada` (escena7).
- El **cono de visión sigue existiendo**, pero solo para **ver** a Velma (`VeJugador()`), ya no para decidir golpes.
- Idea para la diapositiva: *"Atácalo antes de que te vea, porque si te persigue es más difícil de matar."*

---

## 2. Tabla de nombres: antes → ahora

Usa esta tabla para buscar y reemplazar en las escenas anteriores y en las diapositivas.

| Archivo | Antes | Ahora | Nota |
|---|---|---|---|
| Velma | `kickImpulse` | *(borrado en esc7 y esc8)* · `hachazoImpulso` (esc9) | En escenas 7 y 8 ya no hay impulso hacia adelante. En escena 9 lleva `[FormerlySerializedAs("kickImpulse")]` |
| Animator | trigger `"kick"` / estado `VelmaKick` | trigger `"hack"` / estado `VelmaHack` | Cambió en el controller compartido. `SetTrigger("kick")` → `SetTrigger("hack")` |
| Velma | `kickBack` | `knockBack` | Retroceso cuando el zombie golpea a Velma. Lleva `[FormerlySerializedAs("kickBack")]` |
| Velma | `kickDuracion` | `hachazoDuracion` | |
| Velma | `kickAlcance` | `hachazoAlcance` | |
| Velma | `kickRadio` | `hachazoRadio` | |
| Velma | `kickTimer` | `hachazoTimer` | |
| Velma | `kickDir` | `hachazoDir` | |
| Velma | `pateados` | `golpeadosPorHachazo` | |
| Velma | `CheckVelmaKick()` | *(borrada)* | Se reemplaza por `RevisarHachazo()` |
| Velma | `RevisarPatada()` | `RevisarHachazo()` | |
| Velma | `CentroPatada()` | `CentroHachazo()` | |
| Zombie | `RecibirPatada(Vector3)` | `RecibirHachazo(Vector3 origenHachazo)` | Regresa `bool`. La posición de Velma se usa para saber hacia dónde retroceder |
| SoundControl | `kick` (AudioClip) | `hachazo` | Lleva `[FormerlySerializedAs("kick")]` |
| SoundControl | `play_kick()` | `play_hachazo()` | |

**¿Qué es `[FormerlySerializedAs("...")]`?** Si renombras una variable pública, Unity pierde el valor que tenía en el Inspector (por ejemplo el AudioClip asignado). Este atributo le dice a Unity: "esta variable antes se llamaba así, conserva su valor". Requiere `using UnityEngine.Serialization;`.

```csharp
using UnityEngine.Serialization;
...
[FormerlySerializedAs("kick")]
public AudioClip hachazo;
```

No cambiaron:
- El sonido `airWush` / `play_airWush()` (es el sonido del hacha al aire).

---

## 3. Cómo funciona (explicación corta)

### Antes (forma vieja)
- El golpe se detectaba **por choque** (`OnCollisionEnter`) y revisando el Animator (`IsName("VelmaKick")` en escenas 7 y 8, `IsName("VelmaHack")` en escena 9).
- Fallaba porque el Animator tarda unos frames en cambiar, y en el mismo choque el zombie golpeaba primero.
- El zombie decidía si moría según **desde dónde** le pegaban:
  - escena7: `RecibirPatada` → muere si el golpe viene **fuera del cono de visión** (`Vector3.Angle(transform.forward, …) > vision_angulo / 2`).
  - escena8: `InsideConeCheck()` (mismo **cono de visión**) para la patada (fuera del cono = muere) **y** para `GolpeVelma` (dentro del cono = golpea).
  - escena9: `PorDetras()` (semiplano de 180°).

### Ahora
1. **Hachazo = esfera invisible enfrente de Velma** (como el filo del hacha). Al presionar espacio, durante 0.25 s se revisa con `Physics.OverlapSphere` si hay un zombie dentro. No depende de choques ni del Animator.
2. **El zombie decide según su estado.** Si está en `EPerseguirState` cuenta golpes; en cualquier otro estado muere de uno.
3. **Golpe del zombie:** sigue siendo por contacto, pero solo de frente, con invulnerabilidad para Velma.
4. **El zombie tiene Rigidbody kinematic.** Sin él, Unity no detecta bien sus choques.
5. **Retroceso del zombie.** Si el hachazo no lo mata, retrocede lejos de Velma durante `retroceso_tiempo`. Mientras tanto la FSM no corre (no camina) y `GolpeVelma` regresa `false`. Antes de moverse revisa el grid (`Libre`) para no atravesar paredes.
6. **Zombie muerto sin física.** Al entrar a `EMuertoState` se llama `DesactivarFisica()`: apaga los colliders y quita el Rigidbody. Velma ya no choca con el cuerpo.

```
 Espacio ──► hachazoTimer = 0.25s ──► cada frame: OverlapSphere enfrente de Velma
                                          │
                                          ▼
                             enemigo.RecibirHachazo(posVelma)
                                          │
         ¿Está persiguiendo?
          NO ──► muere ──► DesactivarFisica()
          SÍ ──► golpes_recibidos++ ──► ¿llegó a golpes_persiguiendo?
                                          SÍ ──► muere ──► DesactivarFisica()
                                          NO ──► retrocede (retroceso_tiempo)
```

---

## 4. Pasos para actualizar una escena anterior

Cambia el prefijo según la escena: `S8_` en escena8. En escena7 las clases no tienen prefijo: `EnemigoCilindro`, `EnemyStateMachine`, `EPerseguirState`.

### Paso 1: State Machine (`S8_EnemyStateMachine.cs`)
Agregar un getter para saber el estado actual:

```csharp
private S8_IEnemyState currentState;

// para saber en que estado esta el enemigo (ej. EstadoActual is S8_EPerseguirState)
public S8_IEnemyState EstadoActual => currentState;
```

### Paso 2: Enemigo (`S8_EnemigoCilindro.cs`)

**a) Variables nuevas:**
```csharp
public float golpe_angulo = 120.0f;   // que tan ancho es "enfrente" para golpear a Velma (180 = toda la mitad delantera)
public int golpes_persiguiendo = 3;   // hachazos para morir si esta persiguiendo (patrullando muere de 1)
public float retroceso_distancia = 1.0f;  // cuanto retrocede al recibir un hachazo
public float retroceso_tiempo = 0.25f;    // cuanto dura el retroceso
private int golpes_recibidos = 0;     // hachazos que lleva
private Vector3 retroceso_vel;        // velocidad del retroceso
private float retroceso_timer = 0f;   // > 0 = esta retrocediendo
```

**b) En `Start()`, el Rigidbody kinematic:**
```csharp
Rigidbody rb = GetComponent<Rigidbody>();
if (rb == null) rb = gameObject.AddComponent<Rigidbody>();
rb.isKinematic = true;
rb.useGravity = false;
```

**c) Borrar `RecibirPatada(...)` y poner `RecibirHachazo(Vector3)`:**
```csharp
public bool RecibirHachazo(Vector3 origenHachazo)
{
    if (muerto) return false;

    bool persiguiendo = esm.EstadoActual is S8_EPerseguirState;
    golpes_recibidos++;

    if (!persiguiendo || golpes_recibidos >= golpes_persiguiendo)
    {
        retroceso_timer = 0f;
        esm.ChangeState(new S8_EMuertoState(this, esm));
        return true;
    }

    // retroceso: lejos de Velma, en el suelo (XZ)
    Vector3 lejos = transform.position - origenHachazo;
    lejos.y = 0f;
    if (lejos.sqrMagnitude < 0.0001f) lejos = -mirada;
    retroceso_vel = lejos.normalized * (retroceso_distancia / retroceso_tiempo);
    retroceso_timer = retroceso_tiempo;
    return true;
}
```

**c2) Retroceso en `Update()`:** mientras retrocede, la FSM no corre:
```csharp
void Update()
{
    if (retroceso_timer > 0f) { Retroceder(); return; }
    esm.Update();
}

// empuja al zombie lejos de Velma, sin atravesar paredes (revisa el grid)
private void Retroceder()
{
    retroceso_timer -= Time.deltaTime;

    Vector3 siguiente = transform.position + retroceso_vel * Time.deltaTime;
    S8_Grid grid = S8_Grid.Instancia;
    if (grid == null || grid.Libre(grid.MundoACelda(siguiente)))
        transform.position = siguiente;
    else
        retroceso_timer = 0f;   // choco con una pared
}
```

**c3) Apagar la física al morir.** Agregar en el enemigo:
```csharp
public void DesactivarFisica()
{
    foreach (Collider c in GetComponents<Collider>()) c.enabled = false;

    Rigidbody rb = GetComponent<Rigidbody>();
    if (rb != null) Destroy(rb);   // un Rigidbody no se puede "apagar": se quita
}
```
Y en `S8_EMuertoState.Enter()`, junto a `enemy.muerto = true;`:
```csharp
enemy.DesactivarFisica();   // solo queda el sprite en el suelo
```

**d) `GolpeVelma` usa `EnFrente` (con `golpe_angulo`) en vez de `InsideConeCheck` (que usaba `vision_angulo`):**
```csharp
public bool GolpeVelma(Vector3 puntoContacto)
{
    if (muerto) return false;
    if (retroceso_timer > 0f) return false;   // mientras retrocede no golpea
    return EnFrente(puntoContacto);
}

private bool EnFrente(Vector3 posVelma)
{
    Vector3 haciaVelma = posVelma - transform.position;
    haciaVelma.y = 0;
    return Vector3.Angle(transform.forward, haciaVelma) <= golpe_angulo / 2;   // escena9 usa `mirada` en vez de transform.forward
}
```

**e) Borrar `InsideConeCheck()` completa** (en escena9 era `PorDetras()`).

### Paso 3: Velma (`S8_VelmaWalk_3D.cs`)

**a) Usings:** agregar `using System.Collections.Generic;` y `using UnityEngine.Serialization;`. Quitar `using UnityEditor...` (rompe el build).

**b) Quitar el impulso hacia adelante y renombrar `kickBack`:**
- Borrar `public float kickImpulse` y la línea `horizontal = horizontal + (dir * kickImpulse);` (Velma ya no se lanza hacia adelante).
- Cambiar `SetTrigger("kick")` → `SetTrigger("hack")`. El controller compartido ahora usa el trigger `hack`.
- Renombrar `kickBack`, conservando su valor del Inspector:
```csharp
[FormerlySerializedAs("kickBack")]
public float knockBack = 10f;         // retroceso al ser golpeada por un zombie
```
Y reemplazar su uso: `empuje_dir * kickBack` → `empuje_dir * knockBack`.

**c) Variables nuevas:**
```csharp
[Header("Combate")]
public float hachazoDuracion = 0.25f;  // cuanto tiempo el hachazo puede pegar
public float hachazoAlcance = 0.8f;    // que tan enfrente esta la esfera
public float hachazoRadio = 0.6f;      // tamaño de la esfera
public float invulnerableTiempo = 1f;  // segundos sin recibir golpes

private float hachazoTimer = 0f;
private Vector3 hachazoDir;
private HashSet<S8_EnemigoCilindro> golpeadosPorHachazo = new HashSet<S8_EnemigoCilindro>();
private float invulnerableTimer = 0f;
```

**d) En `Update()`, dentro del `if` del hachazo (tecla F en escenas 7 y 8), al final:**
```csharp
hachazoTimer = hachazoDuracion;
hachazoDir = new Vector3(dir.x, 0f, dir.y);
golpeadosPorHachazo.Clear();
```

**e) En `Update()`, justo después de ese `if`:**
```csharp
if (hachazoTimer > 0f)
{
    hachazoTimer -= Time.deltaTime;
    RevisarHachazo();
}

if (invulnerableTimer > 0f) invulnerableTimer -= Time.deltaTime;
```

**f) El empujón sin esperar el suelo:** cambiar `if (grounded && velma_empujada)` por `if (velma_empujada)`.

**g) Colisiones:** dejar solo `CheckGround` y `CheckEnemyHit` en `OnCollisionEnter` y `OnCollisionStay`:
```csharp
void OnCollisionEnter(Collision collision) { CheckGround(collision); CheckEnemyHit(collision); }
void OnCollisionStay(Collision collision)  { CheckGround(collision); CheckEnemyHit(collision); }
```

**h) Borrar `CheckVelmaKick()` y agregar `CentroHachazo()`, `RevisarHachazo()` y el gizmo:**
```csharp
Vector3 CentroHachazo()
{
    return transform.position + hachazoDir * hachazoAlcance;
}

void RevisarHachazo()
{
    Collider[] golpeados = Physics.OverlapSphere(CentroHachazo(), hachazoRadio, LayerMask.GetMask("Enemigos"));
    foreach (Collider c in golpeados)
    {
        S8_EnemigoCilindro enemigo = c.GetComponent<S8_EnemigoCilindro>();
        if (enemigo == null || golpeadosPorHachazo.Contains(enemigo)) continue;   // una vez por hachazo
        golpeadosPorHachazo.Add(enemigo);

        if (enemigo.RecibirHachazo(transform.position)) { S8_SoundControl.play_hachazo(); }
    }
}

void OnDrawGizmosSelected()
{
    Vector3 dir = hachazoDir != Vector3.zero ? hachazoDir : Vector3.right;
    Gizmos.color = hachazoTimer > 0f ? Color.red : Color.yellow;
    Gizmos.DrawWireSphere(transform.position + dir * hachazoAlcance, hachazoRadio);
}
```

**i) Invulnerabilidad en `CheckEnemyHit`:**
```csharp
if (invulnerableTimer > 0f) return false;   // primera línea de la función
...
invulnerableTimer = invulnerableTiempo;     // junto a velma_empujada = true;
```

### Paso 4: Sonido (`S8_SoundControl.cs`)
```csharp
using UnityEngine.Serialization;
...
[FormerlySerializedAs("kick")]
public AudioClip hachazo;   // cuando el hachazo de velma le pega a un enemigo

public static void play_hachazo()
{
    instancia.asource.PlayOneShot(instancia.hachazo);
}
```
Borrar `play_kick()`.

### Paso 5: flipX del zombie (solo escena9)
En escenas 7 y 8 el zombie es un cilindro que **rota su transform** (`Quaternion.LookRotation`), así que este paso **no aplica**. Solo en escena9, donde el zombie es un sprite:
```csharp
// antes
enemy.sprender.flipX = (orientacion_h < 0) ? false : true;
// ahora: solo voltea si de verdad se mueve en X
if (Mathf.Abs(orientacion_h) > 0.01f) enemy.sprender.flipX = orientacion_h > 0;
```

---

## 5. Qué tenía cada escena anterior (✅ ya migrado)

| Escena | Archivo | Forma vieja que tenía | Pasos aplicados |
|---|---|---|---|
| escena7_fsm | `S7_VelmaWalk_3D.cs` | Su `CheckEnemyHit()` (~l.203) **es el golpe de Velma**: choque + `IsName("VelmaKick")` | ✅ 3a–3e, 3g, 3h (se borró esa `CheckEnemyHit`; ahora `RevisarHachazo` sin sonido porque escena7 no tiene SoundControl). Se borró `kickImpulse` (sin impulso). `SetTrigger("kick")` → `"hack"` |
| escena7_fsm | `EnemigoFSM/EnemigoCilindro.cs` | `RecibirPatada(Vector3)` (void): muere si el golpe viene fuera del cono de visión (`transform.forward`). Sin Rigidbody. No golpea a Velma | ✅ 2b, 2c, 2c2, 2c3 (grid `S7_Grid`) |
| escena7_fsm | `EnemigoFSM/EMuertoState.cs` | El collider seguía activo al morir. Tenía `using UnityEditor.Callbacks` (rompe el build) | ✅ `enemy.DesactivarFisica()`; se quitaron los usings |
| escena7_fsm | `EnemigoFSM/EnemyStateMachine.cs` | Sin getter de estado | ✅ 1 |
| escena8_misc | `S8_VelmaWalk_3D.cs` | `CheckVelmaKick()` por choque + `IsName("VelmaKick")`, `return` que bloquea el golpe, `CheckEnemyHit` solo en Enter, empuje esperando `grounded`, sin invulnerabilidad, `kickImpulse`/`kickBack`, `SetTrigger("kick")`, `using UnityEditor` | ✅ Paso 3 completo (sin impulso, trigger `hack`) |
| escena8_misc | `S8_EnemigoCilindro.cs` | `RecibirPatada` y `GolpeVelma` usaban `InsideConeCheck()` (**cono de visión**, `vision_angulo`), sin Rigidbody, `using UnityPipeline...` | ✅ Paso 2 completo |
| escena8_misc | `EnemigoFSM/S8_EnemyStateMachine.cs` | Sin getter de estado | ✅ 1 |
| escena8_misc | `EnemigoFSM/S8_EMuertoState.cs` | El collider seguía activo al morir | ✅ `enemy.DesactivarFisica()` |
| escena8_misc | `S8_SoundControl.cs` | `kick` / `play_kick()` | ✅ 4 |

> En escena7 el zombie no golpea a Velma, así que ahí no aplican `golpe_angulo`, `EnFrente`, `knockBack` ni la invulnerabilidad.
>
> Valores conservados con `[FormerlySerializedAs]` (escena8): `knockBack = 10` y el clip `hachazo`. En escenas 7 y 8 `kickImpulse` se borró: Unity ignora el valor viejo que quedó guardado en la escena.

**Para encontrar todo lo viejo:** busca en el proyecto `kick`, `Kick`, `Patada` y `patea`.

---

## 6. Valores en el Inspector (para ajustar)

| Componente | Variable | Default | Qué hace |
|---|---|---|---|
| Velma | `hachazoImpulso` | 1.5 (solo esc9) | Empujoncito de Velma hacia adelante al dar el hachazo. **No existe en esc7 ni esc8** |
| Velma | `knockBack` | 10 (esc8) · 5 (esc9) | Retroceso de Velma cuando el zombie la golpea (no existe en esc7) |
| Velma | `hachazoDuracion` | 0.25 | Tiempo que el hachazo puede pegar |
| Velma | `hachazoAlcance` | 0.8 | Qué tan lejos enfrente está la esfera |
| Velma | `hachazoRadio` | 0.6 | Tamaño de la esfera |
| Velma | `invulnerableTiempo` | 1 | Segundos sin recibir golpe |
| Zombie | `golpes_persiguiendo` | 3 | Hachazos para matarlo si te persigue |
| Zombie | `golpe_angulo` | 120 | Ancho de su "frente" (180 = mitad delantera completa). Solo esc8 y esc9 |
| Zombie | `retroceso_distancia` | 1 | Cuánto retrocede al recibir un hachazo (tiles) |
| Zombie | `retroceso_tiempo` | 0.25 | Cuánto dura el retroceso (no camina ni golpea) |
| SoundControl | `hachazo` | (clip) | Sonido cuando el hachazo pega |

Selecciona a Velma en la escena para ver la esfera del hachazo: amarilla = inactiva, roja = golpeando.

---

## 7. Cómo probar
En escenas 7 y 8 el hachazo es la tecla **F**; en escena 9 es **espacio**.

1. Al abrir la escena, revisa en el Inspector que `hachazo` (SoundControl) y `knockBack` (Velma) conservaron su valor.
1b. Al presionar F (esc7/esc8) se ve la animación del hacha (`VelmaHack`) y Velma **no** se lanza hacia adelante.
2. Hachazo a un zombie que patrulla: muere de 1 golpe.
3. Dejar que te vea y darle hachazos: muere al 3º.
4. Tocarlo de frente: te golpea una vez y te empuja. Durante 1 s no te vuelve a golpear.
5. Tocarlo de costado: no te golpea.
6. Darle un hachazo mientras te persigue: retrocede ~1 tile, no te golpea mientras retrocede, y te da tiempo del siguiente golpe. Contra una pared no la atraviesa.
7. Al morir: Velma puede caminar sobre el cuerpo (sin collider) y solo queda el sprite en el suelo.

---

## 8. Diapositivas a actualizar (siguiente fase)

Los números son el **orden en la presentación**. En T8.8.2 y T8.8.3 el código sale como **imagen**, y su texto completo está en las **notas**: hay que actualizar las dos cosas.

### T8.8.2 — `T8/T8.8.2-enemigos-fsm/T8.8.2-Enemigos-FSM.pptx` (escena 7)

> ✅ **Hecho** (editado en el PPTX, sin regenerar el deck): diapositivas **1 (notas), 2, 3, 4 (diagrama FSM), 5, 11, 21, 22, 23, 26 y 27**, texto y notas.
> También se actualizaron `snippets.py`, `make_figures.py`, `codigo/`, `figuras/fsm_diagrama.png`, `csharp/` y `LEEME.md`.
> ⏳ **Pendientes**: **16–20** (tutorial del sprite y el Animator: capturas y textos de `VelmaKick` / trigger `kick`).
> ⚠️ `build_deck.py` sigue con el texto viejo: no correrlo, porque sobrescribiría los cambios.

| # | Título | Qué cambiar |
|---|---|---|
| 1 | Portada (notas) | "no reaccionaba a una patada" → hachazo |
| 2 | Lo que veremos | "la visión del enemigo y **la patada**… detección del golpe" |
| 3 | Un enemigo que solo deambula | "¿Y si lo **patean**?" |
| 5 | Patrullar, perseguir y morir | Entrada a Muerto: `RecibirPatada()` → `RecibirHachazo()`. Patrullando muere de 1 y persiguiendo de 3; si no muere, retrocede |
| 11 | Estado morir | Agregar `enemy.DesactivarFisica()`: sin collider ni Rigidbody |
| 16, 17, 19 | Patadas de Velma, agregar sprite | Títulos "PATADAS" → hachazo. El sprite ahora es el del hacha (estado `VelmaHack`) |
| 18 | Sprites del kick | Clip/estado `VelmaKick` → `VelmaHack` (sprites del hacha; revisar fps y duración del clip nuevo) |
| 20 | Patadas de Velma, control | Trigger `kick` → `hack`; `Any State → VelmaKick` → `Any State → VelmaHack` |
| 21 | Velma patea con el botón F | `SetTrigger("kick")` → `SetTrigger("hack")`. **Quitar el paso 4** ("Suma kickImpulse a la velocidad horizontal"): ya no hay impulso. Agregar las 3 líneas nuevas (`hachazoTimer`, `hachazoDir`, `golpeadosPorHachazo.Clear()`) |
| 22 | **Colisión + animación = golpe** | **Reescribir**: la hitbox `OverlapSphere` (`RevisarHachazo`) reemplaza a `CheckEnemyHit` + `IsName("VelmaKick")` |
| 23 | **La patada mata si viene por la espalda** | **Reescribir**: 1 golpe patrullando / 3 persiguiendo (`EstadoActual is EPerseguirState`) + retroceso |
| 26 | Tips de debugeo | Fila "La patada no lo mata… llega de frente… VelmaKick" → "revisa la capa Enemigos, `hachazoAlcance`/`hachazoRadio` (gizmo) y el estado" |
| 27 | ¿Preguntas? | "patadas en la espalda" |

Se quedan igual (el cono solo sirve para **ver**): **12, 13, 14, 15**.

### T8.8.3 — `T8/T8.8.3-misc/T8.8.3-Miscelaneos.pptx` (escena 8)

> ✅ **Hecho** (editado en el PPTX, sin regenerar el deck): diapositivas **2, 6, 17, 18, 19, 21, 22, 23, 24, 25** (texto y notas) y **8, 20** (figura y notas).
> Se respetaron los recortes y textos encimados hechos a mano. El código de las imágenes queda en ≥ 12 pt.
> También se actualizaron `snippets.py`, `make_figures.py`, `codigo/`, `figuras/`, `csharp/` y `LEEME.md`.
> ⚠️ `build_deck.py` y los `manifest.json` siguen con la versión vieja: no correr el build.

| # | Título | Qué cambiar |
|---|---|---|
| 2 | Lo que veremos | "el kickback de Velma" → knockBack |
| 6, 8 | Audio (notas) | Clip `kick` / `play_kick()` → `hachazo` / `play_hachazo()`. Explicar `[FormerlySerializedAs]` |
| 17 | Animator y kickback | Título "KICKBACK" → KNOCKBACK |
| 18 | Seis estados y cinco parámetros | `kick → VelmaKick` → `hack → VelmaHack` (estado y parámetro renombrados) |
| 19 | Transiciones bool/trigger | Fila `kick` / `SetTrigger("kick")` → `hack` / `SetTrigger("hack")` |
| 20 | Del código al Animator (notas) | `SetTrigger("kick")` → `SetTrigger("hack")` al presionar F. Ya no hay `kickImpulse` |
| 21 | **Salir del estado y consultarlo** | **Reescribir**: `IsName("VelmaKick")` / `CheckVelmaKick` ya no deciden el golpe; ahora es la hitbox con timer |
| 22 | **Ataque del enemigo: el enemigo decide** | **Reescribir**: `GolpeVelma` con `golpe_angulo` (ya no el cono de visión), Enter **y** Stay, invulnerabilidad, y ya no "se omite CheckVelmaKick" |
| 23 | El vector que apunta lejos | Agregar `invulnerableTimer = invulnerableTiempo` |
| 24 | Impulso con sonido y animación | Ya no espera el suelo (`if (velma_empujada)`). `kickBack = 10` → `knockBack = 10` |
| 25 | Qué vimos | Bloque "04 KICKBACK: el enemigo autoriza el golpe con su cono" → golpe_angulo + invulnerabilidad |

### Archivos fuente de los decks
- Generadores: `T8-8-2_content/` y `T8-8-3_misc/` → `build_deck.py`, `snippets.py`, `make_figures.py`, `make_code_images.py`.
- Imágenes de código: `T8-8-3_misc/codigo/code_anim_kick.png`, `code_enemy_hit.png`, `code_kick_away.png`, `code_push.png` (y sus equivalentes en T8.8.2).
- Copias del código: carpetas `csharp/` (hay que copiar los `.cs` nuevos).
- `LEEME.md` de cada tema y `T8-8-3_misc/reporte.html`.

### No hay que tocar
T8.1 a T8.7: ahí "golpe", "detrás" o "empuja" no tienen que ver con este combate.
