"""Fragmentos de código que se ven como imagen y se copian en las notas.

Salen de S6_Grid.cs y S6_EnemigoCilindro.cs (se acortan comentarios largos).
"""

# nombre: (código, tamaño de letra, alto de línea)
SNIPPETS = {
    "code_campos": ("""public Transform plano;       // el Plane
public LayerMask capaParedes; // capa "Pared"
public int ancho = 50;        // casillas en X
public int alto = 50;         // casillas en Z
public float celda = 0.5f;    // tamaño de cada casilla
public float margen = 0.1f;   // engorda las paredes

Vector3 origen;               // esquina inferior izquierda
bool[,] bloqueada;            // true = hay pared""", 32, 46),

    "code_conversiones": ("""public Vector2Int MundoACelda(Vector3 p)
{
    int x = Mathf.FloorToInt((p.x - origen.x) / celda);
    int z = Mathf.FloorToInt((p.z - origen.z) / celda);
    return new Vector2Int(x, z);
}

public Vector3 CeldaAMundo(Vector2Int c)
{
    return new Vector3(
        origen.x + (c.x + 0.5f) * celda,
        0.5f,
        origen.z + (c.y + 0.5f) * celda);
}""", 30, 44),

    "code_awake": ("""void Awake()
{
    Instancia = this;
    origen = plano.position - new Vector3(
        ancho * celda / 2f, 0f, alto * celda / 2f);

    bloqueada = new bool[ancho, alto];
    Vector3 mitad = new Vector3(
        celda / 2f + margen, 0.5f, celda / 2f + margen);
    for (int x = 0; x < ancho; x++)
        for (int z = 0; z < alto; z++)
        {
            Vector3 centro = CeldaAMundo(new Vector2Int(x, z))
                           + Vector3.up * 0.75f;
            bloqueada[x, z] = Physics.CheckBox(
                centro, mitad, Quaternion.identity, capaParedes);
        }
}""", 28, 40),

    "code_capa": ("""public LayerMask capaParedes;  // campo del Inspector

void Awake()
{
    // ... (origen y mitad, igual que antes)
    for (int x = 0; x < ancho; x++)
        for (int z = 0; z < alto; z++)
        {
            Vector3 centro = CeldaAMundo(new Vector2Int(x, z))
                           + Vector3.up * 0.75f;
            bloqueada[x, z] = Physics.CheckBox(
                centro, mitad, Quaternion.identity,
                capaParedes);   // solo cuenta la capa Paredes
        }
}""", 28, 40),

    "code_libre": ("""public bool Libre(Vector2Int c)
{
    bool dentro = c.x >= 0 && c.x < ancho
               && c.y >= 0 && c.y < alto;
    return dentro && !bloqueada[c.x, c.y];
}

static readonly Vector2Int[] direcciones =
    { Vector2Int.right, Vector2Int.left,
      Vector2Int.up,    Vector2Int.down };""", 32, 46),

    "code_bfs_a": ("""public List<Vector2Int> BuscarCamino(
    Vector2Int inicio, Vector2Int meta)
{
    if (!Libre(inicio) || !Libre(meta)) return null;

    Queue<Vector2Int> cola = new Queue<Vector2Int>();
    Dictionary<Vector2Int, Vector2Int> vinoDe =
        new Dictionary<Vector2Int, Vector2Int>();

    cola.Enqueue(inicio);
    vinoDe[inicio] = inicio;   // también es "visitado"
""", 32, 46),

    "code_bfs_loop": ("""while (cola.Count > 0)
{
    Vector2Int actual = cola.Dequeue();
    if (actual == meta) break;

    foreach (Vector2Int d in direcciones)
    {
        Vector2Int vecino = actual + d;
        if (!Libre(vecino)) continue;
        if (vinoDe.ContainsKey(vecino)) continue;

        vinoDe[vecino] = actual;
        cola.Enqueue(vecino);
    }
}""", 32, 46),

    "code_bfs_b": ("""    if (!vinoDe.ContainsKey(meta)) return null;

    List<Vector2Int> camino = new List<Vector2Int>();
    Vector2Int c = meta;
    while (c != inicio)
    {
        camino.Add(c);
        c = vinoDe[c];
    }
    camino.Reverse();
    return camino;
}""", 34, 50),

    "code_perseguir": ("""void Perseguir()
{
    S6_Grid grid = S6_Grid.Instancia;

    tiempoRecalculo -= Time.deltaTime;
    if (tiempoRecalculo <= 0f)
    {
        tiempoRecalculo = cadaCuanto;
        camino = grid.BuscarCamino(
            grid.MundoACelda(transform.position),
            grid.MundoACelda(cubo.position));
    }

    if (camino == null || camino.Count == 0) return;

    Vector3 objetivo = grid.CeldaAMundo(camino[0]);
    objetivo.y = transform.position.y;
    transform.position = Vector3.MoveTowards(
        transform.position, objetivo,
        velocidad * Time.deltaTime);
}""", 28, 40),

    "code_campos_enemigo": ("""public Transform cubo;                 // el jugador
public float velocidad = 5.0f;
private List<Vector2Int> camino;       // casillas por recorrer
private float tiempoRecalculo = 0f;
public float cadaCuanto = 0.25f;       // segundos entre cálculos

void Update()
{
    Perseguir();
}""", 32, 46),

    "code_gizmos": ("""void OnDrawGizmos()
{
    S6_Grid grid = S6_Grid.Instancia;
    if (camino == null || camino.Count == 0) return;
    for (int i = 0; i < camino.Count - 1; i++)
    {
        Gizmos.color = new Color(1, 1, 0, 0.9f);
        Gizmos.DrawLine(
            grid.CeldaAMundo(camino[i]) + Vector3.up,
            grid.CeldaAMundo(camino[i + 1]) + Vector3.up);
    }
}""", 30, 44),
}
