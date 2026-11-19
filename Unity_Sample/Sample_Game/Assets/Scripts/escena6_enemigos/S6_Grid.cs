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