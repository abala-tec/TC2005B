# Guía: BFS para que los enemigos persigan al jugador

**Escena:** `escena6_enemigos`  
**Duración:** 2 horas  
**Resultado:** los enemigos salen de su posición, rodean las paredes y llegan al jugador.

La idea completa es:

1. Convertir el piso en una cuadrícula de casillas.
2. Marcar las casillas que tienen pared.
3. Usar BFS para encontrar la ruta más corta entre el enemigo y el jugador.
4. Hacer que el enemigo camine por esa ruta.

## Agenda

| Minutos | Tema |
|---|---|
| 0–10 | Mostrar el resultado y explicar la idea |
| 10–25 | Grid: mundo ↔ casilla |
| 25–45 | Marcar las paredes |
| 45–65 | BFS en el pizarrón |
| 65–95 | BFS en código |
| 95–110 | Enemigo que persigue |
| 110–120 | Spawner, prueba y errores comunes |

---

## 1. Medidas de la escena

Estos son los datos reales de la escena 6:

| Dato | Valor |
|---|---|
| Posición del `Plane` | `(12.59, 0, 12.52)` |
| Escala del `Plane` | `2.5` |
| Tamaño real del `Plane` | `25 × 25` unidades (el Plane base mide 10) |
| Tamaño de cada casilla | `0.5 × 0.5` |
| Casillas del grid | `50 × 50` |
| Origen del grid (esquina inferior izquierda) | `(0.09, 0, 0.02)` |

El origen se calcula así:

```csharp
origen = plano.position - new Vector3(ancho * celda / 2f, 0f, alto * celda / 2f);
```

> Si cambias el tamaño del `Plane`, actualiza `ancho` y `alto`:
> `ancho = tamañoX / 0.5` y `alto = tamañoZ / 0.5`.

```
Z
↑
(0,2)  (1,2)  (2,2)
(0,1)  (1,1)  (2,1)
(0,0)  (1,0)  (2,0)  → X
origen
```

Cada casilla se guarda como `Vector2Int`:

- `.x` = columna en X.
- `.y` = fila en Z.

### Mundo → casilla

```csharp
int x = Mathf.FloorToInt((mundo.x - origen.x) / celda);
int z = Mathf.FloorToInt((mundo.z - origen.z) / celda);
```

### Casilla → mundo

Devuelve el **centro** de la casilla:

```csharp
mundo.x = origen.x + (x + 0.5f) * celda;
mundo.z = origen.z + (z + 0.5f) * celda;
```

**Ejemplo con el jugador:** posición `(1.51, 0.61)`.

```text
x = floor((1.51 - 0.09) / 0.5) = floor(2.84) = 2
z = floor((0.61 - 0.02) / 0.5) = floor(1.18) = 1
```

El jugador está en la casilla `(2, 1)` y su centro es `(1.34, 0.77)`.

> La altura `Y` no se usa. Todo el juego ocurre en el plano `XZ`.

**Mini-check:** antes de seguir, explica por qué se usa `FloorToInt` al entrar al grid y por qué se suma `0.5` al regresar al mundo.

---

## 2. Crear el grid y marcar paredes

### Preparación en Unity

1. Crea una capa llamada `Pared`:
   `Edit → Project Settings → Tags and Layers → Layers → User Layer`.
2. Selecciona el objeto `paredes` y ponle la capa `Pared`.
   Cuando pregunte, elige **“Yes, change children”**.
   Esto incluye las 6 paredes y cualquier hijo que tengan.
3. Crea un GameObject vacío llamado `Grid` en `(0, 0, 0)`.
4. Agrega el script `S6_Grid` y asigna:
   - `plano` = el objeto `Plane`.
   - `capaParedes` = la capa `Pared`.
   - `ancho` = `50`, `alto` = `50`, `celda` = `0.5`.

### Script `S6_Grid.cs` (primera parte)

Crea el archivo en `Assets/Scripts/escena6_enemigos/S6_Grid.cs`:

