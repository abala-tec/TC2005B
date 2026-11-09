# Guía: enemigos que persiguen con BFS (Escena 6)

**Idea en una frase:** convertimos el piso en una cuadrícula (grid) de casillas, marcamos cuáles tienen pared, y BFS nos dice por qué casillas debe caminar el enemigo para llegar al jugador **rodeando las paredes**.

| Bloque | Tema | Tiempo |
|---|---|---|
| 1 | Qué es un grid y cómo se convierte mundo ↔ casilla | 30 min |
| 2 | Marcar casillas con pared | 20 min |
| 3 | BFS en papel (pizarrón) | 25 min |
| 4 | BFS en código | 25 min |
| 5 | Conectar al enemigo y probar | 20 min |

---

## 0. Preparación en la escena

Tu escena: `Plane` en (12.59, 0, 12.52) con escala 2.5 → mide **25 × 25** unidades (el Plane base mide 10). Las paredes (`paredes/pared_1…6`) están encima; algunas están **rotadas** (no alineadas al grid), por eso detectaremos paredes con física y no a mano.

> ⚠️ Con casillas de 0.5, un Plane de 25 son **50 × 50 casillas**. Si quieres exactamente 15 × 15, cambia la escala del Plane a **0.75** (7.5 / 0.5 = 15). El código funciona con cualquier tamaño: solo cambia `ancho` y `alto`.

1. Crea la capa **Pared** (Inspector → Layer → Add Layer).
2. Selecciona el objeto `paredes` → Layer = `Pared` → "Yes, change children".
3. Crea un GameObject vacío llamado `Grid`, ponle el script `S6_Grid` (sección 1) y arrastra el `Plane` al campo `plano`. Selecciona la capa `Pared` en `capaParedes`.

---

## 1. El grid: una casilla = (x, z) enteros

El mundo usa decimales; el grid usa enteros. Solo necesitamos **dos funciones de conversión**.

```
 z
 ↑  (0,2) (1,2) (2,2)        cada casilla mide 0.5 x 0.5
    (0,1) (1,1) (2,1)        casilla (x,z) → centro en el mundo:
    (0,0) (1,0) (2,0)  → x   origen + (x + 0.5) * celda
 origen = esquina inferior izquierda del Plane
```

Guardamos las casillas como `Vector2Int` (`.x` = columna, `.y` = fila en Z del mundo).

---

## 2. Script `S6_Grid.cs` (grid + paredes + BFS)

