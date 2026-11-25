using System.Collections.Generic;
using UnityEngine;

public class S9_Grid : MonoBehaviour
{
    public static S9_Grid Instancia;       // para que los enemigos lo encuentren fácil

    public Transform plano;                // el Plane
    public LayerMask capaParedes;          // capa "Pared"
    public int ancho = 50;                 // casillas en X
    public int alto = 50;                  // casillas en Z
    public float celda = 0.5f;             // tamaño de cada casilla
    public float margen = 0.25f;           // "engorda" las paredes para que quepa el enemigo
    public int version = 0;                // sirve para notificar a los enemigos que se actualizo el grid

    Vector3 origen;                        // esquina inferior izquierda del grid
    bool[,] bloqueada;                     // true = hay pared

    void Awake()
    {
        Instancia = this;
        capaParedes |= LayerMask.GetMask("Cajas");   // las cajas/ataudes tambien bloquean casillas (y no se enciman al generarse)
        calculaGrid();
    }

    public void calculaGrid()
    {
        // centramos el grid sobre el Plane (aqui y no en Awake: el plano cambia al cambiar de manzana)
        origen = Origen();

        // marcamos las casillas con pared
        bloqueada = new bool[ancho, alto];
        // de y = 0.05 a 1.25: ve objetos bajos (ataudes) sin tocar el piso
        Vector3 mitad = new Vector3(celda / 2f + margen, 0.6f, celda / 2f + margen);
        for (int x = 0; x < ancho; x++) {
            for (int z = 0; z < alto; z++)
            {
                Vector3 centro = CeldaAMundo(new Vector2Int(x, z)) + Vector3.up * 0.15f;
                bloqueada[x, z] = Physics.CheckBox(centro, mitad, Quaternion.identity, capaParedes);
            }
        }
        version++;
    }

    // ---------- Conversiones ----------
    // esquina inferior izquierda del grid segun el plano actual (sirve aunque todavia no se llame calculaGrid)
    Vector3 Origen()
    {
        return plano.position - new Vector3(ancho * celda / 2f, 0f, alto * celda / 2f);
    }

    // mueve p (en X,Z) a la linea o centro de casilla mas cercano: un objeto centrado ahi
    // bloquea las mismas casillas a ambos lados (queda en medio de sus bloques)
    public Vector3 Alinear(Vector3 p)
    {
        Vector3 o = Origen();
        float paso = celda / 2f;
        p.x = o.x + Mathf.Round((p.x - o.x) / paso) * paso;
        p.z = o.z + Mathf.Round((p.z - o.z) / paso) * paso;
        return p;
    }

    // esquinas (min y max en X,Z) de las casillas que bloquea este collider, con la MISMA prueba que calculaGrid
    // (CheckBox por casilla engordada por 'margen'), solo que a la altura del collider: sirve aunque este en el aire
    public void RectBloqueado(Collider col, out Vector3 min, out Vector3 max)
    {
        Vector3 o = Origen();
        Bounds b = col.bounds;
        Vector3 mitad = new Vector3(celda / 2f + margen, b.extents.y, celda / 2f + margen);
        int x0 = Mathf.FloorToInt((b.min.x - margen - o.x) / celda) - 1, x1 = Mathf.FloorToInt((b.max.x + margen - o.x) / celda) + 1;
        int z0 = Mathf.FloorToInt((b.min.z - margen - o.z) / celda) - 1, z1 = Mathf.FloorToInt((b.max.z + margen - o.z) / celda) + 1;
        int ax = int.MaxValue, az = int.MaxValue, bx = int.MinValue, bz = int.MinValue;
        Collider[] toca = new Collider[16];
        for (int x = x0; x <= x1; x++)
            for (int z = z0; z <= z1; z++)
            {
                Vector3 centro = new Vector3(o.x + (x + 0.5f) * celda, b.center.y, o.z + (z + 0.5f) * celda);
                int n = Physics.OverlapBoxNonAlloc(centro, mitad, toca, Quaternion.identity, 1 << col.gameObject.layer);
                if (System.Array.IndexOf(toca, col, 0, n) < 0) continue;
                ax = Mathf.Min(ax, x); az = Mathf.Min(az, z); bx = Mathf.Max(bx, x); bz = Mathf.Max(bz, z);
            }
        if (ax == int.MaxValue) { min = max = b.center; return; }   // no toca ninguna casilla
        min = new Vector3(o.x + ax * celda, 0f, o.z + az * celda);
        max = new Vector3(o.x + (bx + 1) * celda, 0f, o.z + (bz + 1) * celda);
    }

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

    // regresa una celda random libre para el estado de patrullar
    public Vector2Int GetRandomCelda()
    {
        // libres = bloqueada al reves: lista de las casillas sin objetos ni paredes
        List<Vector2Int> libres = new List<Vector2Int>();
        for (int x = 0; x < ancho; x++)
            for (int z = 0; z < alto; z++)
                if (!bloqueada[x, z]) libres.Add(new Vector2Int(x, z));

        return libres[UnityEngine.Random.Range(0, libres.Count)];   // el maximo es exclusivo
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