```csharp
using UnityEngine;

public class S6_Grid : MonoBehaviour
{
    public Transform plano;              // el Plane
    public LayerMask capaParedes;        // capa "Pared"
    public int ancho = 50;               // casillas en X
    public int alto = 50;                // casillas en Z
    public float celda = 0.5f;           // tamaño de cada casilla
    public float margen = 0.25f;         // separación extra alrededor de las paredes

    Vector3 origen;                      // esquina inferior izquierda
    bool[,] bloqueada;                   // true = hay pared

    void Awake()
    {
        // El Plane está centrado; el origen es su esquina inferior izquierda.
        origen = plano.position - new Vector3(ancho * celda / 2f, 0f, alto * celda / 2f);

        bloqueada = new bool[ancho, alto];
        Vector3 mitad = new Vector3(celda / 2f + margen, 0.5f, celda / 2f + margen);

        for (int x = 0; x < ancho; x++)
        {
            for (int z = 0; z < alto; z++)
            {
                Vector3 centro = CeldaAMundo(new Vector2Int(x, z));
                centro.y = 0.75f;

                // ¿Hay algún collider de la capa Pared dentro de esta caja?
                bloqueada[x, z] = Physics.CheckBox(
                    centro, mitad, Quaternion.identity, capaParedes);
            }
        }
    }

    // Mundo → casilla
    public Vector2Int MundoACelda(Vector3 p)
    {
        int x = Mathf.FloorToInt((p.x - origen.x) / celda);
        int z = Mathf.FloorToInt((p.z - origen.z) / celda);
        return new Vector2Int(x, z);
    }

    // Casilla → centro en el mundo
    public Vector3 CeldaAMundo(Vector2Int c)
    {
        return new Vector3(
            origen.x + (c.x + 0.5f) * celda,
            0.5f,
            origen.z + (c.y + 0.5f) * celda
        );
    }

    // ¿La casilla existe y no tiene pared?
    public bool Libre(Vector2Int c)
    {
        bool dentro = c.x >= 0 && c.x < ancho && c.y >= 0 && c.y < alto;
        return dentro && !bloqueada[c.x, c.y];
    }

    // Dibuja las casillas bloqueadas en rojo en la vista Scene.
    void OnDrawGizmos()
    {
        if (bloqueada == null) return;

        for (int x = 0; x < ancho; x++)
        {
            for (int z = 0; z < alto; z++)
            {
                if (!bloqueada[x, z]) continue;

                Gizmos.color = Color.red;
                Gizmos.DrawCube(
                    CeldaAMundo(new Vector2Int(x, z)),
                    new Vector3(celda, 0.05f, celda) * 0.95f
                );
            }
        }
    }
}
```

### Qué explicar

- `origen` es la esquina inferior izquierda del Plane, no su centro.
- `Physics.CheckBox` pregunta: “¿hay una pared dentro de esta casilla?”.
  Como usa la capa `Pared`, no detecta el piso, al jugador ni a los enemigos.
- La caja de detección está a `y = 0.75` y mide `1` de alto.
  Las paredes van de `y = 0` a `y = 1.5`, así que quedan cubiertas.
- `margen` agranda la pared para que el enemigo no pase rozando.
  Si se atora en las esquinas, súbelo. Si no encuentra paso por un hueco, bájalo.
- `Gizmos.DrawCube` es solo para ver el grid en la vista **Scene**.

**Mini-check:** dale Play y mira la vista **Scene**.  
Las casillas rojas deben cubrir exactamente las paredes.  
Si no aparece ninguna, revisa la capa `Pared` y el campo `capaParedes`.

---

## 3. BFS en el pizarrón

BFS significa **Breadth-First Search** (búsqueda en anchura).

Imagina que tiras una piedra al agua: la onda avanza primero a las casillas vecinas, luego a las siguientes, y así sucesivamente. Por eso BFS encuentra el camino **más corto en número de casillas**.

### Las tres estructuras

| Estructura | Para qué sirve |
|---|---|
| **Cola** (`Queue`) | Guarda las casillas que faltan por explorar. El primero que entra es el primero que sale. |
| **Visitado** (`bool[,]`) | Evita visitar la misma casilla dos veces. |
| **Padre** (`Vector2Int[,]`) | Guarda de qué casilla llegamos, para reconstruir el camino. |

### Los 5 pasos

1. Mete la casilla del enemigo a la cola y márcala como visitada.
2. Saca la primera casilla de la cola. Es la `actual`.
3. Si `actual` es la casilla del jugador, ya encontramos el camino.
4. Para cada vecino (derecha, izquierda, arriba, abajo):
   - Si tiene pared o está fuera del grid, ignóralo.
   - Si ya fue visitado, ignóralo.
   - Si es libre, guárdalo como hijo de `actual`, márcalo visitado y mételo a la cola.