```csharp
using System.Collections.Generic;
using UnityEngine;

public class S6_Grid : MonoBehaviour
{
    public static S6_Grid Instancia;       // para que los enemigos lo encuentren fácil

    public Transform plano;                // el Plane
    public LayerMask capaParedes;          // capa "Pared"
    public int ancho = 50;                 // casillas en X
    public int alto = 50;                  // casillas en Z
    public float celda = 0.5f;             // tamaño de cada casilla
    public float margen = 0.25f;           // "engorda" las paredes para que quepa el enemigo

    Vector3 origen;                        // esquina inferior izquierda del grid
    bool[,] bloqueada;                     // true = hay pared

    void Awake()
    {
        Instancia = this;

        // centramos el grid sobre el Plane
        origen = plano.position - new Vector3(ancho * celda / 2f, 0f, alto * celda / 2f);

        // marcamos las casillas con pared
        bloqueada = new bool[ancho, alto];
        Vector3 mitad = new Vector3(celda / 2f + margen, 0.5f, celda / 2f + margen);
        for (int x = 0; x < ancho; x++)
            for (int z = 0; z < alto; z++)
            {
                Vector3 centro = CeldaAMundo(new Vector2Int(x, z)) + Vector3.up * 0.75f;
                bloqueada[x, z] = Physics.CheckBox(centro, mitad, Quaternion.identity, capaParedes);
            }
    }

    // ---------- Conversiones ----------
    public Vector2Int MundoACelda(Vector3 p)
    {
        int x = Mathf.FloorToInt((p.x - origen.x) / celda);
        int z = Mathf.FloorToInt((p.z - origen.z) / celda);
        return new Vector2Int(x, z);
    }

    public Vector3 CeldaAMundo(Vector2Int c)
    {
        return new Vector3(origen.x + (c.x + 0.5f) * celda, 0.5f, origen.z + (c.y + 0.5f) * celda);
    }

    // ---------- Consultas ----------
    public bool Libre(Vector2Int c)
    {
        bool dentro = c.x >= 0 && c.x < ancho && c.y >= 0 && c.y < alto;
        return dentro && !bloqueada[c.x, c.y];
    }

    // ---------- BFS ----------
    static readonly Vector2Int[] direcciones =
        { Vector2Int.right, Vector2Int.left, Vector2Int.up, Vector2Int.down };

    // Devuelve la lista de casillas desde (sin incluir) 'inicio' hasta 'meta'. null si no hay camino.
    public List<Vector2Int> BuscarCamino(Vector2Int inicio, Vector2Int meta)
    {
        if (!Libre(inicio) || !Libre(meta)) return null;

        Queue<Vector2Int> cola = new Queue<Vector2Int>();
        Dictionary<Vector2Int, Vector2Int> vinoDe = new Dictionary<Vector2Int, Vector2Int>();

        cola.Enqueue(inicio);
        vinoDe[inicio] = inicio;                       // también sirve como "visitado"

        while (cola.Count > 0)
        {
            Vector2Int actual = cola.Dequeue();
            if (actual == meta) break;                 // ya llegamos

            foreach (Vector2Int d in direcciones)
            {
                Vector2Int vecino = actual + d;
                if (!Libre(vecino)) continue;          // pared o fuera del plano
                if (vinoDe.ContainsKey(vecino)) continue;  // ya visitada

                vinoDe[vecino] = actual;               // recordamos de dónde vinimos
                cola.Enqueue(vecino);
            }
        }

        if (!vinoDe.ContainsKey(meta)) return null;    // la meta nunca fue alcanzada

        // reconstruir camino: de la meta hacia atrás hasta el inicio
        List<Vector2Int> camino = new List<Vector2Int>();
        Vector2Int c = meta;
        while (c != inicio)
        {
            camino.Add(c);
            c = vinoDe[c];
        }
        camino.Reverse();
        return camino;
    }

    // Dibuja el grid en la vista Scene (rojo = pared). Muy útil para explicar.
    void OnDrawGizmos()
    {
        if (bloqueada == null) return;
        for (int x = 0; x < ancho; x++)
            for (int z = 0; z < alto; z++)
            {
                Gizmos.color = bloqueada[x, z] ? new Color(1, 0, 0, 0.5f) : new Color(1, 1, 1, 0.1f);
                Gizmos.DrawCube(CeldaAMundo(new Vector2Int(x, z)), new Vector3(celda, 0.05f, celda) * 0.95f);
            }
    }
}
```

**Qué explicar aquí (bloques 1 y 2):**
- `MundoACelda` / `CeldaAMundo`: son inversas. Prueba con `Debug.Log` la posición del jugador convertida a casilla.
- `Physics.CheckBox` pregunta: "¿hay un collider de la capa `Pared` dentro de esta caja?". Funciona aunque la pared esté rotada.
- `margen`: la esfera enemiga tiene radio 0.5; sin margen pasaría rozando paredes. Súbelo si se atora.
- Dale Play y mira la vista **Scene**: las casillas rojas deben cubrir las paredes. **Verifícalo antes de seguir.**

---

## 3. BFS: la idea (hazlo en el pizarrón)

BFS = *Breadth-First Search* (búsqueda en anchura). Explora como una **onda en el agua**: primero las casillas a 1 paso, luego a 2 pasos, luego a 3… Como explora en orden de distancia, **la primera vez que toca la meta, ya encontró el camino más corto**.

Necesita solo 2 estructuras:

| Estructura | Para qué | En el código |
|---|---|---|
| **Cola** (fila de espera: el primero que entra, sale primero) | casillas por explorar | `Queue` |
| **Diccionario "vino de"** | no repetir casillas y poder reconstruir el camino | `Dictionary` |

