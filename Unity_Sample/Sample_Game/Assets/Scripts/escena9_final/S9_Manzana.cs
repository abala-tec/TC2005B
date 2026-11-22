using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// Genera manzanas (pantallas del beat 'em up) de forma procedural y avanza hacia la derecha.
// Solo hay 2 manzanas: la actual y la siguiente. Al cruzar, la vieja salta adelante (leapfrog).
// Cada manzana necesita los hijos: "Plane" y "entrada" (pared en su borde izquierdo, sirve de puerta).
public class S9_Manzana : MonoBehaviour
{
    public Transform[] manzanas = new Transform[2];
    public GameObject moldePared;               // se clonan para generar el escenario
    public GameObject moldePiedra;
    public GameObject moldeEnemigo;
    public Transform jugador;
    public int numParedes = 8;
    public Vector2 largoPared = new Vector2(4f, 10f);   // largo minimo y maximo de cada pared (al azar)
    public float altoPared = 3f;                // mas alta que los ojos del enemigo (y=2): tapa su cono de vision
    public int numPiedras = 3;
    public int numEnemigos = 3;
    public float tamano = 25f;                  // largo de una manzana (igual al Plane y al Grid)
    public float margenJugador = 0.35f;         // engorda las paredes en el BFS: Velma mide ~1.2 de ancho

    [Header("Animacion de aparicion")]
    public float duracion = 1.2f;
    public float temblor = 0.08f;               // cuanto tiemblan las paredes al salir del suelo

    private int actual = 0;                     // indice de la manzana donde esta el jugador
    private bool abierta = false;               // ya se mataron todos y la puerta esta abierta
    private bool abriendo = false;              // la puerta se esta hundiendo en el suelo
    private List<S9_EnemigoCilindro> enemigos = new List<S9_EnemigoCilindro>();
    private Vector3 mitadPiedra;                // medio tamano de la piedra ya escalada (para CheckBox)

    void Start()
    {
        // escala la piedra a su tamano (rockSize). El paso al moverla (rockStep) es independiente
        float tamanoPiedra = moldePiedra.GetComponent<S9_RockDragDrop>().rockSize;
        Bounds b = moldePiedra.GetComponentInChildren<Renderer>().bounds;   // antes de apagarla: apagada mide 0
        float k = tamanoPiedra / Mathf.Max(b.size.x, b.size.z);
        moldePiedra.transform.localScale *= k;
        Vector3 pp = moldePiedra.transform.position;
        moldePiedra.transform.position = new Vector3(pp.x, b.extents.y * k, pp.z);   // apoyada en el piso (y = 0)
        mitadPiedra = b.extents * k * 0.95f;    // 0.95: tocar el borde de una pared no cuenta como encimarse

        moldePared.SetActive(false);
        moldePiedra.SetActive(false);
        moldeEnemigo.SetActive(false);

        manzanas[1].position = manzanas[0].position + Vector3.right * tamano;
        Generar(manzanas[0]);
    }

    void Update()
    {
        Transform siguiente = manzanas[1 - actual];

        // todos muertos: se abre la entrada de la siguiente manzana
        if (!abierta && !abriendo && enemigos.TrueForAll(e => e.muerto))
            StartCoroutine(Abrir(siguiente.Find("entrada")));

        // el jugador ya cruzo (con el cuerpo completo) a la siguiente manzana
        if (abierta && jugador.position.x > siguiente.position.x + 2f)
        {
            siguiente.Find("entrada").gameObject.SetActive(true);   // se cierra detras del jugador

            Transform vieja = manzanas[actual];
            Limpiar(vieja);
            vieja.position = siguiente.position + Vector3.right * tamano;  // su entrada (cerrada) es la nueva puerta

            actual = 1 - actual;
            abierta = false;
            Generar(siguiente);
        }
    }