5. Repite hasta llegar al jugador o hasta que la cola se vacíe (no hay camino).

### Ejemplo para dibujar

```text
S  1  2  3  4
1  #  #  #  5
2  3  4  #  6
```

- `S` = enemigo.
- `#` = pared.
- `6` = jugador.
- Los números son los pasos desde `S`.

El camino es:

```text
S → 1 → 2 → 3 → 4 → 5 → 6
```

Hay dos casillas marcadas con `1`: las dos están a un paso de `S`. Eso es normal en BFS.

### ¿Por qué es el camino más corto?

Porque BFS explora **por capas**:

1. Primero todas las casillas a 1 paso.
2. Luego todas las que están a 2 pasos.
3. Luego las de 3 pasos.

La primera vez que toca al jugador, lo hace con la menor cantidad de pasos posible.

### Costo

Cada casilla se visita una sola vez y tiene 4 vecinos.

```text
O(ancho × alto) = 50 × 50 = 2500 casillas
```

Para esta escena, BFS es prácticamente instantáneo.

---

## 4. BFS en código

Agrega esta línea arriba del archivo `S6_Grid.cs`:

```csharp
using System.Collections.Generic;
```

Agrega este método **dentro de la clase `S6_Grid`**:

```csharp
static readonly Vector2Int[] direcciones =
{
    Vector2Int.right, Vector2Int.left, Vector2Int.up, Vector2Int.down
};

// Devuelve las casillas del camino, sin incluir el inicio.
// La primera casilla es el siguiente paso. Devuelve null si no hay camino.
public List<Vector2Int> BuscarCamino(Vector2Int inicio, Vector2Int meta)
{
    if (!Libre(inicio)) return null;

    // El jugador puede estar en una casilla marcada por el margen.
    // Si pasa, apuntamos a un vecino libre.
    if (!Libre(meta))
    {
        foreach (Vector2Int d in direcciones)
        {
            if (Libre(meta + d))
            {
                meta += d;
                break;
            }
        }

        if (!Libre(meta)) return null;
    }

    bool[,] visitado = new bool[ancho, alto];
    Vector2Int[,] padre = new Vector2Int[ancho, alto];
    Queue<Vector2Int> cola = new Queue<Vector2Int>();

    cola.Enqueue(inicio);
    visitado[inicio.x, inicio.y] = true;
    bool encontrado = false;

    while (cola.Count > 0)
    {
        Vector2Int actual = cola.Dequeue();

        if (actual == meta)
        {
            encontrado = true;
            break;
        }

        foreach (Vector2Int d in direcciones)
        {
            Vector2Int vecino = actual + d;

            if (!Libre(vecino)) continue;
            if (visitado[vecino.x, vecino.y]) continue;

            visitado[vecino.x, vecino.y] = true;
            padre[vecino.x, vecino.y] = actual;
            cola.Enqueue(vecino);
        }
    }

    if (!encontrado) return null;

    // Reconstruir el camino desde la meta hasta el inicio.
    List<Vector2Int> camino = new List<Vector2Int>();
    Vector2Int c = meta;

    while (c != inicio)
    {
        camino.Add(c);
        c = padre[c.x, c.y];
    }

    camino.Reverse();
    return camino;
}
```

### Qué explicar

- `Libre(inicio)`: el enemigo debe estar en una casilla válida.
- `visitado`: evita ciclos y repeticiones.
- `padre`: guarda “de dónde vine”.
- `cola`: el corazón de BFS; respeta el orden por capas.
- Al final, se camina **hacia atrás** desde la meta usando `padre` y luego se invierte la lista.
- `camino[0]` es el siguiente paso del enemigo, no su casilla actual.
- Si no hay camino, devuelve `null`.

### Prueba rápida (temporal)

Agrega este método a `S6_Grid` solo para comprobar que BFS funciona:

```csharp
void Start()
{
    List<Vector2Int> prueba = BuscarCamino(
        new Vector2Int(2, 1),
        new Vector2Int(45, 45)
    );

    Debug.Log(prueba == null ? "Sin camino" : "Pasos: " + prueba.Count);
}
```

Dale Play. La consola debe mostrar un número de pasos, no `Sin camino`.