Algoritmo en 5 pasos:
1. Mete el `inicio` a la cola.
2. Saca la primera casilla de la cola (`actual`).
3. Para cada vecino (arriba, abajo, izq, der): si no es pared y no se ha visitado → anota `vinoDe[vecino] = actual` y mételo a la cola.
4. Repite 2–3 hasta llegar a la `meta` (o hasta que la cola se vacíe = no hay camino).
5. Reconstruye: parte de la `meta` y sigue `vinoDe` hacia atrás hasta el `inicio`; luego invierte la lista.

Ejemplo para dibujar (`S` = enemigo, `M` = jugador, `#` = pared, número = pasos desde S):

```
 S 1 2 3 4
 1 # # # 5
 2 3 4 # 6      ← el jugador está en la casilla "6"
```
La onda llega a la casilla 6 después de 6 pasos. Para reconstruir el camino vas hacia atrás: 6 → 5 → 4 → 3 → 2 → 1 → S, y luego inviertes la lista.

---

## 4. Enemigo que usa el BFS

En `S6_EnemigoEsfera.cs` agrega estos campos y funciones, y en `MoverEsfera()` **reemplaza** el movimiento cuando `persiguiendo` es verdadero.

```csharp
// --- campos nuevos ---
private List<Vector2Int> camino;       // casillas por recorrer
private float tiempoRecalculo = 0f;
public float cadaCuanto = 0.25f;       // cada cuántos segundos recalcula el camino
```
(agrega `using System.Collections.Generic;` arriba)

```csharp
// --- función nueva ---
void Perseguir()
{
    S6_Grid grid = S6_Grid.Instancia;

    // recalcular el camino cada 0.25 s (no en cada frame: es innecesario)
    tiempoRecalculo -= Time.deltaTime;
    if (tiempoRecalculo <= 0f)
    {
        tiempoRecalculo = cadaCuanto;
        camino = grid.BuscarCamino(grid.MundoACelda(transform.position),
                                   grid.MundoACelda(cubo.position));
    }

    if (camino == null || camino.Count == 0) return;   // sin camino: se queda quieto

    // caminar hacia la siguiente casilla del camino
    Vector3 objetivo = grid.CeldaAMundo(camino[0]);
    objetivo.y = transform.position.y;                  // la altura no cambia
    transform.position = Vector3.MoveTowards(transform.position, objetivo, velocidad * Time.deltaTime);
}
```

Y en `MoverEsfera()`, dentro del `if (persiguiendo)`:

```csharp
void MoverEsfera()
{
    bool persiguiendo = Longitud(cubo.position - transform.position) <= radioDeteccion;

    if (persiguiendo)
    {
        Perseguir();       // <- BFS
        return;            // el resto (esquinas) solo aplica cuando NO persigue
    }

    // ... código de esquinas que ya tenías ...
}
```

**Por qué `camino[0]`:** `BuscarCamino` no incluye la casilla donde está el enemigo, así que `camino[0]` siempre es la **siguiente** casilla a visitar. Al recalcular cada 0.25 s el camino se corrige solo si el jugador se mueve.

---

## 5. Probar y errores comunes

| Síntoma | Causa |
|---|---|
| El enemigo no se mueve | Está/está el jugador fuera del grid o dentro de una pared roja (`BuscarCamino` regresa `null`). Revisa los Gizmos. |
| No hay casillas rojas | `capaParedes` sin asignar o `paredes` sin la capa `Pared`. |
| Casillas rojas desfasadas | El campo `plano` no apunta al Plane, o `ancho/alto × celda` ≠ tamaño del Plane. |
| Se atora en esquinas | Sube `margen`. |
| Enemigos del `Spawner` no persiguen | Se generan en ±50 unidades, fuera del Plane (25 × 25). Reduce `radio` del Spawner o espera a que lleguen. |
| Atraviesa paredes al vagar | Las esquinas (`esquinas[]`) siguen moviéndose en línea recta. BFS solo se usa al perseguir. |

## Extensión (si sobra tiempo)

- **Diagonales:** agrega `(1,1),(1,-1),(-1,1),(-1,-1)` a `direcciones`.
- **Rendimiento con muchos enemigos:** en vez de un BFS por enemigo, haz **un solo BFS desde el jugador** y guarda para cada casilla la dirección a la que debe ir (*flow field*).
- **Dijkstra / A\*:** el siguiente paso cuando las casillas tengan costos distintos.