    void Generar(Transform m)
    {
        S9_Grid grid = S9_Grid.Instancia;
        grid.plano = m.Find("Plane");
        float margenOriginal = grid.margen;
        grid.margen = margenJugador;            // el BFS valida con el tamano de Velma, no del enemigo

        Vector3 inicio = m.position + new Vector3(2f, 0f, tamano / 2f);
        Vector3 fin = m.position + new Vector3(tamano - 2f, 0f, tamano / 2f);
        List<Transform> paredes = new List<Transform>();
        bool hayCamino = false;

        // genera obstaculos al azar hasta que el BFS encuentre camino de izq a der
        for (int intento = 0; intento < 20 && !hayCamino; intento++)
        {
            Transform contenido = NuevoContenido(m);
            paredes.Clear();
            for (int i = 0; i < numParedes; i++)
            {
                float largo = Mathf.Round(Random.Range(largoPared.x, largoPared.y));   // entero: los bordes caen en lineas del grid
                Transform pared = Crear(moldePared, PosPared(m, largo, out Quaternion rot), rot, contenido).transform;
                pared.localScale = new Vector3(largo, altoPared, moldePared.transform.lossyScale.z);
                paredes.Add(pared);
            }
            Physics.SyncTransforms();           // CheckBox debe ver las paredes recien creadas
            for (int i = 0; i < numPiedras; i++)
            {
                for (int intentoP = 0; intentoP < 30; intentoP++)
                {
                    // centro en multiplos de 0.5 (la celda) + lado entero = bordes alineados al grid, igual que las paredes
                    float x = Mathf.Round(Random.Range(3f, tamano - 3f) * 2f) / 2f;
                    float z = Mathf.Round(Random.Range(2f, tamano - 2f) * 2f) / 2f;
                    Vector3 p = m.position + new Vector3(x, moldePiedra.transform.position.y, z);
                    if (Physics.CheckBox(p, mitadPiedra, moldePiedra.transform.rotation, grid.capaParedes)) continue;   // encima de pared/piedra
                    Crear(moldePiedra, p, moldePiedra.transform.rotation, contenido);
                    Physics.SyncTransforms();   // la siguiente piedra tampoco debe caer sobre esta
                    break;
                }
            }

            Physics.SyncTransforms();           // sin esto CheckBox no ve los objetos recien creados
            grid.calculaGrid();
            hayCamino = grid.BuscarCamino(grid.MundoACelda(inicio), grid.MundoACelda(fin)) != null;
        }

        // muy mala suerte: manzana sin obstaculos, siempre tiene camino
        if (!hayCamino)
        {
            NuevoContenido(m);
            paredes.Clear();
            Physics.SyncTransforms();
            grid.calculaGrid();
        }

        // enemigos en celdas libres, lejos de la entrada y alcanzables por Velma (si no, el juego se traba)
        enemigos.Clear();
        for (int i = 0; i < numEnemigos; i++)
        {
            for (int intento = 0; intento < 50; intento++)
            {
                Vector2Int c = grid.GetRandomCelda();
                Vector3 p = grid.CeldaAMundo(c);
                if (p.x < m.position.x + 8f || grid.BuscarCamino(grid.MundoACelda(inicio), c) == null) continue;

                p.y = moldeEnemigo.transform.position.y;
                GameObject g = Instantiate(moldeEnemigo, p, moldeEnemigo.transform.rotation, m.Find("contenido"));
                S9_EnemigoCilindro e = g.GetComponent<S9_EnemigoCilindro>();
                e.enabled = false;              // apagado mientras sale del suelo: su FSM arranca (Start) ya afuera
                g.SetActive(true);
                enemigos.Add(e);
                break;
            }
        }

        grid.margen = margenOriginal;
        grid.calculaGrid();
        StartCoroutine(Aparecer(paredes, new List<S9_EnemigoCilindro>(enemigos)));
    }