Puedes borrar este `Start` después de la prueba.

**Mini-check:** cambia la meta a una casilla dentro de una pared roja.  
BFS debe devolver `null` o buscar un vecino libre, nunca atravesar la pared.

---

## 5. Enemigo que persigue

Abre `Assets/Scripts/escena6_enemigos/S6_EnemigoEsfera.cs` y **reemplaza todo su contenido** por este:

```csharp
using System;
using System.Collections.Generic;
using UnityEngine;

public class S6_EnemigoEsfera : MonoBehaviour
{
    public Transform cubo;              // jugador (ya está asignado en la escena)
    public S6_Grid grid;                // arrastra aquí el objeto Grid
    public float velocidad = 5f;
    public float distanciaContacto = 1.1f;
    public float anguloPisoton = 60f;
    public float cadaCuanto = 0.25f;    // cada cuánto recalcula el camino

    List<Vector2Int> camino;            // casillas por recorrer
    float tiempoRecalculo;
    Vector3 posicionInicial;

    void Start()
    {
        posicionInicial = transform.position;
    }

    void Update()
    {
        Perseguir();
        Pisoton();
    }

    void Perseguir()
    {
        tiempoRecalculo -= Time.deltaTime;

        // Recalcula al inicio y cada "cadaCuanto" segundos.
        if (tiempoRecalculo <= 0f || camino == null || camino.Count == 0)
        {
            tiempoRecalculo = cadaCuanto;

            Vector2Int desde = grid.MundoACelda(transform.position);
            Vector2Int hasta = grid.MundoACelda(cubo.position);

            camino = grid.BuscarCamino(desde, hasta);
        }

        if (camino == null || camino.Count == 0) return;

        // Opcional para la clase: dibuja la ruta en la vista Scene.
        for (int i = 0; i < camino.Count - 1; i++)
        {
            Debug.DrawLine(
                grid.CeldaAMundo(camino[i]) + Vector3.up,
                grid.CeldaAMundo(camino[i + 1]) + Vector3.up,
                Color.yellow
            );
        }

        // Avanzar al centro de la siguiente casilla.
        Vector3 objetivo = grid.CeldaAMundo(camino[0]);
        objetivo.y = transform.position.y;

        transform.position = Vector3.MoveTowards(
            transform.position, objetivo, velocidad * Time.deltaTime);

        // Si ya llegó al centro, quitar esa casilla del camino.
        if ((transform.position - objetivo).sqrMagnitude < 0.001f)
        {
            camino.RemoveAt(0);
        }
    }

    void Pisoton()
    {
        Vector3 haciaCubo = cubo.position - transform.position;

        float horizontal = (float)Math.Sqrt(
            haciaCubo.x * haciaCubo.x + haciaCubo.z * haciaCubo.z);

        float angulo = (float)(Math.Atan2(haciaCubo.y, horizontal) * 180.0 / Math.PI);

        if (angulo >= anguloPisoton && horizontal <= distanciaContacto)
        {
            transform.position = posicionInicial;
            camino = null;
        }
    }
}
```

### Qué explicar

- `cubo` ya apunta al jugador en la escena.
- `grid` es el objeto con el script `S6_Grid`; hay que arrastrarlo en el Inspector.
- `Perseguir` recalcula la ruta cada `0.25` segundos.
  No hace falta recalcular en cada frame; el jugador no cambia de casilla tan rápido.
- `camino[0]` es la siguiente casilla a la que debe caminar el enemigo.
- `MoveTowards` mueve al enemigo sin pasarse del objetivo.
- Cuando llega al centro de la casilla, se elimina de la lista.
- Si el camino se vacía, se vuelve a calcular.
- `Pisoton` conserva el comportamiento de saltar sobre el enemigo.
  Al ser pisado, el enemigo regresa a su posición inicial.

### Asignar en Unity

1. Selecciona el objeto `Enemigo` (está inactivo en la escena).
2. En el componente `S6_EnemigoEsfera`, asigna `grid` = objeto `Grid`.
3. Verifica que `cubo` siga apuntando a `velma_sprite_walk_3D`.

Los clones heredan automáticamente `cubo` y `grid`.

**Mini-check:** coloca un enemigo cerca de una pared y dale Play.  
Debe rodear la pared, no atravesarla.

---

## 6. Spawner: enemigos dentro del grid