    // posicion al azar para una pared (rotada 0 o 90 grados) sin salirse de la manzana ni tapar entrada/salida
    Vector3 PosPared(Transform m, float largo, out Quaternion rot)
    {
        bool girada = Random.value < 0.5f;
        rot = Quaternion.Euler(0f, girada ? 90f : 0f, 0f);
        float grosor = moldePared.transform.lossyScale.z;
        float medioX = (girada ? grosor : largo) / 2f;
        float medioZ = (girada ? largo : grosor) / 2f;
        // centro en multiplos de 0.5 (la celda) + largo y grosor enteros = bordes alineados al grid del BFS
        float x = Mathf.Round(Random.Range(3f + medioX, tamano - 3f - medioX) * 2f) / 2f;
        float z = Mathf.Round(Random.Range(1f + medioZ, tamano - 1f - medioZ) * 2f) / 2f;
        return m.position + new Vector3(x, altoPared / 2f, z);   // apoyada en el piso (y = 0)
    }

    GameObject Crear(GameObject molde, Vector3 pos, Quaternion rot, Transform padre)
    {
        GameObject g = Instantiate(molde, pos, rot, padre);
        g.SetActive(true);
        return g;
    }

    Transform NuevoContenido(Transform m)
    {
        Limpiar(m);
        Transform c = new GameObject("contenido").transform;
        c.SetParent(m, false);
        return c;
    }

    // Destroy es diferido: se apaga y se saca de la manzana para que CheckBox y Find ya no lo vean
    void Limpiar(Transform m)
    {
        Transform c = m.Find("contenido");
        if (c == null) return;
        c.gameObject.SetActive(false);
        c.SetParent(null);
        Destroy(c.gameObject);
    }

    // la puerta se hunde en el suelo (misma animacion que al aparecer, al reves) y luego se apaga
    IEnumerator Abrir(Transform entrada)
    {
        abriendo = true;
        Vector3 pos = entrada.position;
        Renderer r = entrada.GetComponentInChildren<Renderer>();
        float alto = r != null ? r.bounds.size.y : altoPared;
        yield return SalirDelSuelo(new List<Transform> { entrada }, temblor, alto, true);
        entrada.gameObject.SetActive(false);
        entrada.position = pos;                 // lista para cerrarse detras del jugador
        abriendo = false;
        abierta = true;
    }

    // solo visual: las posiciones finales ya las valido el BFS
    IEnumerator Aparecer(List<Transform> paredes, List<S9_EnemigoCilindro> nuevos)
    {
        StartCoroutine(SalirDelSuelo(paredes, temblor));                              // paredes tiemblan
        yield return SalirDelSuelo(nuevos.ConvertAll(e => e.transform), 0f);         // enemigos no
        foreach (S9_EnemigoCilindro e in nuevos) e.enabled = true;                   // su FSM arranca ya afuera
    }

    // sube los objetos desde abajo del piso hasta su posicion final; temblor = 0 para que no tiemblen
    // hundir = true hace lo contrario: de su posicion actual baja 'alto' hasta quedar bajo el piso
    IEnumerator SalirDelSuelo(List<Transform> objs, float temblor, float alto = -1f, bool hundir = false)
    {
        if (alto < 0f) alto = altoPared;
        Vector3[] fin = new Vector3[objs.Count];
        for (int i = 0; i < objs.Count; i++) fin[i] = objs[i].position;

        for (float t = 0f; t < duracion; t += Time.deltaTime)
        {
            float k = t / duracion;
            for (int i = 0; i < objs.Count; i++)
            {
                Vector3 tiembla = Random.insideUnitSphere * temblor;
                tiembla.y = 0f;
                objs[i].position = fin[i] + Vector3.down * alto * (hundir ? k : 1f - k) + tiembla;
            }
            yield return null;
        }

        for (int i = 0; i < objs.Count; i++) objs[i].position = fin[i] + (hundir ? Vector3.down * alto : Vector3.zero);
    }
}