El Spawner original genera enemigos lejos del Plane y además está inactivo.  
Para la clase lo cambiaremos para que elija **casillas libres del grid**.

Abre `Assets/Scripts/escena6_enemigos/S6_Spawner.cs` y reemplaza su contenido por:

```csharp
using UnityEngine;

public class S6_Spawner : MonoBehaviour
{
    [SerializeField] private GameObject enemigo;
    public S6_Grid grid;                // arrastra aquí el objeto Grid
    public int numeroEnemigos = 20;

    void Start()
    {
        for (int i = 0; i < numeroEnemigos; i++)
        {
            Vector2Int celda;

            // Elegir una casilla libre al azar.
            do
            {
                celda = new Vector2Int(
                    Random.Range(0, grid.ancho),
                    Random.Range(0, grid.alto)
                );
            } while (!grid.Libre(celda));

            Vector3 posicion = grid.CeldaAMundo(celda);

            GameObject clon = Instantiate(enemigo, posicion, Quaternion.identity);
            clon.name = "EnemigoClon_" + i;

            // El objeto Enemigo de la escena está inactivo.
            // El clon nace inactivo; hay que activarlo.
            clon.SetActive(true);
        }
    }
}
```

### Asignar en Unity

1. Selecciona el objeto `Spawner`.
2. Asigna `grid` = objeto `Grid`.
3. Verifica que `enemigo` siga apuntando al objeto `Enemigo`.
4. Activa el objeto `Spawner` en la jerarquía.
5. Deja el objeto `Enemigo` **inactivo**; el Spawner se encarga de activar los clones.

La posición del Spawner ya no importa: ahora elige casillas de todo el grid.

**Mini-check:** dale Play. Deben aparecer 20 esferas en casillas libres, no dentro de paredes.

---

## 7. Prueba final y errores comunes

### Lista de comprobación

1. En la vista **Scene**, las paredes están cubiertas de rojo.
2. El jugador está dentro del grid:
   su casilla debe estar entre `(0, 0)` y `(49, 49)`.
3. Con un solo enemigo, la ruta amarilla rodea las paredes.
4. Con 20 enemigos, todos persiguen al jugador.
5. La ruta nunca cruza una casilla roja.

### Errores comunes

| Síntoma | Causa y solución |
|---|---|
| No hay casillas rojas | `capaParedes` sin asignar, o `paredes` y sus hijos no tienen la capa `Pared`. |
| El enemigo no se mueve | `grid` sin asignar en el enemigo; el jugador está fuera del grid; no existe camino. |
| El enemigo se atora en una esquina | Sube `margen` en `S6_Grid` (por ejemplo, a `0.35`). |
| El enemigo no pasa por un hueco | Baja `margen` (por ejemplo, a `0.15`). |
| El enemigo se detiene junto al jugador | La casilla del jugador quedó marcada por el margen. BFS usa un vecino libre; si todos están bloqueados, baja `margen`. |
| No aparecen clones | El objeto `Spawner` está inactivo, o `numeroEnemigos` es 0. |
| Los clones no se mueven | Falta `clon.SetActive(true)` en el Spawner. |
| Todos los enemigos se amontonan | Es normal: no hay separación entre enemigos. BFS solo evita paredes. |
| Va lento con 50 enemigos | Sube `cadaCuanto` a `0.5`; o usa un solo BFS desde el jugador para todos. |

---

## 8. Si sobra tiempo

- **Un solo BFS para todos:** calcula el camino desde el jugador una vez y guarda la dirección para cada casilla. Todos los enemigos consultan esa misma tabla.
- **Diagonales:** agrega `(1,1), (1,-1), (-1,1), (-1,-1)` a `direcciones`. El camino se ve más natural, pero hay que cuidar las esquinas.
- **A\*:** el siguiente algoritmo cuando las casillas tienen costos distintos.

---

## Resumen de archivos

| Archivo | Cambio |
|---|---|
| `S6_Grid.cs` | Nuevo: grid, paredes, conversiones, BFS y Gizmos. |
| `S6_EnemigoEsfera.cs` | Reemplazar: persecución con BFS y pisotón. |
| `S6_Spawner.cs` | Reemplazar: enemigos en casillas libres. |
| Escena | Capa `Pared`, objeto `Grid`, referencias y activar `Spawner`. |
